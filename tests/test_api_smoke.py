from fastapi.testclient import TestClient

from api.main import app
from api.routers import workspace
from api.services.file_storage import FileStorageService

client = TestClient(app)


def test_api_root_reports_running():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "SLM Writing Engine API is running"}


def test_workspace_file_listing_is_available(monkeypatch, tmp_path):
    # Never let an automated API test inspect the user's configured workspace.
    isolated_storage = FileStorageService(
        base_dir=str(tmp_path),
        config_dir=tmp_path / "config",
        workspace_dir=tmp_path / "workspace",
    )
    monkeypatch.setattr(workspace, "storage", isolated_storage)
    response = client.get("/api/workspace/files")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_pilot_direct_edit_api_protects_source_and_exports(monkeypatch, tmp_path):
    isolated_storage = FileStorageService(
        base_dir=str(tmp_path),
        config_dir=tmp_path / "config",
        workspace_dir=tmp_path / "workspace",
    )
    monkeypatch.setattr(workspace, "storage", isolated_storage)
    source = isolated_storage.workspace_dir / "chapters" / "chapter.md"
    original = b"# Original\r\n\r\nBody without final newline"
    source.write_bytes(original)

    started = client.post(
        "/api/workspace/pilot/start",
        json={"source_path": "chapters/chapter.md"},
    )
    assert started.status_code == 200
    state = started.json()

    ordinary = client.put(
        "/api/workspace/files/chapters%2Fchapter.md",
        json={"content": "must not write"},
    )
    assert ordinary.status_code == 400
    assert source.read_bytes() == original

    saved = client.post(
        "/api/workspace/pilot/save",
        json={
            "source_path": state["source_path"],
            "content": "# Direct Edit\n\nBody without final newline",
            "expected_pilot_hash": state["pilot_hash"],
        },
    )
    assert saved.status_code == 200
    assert saved.json()["verification"] == "MANUAL EDIT"
    assert source.read_bytes() == original

    exported = client.post(
        "/api/workspace/pilot/export",
        json={"source_path": state["source_path"]},
    )
    assert exported.status_code == 200
    assert source.read_bytes() == original
