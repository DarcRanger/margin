# Margin Development Supervisor

This repository uses an agent-led build, test, repair, and verification loop.
These instructions govern every coding agent working anywhere in this tree.

## Authority boundary

Agents have authority to inspect, implement, refactor, test, and document Margin
code on a feature branch. Agents do not have authority to make authorial or
canon decisions, rewrite a manuscript, or silently change source material.

The repository code is the development target. A user's linked workspace,
manuscript originals, Obsidian vault, and approved lore are protected inputs.
Do not modify them during development or automated testing. Use temporary
fixtures or `sample-workspace` copies instead.

## Required workflow

1. Read `development/PROJECT_STATE.md`, `development/BACKLOG.md`, and the
   relevant implementation files before editing.
2. Confirm the work is on a non-default branch. Never experiment directly on
   `main`.
3. Select one approved backlog item or one explicit user request. State its
   acceptance criteria before implementation.
4. Builder phase: implement the smallest coherent change and add or update
   automated tests with it.
5. Run `python scripts/margin_test.py --quick` during iteration.
6. Verifier phase: inspect the diff independently from the acceptance criteria,
   then run `python scripts/margin_test.py --full`.
7. On failure, record concrete evidence, return to the Builder phase, repair,
   and rerun. Allow up to three repair rounds before reporting `BLOCKED` with
   the remaining evidence.
8. On success, update `development/PROJECT_STATE.md` and any relevant backlog,
   decision, or lesson entries. Report `PASS` only when the full suite passes.

When the environment supports separate agents, the supervisor should delegate
implementation to a Builder and final validation to a Verifier that did not
author the production change. When it does not, perform the same phases
sequentially and explicitly.

## Ask the user before proceeding

Stop with `DECISION REQUIRED` when work requires any of the following:

- choosing intended product behavior not established by a specification;
- selecting between materially different user-interface or architecture paths;
- destructive or irreversible data behavior;
- expanding the approved feature scope;
- deciding which conflicting story fact is canon;
- editing manuscript prose or approving a story/editorial judgment.

Routine implementation details, test design, bug fixes, dependency corrections,
and refactors needed to satisfy approved acceptance criteria do not require a
user decision.

## Quality and safety gates

- A failing test is a failure. Never mask it with `|| true`, `|| echo`, or an
  equivalent false-success path.
- Add a regression test for every repaired defect when practical.
- Tests that exercise writing must use a temporary directory.
- Do not add credentials, tokens, personal paths, manuscript text, or private
  lore to the repository or test output.
- Preserve cross-platform behavior for Windows, macOS, and Linux.
- Keep commits focused and use Conventional Commit messages.
- Do not merge to `main`; leave the feature branch ready for human acceptance.

## Completion report

Every completed task reports:

- acceptance criteria;
- files changed;
- tests executed and exact result;
- known limitations and manual acceptance steps;
- whether any user decision remains.
