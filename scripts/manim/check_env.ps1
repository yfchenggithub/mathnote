$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$python = Join-Path $root '.venv-manim/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Python environment missing: $python" }
Write-Output "Repository: $root"
& $python --version
if ($LASTEXITCODE -ne 0) { throw 'Python failed' }
& $python -c "import manim, PIL; print('Manim', manim.__version__, 'Pillow', PIL.__version__)"
if ($LASTEXITCODE -ne 0) { throw 'Manim or Pillow import failed' }
foreach ($tool in @('ffmpeg', 'latex', 'dvisvgm', 'fc-match')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "Required tool missing: $tool" }
    Write-Output "$tool`: $((Get-Command $tool).Source)"
}
$font = & fc-match -f '%{family}' 'Microsoft YaHei'
if ($LASTEXITCODE -ne 0 -or $font -notmatch 'Microsoft YaHei|微软雅黑') {
    throw "Microsoft YaHei unavailable (matched: $font)"
}
Write-Output "Chinese font: $font"
Write-Output 'Environment PASS'
