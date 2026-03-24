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
REM Get timestamp (YYYY-MM-DD_HH-MM-SS)
REM =========================
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do (
    set yyyy=%%a
    set mm=%%b
    set dd=%%c
)

for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set hh=%%a
    set min=%%b
    set sec=%%c
)

set timestamp=%yyyy%-%mm%-%dd%_!hh!-!min!-!sec!

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
    pause
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