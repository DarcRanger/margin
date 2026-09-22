import tempfile
import unittest
from pathlib import Path

from api.services.file_storage import FileStorageService
from api.services.pilot_mode import PilotConflict, PilotService, digest, source_patch


class PilotModeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.source = self.workspace / "chapters" / "chapter.md"
        self.source.parent.mkdir()
        self.original = b"# Chapter One\r\n\r\n\r\n  \\[literal\\]  \r\n- list  \r\nA  \xc2\xb7  B"
        self.source.write_bytes(self.original)
        self.pilot = PilotService(self.workspace)

    def start(self):
        state = self.pilot.start("chapters/chapter.md")
        return state, Path(state["pilot"])

    def test_start_is_byte_identical_and_source_unchanged(self):
        state, copy = self.start()
        self.assertEqual(copy.read_bytes(), self.original)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(state["baseline"], digest(self.original))
        self.assertEqual(state["run"], 1)
        self.assertFalse(state["final_newline"])
        self.assertEqual(state["line_endings"], "CRLF")

    def test_manual_editor_save_changes_only_pilot_and_can_export(self):
        state, copy = self.start()
        changed = self.original.decode().replace("Chapter One", "Chapter Direct Edit")
        result = self.pilot.save_manual(
            state["source_path"], changed=changed, expected_pilot_hash=state["pilot_hash"]
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["decision"], "ACCEPT")
        self.assertEqual(result["verification"], "MANUAL EDIT")
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(copy.read_bytes(), self.original.replace(b"Chapter One", b"Chapter Direct Edit"))
        exported = Path(self.pilot.export(state["source_path"])["path"])
        self.assertEqual(exported.read_bytes(), copy.read_bytes())
        report = exported.with_name("RUN_001_RESULT.txt").read_text(encoding="utf-8")
        self.assertIn("Verification: MANUAL EDIT", report)

    def test_manual_save_refuses_stale_state_and_external_source_change(self):
        state, copy = self.start()
        with self.assertRaisesRegex(PilotConflict, "stale"):
            self.pilot.save_manual(state["source_path"], changed="changed", expected_pilot_hash="BAD")
        self.assertEqual(copy.read_bytes(), self.original)
        self.source.write_bytes(b"external source edit")
        with self.assertRaisesRegex(PilotConflict, "Source changed"):
            self.pilot.save_manual(
                state["source_path"], changed="changed", expected_pilot_hash=state["pilot_hash"]
            )
        self.assertEqual(copy.read_bytes(), self.original)

    def test_harness_accept_and_reject_preserve_source(self):
        state, copy = self.start()
        changed = self.original.decode().replace("Chapter One", "Harness Edit")
        copy.write_bytes(changed.encode())
        accepted = self.pilot.review(
            state["source_path"], accept=True, changed=changed,
            expected_pilot_hash=digest(copy.read_bytes()),
        )
        self.assertEqual(accepted["status"], "PASS")
        self.assertEqual(accepted["verification"], "HARNESS REVIEW")
        self.assertEqual(self.source.read_bytes(), self.original)
        reset = self.pilot.reset(state["source_path"])
        self.pilot.review(
            state["source_path"], accept=False, changed=self.original.decode(),
            expected_pilot_hash=reset["pilot_hash"],
        )
        self.assertEqual(copy.read_bytes(), self.original)

    def test_reset_recovers_external_pilot_but_not_changed_source(self):
        state, copy = self.start()
        copy.write_bytes(b"external pilot edit")
        reset = self.pilot.reset(state["source_path"])
        self.assertEqual(reset["run"], 2)
        self.assertEqual(copy.read_bytes(), self.original)
        self.source.write_bytes(b"external source edit")
        copy.write_bytes(b"another pilot edit")
        with self.assertRaisesRegex(PilotConflict, "Source integrity failure"):
            self.pilot.reset(state["source_path"])
        self.assertEqual(copy.read_bytes(), b"another pilot edit")

    def test_ordinary_endpoints_cannot_change_active_source_or_pilot(self):
        state, copy = self.start()
        storage = FileStorageService(
            base_dir=self.temp.name,
            config_dir=self.workspace / ".config",
            workspace_dir=self.workspace,
        )
        for path in (state["source_path"], state["pilot_path"]):
            with self.assertRaisesRegex(ValueError, "Pilot files"):
                storage.update_input_file(path, "ordinary save")
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(copy.read_bytes(), self.original)

    def test_source_patch_preserves_formatting_and_no_change(self):
        text = self.original.decode()
        self.assertEqual(source_patch(text, text).encode(), self.original)
        self.assertEqual(
            source_patch(text, text.replace("Chapter One", "New")).encode(),
            self.original.replace(b"Chapter One", b"New"),
        )


if __name__ == "__main__":
    unittest.main()
