from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import urllib.parse
import sys
import subprocess
from api.services.file_storage import storage
from api.services.pilot_mode import PilotConflict, PilotService, digest

router = APIRouter(prefix="/api/workspace", tags=["workspace"])


class CreateFileRequest(BaseModel):
    folder: str
    name: str
    content: str = ""


class RenameFileRequest(BaseModel):
    name: str


class UpdateFileRequest(BaseModel):
    content: str


class PilotSourceRequest(BaseModel):
    source_path: str


class PilotSaveRequest(PilotSourceRequest):
    content: str
    expected_pilot_hash: str


class PilotReviewRequest(PilotSourceRequest):
    accept: bool
    changed: str
    expected_saved: str


def _pilot_call(method: str, source_path: str, **kwargs):
    try:
        service = PilotService(storage.workspace_dir)
        return getattr(service, method)(source_path, **kwargs)
    except PilotConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Cross-platform folder picker
# ---------------------------------------------------------------------------

def _pick_folder_tkinter() -> str | None:
    """Universal fallback using tkinter (ships with CPython on all platforms)."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()          # hide the empty root window
        root.wm_attributes("-topmost", True)
        path = filedialog.askdirectory(title="Select Workspace Folder")
        root.destroy()
        return path or None
    except Exception:
        return None


def _pick_folder_native() -> str | None:
    """Try the best native picker for the current OS; return None on failure."""
    try:
        if sys.platform == "darwin":
            result = subprocess.run(
                ["osascript", "-e",
                 'POSIX path of (choose folder with prompt "Select Workspace Folder")'],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                return result.stdout.strip() or None

        elif sys.platform == "win32":
            # PowerShell one-liner — works on Win 10/11 without extra deps
            ps_cmd = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
                "$f.Description = 'Select Workspace Folder'; "
                "$f.ShowNewFolderButton = $true; "
                "if ($f.ShowDialog() -eq 'OK') { $f.SelectedPath }"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=60,
            )
            if result.returncode == 0:
                return result.stdout.strip() or None

        elif sys.platform.startswith("linux"):
            # Try zenity (GTK / GNOME), then kdialog (KDE), then yad
            for cmd in [
                ["zenity", "--file-selection", "--directory",
                 "--title=Select Workspace Folder"],
                ["kdialog", "--getexistingdirectory", "."],
                ["yad", "--file", "--directory"],
            ]:
                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=60,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                except FileNotFoundError:
                    continue   # binary not installed — try next

    except Exception as e:
        print(f"Native folder picker error: {e}")

    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/files")
def get_input_files():
    try:
        return storage.list_input_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{path:path}")
def read_input_file(path: str):
    try:
        decoded_path = urllib.parse.unquote(path)
        content = storage.read_input_file(decoded_path)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/pick-folder")
def pick_folder():
    """Open a native folder-picker dialog.

    Strategy:
      1. Try the best native dialog for the running OS.
      2. Fall back to tkinter (cross-platform, ships with CPython).
      3. Return {"path": null} if nothing worked — the UI should then let
         the user type a path manually.
    """
    path = _pick_folder_native() or _pick_folder_tkinter()
    return {"path": path}


@router.post("/files")
def create_input_file(req: CreateFileRequest):
    try:
        return storage.create_input_file(req.folder, req.name, req.content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/files/{path:path}")
def delete_input_file(path: str):
    try:
        decoded_path = urllib.parse.unquote(path)
        storage.delete_input_file(decoded_path)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/files/{path:path}")
def update_input_file(path: str, req: UpdateFileRequest):
    try:
        decoded_path = urllib.parse.unquote(path)
        storage.update_input_file(decoded_path, req.content)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/files/{path:path}")
def rename_input_file(path: str, req: RenameFileRequest):
    try:
        decoded_path = urllib.parse.unquote(path)
        return storage.rename_input_file(decoded_path, req.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pilot/start")
def start_pilot(req: PilotSourceRequest):
    return _pilot_call("start", req.source_path)


@router.get("/pilot/status")
def pilot_status(source_path: str):
    return _pilot_call("status", source_path)


@router.post("/pilot/reset")
def reset_pilot(req: PilotSourceRequest):
    return _pilot_call("reset", req.source_path)


@router.post("/pilot/save")
def save_pilot(req: PilotSaveRequest):
    return _pilot_call(
        "save_manual",
        req.source_path,
        changed=req.content,
        expected_pilot_hash=req.expected_pilot_hash,
    )


@router.post("/pilot/review")
def review_pilot(req: PilotReviewRequest):
    return _pilot_call(
        "review",
        req.source_path,
        accept=req.accept,
        changed=req.changed,
        expected_pilot_hash=digest(req.changed.encode("utf-8")),
        expected_saved=req.expected_saved,
    )


@router.post("/pilot/export")
def export_pilot(req: PilotSourceRequest):
    return _pilot_call("export", req.source_path)


@router.post("/pilot/finish")
def finish_pilot(req: PilotSourceRequest):
    return _pilot_call("finish", req.source_path)


@router.get("/styles")
def get_styles():
    try:
        manifest = storage._load_manifest("styles/STYLES.md")
        styles = []
        for name, desc in manifest.items():
            if not name.lower().endswith(".md"):
                styles.append({
                    "name": name.lower(),
                    "description": desc or ""
                })
        return styles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
