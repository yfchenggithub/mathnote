@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0"

if "%~3"=="" (
    echo Usage: encrypt_pdf.bat ^<input.pdf^> ^<output.pdf^> ^<user_id^>
    echo Example: encrypt_pdf.bat 99_build\main.pdf 99_build\encrypted\main_enc.pdf user001
    exit /b 1
)

echo Encrypting PDF...
py "%ROOT%scripts\encrypt_pdf.py" "%~1" "%~2" "%~3"
if errorlevel 1 (
    echo Failed.
    exit /b 1
)

echo Finished.
