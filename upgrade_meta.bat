@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0"
set "PYTHONIOENCODING=utf-8"

echo ===============================
echo Sync/upgrade meta.json files...
echo ===============================

py "%ROOT%scripts\meta_schema_sync.py" %*
if errorlevel 1 (
    echo.
    echo Failed.
    exit /b 1
)

echo.
echo Finished.
