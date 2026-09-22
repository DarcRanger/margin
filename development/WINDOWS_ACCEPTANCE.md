# Windows Acceptance — Development Harness v1

Status: `PASS` — 6/6 checks passed on the Windows laptop on 2026-09-21
from an isolated clone.

Run this once after pulling the feature branch on the Windows laptop.

## Setup

```text
python -m pip install -r requirements-dev.txt
npm ci --prefix ui
```

## Test

Double-click `margin-test.bat`, or run:

```text
.\margin-test.bat
```

Expected result:

```text
MARGIN TEST SUITE
Python dependencies    PASS
Backend imports        PASS
Backend tests          PASS
Frontend dependencies  PASS
Frontend build         PASS
Frontend lint          PASS

6/6 checks passed
```

## Safety confirmation

Confirm that the test did not change the linked Darc workspace, manuscript
files, Obsidian vault, or Margin's selected workspace setting. Automated tests
use disposable config and workspace directories, but this manual observation
closes the platform-specific acceptance gate.

If the command fails, capture the complete terminal output. Do not modify
manuscript files or switch the test to the live workspace to troubleshoot it.
