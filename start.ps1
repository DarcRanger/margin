# start.ps1 — Windows PowerShell startup script
# Run with:  powershell -ExecutionPolicy Bypass -File start.ps1

param(
    [switch]$SkipSetup,
    [int]$ApiPort = 8000,
    [int]$UiPort = 5173,
    [string]$ShutdownFile = ""
)

$ErrorActionPreference = "Stop"
$RootDir = $PSScriptRoot
Set-Location $RootDir

# ── Python and Node environments ────────────────────────────────────────────
if (-not $SkipSetup) {
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating virtual environment..."
        python -m venv .venv
    }

    & ".venv\Scripts\Activate.ps1"
    python -m pip install -q --upgrade pip
    python -m pip install -q -r requirements.txt

    if (-not (Test-Path "ui\node_modules")) {
        Write-Host "Installing frontend dependencies..."
        Push-Location ui
        npm install
        Pop-Location
    }
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

# ── Launch ──────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Starting SLM Writing Engine..."
Write-Host "  API  -> http://localhost:$ApiPort"
Write-Host "  UI   -> http://localhost:$UiPort"
Write-Host ""

$env:VITE_API_BASE = "http://127.0.0.1:$ApiPort"
function Stop-ProcessTree($Process) {
    if (-not $Process -or $Process.HasExited) { return }

    # Both uvicorn --reload and npm can create child processes. taskkill /T is
    # required on Windows so closing Margin cannot leave a port-owning orphan.
    $killer = Start-Process -NoNewWindow -PassThru -Wait -FilePath "taskkill.exe" `
        -ArgumentList "/PID", "$($Process.Id)", "/T", "/F"
    if ($killer.ExitCode -ne 0 -and -not $Process.HasExited) {
        throw "Could not stop process tree $($Process.Id)"
    }
}

$api = $null
$ui = $null
try {
    $api = Start-Process -NoNewWindow -PassThru -FilePath "python" `
        -ArgumentList "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "$ApiPort", "--reload"

    $ui = Start-Process -NoNewWindow -PassThru -FilePath "npm.cmd" `
        -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "$UiPort", "--strictPort" `
        -WorkingDirectory "ui"

    while ($true) {
        if ($api.HasExited) { throw "Margin API exited unexpectedly ($($api.ExitCode))" }
        if ($ui.HasExited) { throw "Margin UI exited unexpectedly ($($ui.ExitCode))" }
        if ($ShutdownFile -and (Test-Path -LiteralPath $ShutdownFile)) { break }
        Start-Sleep -Milliseconds 250
    }
} finally {
    Stop-ProcessTree $ui
    Stop-ProcessTree $api
}
