param([switch]$SkipRender)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$python = Join-Path $root '.venv-manim/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Manim environment missing: $python" }
$scene = Join-Path $PSScriptRoot 'scene_max_distance.py'
$media = Join-Path $root 'build/manim/C001'
$mp4 = Join-Path $media 'C001_max_distance.mp4'
$gif = Join-Path $PSScriptRoot '../images/ellipse_circle_max_distance.gif'
New-Item -ItemType Directory -Force -Path $media | Out-Null

Push-Location $root
try {
    & $python -B -m unittest discover -s $PSScriptRoot -p test_max_distance.py
    if ($LASTEXITCODE -ne 0) { throw 'Maximum-distance mathematical checks failed' }
    if (-not $SkipRender) {
        & $python -m manim --disable_caching -r 576,1024 --fps 24 `
            --media_dir $media --output_file 'C001_max_distance.mp4' `
            $scene C001MaxDistance
        if ($LASTEXITCODE -ne 0) { throw 'Manim render failed' }
        $rendered = @(Get-ChildItem -LiteralPath (Join-Path $media 'videos') -Recurse -File `
            -Filter 'C001_max_distance.mp4' | Where-Object {
                $_.FullName -notmatch 'partial_movie_files'
            })
        if ($rendered.Count -ne 1) { throw "Expected one MP4; found $($rendered.Count)" }
        Copy-Item -LiteralPath $rendered[0].FullName -Destination $mp4 -Force
    }
    if (-not (Test-Path -LiteralPath $mp4 -PathType Leaf)) { throw "MP4 missing: $mp4" }
    $ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
    $palette = Join-Path $media 'max_distance_palette.png'
    $staged = Join-Path $media 'ellipse_circle_max_distance.gif'
    & $ffmpeg -hide_banner -loglevel error -y -i $mp4 `
        -vf 'fps=12,scale=576:-1:flags=lanczos,palettegen=max_colors=128:stats_mode=diff' $palette
    if ($LASTEXITCODE -ne 0) { throw 'Palette generation failed' }
    & $ffmpeg -hide_banner -loglevel error -y -i $mp4 -i $palette `
        -filter_complex '[0:v]fps=12,scale=576:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle' `
        -loop 0 $staged
    if ($LASTEXITCODE -ne 0) { throw 'GIF export failed' }
    & $python (Join-Path $root 'scripts/manim/verify_gif.py') $staged
    if ($LASTEXITCODE -ne 0) { throw 'GIF verification failed' }
    Copy-Item -LiteralPath $staged -Destination $gif -Force
    Write-Output "MP4: $mp4"
    Write-Output "GIF: $gif"
} finally {
    Pop-Location
}
