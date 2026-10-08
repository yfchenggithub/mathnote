param(
    [Parameter(Mandatory = $true)][ValidatePattern('^[A-Z][0-9]{3}$')][string]$Uid
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$python = Join-Path $root '.venv-manim/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Manim environment missing: $python" }
$matches = @(Get-ChildItem -LiteralPath $root -Directory | Where-Object Name -Match '^([0-9]{2}|10)_' | ForEach-Object {
    Get-ChildItem -LiteralPath $_.FullName -Directory -Filter "${Uid}_*"
})
if ($matches.Count -ne 1) { throw "Expected one conclusion directory for $Uid; found $($matches.Count)" }
$scene = Join-Path $matches[0].FullName 'manim/scene.py'
if (-not (Test-Path -LiteralPath $scene -PathType Leaf)) { throw "Scene missing: $scene" }
$media = Join-Path $root "build/manim/$Uid"
New-Item -ItemType Directory -Force -Path $media | Out-Null
$outName = "${Uid}_distance.mp4"
$sceneName = "${Uid}DistancePilot"
Push-Location $root
try {
    & $python -m manim --disable_caching -r 576,1024 --fps 24 --media_dir $media --output_file $outName $scene $sceneName
} finally {
    Pop-Location
}
if ($LASTEXITCODE -ne 0) { throw "Manim render failed with exit code $LASTEXITCODE" }
$rendered = @(Get-ChildItem -LiteralPath (Join-Path $media 'videos') -Recurse -File -Filter $outName |
    Where-Object { $_.FullName -notmatch 'partial_movie_files' })
if ($rendered.Count -ne 1) { throw "Expected one rendered MP4, found $($rendered.Count)" }
$stable = Join-Path $media $outName
Copy-Item -LiteralPath $rendered[0].FullName -Destination $stable -Force
Write-Output "MP4: $stable"
