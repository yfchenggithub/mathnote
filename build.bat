@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
set "BUILD_DIR=99_build"

REM =========================
REM Clean build directory
REM =========================
if exist "%BUILD_DIR%" (
    echo Cleaning %BUILD_DIR% directory...
    rmdir /s /q "%BUILD_DIR%"
)

mkdir "%BUILD_DIR%"
mkdir "%BUILD_DIR%\encrypted"

REM =========================
REM Use PowerShell to avoid locale-dependent %date% parsing issues.
REM =========================
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd-HH-mm-ss'"`) do (
    set "timestamp=%%i"
)

if "%USER_ID%"=="" (
    echo 警告: USER_ID 环境变量未设置，加密文件名将不包含用户标识。
)

REM =========================
REM Create build timestamp file
REM =========================
echo Build time: %timestamp% > "%BUILD_DIR%\build-%timestamp%.txt"

REM =========================
REM Compile with XeLaTeX
REM =========================
set "LATEXMK_LOG=%BUILD_DIR%\latexmk.log"
echo Compiling main.tex ...
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir="%BUILD_DIR%" main.tex > "%LATEXMK_LOG%" 2>&1
IF ERRORLEVEL 1 GOTO :LATEXMK_FAILED
GOTO :LATEXMK_DONE

IF ERRORLEVEL 1 (
    echo LaTeX 编译失败！
    exit /b
)

:LATEXMK_FAILED
echo LaTeX compilation failed.
echo Log file: %LATEXMK_LOG%
echo ----- latexmk log (last 60 lines) -----
powershell -NoProfile -Command "if (Test-Path -LiteralPath '%LATEXMK_LOG%') { Get-Content -LiteralPath '%LATEXMK_LOG%' -Tail 60 } else { Write-Host 'No compile log found.' }"
echo ---------------------------------------
exit /b 1

:LATEXMK_DONE
if exist "%LATEXMK_LOG%" del "%LATEXMK_LOG%"
echo Build finished.

REM =========================
REM 原始PDF路径
REM =========================
set INPUT_PDF=%BUILD_DIR%\main.pdf

REM =========================
REM 输出文件（未加密）
REM =========================
set RAW_OUTPUT=%BUILD_DIR%\raw_%timestamp%.pdf
copy %INPUT_PDF% %RAW_OUTPUT%

echo 已保存未加密PDF:%RAW_OUTPUT%

REM =========================
REM 输出文件（加密）
REM =========================
set ENCRYPTED_OUTPUT=%BUILD_DIR%\encrypted\enc_%USER_ID%_%timestamp%.pdf

echo 开始加密 PDF...
echo 输入PDF: %INPUT_PDF%
echo 输出PDF: %ENCRYPTED_OUTPUT%
echo 用户ID: %USER_ID%
python scripts/encrypt_pdf.py "%INPUT_PDF%" "%ENCRYPTED_OUTPUT%" "%USER_ID%"
IF ERRORLEVEL 1 (
    echo 加密失败！
    pause
    exit /b
)

echo 已保存加密PDF:%ENCRYPTED_OUTPUT%

echo.
echo =========================
echo 构建完成！
echo 原始PDF:%RAW_OUTPUT%
echo 加密PDF:%ENCRYPTED_OUTPUT%
echo =========================
