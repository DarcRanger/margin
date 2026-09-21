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
