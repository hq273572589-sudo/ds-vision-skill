@echo off
setlocal EnableExtensions

rem ============================================================
rem  vision-bridge launcher
rem  Finds a suitable Python 3 (prefers official 3.12), ensures
rem  optional deps, then runs scripts/read_content.py.
rem  Portable: works on any Windows machine with Python 3.9+.
rem  Prefers an active conda env when present.
rem ============================================================

set "SD=%~dp0"
set "PYTHON="

rem 0) Prefer an active conda env
if exist "%CONDA_PREFIX%\python.exe" (
    set "PYTHON=%CONDA_PREFIX%\python.exe"
    goto :verify
)

rem 1) Windows py launcher (official Python installs)
where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=py -3"
    goto :verify
)

rem 2) Common official install locations (per-user first, then system)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :verify
)
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :verify
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :verify
)
if exist "C:\Python312\python.exe" (
    set "PYTHON=C:\Python312\python.exe"
    goto :verify
)
if exist "C:\Python313\python.exe" (
    set "PYTHON=C:\Python313\python.exe"
    goto :verify
)
if exist "C:\Python311\python.exe" (
    set "PYTHON=C:\Python311\python.exe"
    goto :verify
)

rem 3) Explicitly named commands on PATH
where python3.12 >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=python3.12"
    goto :verify
)
where python3 >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=python3"
    goto :verify
)
where python >nul 2>nul
if not errorlevel 1 (
    set "PYTHON=python"
    goto :verify
)

echo [vision-bridge] ERROR: no Python 3 found. Install Python 3.12 from https://www.python.org/downloads/
exit /b 1

:verify
%PYTHON% -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" >nul 2>nul
if errorlevel 1 goto :badver

rem Optional deps: Pillow / PyMuPDF / python-docx / openpyxl / python-pptx
rem Images work without them (raw base64 fallback).
%PYTHON% -c "import PIL, pymupdf, docx, openpyxl, pptx" >nul 2>nul
if not errorlevel 1 goto :run

echo [vision-bridge] optional deps missing, trying to install...
%PYTHON% -m pip install --quiet pillow pymupdf python-docx openpyxl python-pptx
if errorlevel 1 (
    echo [vision-bridge] auto install failed ^(no pip / offline?^).
    echo [vision-bridge] images still work. To enable local PDF/Office extraction run:
    echo [vision-bridge]   %PYTHON% -m pip install pillow pymupdf python-docx openpyxl python-pptx
)

:run
%PYTHON% "%SD%scripts\read_content.py" %*
exit /b %errorlevel%

:badver
echo [vision-bridge] ERROR: need Python 3.9+, but found:
%PYTHON% --version
exit /b 1