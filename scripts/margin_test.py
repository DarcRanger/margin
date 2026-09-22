#!/usr/bin/env python3
"""Cross-platform Margin development test harness.

This command is the single quality gate used by coding agents, humans, and CI.
It intentionally returns a non-zero exit code when any required check fails.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI_DIR = ROOT / "ui"


@dataclass
class CheckResult:
    name: str
    status: str
    seconds: float
    detail: str = ""


def _run(
    name: str,
    command: Sequence[str],
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
) -> CheckResult:
    started = time.monotonic()
    print(f"\n[{name}] {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=cwd, env=env, check=False)
    elapsed = time.monotonic() - started
    status = "PASS" if completed.returncode == 0 else "FAIL"
    detail = "" if completed.returncode == 0 else f"exit code {completed.returncode}"
    return CheckResult(name, status, elapsed, detail)


def _dependency_check() -> CheckResult:
    started = time.monotonic()
    required = ("fastapi", "httpx", "pytest", "sqlmodel", "uvicorn")
    missing = []
    for module in required:
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(module)
    elapsed = time.monotonic() - started
    if missing:
        return CheckResult(
            "Python dependencies",
            "FAIL",
            elapsed,
            "missing: " + ", ".join(missing) + "; run: python -m pip install -r requirements-dev.txt",
        )
    return CheckResult("Python dependencies", "PASS", elapsed)


def _frontend_dependency_check() -> CheckResult:
    started = time.monotonic()
    exists = (UI_DIR / "node_modules").is_dir()
    elapsed = time.monotonic() - started
    if exists:
        return CheckResult("Frontend dependencies", "PASS", elapsed)
    return CheckResult(
        "Frontend dependencies",
        "FAIL",
        elapsed,
        "ui/node_modules is missing; run: npm ci --prefix ui",
    )


def _npm_command() -> str | None:
    # Windows installs npm as npm.cmd; Unix-like systems normally use npm.
    return shutil.which("npm.cmd") or shutil.which("npm")


def run_suite(full: bool) -> list[CheckResult]:
    results = [_dependency_check()]
    if results[-1].status == "FAIL":
        return results

    # Imports instantiate Margin's global storage service. Force every backend
    # check to use a disposable config so a user's linked manuscript workspace
    # cannot be selected or modified by automated tests.
    with tempfile.TemporaryDirectory(prefix="margin-test-root-") as test_root:
        test_root_path = Path(test_root)
        test_env = os.environ.copy()
        test_env["MARGIN_CONFIG_DIR"] = str(test_root_path / "config")
        test_env["MARGIN_WORKSPACE_DIR"] = str(test_root_path / "workspace")
        results.extend(
            [
                _run(
                    "Backend imports",
                    [
                        sys.executable,
                        "-c",
                        (
                            "from api.main import app; "
                            "from api.services.file_storage import storage; "
                            "from api.routers.workspace import router"
                        ),
                    ],
                    env=test_env,
                ),
                _run(
                    "Backend tests",
                    [sys.executable, "-m", "pytest", "tests", "-q"],
                    env=test_env,
                ),
            ]
        )

    if not full:
        return results

    results.append(_frontend_dependency_check())
    npm = _npm_command()
    if not npm:
        results.append(CheckResult("Node/npm", "FAIL", 0.0, "npm was not found on PATH"))
        return results
    if results[-1].status == "PASS":
        results.extend(
            [
                _run("Frontend tests", [npm, "run", "test"], UI_DIR),
                _run("Browser Pilot lifecycle", [npm, "run", "test:browser"], UI_DIR),
                _run("Frontend build", [npm, "run", "build"], UI_DIR),
                _run("Frontend lint", [npm, "run", "lint"], UI_DIR),
            ]
        )
    return results


def _print_summary(results: list[CheckResult]) -> None:
    print("\nMARGIN TEST SUITE")
    width = max(len(result.name) for result in results)
    for result in results:
        suffix = f" ({result.detail})" if result.detail else ""
        print(f"{result.name:<{width}}  {result.status:<4}  {result.seconds:6.2f}s{suffix}")
    passed = sum(result.status == "PASS" for result in results)
    print(f"\n{passed}/{len(results)} checks passed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Margin's development quality gate")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Run backend imports and unit tests")
    mode.add_argument("--full", action="store_true", help="Also build and lint the frontend (default)")
    parser.add_argument("--json", type=Path, help="Optionally write a machine-readable result file")
    args = parser.parse_args()

    results = run_suite(full=not args.quick)
    _print_summary(results)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps([asdict(result) for result in results], indent=2), encoding="utf-8")
    return 0 if results and all(result.status == "PASS" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
