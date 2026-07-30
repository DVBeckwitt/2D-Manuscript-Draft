<#
.SYNOPSIS
Creates a dependency-only, graphics-cached Overleaf package and ZIP.

.DESCRIPTION
Copies the main manuscript and Supporting Information dependency closure into
build_overleaf/overleaf. Referenced TikZ and raster graphics are losslessly
pre-rendered as cached PDFs, so Overleaf does not rebuild or decode them on
each LaTeX pass. Git metadata, scripts, existing PDFs, and LaTeX auxiliaries
are not included. By default, both document entry points are compile-checked
before build_overleaf/overleaf.zip is created.

.EXAMPLE
.\scripts\export-overleaf.ps1

.EXAMPLE
.\scripts\export-overleaf.ps1 -SkipCompileCheck
#>

param(
    [string]$PackageDirectory,
    [string]$ArchivePath,
    [switch]$SkipCompileCheck
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$buildRoot = Join-Path $repoRoot 'build_overleaf'
$graphicsCache = Join-Path $buildRoot 'graphics-cache'
$graphicsWork = Join-Path $buildRoot 'graphics-work'
$validationRoot = Join-Path $buildRoot 'validation'
$graphicsCacheVersion = '6'

if (-not $PackageDirectory) {
    $PackageDirectory = Join-Path $buildRoot 'overleaf'
}
if (-not $ArchivePath) {
    $ArchivePath = Join-Path $buildRoot 'overleaf.zip'
}

function Get-FullPath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $repoRoot $Path))
}

function Assert-GeneratedPath {
    param([string]$Path)

    $fullPath = Get-FullPath -Path $Path
    $fullBuildRoot = Get-FullPath -Path $buildRoot
    $expectedPrefix = $fullBuildRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $fullPath.StartsWith($expectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Generated paths must remain inside build_overleaf. Refusing: $fullPath"
    }
    if ($fullPath.Equals($fullBuildRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to use build_overleaf itself as a generated file target: $fullPath"
    }
}

function Remove-GeneratedItem {
    param([string]$Path)

    Assert-GeneratedPath -Path $Path
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

function Copy-RepositoryFile {
    param(
        [string]$RelativePath,
        [string]$DestinationRoot = $PackageDirectory
    )

    $normalized = $RelativePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    $source = Join-Path $repoRoot $normalized
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Missing repository file required by the Overleaf export: $RelativePath"
    }

    $destination = Join-Path $DestinationRoot $normalized
    $destinationParent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination -Force
}

function Get-RepositoryRelativePath {
    param([string]$FullPath)

    $fullRepoRoot = Get-FullPath -Path $repoRoot
    $fullCandidate = Get-FullPath -Path $FullPath
    $expectedPrefix = $fullRepoRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $fullCandidate.StartsWith($expectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Referenced dependency is outside the repository: $fullCandidate"
    }
    return $fullCandidate.Substring($expectedPrefix.Length).Replace('\', '/')
}

function Resolve-TeXReference {
    param(
        [string]$Reference,
        [string]$SourceFile
    )

    $platformReference = $Reference.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    $sourceDirectory = Split-Path -Parent $SourceFile
    $candidates = @(
        [System.IO.Path]::GetFullPath((Join-Path $sourceDirectory $platformReference)),
        [System.IO.Path]::GetFullPath((Join-Path $repoRoot $platformReference))
    )

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }
    throw "Could not resolve TeX dependency '$Reference' referenced by '$SourceFile'."
}

function Invoke-CommandChecked {
    param(
        [string]$Command,
        [string[]]$Arguments,
        [string]$WorkingDirectory
    )

    Push-Location -LiteralPath $WorkingDirectory
    try {
        $commandOutput = & $Command @Arguments 2>&1
        if ($LASTEXITCODE -ne 0) {
            $details = $commandOutput -join [Environment]::NewLine
            throw "$Command $($Arguments -join ' ') failed with exit code $LASTEXITCODE.`n$details"
        }
    }
    finally {
        Pop-Location
    }
}

function Get-GraphicCacheName {
    param(
        [string]$RelativeSourcePath,
        [string]$Kind
    )

    $withoutExtension = $RelativeSourcePath -replace '\.[^./\\]+$', ''
    return ($Kind + '__' + ($withoutExtension -replace '[^A-Za-z0-9._-]', '__') + '.pdf')
}

function Build-CachedGraphic {
    param([string]$RelativeSourcePath)

    $sourcePath = Join-Path $repoRoot $RelativeSourcePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourcePath).Hash.ToLowerInvariant()
    $cacheKey = "$graphicsCacheVersion`:$sourceHash"
    $cacheName = Get-GraphicCacheName -RelativeSourcePath $RelativeSourcePath -Kind 'tikz'
    $cachedPdf = Join-Path $graphicsCache $cacheName
    $cachedHash = "$cachedPdf.sha256"

    if ((Test-Path -LiteralPath $cachedPdf -PathType Leaf) -and
        (Test-Path -LiteralPath $cachedHash -PathType Leaf) -and
        ((Get-Content -Raw -LiteralPath $cachedHash).Trim() -eq $cacheKey)) {
        $script:cacheHits++
        return $cachedPdf
    }

    $script:cacheMisses++
    $workName = [System.IO.Path]::GetFileNameWithoutExtension($cacheName)
    $workDirectory = Join-Path $graphicsWork $workName
    Remove-GeneratedItem -Path $workDirectory
    New-Item -ItemType Directory -Path $workDirectory -Force | Out-Null

    Copy-Item -LiteralPath $sourcePath -Destination (Join-Path $workDirectory 'figure-source.tex') -Force
    $wrapper = @'
\documentclass[12pt,border=40bp]{standalone}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{setspace}
\setstretch{1.1}
\usepackage{tikz-3dplot}
\usetikzlibrary{calc,arrows.meta}
\usepackage{amsmath,amssymb,amsfonts,bm}
\definecolor{oiPurple}{RGB}{204,121,167}
\definecolor{oiOrange}{RGB}{230,159,0}
\begin{document}
\input{figure-source.tex}
\end{document}
'@
    Set-Content -LiteralPath (Join-Path $workDirectory 'graphic-wrapper.tex') -Value $wrapper -Encoding utf8

    Invoke-CommandChecked -Command 'pdflatex' -Arguments @(
        '-interaction=nonstopmode',
        '-halt-on-error',
        '-file-line-error',
        'graphic-wrapper.tex'
    ) -WorkingDirectory $workDirectory

    $builtPdf = Join-Path $workDirectory 'graphic-wrapper.pdf'
    if (-not (Test-Path -LiteralPath $builtPdf -PathType Leaf)) {
        throw "Graphic compilation did not produce a PDF for $RelativeSourcePath"
    }

    New-Item -ItemType Directory -Path $graphicsCache -Force | Out-Null
    Copy-Item -LiteralPath $builtPdf -Destination $cachedPdf -Force
    Set-Content -LiteralPath $cachedHash -Value $cacheKey -Encoding ascii
    return $cachedPdf
}

function Build-CachedRasterGraphic {
    param([string]$RelativeSourcePath)

    $sourcePath = Join-Path $repoRoot $RelativeSourcePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourcePath).Hash.ToLowerInvariant()
    $cacheKey = "$graphicsCacheVersion`:$sourceHash"
    $cacheName = Get-GraphicCacheName -RelativeSourcePath $RelativeSourcePath -Kind 'image'
    $cachedPdf = Join-Path $graphicsCache $cacheName
    $cachedHash = "$cachedPdf.sha256"

    if ((Test-Path -LiteralPath $cachedPdf -PathType Leaf) -and
        (Test-Path -LiteralPath $cachedHash -PathType Leaf) -and
        ((Get-Content -Raw -LiteralPath $cachedHash).Trim() -eq $cacheKey)) {
        $script:cacheHits++
        return $cachedPdf
    }

    $script:cacheMisses++
    $workName = [System.IO.Path]::GetFileNameWithoutExtension($cacheName)
    $workDirectory = Join-Path $graphicsWork $workName
    Remove-GeneratedItem -Path $workDirectory
    New-Item -ItemType Directory -Path $workDirectory -Force | Out-Null

    $sourceExtension = [System.IO.Path]::GetExtension($sourcePath).ToLowerInvariant()
    $workImageName = 'image-source' + $sourceExtension
    Copy-Item -LiteralPath $sourcePath -Destination (Join-Path $workDirectory $workImageName) -Force
    $wrapper = @"
\documentclass[border=0pt]{standalone}
\usepackage{graphicx}
\begin{document}
\includegraphics{$workImageName}
\end{document}
"@
    Set-Content -LiteralPath (Join-Path $workDirectory 'graphic-wrapper.tex') -Value $wrapper -Encoding utf8

    Invoke-CommandChecked -Command 'pdflatex' -Arguments @(
        '-interaction=nonstopmode',
        '-halt-on-error',
        '-file-line-error',
        'graphic-wrapper.tex'
    ) -WorkingDirectory $workDirectory

    $builtPdf = Join-Path $workDirectory 'graphic-wrapper.pdf'
    if (-not (Test-Path -LiteralPath $builtPdf -PathType Leaf)) {
        throw "Raster wrapping did not produce a PDF for $RelativeSourcePath"
    }

    Copy-Item -LiteralPath $builtPdf -Destination $cachedPdf -Force
    Set-Content -LiteralPath $cachedHash -Value $cacheKey -Encoding ascii
    return $cachedPdf
}

function Rewrite-StagedTeX {
    param([string]$StagedTexPath)

    $text = Get-Content -Raw -LiteralPath $StagedTexPath
    $rasterReferencePattern = '(?<path>(?:\.\./)?(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+)\.(?:png|jpe?g|eps)'
    $text = [System.Text.RegularExpressions.Regex]::Replace(
        $text,
        $rasterReferencePattern,
        '${path}.pdf',
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    $figureInputPattern = '\\input\{(?<path>(?:\.\./)?figures/[^}]+?)(?:\.tex)?\}'
    $text = [System.Text.RegularExpressions.Regex]::Replace(
        $text,
        $figureInputPattern,
        {
            param($match)
            $reference = $match.Groups['path'].Value
            $pdfReference = [System.IO.Path]::ChangeExtension($reference, '.pdf').Replace('\', '/')
            return "\includegraphics[trim=40 40 40 40]{$pdfReference}"
        }
    )

    if ([System.IO.Path]::GetFileName($StagedTexPath) -eq 'main.tex') {
        $panelTaggedPattern = '(?s)\\newcommand\{\\paneltagged\}\[2\]\{%.*?\\end\{tikzpicture\}%\s*\}'
        $panelTaggedReplacement = @'
\newsavebox{\panelcontent}
\newsavebox{\panellabel}
\newcommand{\paneltagged}[2]{%
  \begingroup
  \sbox{\panelcontent}{#2}%
  \sbox{\panellabel}{\bfseries #1}%
  \vbox{\offinterlineskip
    \kern1.9pt
    \hbox{\kern1.5pt\usebox{\panellabel}\kern1.5pt}%
    \kern4.5pt
    \hbox{\usebox{\panelcontent}}%
  }%
  \endgroup
}
'@
        $updatedText = [System.Text.RegularExpressions.Regex]::Replace(
            $text,
            $panelTaggedPattern,
            $panelTaggedReplacement
        )
        if ($updatedText -eq $text) {
            throw 'Could not replace the TikZ-based \paneltagged helper in staged main.tex.'
        }
        $text = $updatedText

        $panelGraphicPattern = '(?s)\\newcommand\{\\panelgraphic\}\[3\]\[\]\{%.*?\\end\{tikzpicture\}%\s*\}\s*'
        $text = [System.Text.RegularExpressions.Regex]::Replace($text, $panelGraphicPattern, '')

        $linesToRemove = @(
            '(?m)^\s*\\usepackage\{tikz\}\s*\r?\n',
            '(?m)^\s*\\usepackage\{pgfplots\}\s*\r?\n',
            '(?m)^\s*\\pgfplotsset\{[^\r\n]*\}\s*\r?\n',
            '(?m)^\s*\\usepackage\{pgf\}\s*\r?\n',
            '(?m)^\s*\\usepgfplotslibrary\{fillbetween\}\s*\r?\n',
            '(?m)^\s*\\usepackage\{tikz-3dplot\}\s*\r?\n',
            '(?m)^\s*\\usetikzlibrary\{[^\r\n]*\}\s*\r?\n'
        )
        foreach ($pattern in $linesToRemove) {
            $text = [System.Text.RegularExpressions.Regex]::Replace($text, $pattern, '')
        }
    }

    Set-Content -LiteralPath $StagedTexPath -Value $text -Encoding utf8
}

function Invoke-PackageCompileCheck {
    Remove-GeneratedItem -Path $validationRoot
    New-Item -ItemType Directory -Path $validationRoot -Force | Out-Null
    Copy-Item -Path (Join-Path $PackageDirectory '*') -Destination $validationRoot -Recurse -Force

    $mainTimer = [System.Diagnostics.Stopwatch]::StartNew()
    Invoke-CommandChecked -Command 'latexmk' -Arguments @(
        '-pdf',
        '-interaction=nonstopmode',
        '-halt-on-error',
        '-file-line-error',
        'main.tex'
    ) -WorkingDirectory $validationRoot
    $mainTimer.Stop()

    $mainPdf = Join-Path $validationRoot 'main.pdf'
    if (-not (Test-Path -LiteralPath $mainPdf -PathType Leaf)) {
        throw 'The staged main manuscript did not produce main.pdf.'
    }

    $siDirectory = Join-Path $validationRoot '2D_Supplemental'
    $siTimer = [System.Diagnostics.Stopwatch]::StartNew()
    Invoke-CommandChecked -Command 'latexmk' -Arguments @(
        '-pdf',
        '-interaction=nonstopmode',
        '-halt-on-error',
        '-file-line-error',
        'SI_failure_modes.tex'
    ) -WorkingDirectory $siDirectory
    $siTimer.Stop()

    $siPdf = Join-Path $siDirectory 'SI_failure_modes.pdf'
    if (-not (Test-Path -LiteralPath $siPdf -PathType Leaf)) {
        throw 'The staged Supporting Information did not produce SI_failure_modes.pdf.'
    }

    $script:mainCompileSeconds = $mainTimer.Elapsed.TotalSeconds
    $script:siCompileSeconds = $siTimer.Elapsed.TotalSeconds
    Remove-GeneratedItem -Path $validationRoot
}

$PackageDirectory = Get-FullPath -Path $PackageDirectory
$ArchivePath = Get-FullPath -Path $ArchivePath
Assert-GeneratedPath -Path $PackageDirectory
Assert-GeneratedPath -Path $ArchivePath

if (-not (Get-Command pdflatex -ErrorAction SilentlyContinue)) {
    throw 'pdflatex is required to pre-render the TikZ figures.'
}
if ((-not $SkipCompileCheck) -and (-not (Get-Command latexmk -ErrorAction SilentlyContinue))) {
    throw 'latexmk is required for the package compile check.'
}

$script:cacheHits = 0
$script:cacheMisses = 0
$script:mainCompileSeconds = $null
$script:siCompileSeconds = $null

Remove-GeneratedItem -Path $PackageDirectory
Remove-GeneratedItem -Path $ArchivePath
Remove-GeneratedItem -Path $graphicsWork
New-Item -ItemType Directory -Path $PackageDirectory -Force | Out-Null
New-Item -ItemType Directory -Path $graphicsWork -Force | Out-Null

$cacheVersionFile = Join-Path $graphicsCache '.cache-version'
$cacheVersionMatches = (Test-Path -LiteralPath $cacheVersionFile -PathType Leaf) -and
    ((Get-Content -Raw -LiteralPath $cacheVersionFile).Trim() -eq $graphicsCacheVersion)
if (-not $cacheVersionMatches) {
    Remove-GeneratedItem -Path $graphicsCache
    New-Item -ItemType Directory -Path $graphicsCache -Force | Out-Null
    Set-Content -LiteralPath $cacheVersionFile -Value $graphicsCacheVersion -Encoding ascii
}

$sourceFiles = @(
    'main.tex',
    'latexmkrc',
    'bibliography/references.bib'
)
$sourceFiles += Get-ChildItem -LiteralPath (Join-Path $repoRoot 'sections') -Filter '*.tex' -File |
    ForEach-Object { 'sections/' + $_.Name }
$sourceFiles += Get-ChildItem -LiteralPath (Join-Path $repoRoot '2D_Supplemental') -Filter '*.tex' -File |
    ForEach-Object { '2D_Supplemental/' + $_.Name }
$sourceFiles = @($sourceFiles | Sort-Object -Unique)

foreach ($relativePath in $sourceFiles) {
    Copy-RepositoryFile -RelativePath $relativePath
}

$texSourceFiles = @($sourceFiles | Where-Object { $_.EndsWith('.tex', [System.StringComparison]::OrdinalIgnoreCase) })
$imageReferences = @{}
$figureSourceReferences = @{}
$imagePattern = '(?<path>(?:\.\./)?(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:png|jpe?g|pdf|eps))'
$figureInputPattern = '\\input\{(?<path>(?:\.\./)?figures/[^}]+?)(?:\.tex)?\}'

foreach ($relativeTexPath in $texSourceFiles) {
    $sourceTexPath = Join-Path $repoRoot $relativeTexPath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    $text = Get-Content -Raw -LiteralPath $sourceTexPath

    foreach ($match in [System.Text.RegularExpressions.Regex]::Matches($text, $imagePattern)) {
        $reference = $match.Groups['path'].Value
        try {
            $resolved = Resolve-TeXReference -Reference $reference -SourceFile $sourceTexPath
            $relativeDependency = Get-RepositoryRelativePath -FullPath $resolved
            $imageReferences[$relativeDependency] = $true
        }
        catch {
            if ($match.Value -notmatch '^#') {
                throw
            }
        }
    }

    foreach ($match in [System.Text.RegularExpressions.Regex]::Matches($text, $figureInputPattern)) {
        $reference = $match.Groups['path'].Value
        if (-not $reference.EndsWith('.tex', [System.StringComparison]::OrdinalIgnoreCase)) {
            $reference += '.tex'
        }
        $resolved = Resolve-TeXReference -Reference $reference -SourceFile $sourceTexPath
        $relativeDependency = Get-RepositoryRelativePath -FullPath $resolved
        $figureSourceReferences[$relativeDependency] = $true
    }
}

foreach ($relativePath in $imageReferences.Keys | Sort-Object) {
    $extension = [System.IO.Path]::GetExtension($relativePath).ToLowerInvariant()
    if ($extension -eq '.pdf') {
        Copy-RepositoryFile -RelativePath $relativePath
        continue
    }

    $cachedPdf = Build-CachedRasterGraphic -RelativeSourcePath $relativePath
    $relativePdfPath = [System.IO.Path]::ChangeExtension($relativePath, '.pdf').Replace('\', '/')
    $destinationPdf = Join-Path $PackageDirectory $relativePdfPath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    New-Item -ItemType Directory -Path (Split-Path -Parent $destinationPdf) -Force | Out-Null
    Copy-Item -LiteralPath $cachedPdf -Destination $destinationPdf -Force
}

foreach ($relativeSourcePath in $figureSourceReferences.Keys | Sort-Object) {
    $cachedPdf = Build-CachedGraphic -RelativeSourcePath $relativeSourcePath
    $relativePdfPath = [System.IO.Path]::ChangeExtension($relativeSourcePath, '.pdf').Replace('\', '/')
    $destinationPdf = Join-Path $PackageDirectory $relativePdfPath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    New-Item -ItemType Directory -Path (Split-Path -Parent $destinationPdf) -Force | Out-Null
    Copy-Item -LiteralPath $cachedPdf -Destination $destinationPdf -Force
}

$stagedTexFiles = @(Get-ChildItem -LiteralPath $PackageDirectory -Recurse -Filter '*.tex' -File)
foreach ($stagedTexFile in $stagedTexFiles) {
    Rewrite-StagedTeX -StagedTexPath $stagedTexFile.FullName
}

$liveFigureInputs = Select-String -Path ($stagedTexFiles.FullName) -Pattern '\\input\{(?:\.\./)?figures/' -AllMatches
if ($liveFigureInputs) {
    throw 'The staged package still contains live figure inputs after rewriting.'
}

if (-not $SkipCompileCheck) {
    Invoke-PackageCompileCheck
}

Remove-GeneratedItem -Path $graphicsWork
New-Item -ItemType Directory -Path (Split-Path -Parent $ArchivePath) -Force | Out-Null
Compress-Archive -Path (Join-Path $PackageDirectory '*') -DestinationPath $ArchivePath -CompressionLevel Optimal

$packageFileCount = @(Get-ChildItem -LiteralPath $PackageDirectory -Recurse -File).Count
$archiveSizeMb = (Get-Item -LiteralPath $ArchivePath).Length / 1MB
Write-Output "Overleaf package created: $PackageDirectory"
Write-Output "Overleaf ZIP created: $ArchivePath"
Write-Output ("Package files: {0}; ZIP size: {1:N2} MB" -f $packageFileCount, $archiveSizeMb)
Write-Output "Graphics cache: $($script:cacheHits) hit(s), $($script:cacheMisses) rebuilt"
if (-not $SkipCompileCheck) {
    Write-Output ("Compile checks: main {0:N2}s; SI {1:N2}s" -f $script:mainCompileSeconds, $script:siCompileSeconds)
}
