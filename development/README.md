# Margin Agent Development Loop

This directory is the durable memory for Margin's coding supervisor. Agent
sessions are temporary; project state, decisions, and lessons live here.

The operating loop is:

1. Supervisor selects one approved backlog item.
2. Builder implements code and tests on a feature branch.
3. Automated checks run with `python scripts/margin_test.py --quick`.
4. Verifier reviews the diff and runs `python scripts/margin_test.py --full`.
5. Failure returns to the Builder with evidence; success updates project state.
6. Joe performs manual acceptance when the change has a user-facing workflow.

The loop controls software development only. It can detect or report manuscript
and lore conflicts, but it cannot decide canon or rewrite source material.

## Local setup

```text
python -m pip install -r requirements-dev.txt
npm ci --prefix ui
python scripts/margin_test.py --full
```

On Windows, `margin-test.bat` or `./margin-test.ps1` runs the same full gate.

## Status vocabulary

- `WORKING`: demonstrated by an automated test or recorded acceptance test.
- `PARTIAL`: present, but not fully specified or covered.
- `MISSING`: approved capability is not implemented.
- `BROKEN`: expected capability currently fails.
- `DECISION REQUIRED`: progress depends on Joe's product/UX/canon decision.
- `PASS`: all acceptance criteria and the full automated gate pass.
