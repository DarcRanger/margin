param(
    [int]$StartupTimeoutSeconds = 240
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $PSScriptRoot
$TestRoot = Join-Path $env:TEMP ("margin-launch-test-" + [guid]::NewGuid())
$ApiPort = 18123
$UiPort = 15173
$ApiUrl = "http://127.0.0.1:$ApiPort/"
$UiUrl = "http://127.0.0.1:$UiPort/"

function Wait-ForUrl([string]$Url) {
    $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
    do {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
            if ($response.StatusCode -eq 200) { return }
        } catch {
            Start-Sleep -Milliseconds 500
        }
    } while ((Get-Date) -lt $deadline)
    throw "Timed out waiting for $Url"
}

function Wait-ForExit([System.Diagnostics.Process]$Process) {
    if (-not $Process.WaitForExit(30000)) {
        throw "Launcher did not exit after the shutdown request"
    }
    # Windows PowerShell can report HasExited before the redirected process
    # handle has populated ExitCode. An untimed wait and refresh synchronize it.
    $Process.WaitForExit()
    $Process.Refresh()
    if ($Process.ExitCode -ne 0) {
        throw "Launcher exited with code $($Process.ExitCode)"
    }
}

function Assert-NoMarginProcesses {
    Start-Sleep -Seconds 2
    $markers = @("--port $ApiPort", "--port $UiPort")
    $orphans = Get-CimInstance Win32_Process | Where-Object {
        $command = $_.CommandLine
        $command -and ($markers | Where-Object { $command.Contains($_) })
    }
    if ($orphans) {
        $details = ($orphans | ForEach-Object { "$($_.ProcessId): $($_.CommandLine)" }) -join "`n"
        throw "Margin left orphan processes:`n$details"
    }
}

function Stop-TestOrphans {
    $markers = @("--port $ApiPort", "--port $UiPort")
    Get-CimInstance Win32_Process | Where-Object {
        $command = $_.CommandLine
        $command -and ($markers | Where-Object { $command.Contains($_) })
    } | ForEach-Object {
        Start-Process -NoNewWindow -Wait -FilePath "taskkill.exe" `
            -ArgumentList "/PID", "$($_.ProcessId)", "/T", "/F" | Out-Null
    }
}

function Run-LaunchCycle([int]$Cycle, [bool]$SkipSetup) {
    $shutdown = Join-Path $TestRoot "stop-$Cycle.signal"
    $stdout = Join-Path $TestRoot "launch-$Cycle.stdout.log"
    $stderr = Join-Path $TestRoot "launch-$Cycle.stderr.log"
    $startScript = Join-Path $RootDir "start.ps1"
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$startScript`"" +
        " -ApiPort $ApiPort -UiPort $UiPort -ShutdownFile `"$shutdown`""
    if ($SkipSetup) { $arguments += " -SkipSetup" }

    $launcher = Start-Process -PassThru -FilePath "powershell.exe" `
        -ArgumentList $arguments -WorkingDirectory $RootDir `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr

    try {
        Wait-ForUrl $ApiUrl
        Wait-ForUrl $UiUrl
        New-Item -ItemType File -Force $shutdown | Out-Null
        Wait-ForExit $launcher
        Assert-NoMarginProcesses
    } catch {
        if (-not $launcher.HasExited) {
            New-Item -ItemType File -Force $shutdown | Out-Null
            if (-not $launcher.WaitForExit(30000)) {
                Start-Process -NoNewWindow -Wait -FilePath "taskkill.exe" `
                    -ArgumentList "/PID", "$($launcher.Id)", "/T", "/F" | Out-Null
            }
        }
        Stop-TestOrphans
        Write-Host "--- launcher stdout ---"
        if (Test-Path $stdout) { Get-Content $stdout }
        Write-Host "--- launcher stderr ---"
        if (Test-Path $stderr) { Get-Content $stderr }
        throw
    }
}

try {
    New-Item -ItemType Directory -Force $TestRoot | Out-Null
    $env:MARGIN_CONFIG_DIR = Join-Path $TestRoot "config"
    $env:MARGIN_WORKSPACE_DIR = Join-Path $TestRoot "workspace"

    # The first cycle exercises a clean checkout's normal dependency setup.
    # The second uses those installed dependencies to prove an immediate
    # relaunch on the same ports.
    Run-LaunchCycle 1 $false
    Run-LaunchCycle 2 $true
    Write-Host "Windows launch/quit/relaunch acceptance PASS"
} finally {
    Remove-Item -LiteralPath $TestRoot -Recurse -Force -ErrorAction SilentlyContinue
}
