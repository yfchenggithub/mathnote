@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM =========================
REM Clean build directory
REM =========================
if exist build (
    echo Cleaning build directory...
    rmdir /s /q build
)

mkdir build
mkdir build\encrypted

REM =========================
REM Get timestamp (周X-YYYY-MM_DD-MM-SS)
REM Use PowerShell to avoid locale-dependent %date% parsing issues.
REM =========================
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "[System.Threading.Thread]::CurrentThread.CurrentCulture='zh-CN'; Get-Date -Format 'ddd-yyyy-MM_dd-mm-ss'"`) do (
    set "timestamp=%%i"
)

REM =========================
REM Create build timestamp file
REM =========================
echo Build time: %timestamp% > build\build-%timestamp%.txt

REM =========================
REM Compile with XeLaTeX
REM =========================
echo Compiling main.tex ...
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex

IF ERRORLEVEL 1 (
    echo LaTeX 编译失败！
    exit /b
)

echo Build finished.

REM =========================
REM 原始PDF路径
REM =========================
set INPUT_PDF=build\main.pdf

REM =========================
REM 输出文件（未加密）
REM =========================
set RAW_OUTPUT=build\raw_%timestamp%.pdf
copy %INPUT_PDF% %RAW_OUTPUT%

echo 已保存未加密PDF:%RAW_OUTPUT%

REM =========================
REM 输出文件（加密）
REM =========================
set ENCRYPTED_OUTPUT=build\encrypted\enc_%USER_ID%_%timestamp%.pdf

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
