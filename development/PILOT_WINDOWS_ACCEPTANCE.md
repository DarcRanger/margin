# Windows Manual Acceptance — DARC Pilot

Target time: 5–7 minutes  
Status: `NOT RUN`

Run this only after the feature branch and automated gate are green. This is a
short visual acceptance check; automated tests already cover conflict handling,
approved-output bytes, source hashes, and cross-platform behavior.

## 1. Start with a disposable workspace

From PowerShell in the isolated Margin clone:

```powershell
$env:MARGIN_ACCEPTANCE_ROOT = Join-Path $env:TEMP ("margin-pilot-acceptance-" + [guid]::NewGuid())
$env:MARGIN_CONFIG_DIR = Join-Path $env:MARGIN_ACCEPTANCE_ROOT "config"
$env:MARGIN_WORKSPACE_DIR = Join-Path $env:MARGIN_ACCEPTANCE_ROOT "workspace"
New-Item -ItemType Directory -Force $env:MARGIN_CONFIG_DIR, $env:MARGIN_WORKSPACE_DIR | Out-Null
Copy-Item ".\sample-workspace\*" $env:MARGIN_WORKSPACE_DIR -Recurse
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Open <http://localhost:5173>. Do not select the live Darc workspace.

## 2. Complete the five checks

- [ ] **Open and eligibility:** Select `chapters/chapter-1.md`. The chapter
      opens in the main editor and **Start Protected Pilot** is enabled.
- [ ] **Protected start:** Select **Start Protected Pilot**. A run number and
      disposable `PILOT/` path appear, source protection reads
      **Protected by workspace API**, and the editor remains usable.
- [ ] **Save and reset:** Add `WINDOWS ACCEPTANCE EDIT` in the main editor,
      select **Save Pilot Edits**, and confirm **PASS** with
      **Verified by: MANUAL EDIT**. Select **Reset Pilot**; the run number
      advances and that edit disappears.
- [ ] **Export and finish:** Add `WINDOWS APPROVED COPY`, save, select
      **Export Approved Copy**, then **Finish Pilot**. Reselect
      `chapters/chapter-1.md`; neither acceptance phrase appears in the source.
- [ ] **Pilot-source guard:** Open the Pilot copy under `PILOT/`.
      **Start Protected Pilot** is disabled and the page says to select a
      Markdown chapter outside `PILOT/`.

## 3. Record and clean up

Record `PASS — 5/5` only if every check succeeds. Otherwise record the failed
check and capture one screenshot; do not troubleshoot against live writing
files.

Stop Margin with `Ctrl+C`, then remove only the disposable folder:

```powershell
if ($env:MARGIN_ACCEPTANCE_ROOT -like "$env:TEMP\margin-pilot-acceptance-*") {
    Remove-Item -LiteralPath $env:MARGIN_ACCEPTANCE_ROOT -Recurse -Force
}
```

Result: `NOT RUN`  
Date: `—`  
Tester: `—`
