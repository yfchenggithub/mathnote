param(
    [Parameter(Mandatory = $true)][ValidatePattern('^[A-Z][0-9]{3}$')][string]$Uid,
    [switch]$Rebuild
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$matches = @(Get-ChildItem -LiteralPath $root -Directory | Where-Object Name -Match '^([0-9]{2}|10)_' | ForEach-Object {
    Get-ChildItem -LiteralPath $_.FullName -Directory -Filter "${Uid}_*"
})
if ($matches.Count -ne 1) { throw "Expected one conclusion directory for $Uid; found $($matches.Count)" }
$media = Join-Path $root "build/manim/$Uid"
$mp4 = Join-Path $media "${Uid}_distance.mp4"
if ($Rebuild -or -not (Test-Path -LiteralPath $mp4 -PathType Leaf)) {
    & (Join-Path $PSScriptRoot 'render.ps1') -Uid $Uid
    if ($LASTEXITCODE -ne 0) { throw "MP4 render failed with exit code $LASTEXITCODE" }
}
$ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
$palette = Join-Path $media 'palette.png'
$staged = Join-Path $media 'ellipse_circle_distance.gif'
$asset = Join-Path $matches[0].FullName 'images/ellipse_circle_distance.gif'
& $ffmpeg -hide_banner -loglevel error -y -i $mp4 -vf 'fps=12,scale=576:-1:flags=lanczos,palettegen=max_colors=128:stats_mode=diff' $palette
if ($LASTEXITCODE -ne 0) { throw "FFmpeg palette generation failed with exit code $LASTEXITCODE" }
& $ffmpeg -hide_banner -loglevel error -y -i $mp4 -i $palette -filter_complex '[0:v]fps=12,scale=576:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle' -loop 0 $staged
if ($LASTEXITCODE -ne 0) { throw "FFmpeg GIF export failed with exit code $LASTEXITCODE" }
if (-not (Test-Path -LiteralPath $staged -PathType Leaf) -or (Get-Item -LiteralPath $staged).Length -eq 0) { throw 'GIF missing or empty' }
$python = Join-Path $root '.venv-manim/Scripts/python.exe'
& $python (Join-Path $PSScriptRoot 'verify_gif.py') $staged
if ($LASTEXITCODE -ne 0) { throw "GIF validation failed with exit code $LASTEXITCODE" }
Copy-Item -LiteralPath $staged -Destination $asset -Force
Write-Output "GIF: $asset"
