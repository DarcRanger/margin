from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.routers import workspace
from api.services.file_storage import FileStorageService


client = TestClient(app)


@pytest.fixture()
def isolated_storage(tmp_path, monkeypatch):
    storage = FileStorageService(
        base_dir=str(tmp_path),
        config_dir=tmp_path / "config",
        workspace_dir=tmp_path / "workspace",
    )
    monkeypatch.setattr(workspace, "storage", storage)
    return storage


def test_workspace_api_file_lifecycle(isolated_storage):
    created = client.post(
        "/api/workspace/files",
        json={"folder": "chapters", "name": "draft", "content": "first"},
    )
    assert created.status_code == 200
    assert created.json() == {
        "name": "draft.md",
        "path": "chapters/draft.md",
        "content": "first",
    }

    listed = client.get("/api/workspace/files")
    assert listed.status_code == 200
    assert [item["path"] for item in listed.json()] == ["chapters/draft.md"]

    read = client.get("/api/workspace/files/chapters%2Fdraft.md")
    assert read.status_code == 200
    assert read.json() == {"content": "first"}

    saved = client.put(
        "/api/workspace/files/chapters%2Fdraft.md",
        json={"content": "second\r\nline"},
    )
    assert saved.status_code == 200
    assert saved.json() == {"success": True}
    target = isolated_storage.workspace_dir / "chapters" / "draft.md"
    assert target.read_bytes() == b"second\r\nline"

    renamed = client.patch(
        "/api/workspace/files/chapters%2Fdraft.md",
        json={"name": "final"},
    )
    assert renamed.status_code == 200
    assert renamed.json() == {"name": "final.md", "path": "chapters/final.md"}
    assert not target.exists()

    deleted = client.delete("/api/workspace/files/chapters%2Ffinal.md")
    assert deleted.status_code == 200
    assert deleted.json() == {"success": True}
    assert not (isolated_storage.workspace_dir / "chapters" / "final.md").exists()


def test_failed_save_is_reported_and_preserves_file(isolated_storage, monkeypatch):
    target = isolated_storage.workspace_dir / "chapters" / "draft.md"
    target.write_text("before", encoding="utf-8")

    def fail_write(path: str, content: str):
        raise OSError("simulated write failure")

    monkeypatch.setattr(isolated_storage, "update_input_file", fail_write)
    response = client.put(
        "/api/workspace/files/chapters%2Fdraft.md",
        json={"content": "after"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "simulated write failure"}
    assert target.read_text(encoding="utf-8") == "before"


@pytest.mark.parametrize("operation", ["read", "save", "rename", "delete"])
def test_existing_file_operations_cannot_cross_workspace_boundary(
    isolated_storage, tmp_path, operation
):
    outside = tmp_path / "outside.md"
    outside.write_text("protected", encoding="utf-8")
    escaped = "../outside.md"

    with pytest.raises(ValueError, match="Access denied"):
        if operation == "read":
            isolated_storage.read_input_file(escaped)
        elif operation == "save":
            isolated_storage.update_input_file(escaped, "changed")
        elif operation == "rename":
            isolated_storage.rename_input_file(escaped, "renamed.md")
        else:
            isolated_storage.delete_input_file(escaped)

    assert outside.read_text(encoding="utf-8") == "protected"


@pytest.mark.parametrize("folder", ["../outside", "outputs", ".private"])
def test_create_rejects_protected_or_escaped_folders(isolated_storage, folder):
    with pytest.raises(ValueError):
        isolated_storage.create_input_file(folder, "draft.md", "blocked")

    assert not (isolated_storage.workspace_dir.parent / "outside" / "draft.md").exists()
