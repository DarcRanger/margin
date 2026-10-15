# DARC Pilot Source Manifest

Recovery date: 2026-09-22
Branch: `feat/development-supervisor-v1`

## Acceptance contract

- The user edits the disposable Pilot chapter directly in Margin's main text
  editor. AI prompt boxes remain optional.
- Starting a Pilot creates a byte-identical workspace-local copy and records the
  source SHA-256, line endings, and final-newline state.
- Ordinary workspace update, rename, and delete routes cannot modify an active
  source or Pilot copy.
- Direct save changes only the Pilot copy, preserves its newline form, verifies
  that the source has not changed, and records `MANUAL EDIT` verification.
- Harness editing is scoped to the Pilot directory. Accept or Reject rewrites
  only the Pilot copy and records `HARNESS REVIEW` verification.
- Reset restores the Pilot from the unchanged source and advances the run
  number. It refuses to proceed if the source integrity check fails.
- Export requires an accepted PASS, writes an immutable approved copy under the
  Pilot `OUTPUT` directory, and records the final hashes and verification type.
- Navigation remains locked to the active Pilot until an accepted PASS has been
  exported and the Pilot session is finished.

## Recovered and integrated files

| Area | Files | Purpose |
|---|---|---|
| Pilot backend | `api/services/pilot_mode.py`, `api/routers/workspace.py` | Lifecycle, integrity checks, direct save, review, reset, export, API routes |
| Storage safety | `api/services/file_storage.py` | Newline-preserving I/O and protection of active source/Pilot files |
| Harness safety | `api/routers/assist.py` | Explicit active path, Pilot-only workspace scope, Codex stdin/resume reliability |
| Windows startup | `start.ps1` | Uses the activated interpreter for dependency installation |
| Pilot UI | `ui/src/components/PilotPanel.tsx`, `ui/src/lib/pilotControls.ts` | Start, direct save, reset, export, finish, status and navigation gate |
| Editor integration | `ui/src/pages/SimpleEditor.tsx`, `ui/src/stores/editorStore.ts`, `ui/src/components/FileSidebar.tsx` | Direct main-field editing, Pilot state, guarded navigation |
| AI review | `ui/src/lib/applyHarnessResult.ts`, `ui/src/lib/harnessSourcePatch.ts`, `ui/src/components/SimpleAssist.tsx`, `ui/src/components/Editor/WritingBubbleMenu.tsx` | Source-aware review and active Pilot routing |
| Verification | `tests/test_pilot_mode.py`, `tests/test_file_storage_newlines.py`, `tests/test_harness_resume.py`, `ui/tests/*.test.mjs`, `scripts/margin_test.py` | Integrity, direct edit, newline, Codex transport, UI control, and full-gate coverage |

## Deliberate merge decisions

- Preserved the GitHub version's isolated `MARGIN_CONFIG_DIR` and
  `MARGIN_WORKSPACE_DIR` test controls.
- Preserved strict zero-warning frontend lint instead of the installed copy's
  weaker lint command.
- Selectively recovered the installed Pilot and Codex reliability changes;
  generated `ui/dist` output and the installed environment were not imported.
- No manuscript, linked workspace, Obsidian vault, secrets, or runtime settings
  were copied into the repository or used by automated tests.

## Automated evidence

`python scripts/margin_test.py --full` passed on 2026-09-22:

- backend imports: PASS;
- backend tests: 56 passed plus 2 subtests;
- frontend Pilot/source-patch tests: 5 passed;
- frontend production build: PASS;
- frontend strict lint: PASS.

The remaining release gate is a small hands-on Windows acceptance run from the
clean GitHub clone. It must use a disposable chapter, not linked writing data.
