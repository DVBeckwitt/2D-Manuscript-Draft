param(
    [switch]$StopWatchers
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

function Get-MainLatexWatchers {
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @('latexmk.exe', 'perl.exe') -and
            $_.CommandLine -and
            $_.CommandLine -match 'latexmk' -and
            $_.CommandLine -match 'main\.tex' -and
            $_.CommandLine -match '-pvc'
        }
}

function Assert-FileWritable {
    param(
        [string]$Path,
        [int]$TimeoutSeconds = 10
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $lastError = $null
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while ([DateTime]::UtcNow -lt $deadline) {
        $stream = $null
        try {
            $stream = [System.IO.File]::Open(
                $Path,
                [System.IO.FileMode]::Open,
                [System.IO.FileAccess]::ReadWrite,
                [System.IO.FileShare]::None
            )
            return
        }
        catch {
            $lastError = $_.Exception.Message
            Start-Sleep -Milliseconds 500
        }
        finally {
            if ($stream) {
                $stream.Dispose()
            }
        }
    }

    throw "$Path is not writable. Close any PDF viewer or build process using it, then rerun this script. $lastError"
}

function Invoke-Latexmk {
    param([string[]]$Arguments)

    & latexmk @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "latexmk $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
    }
}

$watchers = @(Get-MainLatexWatchers)
if ($StopWatchers) {
    throw '-StopWatchers is intentionally disabled. Stop the printed watcher process manually, then rerun .\scripts\build-main.ps1.'
}

if ($watchers.Count -gt 0) {
    Write-Output @"
Active latexmk continuous watcher process(es) are running for main.tex.
Stop the editor watcher first, then rerun this script.

$($watchers | ForEach-Object { "PID=$($_.ProcessId) $($_.CommandLine)" } | Out-String)
"@
    exit 2
}

$auxPath = Join-Path $repoRoot 'build/main.aux'
$bblPath = Join-Path $repoRoot 'build/main.bbl'
$pdfPath = Join-Path $repoRoot 'build/main.pdf'

Assert-FileWritable -Path $pdfPath
Invoke-Latexmk -Arguments @('-C', 'main.tex')
Invoke-Latexmk -Arguments @('-pdf', '-g', '-interaction=nonstopmode', '-file-line-error', 'main.tex')

if (-not (Test-Path -LiteralPath $auxPath)) {
    throw "Missing expected auxiliary file: $auxPath"
}

if (-not (Test-Path -LiteralPath $bblPath)) {
    throw "Missing expected bibliography file: $bblPath"
}

$aux = Get-Content -Raw -LiteralPath $auxPath
$bblFile = Get-Item -LiteralPath $bblPath
$bbl = Get-Content -Raw -LiteralPath $bblPath

if ($aux -notmatch '\\bibstyle\{apsrev4-2\}') {
    throw 'build/main.aux is missing \bibstyle{apsrev4-2}'
}

if ($aux -notmatch '\\bibdata\{bibliography/references\}') {
    throw 'build/main.aux is missing \bibdata{bibliography/references}'
}

if ($bblFile.Length -le 0) {
    throw 'build/main.bbl is empty'
}

if ($bbl -notmatch '\\begin\{thebibliography\}') {
    throw 'build/main.bbl is missing \begin{thebibliography}'
}

Write-Output "Build succeeded: build/main.pdf"
