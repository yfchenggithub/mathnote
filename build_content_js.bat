@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0"

echo ================================
echo Building detail content JS
echo ================================

py "%ROOT%scripts\build_detail_page_js.py" %*
if errorlevel 1 (
    echo.
    echo Failed.
    exit /b 1
)

echo.
echo Finished.
