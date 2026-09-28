# Development Lessons

## 2026-09-21 — Green CI must be fail-closed

The original CI command appended a successful `echo` when pytest failed. This
allowed genuine test failures to appear green. Quality gates must preserve the
failing exit code.

## 2026-09-21 — CLI tests must not require installed agent products

Argument-construction unit tests failed on machines without every supported
agent CLI. Mock executable discovery so the test verifies Margin's behavior,
not the test machine's installed products.

## 2026-09-21 — Temporary base paths do not guarantee test isolation

Margin settings can redirect storage from a temporary base directory to the
user's linked workspace. The quality gate now forces disposable config and
workspace environment paths before application imports, and fixtures inject
both paths explicitly. A regression test proves a configured external linked
workspace remains unchanged.

## 2026-09-21 — Borrow patterns, not whole systems

Claude Mission Control's Overseer/Builder/Oracle loop, Story-Film-Skills'
checkpoints, Fiction Forge's regression fences, and AGI Memory's durable lesson
model fit Margin. Their complete runtimes are not required for Harness v1.
