# Project State

Last updated: 2026-09-22
Branch: `feat/development-supervisor-v1`
Milestone: Margin Development Harness v1

## Current baseline

- `WORKING`: Margin launches on the user's Windows machine.
- `WORKING`: More than one chapter has completed the protected pilot workflow.
- `WORKING`: The full quality gate passes: 79 backend tests plus 2 subtests,
  7 frontend unit tests, backend imports, frontend build, and zero-warning lint.
- `WORKING`: Cross-platform GitHub Actions are fail-closed on Windows, macOS,
  and Linux and explicitly install development/test dependencies.
- `WORKING`: Automated checks force disposable config and workspace paths;
  regression coverage proves linked manuscript data is not selected.
- `WORKING`: Protected Pilot, file lifecycle, and AI/harness failure recovery
  have isolated automated coverage; all writes remain confined to disposable
  test workspaces.
- `WORKING`: The read-only functional-completeness inventory and ordered backlog
  are recorded in `development/FEATURE_INVENTORY.md`.
- `WORKING`: Automated real-browser acceptance passes on Windows, macOS, and
  Linux for protected Pilot and pending-edit file switching behavior.
- `WORKING`: Windows hands-on acceptance passed 6/6 from an isolated clone on
  Joe's Windows laptop; the live Margin installation and linked writing data
  were not selected for the test.
- `WORKING`: The production frontend build has no ineffective-import or
  oversized-chunk warnings; the quality gate rejects either warning if it
  returns.
- `WORKING`: The live npm audit reports zero vulnerabilities after non-forced,
  same-major dependency remediation. CI now fails on future high-severity
  findings.

## Completed task

Development Harness v1 automated foundation:

- durable supervisor instructions;
- one cross-platform test command;
- deterministic baseline tests;
- fail-closed CI;
- protected-source regression tests;
- durable backlog, decisions, lessons, and state.

Automated verification: `PASS` (6/6 checks, 43 tests).

## Completed platform gate

Windows hands-on acceptance: `PASS` (6/6 checks) on 2026-09-21.

## Completed recovery

The installed DARC Pilot source was recovered without modifying the working
installation or linked writing data. Reviewed Pilot and Codex reliability
changes were integrated while newer GitHub isolation and lint fixes were
preserved. Direct editing in the main chapter editor now saves only to the
disposable Pilot copy. The source contract and file inventory are recorded in
`development/PILOT_SOURCE_MANIFEST.md`.

Automated verification: `PASS` (7/7 checks).

## Active task

Run the three-chapter protected pilot and freeze the functional-complete
baseline. Then begin the approved selectable chapter-audit feature before Lore
Control.

External GitHub and Reddit candidates are classified in
`development/EXTERNAL_IDEA_REVIEW.md`. External product ideas remain gated until
the Windows Pilot acceptance run and baseline freeze are complete.
