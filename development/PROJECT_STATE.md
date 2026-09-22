# Project State

Last updated: 2026-09-22
Branch: `feat/development-supervisor-v1`
Milestone: Margin Development Harness v1

## Current baseline

- `WORKING`: Margin launches on the user's Windows machine.
- `WORKING`: More than one chapter has completed the protected pilot workflow.
- `WORKING`: The full quality gate passes: 43 backend tests, backend imports,
  frontend build, and zero-warning frontend lint.
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

## Active task

Recover the installed DARC Pilot source without modifying the working
installation or linked writing data. Compare it with the isolated GitHub clone,
capture only reviewed source changes, and verify direct editing and protected
pilot behavior before importing new product ideas.

External GitHub and Reddit candidates are classified in
`development/EXTERNAL_IDEA_REVIEW.md`. No candidate is approved for wholesale
installation or allowed to bypass the functional-complete baseline.
