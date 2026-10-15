# One-command Margin quality gate for Windows PowerShell.
$ErrorActionPreference = "Stop"
python (Join-Path $PSScriptRoot "scripts\margin_test.py") --full @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
