"""Protected, workspace-local Markdown pilot runs."""

import difflib
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _lines(text: str):
    return [
        (match.group(1), match.group(2))
        for match in re.finditer(r"([^\r\n]*)(\r\n|\n|\r|$)", text)
        if match.group(0)
    ]


def source_patch(original: str, changed: str) -> str:
    """Apply changed line content while retaining the source line endings."""
    before, after = _lines(original), _lines(changed)
    preferred = next((ending for _, ending in before if ending), "\n")
    result = []
    matcher = difflib.SequenceMatcher(
        None,
        [line for line, _ in before],
        [line for line, _ in after],
        autojunk=False,
    )
    for tag, start, end, changed_start, changed_end in matcher.get_opcodes():
        if tag == "equal":
            result.extend(before[start:end])
        else:
            old = before[start:end]
            result.extend(
                (line, old[index][1] if index < len(old) else preferred)
                for index, (line, _) in enumerate(after[changed_start:changed_end])
            )
    if result:
        result[-1] = (result[-1][0], before[-1][1] if before else "")
        result = [
            (line, ending or preferred) if index < len(result) - 1 else (line, ending)
            for index, (line, ending) in enumerate(result)
        ]
    return "".join(line + ending for line, ending in result)


class PilotConflict(ValueError):
    """Raised when a protected pilot safety condition is not satisfied."""


class PilotService:
    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()
        self.root = self.workspace / "PILOT"

    def _resolve_source(self, relative: str) -> Path:
        path = (self.workspace / relative).resolve()
        try:
            path.relative_to(self.workspace)
        except ValueError as exc:
            raise PilotConflict("Source must be inside the workspace") from exc
        if (
            self.root == path
            or self.root in path.parents
            or path.suffix.lower() != ".md"
            or not path.is_file()
        ):
            raise PilotConflict("Select an existing Markdown source outside PILOT")
        return path

    def _manifest_path(self, source: Path) -> Path:
        return self.root / f"{source.stem}_Margin_Pilot" / "manifest.json"

    def _read(self, source: Path):
        path = self._manifest_path(source)
        if not path.exists():
            return None
        state = json.loads(path.read_text(encoding="utf-8"))
        approved = (
            Path(state["pilot"]).parent
            / "OUTPUT"
            / f"RUN_{state['run']:03d}_APPROVED.md"
        )
        state["exported"] = approved.exists()
        return state

    def _write(self, state: dict):
        folder = Path(state["pilot"]).parent
        (folder / "OUTPUT").mkdir(parents=True, exist_ok=True)
        (folder / "manifest.json").write_text(
            json.dumps(state, indent=2), encoding="utf-8"
        )
        readable = (
            f"DARC PILOT MODE\nSource: {state['source']}\nPilot: {state['pilot']}\n"
            f"Run: {state['run']:03d}\nBaseline SHA-256: {state['baseline']}\n"
            f"Started: {state['timestamp']}\nLine endings: {state['line_endings']}\n"
            f"Final newline: {state['final_newline']}\nStatus: {state['status']}\n"
        )
        (folder / "PILOT_MANIFEST.txt").write_text(readable, encoding="utf-8")

    def _check(self, state: dict, *, pilot_hash: str | None = None):
        if digest(Path(state["source"]).read_bytes()) != state["baseline"]:
            raise PilotConflict("Source changed externally; pilot save refused")
        if (
            pilot_hash is not None
            and digest(Path(state["pilot"]).read_bytes()) != pilot_hash
        ):
            raise PilotConflict("Pilot changed externally; pilot save refused")

    def active_pilot(self, relative: str):
        for manifest in self.root.glob("*/manifest.json"):
            state = json.loads(manifest.read_text(encoding="utf-8"))
            if state["pilot_path"] == relative and not state.get("finished", False):
                self._check(state, pilot_hash=state["pilot_hash"])
                return state
        return None

    def protected_source(self, relative: str) -> bool:
        for manifest in self.root.glob("*/manifest.json"):
            state = json.loads(manifest.read_text(encoding="utf-8"))
            if state["source_path"] == relative and not state.get("finished", False):
                return True
        return False

    def start(self, relative: str):
        source = self._resolve_source(relative)
        previous = self._read(source)
        if previous and not previous.get("finished", False):
            raise PilotConflict("Pilot exists; use Reset Pilot for another run")
        folder = self._manifest_path(source).parent
        if folder.exists() and not previous:
            raise PilotConflict(
                "Pilot directory exists without a manifest; refusing overwrite"
            )
        raw = source.read_bytes()
        text = raw.decode("utf-8")
        pilot = folder / source.name
        folder.mkdir(parents=True, exist_ok=bool(previous))
        pilot.write_bytes(raw)
        state = {
            "source": str(source),
            "pilot": str(pilot),
            "source_path": relative,
            "pilot_path": pilot.relative_to(self.workspace).as_posix(),
            "run": previous["run"] + 1 if previous else 1,
            "baseline": digest(raw),
            "pilot_hash": digest(raw),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "line_endings": (
                "MIXED"
                if "\r\n" in text and re.search(r"(?<!\r)\n", text)
                else "CRLF"
                if "\r\n" in text
                else "LF"
                if "\n" in text
                else "NONE"
            ),
            "final_newline": text.endswith(("\n", "\r")),
            "status": "NOT VERIFIED",
            "decision": None,
            "verification": None,
            "exported": False,
            "finished": False,
        }
        self._write(state)
        return state

    def status(self, relative: str):
        source = self._resolve_source(relative)
        state = self._read(source)
        return None if state and state.get("finished", False) else state

    def finish(self, relative: str):
        source = self._resolve_source(relative)
        state = self._read(source)
        if not state or state.get("finished", False):
            raise PilotConflict("No active pilot")
        if (
            state["status"] != "PASS"
            or state.get("decision") != "ACCEPT"
            or not state.get("exported", False)
        ):
            raise PilotConflict("An exported accepted PASS result is required before finish")
        self._check(state, pilot_hash=state["pilot_hash"])
        state["finished"] = True
        state["finished_at"] = datetime.now(timezone.utc).isoformat()
        self._write(state)
        return state

    def reset(self, relative: str):
        source = self._resolve_source(relative)
        state = self._read(source)
        if not state:
            raise PilotConflict("No pilot to reset")
        raw = source.read_bytes()
        if digest(raw) != state["baseline"]:
            raise PilotConflict("Source integrity failure; pilot reset refused")
        output_dir = Path(state["pilot"]).parent / "OUTPUT"
        current_report = output_dir / f"RUN_{state['run']:03d}_RESULT.txt"
        next_report = output_dir / f"RUN_{state['run'] + 1:03d}_RESULT.txt"
        if next_report.exists():
            raise PilotConflict("Next run report exists; refusing overwrite")
        if not current_report.exists():
            with current_report.open("x", encoding="utf-8") as file:
                file.write(
                    f"DARC PILOT RUN {state['run']:03d}\nResult: NOT VERIFIED\n"
                    "Decision: RESET WITHOUT REVIEW\n"
                    f"Source SHA-256: {state['baseline']}\n"
                )
        state["run"] += 1
        Path(state["pilot"]).write_bytes(raw)
        state.update(
            pilot_hash=digest(raw),
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="NOT VERIFIED",
            decision=None,
            verification=None,
            exported=False,
        )
        self._write(state)
        return state

    def save_manual(
        self,
        relative: str,
        *,
        changed: str,
        expected_pilot_hash: str,
    ):
        """Save a user-authored editor change only to the disposable pilot."""
        source = self._resolve_source(relative)
        state = self._read(source)
        if not state:
            raise PilotConflict("No active pilot")
        if expected_pilot_hash != state["pilot_hash"]:
            raise PilotConflict("Pilot state is stale; reload before saving")
        self._check(state, pilot_hash=expected_pilot_hash)
        pilot_path = Path(state["pilot"])
        current = pilot_path.read_bytes()
        output = source_patch(current.decode("utf-8"), changed).encode("utf-8")
        pilot_path.write_bytes(output)
        try:
            self._check(state)
        except PilotConflict:
            pilot_path.write_bytes(current)
            raise
        state.update(
            pilot_hash=digest(output),
            status="PASS",
            decision="ACCEPT",
            verification="MANUAL EDIT",
            exported=False,
        )
        self._write(state)
        return state

    def review(
        self,
        relative: str,
        *,
        accept: bool,
        changed: str,
        expected_pilot_hash: str,
        expected_saved: str | None = None,
    ):
        source = self._resolve_source(relative)
        state = self._read(source)
        if not state:
            raise PilotConflict("No active pilot")
        report = (
            Path(state["pilot"]).parent
            / "OUTPUT"
            / f"RUN_{state['run']:03d}_RESULT.txt"
        )
        try:
            self._check(state, pilot_hash=expected_pilot_hash)
        except PilotConflict as exc:
            if not report.exists():
                state["status"] = "FAIL"
                self._write(state)
                with report.open("x", encoding="utf-8") as file:
                    file.write(
                        f"DARC PILOT RUN {state['run']:03d}\nResult: FAIL\n"
                        f"Reason: {exc}\n"
                    )
            raise
        if (
            expected_pilot_hash != state["pilot_hash"]
            and digest(changed.encode("utf-8")) != expected_pilot_hash
        ):
            raise PilotConflict("Pilot content differs from reviewed harness result")
        raw = source.read_bytes()
        output = (
            source_patch(raw.decode("utf-8"), changed)
            if accept
            else raw.decode("utf-8")
        )
        if expected_saved is not None and output != expected_saved:
            raise PilotConflict(
                "Accepted source ranges do not match the reviewed content"
            )
        if report.exists():
            raise PilotConflict("Run result exists; refusing overwrite")
        pilot_path = Path(state["pilot"])
        previous_pilot = pilot_path.read_bytes()
        pilot_path.write_bytes(output.encode("utf-8"))
        try:
            self._check(state)
        except PilotConflict:
            pilot_path.write_bytes(previous_pilot)
            raise
        saved = pilot_path.read_bytes()
        verified = saved == output.encode("utf-8") and (
            not accept
            or output == source_patch(raw.decode("utf-8"), changed)
        )
        state.update(
            pilot_hash=digest(saved),
            status="PASS" if verified else "FAIL",
            decision="ACCEPT" if accept else "REJECT",
            verification="HARNESS REVIEW",
        )
        self._write(state)
        with report.open("x", encoding="utf-8") as file:
            file.write(
                f"DARC PILOT RUN {state['run']:03d}\nResult: {state['status']}\n"
                f"Decision: {'ACCEPT' if accept else 'REJECT'}\n"
                f"Source SHA-256: {state['baseline']}\n"
                f"Pilot SHA-256: {state['pilot_hash']}\n"
                f"Timestamp: {datetime.now(timezone.utc).isoformat()}\n"
            )
        return state

    def export(self, relative: str):
        source = self._resolve_source(relative)
        state = self._read(source)
        if (
            not state
            or state["status"] != "PASS"
            or state.get("decision") != "ACCEPT"
        ):
            raise PilotConflict("An accepted PASS result is required before export")
        self._check(state, pilot_hash=state["pilot_hash"])
        target = (
            Path(state["pilot"]).parent
            / "OUTPUT"
            / f"RUN_{state['run']:03d}_APPROVED.md"
        )
        report = target.with_name(f"RUN_{state['run']:03d}_RESULT.txt")
        if not report.exists():
            with report.open("x", encoding="utf-8") as file:
                file.write(
                    f"DARC PILOT RUN {state['run']:03d}\nResult: PASS\n"
                    "Decision: ACCEPT\n"
                    f"Verification: {state.get('verification') or 'MANUAL EDIT'}\n"
                    f"Source SHA-256: {state['baseline']}\n"
                    f"Pilot SHA-256: {state['pilot_hash']}\n"
                    f"Timestamp: {datetime.now(timezone.utc).isoformat()}\n"
                )
        try:
            with target.open("xb") as file:
                file.write(Path(state["pilot"]).read_bytes())
        except FileExistsError as exc:
            raise PilotConflict("Approved copy already exported") from exc
        state["exported"] = True
        self._write(state)
        return {"path": str(target), "sha256": digest(target.read_bytes())}
