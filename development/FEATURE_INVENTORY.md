# Margin Feature Inventory

Inventory date: 2026-09-22

Source inspected: `feat/development-supervisor-v1` at `d7ce831`
Method: read-only source inspection plus the verified automated and Windows gates

## Classification rules

- `WORKING`: directly exercised by an automated test or the Windows acceptance
  gate with a clear passing result.
- `PARTIAL`: implementation is present and builds, but its full user behavior is
  not yet covered or independently verified.
- `MISSING`: required or previously demonstrated behavior is absent from the
  inspected GitHub source.
- `BROKEN`: a present behavior has a reproducible failure. None was established
  by this inventory; unverified behavior is `PARTIAL`, not presumed broken.

## Critical source finding

`MISSING`: The protected **DARC Pilot Mode** shown and used in Joe's installed
Windows copy is absent from every GitHub branch (`main`,
`feat/development-supervisor-v1`, and `gh-pages`). No repository source contains
the visible controls `Start Protected Pilot`, `Reset Pilot`,
`Export Approved Copy`, or `Finish Pilot`.

This is source drift, not evidence that the working local feature is defective.
The installed working copy must be treated as a protected source until its pilot
implementation is captured and compared with GitHub. Do not replace that
directory with the clone or rebuild the feature from memory.

## User interface

| Surface | Status | Evidence and boundary |
|---|---|---|
| Main editor route (`/`) | `PARTIAL` | React route and editor build/lint pass; no browser test covers loading, typing, or persistence. |
| File sidebar/tree | `PARTIAL` | Lists and lazy-loads Markdown files; create, rename, delete, refresh, and file switching are implemented but not end-to-end tested. |
| Markdown editor | `PARTIAL` | TipTap editing, selection tracking, formatting, counts, and AI highlighting are present; build/lint pass only. |
| Save on file switch or tab hide | `PARTIAL` | Save calls are implemented; no crash/quit or failed-write recovery test. |
| AI Assist panel | `PARTIAL` | Chat/edit streaming, context chips, sessions, stop, and logs are present; only lower-level parsing/resume behavior is tested. |
| Selection rewrite bubble menu | `PARTIAL` | Formatting, Add to Margin, and rewrite controls are implemented; no UI acceptance coverage. |
| Settings modal | `PARTIAL` | Workspace, appearance, endpoints, prompts, and harness settings are implemented; no end-to-end coverage. |
| Resizable/collapsible panels | `PARTIAL` | Implemented with local persistence; no browser coverage. |
| DARC Pilot Mode panel | `MISSING` | Demonstrated in the installed Windows copy, absent from GitHub source. |
| Lore Control interface | `MISSING` | Correctly deferred until Margin reaches a frozen functional-complete baseline. |

## API routes

| Route | Status | Evidence and boundary |
|---|---|---|
| `GET /` | `WORKING` | API smoke test passes. |
| `GET /api/workspace/files` | `WORKING` | Smoke test plus isolated-workspace safety tests pass. |
| `GET /api/workspace/files/{path}` | `PARTIAL` | Present; traversal and hidden/output path protection are tested, ordinary read is not directly asserted. |
| `POST /api/workspace/files` | `PARTIAL` | Safe-name checks exist; create lifecycle is not integration-tested. |
| `PUT /api/workspace/files/{path}` | `WORKING` | Isolated update test proves only the named fixture changes. |
| `PATCH /api/workspace/files/{path}` | `PARTIAL` | Rename validation exists; no route lifecycle test. |
| `DELETE /api/workspace/files/{path}` | `PARTIAL` | Markdown-only deletion rule exists; no route lifecycle test. |
| `GET /api/workspace/pick-folder` | `PARTIAL` | Windows/macOS/Linux strategies exist; manual Windows selection worked previously, but the cloned source was not rechecked. |
| `GET /api/workspace/styles` | `PARTIAL` | Manifest parsing is present; no route test. |
| `GET /api/settings/` | `PARTIAL` | Present and used by the UI; no direct test. |
| `PATCH /api/settings/` | `PARTIAL` | Persists settings and reloads workspace; no rollback/invalid-path test. |
| `POST /api/settings/test-endpoint` | `PARTIAL` | OpenAI-compatible model probe exists; dependent on external endpoint and not tested. |
| `GET /api/harnesses` | `PARTIAL` | Discovery code exists; executable availability varies by machine. |
| `GET /api/harnesses/{id}/models` | `PARTIAL` | Static/dynamic model resolution exists; parser paths are only partly tested. |
| `POST /api/assist/simple` | `PARTIAL` | Large chat/edit pipeline exists; anchor extraction, CLI argument construction, parser/session handling, and outcome rules are tested, but the full request is not. |
| `POST /api/assist/simple/stop/{session}` | `PARTIAL` | Stop signaling exists; no integration test. |
| `GET /api/assist/simple/logs` | `PARTIAL` | Workspace-local log storage exists; no route test. |
| `DELETE /api/assist/simple/session/{session}` | `PARTIAL` | Deletes logs and stale harness mapping; mapping behavior is tested, route is not. |
| `GET /api/assist/prompts` | `PARTIAL` | Present; no route test. |
| `GET /api/assist/prompts/{file}` | `PARTIAL` | Present with filename restrictions; no route test. |
| `POST /api/assist/prompts/{file}` | `PARTIAL` | Present with filename restrictions; no route test. |

## Services and data safety

| Service | Status | Evidence and boundary |
|---|---|---|
| Workspace path containment | `WORKING` | Traversal, hidden paths, and `outputs` exposure are denied by tests. |
| Disposable test configuration/workspace | `WORKING` | Test override beats linked settings; Windows 6/6 gate ran without selecting the live writing workspace. |
| Markdown file storage | `PARTIAL` | Listing and explicit update are tested; complete CRUD/error recovery is not. |
| Context anchor extraction | `WORKING` | Exact, partial, multiline, cursor, fallback, empty, and single-paragraph cases pass. |
| Context injection and pinned references | `PARTIAL` | Implemented; relevance and token-boundary behavior lack integration tests. |
| Harness registry/discovery | `PARTIAL` | Central registry supports OpenCode, Claude Code, Codex, and Antigravity; installed/authenticated combinations are environment-specific. |
| Harness stream parsing | `PARTIAL` | Session capture and essential event parsing are tested; real authenticated runs are not fully covered for every provider. |
| Harness conversation resume | `PARTIAL` | Argument shapes and local session map pass; comments record live verification only for OpenCode and Antigravity. |
| AI log/session storage | `PARTIAL` | Workspace-local persistence and cleanup code exist; corruption/recovery is not tested. |
| Approved-copy export and baseline protection | `MISSING` | Exists only in the unsynchronized installed DARC Pilot implementation. |

## Prompt assets

| Prompt | Status | Evidence and boundary |
|---|---|---|
| `simple-chat.md` | `PARTIAL` | Present and wired to Assist; output behavior depends on the selected model. |
| `simple-planner.md` | `PARTIAL` | Present and wired to context selection/refinement; no contract test for valid JSON. |
| `simple-writer.md` | `PARTIAL` | Present and wired to prose generation; no contract test for prose-only output. |
| `harness-edit.md` | `PARTIAL` | Present for agent-driven editing; no full protected-pilot acceptance test. |

## Launch and quality paths

| Path | Status | Evidence and boundary |
|---|---|---|
| `margin-test.bat` | `WORKING` | Passed 6/6 on Joe's Windows laptop on 2026-09-21. |
| `margin-test.ps1` | `PARTIAL` | Same Python gate wrapper; not separately invoked on Windows. |
| CI on Windows/macOS/Linux | `WORKING` | Fail-closed workflow and the same six checks pass in the development baseline. |
| `start.bat` → `start.ps1` | `PARTIAL` | Windows npm launcher fix is present and the installed app launches; a fresh-clone launch/quit acceptance is still required. |
| `start.sh` | `PARTIAL` | Present and executable; no current hands-on macOS/Linux launch acceptance. |
| Clean shutdown | `PARTIAL` | PowerShell and shell launchers attempt paired-process cleanup; no Windows close/kill/relaunch test. |

## Ordered Margin Functional Complete backlog

1. **Recover the installed DARC Pilot source.** Copy nothing over the installed
   app. Produce a read-only diff between the working installation and isolated
   GitHub clone, identify the exact pilot files, exclude `.venv`, dependencies,
   logs, backups, settings, and manuscript data, then commit only reviewed source
   changes to the feature branch.
2. **Write the source manifest and acceptance contract.** Record which GitHub
   commit and local files define launch, chapter editing, protected pilot,
   approved export, reset, finish, and safe quit behavior.
3. **Test protected pilot safety.** Add disposable-workspace coverage for start,
   baseline hash/snapshot, pilot edit, reset, approved export, finish, failure,
   and proof that the source chapter is unchanged.
4. **Close launch/quit behavior.** Verify fresh-clone launch, one-click start,
   browser availability, graceful quit, no orphan processes, and safe relaunch
   on Windows.
5. **Complete file lifecycle coverage.** Test read/create/rename/delete/save,
   failed writes, switching files with pending edits, and path boundaries.
6. **Complete AI/harness coverage.** Test chat versus edit permissions,
   stop/retry, provider failure, invalid planner output, diff accept/reject,
   session resume, and no-write failure handling.
7. **Add browser acceptance tests.** Cover startup, chapter load, edit, protected
   save, diff review, reset/export/finish, settings, and recovery.
8. **Triage build warnings and dependency audit.** Record and prioritize the
   current bundle-size/dynamic-import warnings and npm audit findings without
   applying an unreviewed force upgrade.
9. **Run the three-chapter protected pilot and freeze the baseline.** Joe retains
   KEEP/FIX/REWRITE and manuscript approval authority.
10. **Begin Lore Control only after the freeze.** Keep it a separate module with
    book/universe scope, proposal/approval states, provenance, conflict review,
    and approved-only Obsidian synchronization.

## Role confirmation

- **Supervisor:** maintains state, enforces the ordered gate, assigns bounded
  work, and stops on product or safety decisions.
- **Builder:** implements one approved backlog item and its tests; it does not
  change canon, manuscript wording, or protected inputs on its own.
- **Verifier:** independently checks the diff, full gate, safety boundaries, and
  acceptance evidence; failures return to Builder.
- **Joe:** decides product/UX alternatives, scope expansion, destructive actions,
  manuscript changes, KEEP/FIX/REWRITE, and all canon rulings.

No agent may treat generated prose, extracted lore, or conflict suggestions as
approved canon.
