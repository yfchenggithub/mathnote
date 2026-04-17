@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "BUILD_DIR=99_build"
set "BUILD_MODE=full"

if not "%~1"=="" (
    if /I "%~1"=="toc" (
        set "BUILD_MODE=toc"
    ) else if /I "%~1"=="full" (
        set "BUILD_MODE=full"
    ) else (
        echo Usage: build.bat [full^|toc]
        exit /b 1
    )
)

echo Build mode: %BUILD_MODE%

REM =========================
REM Clean build directory
REM =========================
if exist "%BUILD_DIR%" (
    echo Cleaning %BUILD_DIR% directory...
    rmdir /s /q "%BUILD_DIR%" >nul 2>&1
    if exist "%BUILD_DIR%" (
        echo Warning: %BUILD_DIR% could not be fully cleaned. Continuing with existing files.
    )
)

if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if not exist "%BUILD_DIR%\encrypted" mkdir "%BUILD_DIR%\encrypted"

REM =========================
REM Create timestamp safely
REM =========================
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd-HH-mm-ss'"`) do (
    set "timestamp=%%i"
)

if "%USER_ID%"=="" (
    echo Warning: USER_ID is empty. Encrypted filename will not include a user id.
)

REM =========================
REM Build metadata
REM =========================
set "BUILD_INFO=%BUILD_DIR%\build-%timestamp%.txt"
echo Build time: %timestamp% > "%BUILD_INFO%"
echo Build mode: %BUILD_MODE% >> "%BUILD_INFO%"

set "COMPILE_TARGET=main.tex"
set "INPUT_PDF=%BUILD_DIR%\main.pdf"

if /I "%BUILD_MODE%"=="toc" (
    set "TOC_SEED=%BUILD_DIR%\toc_seed.tex"
    set "TOC_MAIN=%BUILD_DIR%\toc_only_main.tex"

    echo Generating TOC seed from source structure...
    python scripts/generate_toc_seed.py --root main.tex --output "!TOC_SEED!"
    IF ERRORLEVEL 1 GOTO :PREP_FAILED

    > "!TOC_MAIN!" (
        echo \documentclass[12pt]{article}
        echo.
        echo \input{preamble}
        echo \input{settings}
        echo \graphicspath{{assets/figures/}{./}}
        echo.
        echo \title{Math Notes TOC Build}
        echo \author{Math ^& Code Lab}
        echo \date{\today}
        echo \hypersetup{
        echo     pdfauthor={Math ^& Code Lab},
        echo     pdftitle={Math Notes TOC Build},
        echo     pdfsubject={TOC only build},
        echo     pdfkeywords={math, toc, build},
        echo }
        echo.
        echo \begin{document}
        echo \input{titlepage}
        echo \pagenumbering{Roman}
        echo \tableofcontents
        echo.
        echo \newcounter{tocseedsection}
        echo \newcounter{tocseedsubsection}[tocseedsection]
        echo \newcommand{\SeedSection}[1]{
        echo   \refstepcounter{tocseedsection}
        echo   \setcounter{tocseedsubsection}{0}
        echo   \addcontentsline{toc}{section}{\protect\numberline{\arabic{tocseedsection}}#1}
        echo }
        echo \newcommand{\SeedSubsection}[1]{
        echo   \refstepcounter{tocseedsubsection}
        echo   \addcontentsline{toc}{subsection}{\protect\numberline{\arabic{tocseedsection}.\arabic{tocseedsubsection}}#1}
        echo }
        echo \input{99_build/toc_seed.tex}
        echo \end{document}
    )

    set "COMPILE_TARGET=!TOC_MAIN!"
    set "INPUT_PDF=%BUILD_DIR%\toc_only_main.pdf"
)

REM =========================
REM Compile with XeLaTeX
REM =========================
set "LATEXMK_LOG=%BUILD_DIR%\latexmk.log"
echo Compiling %COMPILE_TARGET% ...
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir="%BUILD_DIR%" "%COMPILE_TARGET%" > "%LATEXMK_LOG%" 2>&1
IF ERRORLEVEL 1 GOTO :LATEXMK_FAILED

echo Build finished.

if not exist "%INPUT_PDF%" (
    echo Build output PDF not found: %INPUT_PDF%
    exit /b 1
)

REM =========================
REM Output files
REM =========================
set "RAW_OUTPUT=%BUILD_DIR%\raw_%BUILD_MODE%_%timestamp%.pdf"
copy /Y "%INPUT_PDF%" "%RAW_OUTPUT%" >nul
if ERRORLEVEL 1 (
    echo Failed to save raw PDF.
    exit /b 1
)

echo Saved raw PDF: %RAW_OUTPUT%

set "ENCRYPTED_OUTPUT=%BUILD_DIR%\encrypted\enc_%BUILD_MODE%_%USER_ID%_%timestamp%.pdf"
echo Encrypting PDF...
echo Input PDF : %INPUT_PDF%
echo Output PDF: %ENCRYPTED_OUTPUT%
echo USER_ID   : %USER_ID%
python scripts/encrypt_pdf.py "%INPUT_PDF%" "%ENCRYPTED_OUTPUT%" "%USER_ID%"
IF ERRORLEVEL 1 (
    echo PDF encryption failed.
    exit /b 1
)

echo Saved encrypted PDF: %ENCRYPTED_OUTPUT%

echo.
echo =========================
echo Build completed.
echo Raw PDF      : %RAW_OUTPUT%
echo Encrypted PDF: %ENCRYPTED_OUTPUT%
echo =========================
exit /b 0

:PREP_FAILED
echo Failed to prepare TOC mode build files.
exit /b 1

:LATEXMK_FAILED
echo LaTeX compilation failed.
echo Log file: %LATEXMK_LOG%
echo ----- latexmk log ^(last 60 lines^) -----
powershell -NoProfile -Command "if (Test-Path -LiteralPath '%LATEXMK_LOG%') { Get-Content -LiteralPath '%LATEXMK_LOG%' -Tail 60 } else { Write-Host 'No compile log found.' }"
echo ---------------------------------------
exit /b 1
