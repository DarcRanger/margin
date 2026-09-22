# Project State

Last updated: 2026-09-22
Branch: `feat/development-supervisor-v1`
Milestone: Margin Development Harness v1

## Current baseline

- `WORKING`: Margin launches on the user's Windows machine.
- `WORKING`: More than one chapter has completed the protected pilot workflow.
- `WORKING`: The full quality gate passes: 56 backend tests plus 2 subtests,
  5 frontend unit tests, backend imports, frontend build, and zero-warning lint.
- `WORKING`: Cross-platform GitHub Actions are fail-closed on Windows, macOS,
  and Linux and explicitly install development/test dependencies.
- `WORKING`: Automated checks force disposable config and workspace paths;
  regression coverage proves linked manuscript data is not selected.
- `PARTIAL`: Functional coverage is concentrated in harness resume/parsing,
  context extraction, and statistics; end-to-end feature coverage is limited.
- `WORKING`: The read-only functional-completeness inventory and ordered backlog
  are recorded in `development/FEATURE_INVENTORY.md`.
- `MISSING`: Automated browser/UI acceptance tests.
- `WORKING`: Windows hands-on acceptance passed 6/6 from an isolated clone on
  Joe's Windows laptop; the live Margin installation and linked writing data
  were not selected for the test.

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

Run the minimal clean-clone Windows acceptance checklist for Pilot start,
direct edit/save, reset, export, finish, relaunch, and source-integrity proof.

External GitHub and Reddit candidates are classified in
`development/EXTERNAL_IDEA_REVIEW.md`. External product ideas remain gated until
the Windows Pilot acceptance run and baseline freeze are complete.
