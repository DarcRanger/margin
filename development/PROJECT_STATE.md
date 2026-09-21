# Project State

Last updated: 2026-09-21
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
- `MISSING`: A verified functional-completeness inventory for Margin.
- `MISSING`: Automated browser/UI acceptance tests.
- `MISSING`: Windows hands-on acceptance of the new one-command test gate.

## Completed task

Development Harness v1 automated foundation:

- durable supervisor instructions;
- one cross-platform test command;
- deterministic baseline tests;
- fail-closed CI;
- protected-source regression tests;
- durable backlog, decisions, lessons, and state.

Automated verification: `PASS` (6/6 checks, 43 tests).

## Active task

Run the Windows hands-on acceptance in `development/WINDOWS_ACCEPTANCE.md`.

## Next gate

Joe runs `margin-test.bat` on Windows. Once that passes,
the supervisor performs a read-only feature inventory and proposes the ordered
Margin Functional Complete backlog before new product functionality is added.
