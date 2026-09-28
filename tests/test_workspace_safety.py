import os
import tempfile
from pathlib import Path

import pytest

from api.services import file_storage
from api.services.file_storage import FileStorageService


@pytest.fixture()
def storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield FileStorageService(
            base_dir=tmpdir,
            config_dir=Path(tmpdir) / "config",
            workspace_dir=Path(tmpdir) / "sample-workspace",
        )


def test_path_traversal_cannot_escape_workspace(storage):
    with pytest.raises(ValueError, match="Access denied"):
        storage.read_input_file("../../outside.md")


def test_outputs_are_not_exposed_as_editable_inputs(storage):
    output = storage.outputs_dir / "agent-result.md"
    output.write_text("generated", encoding="utf-8")

    with pytest.raises(ValueError, match="Access denied"):
        storage.read_input_file("outputs/agent-result.md")


def test_update_changes_only_explicit_temporary_fixture(storage):
    chapter = storage.workspace_dir / "chapters" / "chapter-1.md"
    neighbor = storage.workspace_dir / "chapters" / "chapter-2.md"
    chapter.write_text("before", encoding="utf-8")
    neighbor.write_text("protected", encoding="utf-8")

    storage.update_input_file("chapters/chapter-1.md", "after")

    assert chapter.read_text(encoding="utf-8") == "after"
    assert neighbor.read_text(encoding="utf-8") == "protected"


def test_hidden_paths_are_blocked(storage):
    hidden = Path(storage.workspace_dir) / ".private" / "notes.md"
    hidden.parent.mkdir(parents=True)
    hidden.write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError, match="Access denied"):
        storage.read_input_file(".private/notes.md")


def test_test_process_uses_isolated_config_directory():
    assert "MARGIN_CONFIG_DIR" in os.environ
    assert "MARGIN_WORKSPACE_DIR" in os.environ
    assert file_storage._CONFIG_DIR == Path(os.environ["MARGIN_CONFIG_DIR"])
    assert file_storage.storage.workspace_dir == Path(os.environ["MARGIN_WORKSPACE_DIR"])


def test_workspace_override_beats_linked_settings(monkeypatch, tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    external_workspace = tmp_path / "protected-manuscript"
    external_workspace.mkdir()
    marker = external_workspace / "chapter.md"
    marker.write_text("must remain unchanged", encoding="utf-8")
    (config_dir / "settings.json").write_text(
        '{"linked_workspace_dir": "' + external_workspace.as_posix() + '"}',
        encoding="utf-8",
    )
    isolated_workspace = tmp_path / "isolated-workspace"
    monkeypatch.setenv("MARGIN_WORKSPACE_DIR", str(isolated_workspace))

    test_storage = FileStorageService(base_dir=str(tmp_path), config_dir=config_dir)

    assert test_storage.workspace_dir == isolated_workspace
    assert marker.read_text(encoding="utf-8") == "must remain unchanged"
    assert sorted(path.name for path in external_workspace.iterdir()) == ["chapter.md"]
