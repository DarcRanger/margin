import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from api.routers import assist
from api.services.file_storage import FileStorageService


def _subseq(argv, seq):
    """True when seq appears in argv in order (not necessarily adjacent)."""
    it = iter(argv)
    return all(any(item == want for item in it) for want in seq)


class TestResumeArgv(unittest.TestCase):

    def setUp(self):
        # These tests verify argv construction, not whether every supported
        # third-party agent CLI happens to be installed on the test machine.
        self.which_patcher = patch(
            "api.routers.assist.harness_env.which_harness",
            side_effect=lambda command: command,
        )
        self.which_patcher.start()

    def tearDown(self):
        self.which_patcher.stop()

    def test_opencode_resume_flag(self):
        argv = assist._resolve_harness_argv(
            "opencode", "do it", "/tmp/w", mode="edit", resume_id="ses_abc")
        self.assertTrue(_subseq(argv, ["run", "--session", "ses_abc"]))
        self.assertEqual(argv[-1], "do it")

    def test_opencode_fresh_has_no_resume(self):
        argv = assist._resolve_harness_argv("opencode", "do it", "/tmp/w")
        self.assertNotIn("--session", argv)

    def test_claude_resume_flag(self):
        argv = assist._resolve_harness_argv(
            "claude-code", "do it", "/tmp/w", mode="chat", resume_id="sid-1")
        self.assertTrue(_subseq(argv, ["--resume", "sid-1"]))
        self.assertEqual(argv[-1], "do it")

    def test_codex_resume_subcommand(self):
        argv = assist._resolve_harness_argv(
            "codex", "do it", "/tmp/w", mode="edit", resume_id="tid-1")
        self.assertEqual(argv[1:], [
            "-C", "/tmp/w", "-s", "workspace-write", "exec", "resume",
            "tid-1", "--json", "--skip-git-repo-check", "--", "-",
        ])

    def test_codex_fresh_command_keeps_exec_options(self):
        argv = assist._resolve_harness_argv("codex", "do it", "/tmp/w")
        self.assertEqual(argv[1:], [
            "exec", "--json", "--skip-git-repo-check", "-C", "/tmp/w",
            "-s", "workspace-write", "--", "-",
        ])

    def test_codex_chat_is_read_only(self):
        argv = assist._resolve_harness_argv(
            "codex", "explain it", "/tmp/w", mode="chat")
        self.assertTrue(_subseq(argv, ["-s", "read-only"]))
        self.assertNotIn("workspace-write", argv)

    def test_provider_chat_modes_do_not_auto_approve_edits(self):
        opencode = assist._resolve_harness_argv(
            "opencode", "explain", "/tmp/w", mode="chat")
        claude = assist._resolve_harness_argv(
            "claude-code", "explain", "/tmp/w", mode="chat")
        agy = assist._resolve_harness_argv(
            "agy", "explain", "/tmp/w", mode="chat")
        self.assertNotIn("--auto", opencode)
        self.assertTrue(_subseq(claude, ["--permission-mode", "plan"]))
        self.assertNotIn("acceptEdits", claude)
        self.assertTrue(_subseq(agy, ["--mode", "plan"]))
        self.assertNotIn("--dangerously-skip-permissions", agy)

    def test_agy_resume_flag_before_print(self):
        argv = assist._resolve_harness_argv(
            "agy", "do it", "/tmp/w", mode="edit", resume_id="cid-1")
        self.assertTrue(_subseq(argv, ["--conversation", "cid-1"]))
        # agy's --print swallows the next arg, so the prompt stays last.
        self.assertEqual(argv[-2:], ["--print", "do it"])

    def test_unknown_harness_raises(self):
        with self.assertRaises(ValueError):
            assist._resolve_harness_argv("nope", "do it", "/tmp/w")


class TestCodexStdin(unittest.IsolatedAsyncioTestCase):
    async def _turn(self, resume_id=None, failure=False):
        chapter = "--- chapter\r\n" + "Prose — café 'quoted' 🚀\n" * 2200
        prompt = chapter + "\n\n--- USER MESSAGE ---\nReview the chapter."
        self.assertGreater(len(prompt), 40000)
        expected_digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        real_popen = subprocess.Popen
        seen_argv = []

        def launch(argv, **kwargs):
            seen_argv.append(argv)
            self.assertEqual(kwargs["stdin"], subprocess.PIPE)
            script = (
                "import sys,hashlib,json; data=sys.stdin.buffer.read(); "
                "print(json.dumps({'type':'item.completed','item':"
                "{'type':'agent_message','text':hashlib.sha256(data).hexdigest()}}))"
            )
            if failure:
                script = (
                    "import sys; sys.stdin.buffer.read(); "
                    "sys.stderr.write('fatal: smoke diagnostic'); sys.exit(2)"
                )
            return real_popen([sys.executable, "-c", script], **kwargs)

        with tempfile.TemporaryDirectory() as workspace, \
                patch.object(assist.storage, "workspace_dir", Path(workspace)), \
                patch.object(assist.storage, "get_settings", return_value={}), \
                patch.object(assist.storage, "get_harness_session", return_value=resume_id), \
                patch.object(assist.storage, "clear_harness_session"), \
                patch.object(assist.harness_env, "which_harness", return_value="codex"), \
                patch.object(assist, "_compose_chat_prompts", return_value=(chapter, "Review the chapter.", {})), \
                patch.object(assist, "_workspace_index_line", return_value=""), \
                patch.object(assist, "_log_simple_assist"), \
                patch.object(assist.subprocess, "Popen", side_effect=launch):
            response = await assist.simple_assist(assist.SimpleAssistRequest(
                message="Review the chapter.", harness="codex", mode="chat", session_id="test",
            ))
            events = [json.loads(event["data"]) async for event in response.body_iterator]

        argv = seen_argv[0]
        self.assertEqual(argv[-2:], ["--", "-"])
        self.assertNotIn(prompt, argv)
        self.assertLess(len(" ".join(argv)), 1000)
        if resume_id:
            self.assertLess(argv.index("-C"), argv.index("exec"))
        if failure:
            error = next(event["detail"] for event in events if event["status"] == "error")
            self.assertIn("fatal: smoke diagnostic", error)
        else:
            self.assertIn(
                expected_digest,
                "".join(event.get("chunk", "") for event in events),
            )

    async def test_fresh_long_prompt_reaches_stdin_intact(self):
        await self._turn()

    async def test_resumed_long_prompt_reaches_stdin_intact(self):
        await self._turn(resume_id="tid-1")

    async def test_non_json_stderr_survives_failure_without_newline(self):
        await self._turn(failure=True)


class TestSessionCapture(unittest.TestCase):

    def test_opencode_session_id(self):
        line = json.dumps({"type": "text", "sessionID": "ses_X",
                           "part": {"type": "text", "text": "yo"}})
        events = assist._parse_opencode_line(line)
        self.assertIn(("session", "ses_X"), events)
        self.assertIn(("chunk", "yo"), events)

    def test_claude_session_id(self):
        line = json.dumps({"type": "result", "session_id": "cl-1",
                           "usage": {}})
        events = assist._parse_claude_line(line)
        self.assertIn(("session", "cl-1"), events)

    def test_codex_thread_id(self):
        line = json.dumps({"type": "thread.started",
                           "thread_id": "tid-9"})
        events = assist._parse_codex_line(line, {})
        self.assertIn(("session", "tid-9"), events)

    def test_agy_conversation_id(self):
        events = assist._parse_agy_line(
            json.dumps({"event": "init", "conversation_id": "cid-7"}))
        self.assertIn(("session", "cid-7"), events)
        events = assist._parse_agy_line(json.dumps(
            {"event": "result",
             "result": {"conversation_id": "cid-7", "status": "SUCCESS"}}))
        self.assertIn(("session", "cid-7"), events)


class TestRunOutcome(unittest.TestCase):

    def test_write_tool_counts(self):
        self.assertTrue(assist._is_write_tool("write", "a/b.md"))
        self.assertTrue(assist._is_write_tool("replace_file_content", "/x/y.md"))
        self.assertTrue(assist._is_write_tool("edit", "CHAPTERS.md"))

    def test_reads_and_pathless_do_not_count(self):
        self.assertFalse(assist._is_write_tool("read", "a/b.md"))
        self.assertFalse(assist._is_write_tool("glob", "a/*.md"))
        self.assertFalse(assist._is_write_tool("grep", "pattern"))
        self.assertFalse(assist._is_write_tool("bash", None))
        self.assertFalse(assist._is_write_tool("mcp", None))

    def test_mutating_shell_counts_as_write(self):
        self.assertTrue(assist._is_write_tool(
            "bash", None, "rm chapters/chapter-3.md"))
        self.assertTrue(assist._is_write_tool(
            "bash", None, "git status; rm -f tmp.md"))
        self.assertTrue(assist._is_write_tool(
            "bash", None, "mv a.md b.md"))
        self.assertFalse(assist._is_write_tool(
            "bash", None, "git status; ls -la"))
        self.assertFalse(assist._is_write_tool(
            "bash", None, "echo hello"))

    def test_error_without_writes_fails(self):
        self.assertFalse(assist._harness_run_ok(True, False))

    def test_error_with_writes_succeeds(self):
        self.assertTrue(assist._harness_run_ok(True, True))

    def test_clean_run_succeeds(self):
        self.assertTrue(assist._harness_run_ok(False, False))
        self.assertTrue(assist._harness_run_ok(False, True))


class TestPlannerFallback(unittest.TestCase):

    def test_invalid_shapes_fall_back_without_context(self):
        fallback = {"context_needed": [], "refined_query": "revise this"}
        self.assertEqual(assist._normalize_planner_plan(None, "revise this"), fallback)
        self.assertEqual(assist._normalize_planner_plan([], "revise this"), fallback)
        self.assertEqual(
            assist._normalize_planner_plan(
                {"context_needed": "chapters/a.md", "refined_query": 42},
                "revise this",
            ),
            fallback,
        )

    def test_valid_plan_filters_non_string_context_entries(self):
        self.assertEqual(
            assist._normalize_planner_plan(
                {"context_needed": ["chapters/a.md", None], "refined_query": "tighten"},
                "revise this",
            ),
            {"context_needed": ["chapters/a.md"], "refined_query": "tighten"},
        )


class TestStopEndpoint(unittest.TestCase):

    def test_stop_signals_active_turn_and_unknown_session_is_safe(self):
        event = assist.threading.Event()
        assist._active_stop_events["turn-1"] = event
        try:
            self.assertEqual(assist.stop_simple_generation("turn-1"), {"status": "ok"})
            self.assertTrue(event.is_set())
            self.assertEqual(assist.stop_simple_generation("missing"), {"status": "ok"})
        finally:
            assist._active_stop_events.pop("turn-1", None)


class TestHarnessSessionMap(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = FileStorageService(
            base_dir=self.tmp.name,
            config_dir=Path(self.tmp.name) / "config",
            workspace_dir=Path(self.tmp.name) / "sample-workspace",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_round_trip(self):
        self.assertIsNone(self.storage.get_harness_session("m1", "opencode"))
        self.storage.set_harness_session("m1", "opencode", "ses_1")
        self.assertEqual(
            self.storage.get_harness_session("m1", "opencode"), "ses_1")
        # Other harnesses/sessions are independent.
        self.assertIsNone(self.storage.get_harness_session("m1", "agy"))
        self.assertIsNone(self.storage.get_harness_session("m2", "opencode"))

    def test_clear_single_harness(self):
        self.storage.set_harness_session("m1", "opencode", "ses_1")
        self.storage.set_harness_session("m1", "agy", "cid_1")
        self.storage.clear_harness_session("m1", "opencode")
        self.assertIsNone(self.storage.get_harness_session("m1", "opencode"))
        self.assertEqual(
            self.storage.get_harness_session("m1", "agy"), "cid_1")

    def test_map_file_lives_in_workspace_outputs(self):
        self.storage.set_harness_session("m1", "opencode", "ses_1")
        path = Path(self.tmp.name) / "sample-workspace" / "outputs" \
            / "harness_sessions.json"
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
