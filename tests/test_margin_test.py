from __future__ import annotations

from subprocess import CompletedProcess

from scripts import margin_test


def test_output_guard_fails_when_known_build_warning_reappears(monkeypatch, tmp_path):
    monkeypatch.setattr(
        margin_test.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(
            args[0],
            0,
            stdout="[INEFFECTIVE_DYNAMIC_IMPORT] module is already statically imported\n",
        ),
    )

    result = margin_test._run_with_forbidden_output(
        "Frontend build",
        ["npm", "run", "build"],
        ("INEFFECTIVE_DYNAMIC_IMPORT", "Some chunks are larger than"),
        tmp_path,
    )

    assert result.status == "FAIL"
    assert result.detail == "warning: INEFFECTIVE_DYNAMIC_IMPORT"


def test_output_guard_preserves_success_for_clean_build(monkeypatch, tmp_path):
    monkeypatch.setattr(
        margin_test.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(args[0], 0, stdout="built in 1.2s\n"),
    )

    result = margin_test._run_with_forbidden_output(
        "Frontend build",
        ["npm", "run", "build"],
        ("INEFFECTIVE_DYNAMIC_IMPORT", "Some chunks are larger than"),
        tmp_path,
    )

    assert result.status == "PASS"
    assert result.detail == ""
