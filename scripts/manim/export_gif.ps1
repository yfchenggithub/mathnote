param(
    [Parameter(Mandatory = $true)][string]$Uid,
    [string]$Scene,
    [string]$SceneFile,
    [string]$Name,
    [string]$AssetName,
    [string]$BuildRoot = 'build/manim',
    [switch]$Rebuild,
    [switch]$Publish,
    [switch]$Overwrite
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$python = Join-Path $root '.venv-manim/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "Manim environment missing: $python" }
$arguments = @((Join-Path $PSScriptRoot 'production.py'), 'export', '--uid', $Uid, '--build-root', $BuildRoot)
if ($Scene) { $arguments += @('--scene', $Scene) }
if ($SceneFile) { $arguments += @('--scene-file', $SceneFile) }
if ($Name) { $arguments += @('--name', $Name) }
if ($AssetName) { $arguments += @('--asset-name', $AssetName) }
if ($Rebuild) { $arguments += '--rebuild' }
if ($Publish) { $arguments += '--publish' }
if ($Overwrite) { $arguments += '--overwrite' }
$ErrorActionPreference = 'Continue' # Native stderr must not interrupt redirected builds.
& $python @arguments
$code = $LASTEXITCODE
if ($code -ne 0) { exit $code }
