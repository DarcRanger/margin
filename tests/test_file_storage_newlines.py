import tempfile
import unittest

from api.services.file_storage import FileStorageService


class TestFileStorageNewlines(unittest.TestCase):
    def test_read_write_keeps_original_line_endings_and_final_newline(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = FileStorageService(base_dir=directory)
            path = storage.workspace_dir / "chapters" / "roundtrip.md"
            for original in (b"# Title\r\n\r\nA  \xc2\xb7  B", b"# Title\n\nA  \xc2\xb7  B\n"):
                with self.subTest(original=original):
                    path.write_bytes(original)
                    content = storage.read_input_file("chapters/roundtrip.md")
                    storage.update_input_file("chapters/roundtrip.md", content)
                    self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
