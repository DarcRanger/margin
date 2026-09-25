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

External repositories and Reddit ideas are triaged in
[`EXTERNAL_IDEA_REVIEW.md`](EXTERNAL_IDEA_REVIEW.md). Inclusion there records a
candidate or decision; it does not authorize a dependency or feature by itself.

## Local setup

```text
python -m pip install -r requirements-dev.txt
npm ci --prefix ui
npx --prefix ui playwright install chromium
python scripts/margin_test.py --full
```

On Windows, `margin-test.bat` or `./margin-test.ps1` runs the same full gate.
The full gate includes a named `Browser Pilot lifecycle` check. It starts the
actual API and Vite UI on available local ports, generates a temporary generic
Markdown workspace, runs Chromium, verifies source bytes, and removes the
temporary workspace afterward. No linked workspace or user manuscript is read.

To run only that check on Windows, macOS, or Linux:

```text
npm run test:browser --prefix ui
```

If Chromium is not installed, run `npx --prefix ui playwright install chromium`.
Linux CI uses `--with-deps`; the other supported runners use the standard
Chromium installation.

## Status vocabulary

- `WORKING`: demonstrated by an automated test or recorded acceptance test.
- `PARTIAL`: present, but not fully specified or covered.
- `MISSING`: approved capability is not implemented.
- `BROKEN`: expected capability currently fails.
- `DECISION REQUIRED`: progress depends on Joe's product/UX/canon decision.
- `PASS`: all acceptance criteria and the full automated gate pass.
