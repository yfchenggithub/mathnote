@echo off
chcp 65001 >nul
echo ================================
echo Building search index
echo ================================

py scripts\build_content_js.py

echo.
echo Finished.