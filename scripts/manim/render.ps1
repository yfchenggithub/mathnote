param(
    [Parameter(Mandatory = $true)][string]$Uid,
    [string]$Scene,
    [string]$SceneFile,
    [string]$Name,
    [string]$BuildRoot = 'build/manim'
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$python = Join-Path $root '.venv-manim/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Manim environment missing: $python" }
$arguments = @((Join-Path $PSScriptRoot 'production.py'), 'render', '--uid', $Uid, '--build-root', $BuildRoot)
if ($Scene) { $arguments += @('--scene', $Scene) }
if ($SceneFile) { $arguments += @('--scene-file', $SceneFile) }
if ($Name) { $arguments += @('--name', $Name) }
$ErrorActionPreference = 'Continue' # PowerShell 5 treats redirected native stderr as an error record.
& $python @arguments
$code = $LASTEXITCODE
if ($code -ne 0) { exit $code }
