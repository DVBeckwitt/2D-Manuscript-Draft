<#
.SYNOPSIS
Builds the supplied supplemental note and then the complete Supporting Information.

.DESCRIPTION
Keeps incremental LaTeX build state under build_codex/supplement and publishes
the note PDF beside SI_failure_modes.tex before compiling the SI. The supplied
note is assembled from its retained PDF pages and editable replacement page.
Figure-regeneration scripts are optional and are not run by this helper.

.EXAMPLE
.\scripts\build-supplement.ps1

.EXAMPLE
.\scripts\build-supplement.ps1 -NoteOnly
#>

param(
    [switch]$NoteOnly
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$siDirectory = Join-Path $repoRoot '2D_Supplemental'
$noteSource = Join-Path $siDirectory 'verbatim_supplemental_note_source'
$buildRoot = Join-Path $repoRoot 'build_codex/supplement'

if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
    throw 'latexmk is required to build the supplemental note and Supporting Information.'
}

function Build-Document {
    param(
        [string]$SourceDirectory,
        [string]$EntryPoint,
        [string]$JobName,
        [string]$BuildDirectory,
        [string]$Destination
    )

    $sourcePath = Join-Path $SourceDirectory $EntryPoint
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        throw "Missing document source: $sourcePath"
    }
    New-Item -ItemType Directory -Path $BuildDirectory -Force | Out-Null
    Push-Location -LiteralPath $SourceDirectory
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        # latexmk's recorder and dependency hashes provide the persistent cache.
        # Ignore the manuscript's root rc so each document has isolated state.
        $ErrorActionPreference = 'Continue'
        # Keep BibTeX in the source directory so ../bibliography paths resolve.
        $buildOutput = & latexmk '-norc' '-bibtexfudge-' '-pdf' '-interaction=nonstopmode' `
            '-halt-on-error' '-file-line-error' "-outdir=$BuildDirectory" `
            "-jobname=$JobName" $EntryPoint 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
        Pop-Location
    }
    if ($exitCode -ne 0) {
        throw "Failed to build $EntryPoint (exit $exitCode).`n$($buildOutput -join [Environment]::NewLine)"
    }

    $builtPdf = Join-Path $BuildDirectory "$JobName.pdf"
    if (-not (Test-Path -LiteralPath $builtPdf -PathType Leaf)) {
        throw "Document build did not produce $builtPdf"
    }
    # Avoid replacing an unchanged dependency on every Overleaf export.
    $samePdf = (Test-Path -LiteralPath $Destination -PathType Leaf) -and
        ((Get-FileHash -LiteralPath $builtPdf -Algorithm SHA256).Hash -eq
         (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash)
    if (-not $samePdf) {
        Copy-Item -LiteralPath $builtPdf -Destination $Destination -Force
    }
    Write-Output "Built document: $Destination"
}

Build-Document -SourceDirectory $noteSource -EntryPoint 'main.tex' `
    -JobName 'verbatim_supplemental_note' -BuildDirectory (Join-Path $buildRoot 'note') `
    -Destination (Join-Path $siDirectory 'verbatim_supplemental_note.pdf')

if (-not $NoteOnly) {
    Build-Document -SourceDirectory $siDirectory -EntryPoint 'SI_failure_modes.tex' `
        -JobName 'SI_failure_modes' -BuildDirectory (Join-Path $buildRoot 'si') `
        -Destination (Join-Path $siDirectory 'SI_failure_modes.pdf')
}
