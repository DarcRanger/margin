# Development Backlog

## Completed

- [x] Complete and independently verify Development Harness v1 automated gate.
- [x] Run the Development Harness v1 Windows acceptance checklist (6/6 PASS).
- [x] Inventory current Margin surfaces and propose the ordered functional-
      completeness backlog.
- [x] Review external GitHub/Reddit ideas and record staged adoption decisions.
- [x] Recover and integrate the installed DARC Pilot source without touching
      linked writing data.
- [x] Write the protected-pilot source manifest and direct-editor contract.
- [x] Verify the recovered source against the full automated quality gate.
- [x] Add Pilot API smoke/integration coverage using a temporary workspace.
- [x] Prevent an exported finished Pilot run from resuming; preserve unfinished
      resume behavior and advance the next run number.
- [x] Complete Windows Pilot lifecycle acceptance on 2026-09-22, including
      start, direct edit/save, reset, export, finish, resume, and source checks.
- [x] Keep Pilot artifacts visible for audit while disabling Pilot start for
      files at or under `PILOT/` and showing corrective source guidance.

## In progress

- [ ] Add automated real-browser coverage for startup, chapter loading,
      protected direct save, conflict recovery, reset, export, finish, finished-
      run resume prevention, source eligibility guidance, and byte-preserved
      source protection in an isolated temporary workspace. Implementation,
      test discovery, API/UI startup, build, lint, and quick checks pass; local
      Chromium execution awaits a browser runtime because this environment's
      Playwright CDN downloads were truncated.

## Next

- [ ] Complete the real-browser execution locally or in cross-platform CI.
- [ ] Create the minimal Windows manual-acceptance checklist.
- [ ] Work through the approved functional-completeness backlog one item at a
      time with Builder/Verifier repair loops.

## Later: Lore Control

- [ ] Define module boundaries and book/universe scopes.
- [ ] Test search, retrieval, proposed additions, proposed modifications,
      provenance, conflict detection, and approval states.
- [ ] Integrate with Obsidian only after core Lore Control behavior is stable.

Lore extraction and conflict detection may be automated. Canon approval remains
a user decision.
