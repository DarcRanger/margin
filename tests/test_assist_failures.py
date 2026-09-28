import asyncio
import json
from functools import wraps
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from api.routers import assist


async def _events(payload):
    response = await assist.simple_assist(payload)
    return [json.loads(event["data"]) async for event in response.body_iterator]


def async_test(function):
    @wraps(function)
    def run(*args, **kwargs):
        return asyncio.run(function(*args, **kwargs))
    return run


@async_test
async def test_harness_chat_does_not_flush_or_apply_file_changes(tmp_path):
    chapter = tmp_path / "chapters" / "chapter.md"
    chapter.parent.mkdir(parents=True)
    chapter.write_text("disk content", encoding="utf-8")

    async def finish_without_tools(argv, cwd, stop_event, queue, stdin_text=None):
        await queue.put(("done", 0))

    with patch.object(assist.storage, "workspace_dir", tmp_path), \
            patch.object(assist.storage, "get_settings", return_value={}), \
            patch.object(assist.storage, "get_harness_session", return_value=None), \
            patch.object(assist.storage, "update_input_file") as update, \
            patch.object(assist.storage, "set_harness_session"), \
            patch.object(assist.harness_env, "which_harness", return_value="codex"), \
            patch.object(assist, "run_harness", side_effect=finish_without_tools), \
            patch.object(assist, "_log_simple_assist"):
        events = await _events(assist.SimpleAssistRequest(
            message="Explain this chapter",
            content="unsaved editor content",
            mode="chat",
            harness="codex",
            session_id="chat-1",
            active_path="chapters/chapter.md",
        ))

    update.assert_not_called()
    assert chapter.read_text(encoding="utf-8") == "disk content"
    assert events[-1]["status"] == "harness_done"


@async_test
async def test_edit_preflush_failure_stops_before_harness_launch(tmp_path):
    chapter = tmp_path / "chapters" / "chapter.md"
    chapter.parent.mkdir(parents=True)
    chapter.write_text("disk content", encoding="utf-8")
    launch = AsyncMock()

    with patch.object(assist.storage, "workspace_dir", tmp_path), \
            patch.object(assist.storage, "update_input_file", side_effect=OSError("disk full")), \
            patch.object(assist, "run_harness", launch):
        events = await _events(assist.SimpleAssistRequest(
            message="Revise this chapter",
            content="pending editor content",
            mode="edit",
            harness="codex",
            session_id="edit-1",
            active_path="chapters/chapter.md",
        ))

    launch.assert_not_awaited()
    assert events[-1] == {
        "status": "error",
        "detail": "Could not save the active file before the harness run: disk full",
    }
    assert chapter.read_text(encoding="utf-8") == "disk content"


@async_test
async def test_no_write_harness_error_is_not_reported_as_done_and_retry_is_fresh(tmp_path):
    async def denied_turn(argv, cwd, stop_event, queue, stdin_text=None):
        await queue.put(("chunk", json.dumps({
            "type": "turn.failed",
            "error": {"message": "write permission denied"},
        }) + "\n"))
        await queue.put(("done", 0))

    clear = Mock()
    store = Mock()
    with patch.object(assist.storage, "workspace_dir", tmp_path), \
            patch.object(assist.storage, "get_settings", return_value={}), \
            patch.object(assist.storage, "get_harness_session", return_value="stale-thread"), \
            patch.object(assist.storage, "clear_harness_session", clear), \
            patch.object(assist.storage, "set_harness_session", store), \
            patch.object(assist.harness_env, "which_harness", return_value="codex"), \
            patch.object(assist, "run_harness", side_effect=denied_turn), \
            patch.object(assist, "_log_simple_assist"):
        events = await _events(assist.SimpleAssistRequest(
            message="Revise this chapter",
            mode="edit",
            harness="codex",
            session_id="edit-2",
        ))

    assert events[-1] == {"status": "error", "detail": "write permission denied"}
    assert not any(event["status"] == "harness_done" for event in events)
    clear.assert_called_with("edit-2", "codex")
    store.assert_not_called()


@async_test
async def test_endpoint_provider_failure_is_visible_and_logged():
    client = Mock()
    client.generate_stream_with_history.side_effect = RuntimeError("provider unavailable")
    logged = Mock()
    with patch.object(assist, "_resolve_simple_assist_client", return_value=client), \
            patch.object(assist, "_compose_chat_prompts", return_value=("system", "question", {})), \
            patch.object(assist, "_log_simple_assist", logged):
        events = await _events(assist.SimpleAssistRequest(
            message="Question",
            mode="chat",
            harness="none",
            session_id="provider-1",
        ))

    assert events[-1] == {"status": "error", "detail": "provider unavailable"}
    assert logged.call_args.kwargs["success"] is False


@async_test
async def test_invalid_mode_is_rejected_before_streaming():
    with pytest.raises(HTTPException, match="Mode must be") as exc:
        await assist.simple_assist(assist.SimpleAssistRequest(
            message="Question", mode="write-anywhere", harness="none"
        ))
    assert exc.value.status_code == 400
