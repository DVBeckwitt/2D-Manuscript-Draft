param(
    [switch]$IncludeCompileCheck
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$buildRoot = Join-Path $repoRoot 'build_overleaf'
$testRoot = Join-Path $buildRoot 'test-export'
$packageDirectory = Join-Path $testRoot 'package'
$archivePath = Join-Path $testRoot 'overleaf.zip'
$expandedArchive = Join-Path $testRoot 'expanded'
$exportScript = Join-Path $PSScriptRoot 'export-overleaf.ps1'

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Assert-SafeTestPath {
    param([string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $fullBuildRoot = [System.IO.Path]::GetFullPath($buildRoot)
    $expectedPrefix = $fullBuildRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $fullPath.StartsWith($expectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean test path outside build_overleaf: $fullPath"
    }
}

Assert-SafeTestPath -Path $testRoot
if (Test-Path -LiteralPath $testRoot) {
    Remove-Item -LiteralPath $testRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null

Assert-True -Condition (Test-Path -LiteralPath $exportScript) -Message "Missing exporter: $exportScript"

$arguments = @{
    PackageDirectory = $packageDirectory
    ArchivePath = $archivePath
}
if (-not $IncludeCompileCheck) {
    $arguments['SkipCompileCheck'] = $true
}

& $exportScript @arguments

$requiredFiles = @(
    'main.tex',
    'latexmkrc',
    'bibliography/references.bib',
    'sections/introduction.tex',
    'sections/results_diffuse_pbi2.tex',
    '2D_Supplemental/SI_failure_modes.tex',
    '2D_Supplemental/SI_ordered_structure_parameters.tex',
    'figures/intro/area_detector_bragg_peaks_overview.pdf',
    'figures/geometry/system_geometry.pdf',
    'figures/geometry/sample_geometry_rotation.pdf',
    'figures/geometry/sample_geometry_alignment.pdf',
    'figures/mosaic/mosaic_bragg_inplane.pdf',
    'figures/mosaic/mosaic_bragg_specular.pdf',
    'figures/results_pbi2/transition_matrix/pbi2_polytype_stacks.pdf'
)
foreach ($relativePath in $requiredFiles) {
    $candidate = Join-Path $packageDirectory $relativePath
    Assert-True -Condition (Test-Path -LiteralPath $candidate -PathType Leaf) -Message "Missing package dependency: $relativePath"
}

$packagedFiles = @(Get-ChildItem -LiteralPath $packageDirectory -Recurse -Force -File)
$forbiddenNames = @('.git', '.github', 'build', 'build_overleaf', 'scripts', '__pycache__')
$forbiddenExtensions = @('.aux', '.bbl', '.blg', '.fdb_latexmk', '.fls', '.log', '.out', '.synctex.gz')
foreach ($file in $packagedFiles) {
    $relativePath = $file.FullName.Substring($packageDirectory.Length).TrimStart('\', '/')
    $segments = $relativePath -split '[\\/]'
    Assert-True -Condition (-not ($segments | Where-Object { $_ -in $forbiddenNames })) -Message "Forbidden path in package: $relativePath"
    Assert-True -Condition (-not ($forbiddenExtensions | Where-Object { $relativePath.EndsWith($_, [System.StringComparison]::OrdinalIgnoreCase) })) -Message "Forbidden build artifact in package: $relativePath"
}

$liveFigureSources = @(Get-ChildItem -LiteralPath (Join-Path $packageDirectory 'figures') -Recurse -Filter '*.tex' -File)
Assert-True -Condition ($liveFigureSources.Count -eq 0) -Message 'The package still contains live TikZ figure sources.'
$liveRasterSources = @(Get-ChildItem -LiteralPath (Join-Path $packageDirectory 'figures') -Recurse -File | Where-Object { $_.Extension -in '.png', '.jpg', '.jpeg', '.eps' })
Assert-True -Condition ($liveRasterSources.Count -eq 0) -Message 'The package still contains raster graphics instead of cached PDFs.'

$packagedTex = Get-Content -Raw -LiteralPath (Join-Path $packageDirectory 'main.tex')
Assert-True -Condition ($packagedTex -notmatch '\\usepackage\{pgfplots\}|\\usepgfplotslibrary|\\pgfplotsset') -Message 'The staged main.tex still loads unused pgfplots code.'
Assert-True -Condition ($packagedTex -notmatch '\\usepackage\{tikz(?:-3dplot)?\}|\\usetikzlibrary|\\begin\{tikzpicture\}') -Message 'The staged main.tex still builds live TikZ content.'

$sectionText = (Get-ChildItem -LiteralPath (Join-Path $packageDirectory 'sections') -Filter '*.tex' -File | ForEach-Object { Get-Content -Raw -LiteralPath $_.FullName }) -join "`n"
Assert-True -Condition ($sectionText -notmatch '\\input\{figures/') -Message 'A staged section still inputs a live figure source.'

Assert-True -Condition (Test-Path -LiteralPath $archivePath -PathType Leaf) -Message 'The Overleaf ZIP was not created.'
Expand-Archive -LiteralPath $archivePath -DestinationPath $expandedArchive
Assert-True -Condition (Test-Path -LiteralPath (Join-Path $expandedArchive 'main.tex') -PathType Leaf) -Message 'The ZIP does not place main.tex at its root.'
Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $expandedArchive '.git'))) -Message 'The ZIP contains Git metadata.'

$cacheDirectory = Join-Path $buildRoot 'graphics-cache'
$cacheBefore = @(Get-ChildItem -LiteralPath $cacheDirectory -Filter '*.pdf' -File | Sort-Object Name)
Assert-True -Condition ($cacheBefore.Count -eq 34) -Message "Expected 34 cached graphics, found $($cacheBefore.Count)."
$timestampsBefore = @{}
foreach ($file in $cacheBefore) {
    $timestampsBefore[$file.Name] = $file.LastWriteTimeUtc
}

& $exportScript @arguments

$cacheAfter = @(Get-ChildItem -LiteralPath $cacheDirectory -Filter '*.pdf' -File | Sort-Object Name)
foreach ($file in $cacheAfter) {
    Assert-True -Condition ($timestampsBefore[$file.Name] -eq $file.LastWriteTimeUtc) -Message "Cached graphic was rebuilt unnecessarily: $($file.Name)"
}

Write-Output "Overleaf export integration test passed: $archivePath"
