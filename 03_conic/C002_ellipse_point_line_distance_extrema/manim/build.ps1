param([switch]$SkipRender)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$python = Join-Path $root '.venv-manim/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Manim environment missing: $python" }
$media = Join-Path $root 'build/manim/C002'
$mp4 = Join-Path $media 'C002_ellipse_line_distance.mp4'
$gif = Join-Path $PSScriptRoot '../images/ellipse_line_distance.gif'
New-Item -ItemType Directory -Force -Path $media | Out-Null
Push-Location $root
try {
    & $python -B -m unittest discover -s $PSScriptRoot -p test_math_model.py
    if ($LASTEXITCODE -ne 0) { throw 'C002 mathematical validation failed' }
    if (-not $SkipRender) {
        & $python -m manim --disable_caching -r 576,1024 --fps 24 `
            --media_dir $media --output_file 'C002_ellipse_line_distance.mp4' `
            (Join-Path $PSScriptRoot 'scene.py') C002DistanceLesson
        if ($LASTEXITCODE -ne 0) { throw 'C002 render failed' }
        $rendered = @(Get-ChildItem -LiteralPath (Join-Path $media 'videos') -Recurse -File `
            -Filter 'C002_ellipse_line_distance.mp4' | Where-Object {
                $_.FullName -notmatch 'partial_movie_files'
            })
        if ($rendered.Count -ne 1) { throw "Expected one MP4; found $($rendered.Count)" }
        Copy-Item -LiteralPath $rendered[0].FullName -Destination $mp4 -Force
    }
    if (-not (Test-Path -LiteralPath $mp4 -PathType Leaf)) { throw "Missing MP4: $mp4" }
    $ffmpeg = (Get-Command ffmpeg -ErrorAction Stop).Source
    $palette = Join-Path $media 'C002_palette.png'
    $staged = Join-Path $media 'C002_ellipse_line_distance.gif'
    & $ffmpeg -hide_banner -loglevel error -y -i $mp4 `
        -vf 'fps=12,scale=576:-1:flags=lanczos,palettegen=max_colors=128:stats_mode=diff' $palette
    if ($LASTEXITCODE -ne 0) { throw 'C002 palette generation failed' }
    & $ffmpeg -hide_banner -loglevel error -y -i $mp4 -i $palette `
        -filter_complex '[0:v]fps=12,scale=576:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle' `
        -loop 0 $staged
    if ($LASTEXITCODE -ne 0) { throw 'C002 GIF export failed' }
    & $python (Join-Path $root 'scripts/manim/verify_gif.py') $staged
    if ($LASTEXITCODE -ne 0) { throw 'C002 GIF validation failed' }
    Copy-Item -LiteralPath $staged -Destination $gif
    Write-Output "MP4: $mp4"
    Write-Output "GIF: $gif"
} finally {
    Pop-Location
}
