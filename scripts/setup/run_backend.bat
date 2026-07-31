@echo off
REM Wrapper to run the backend with UTF-8 enabled and log redirection.
REM This file is intended to be invoked with START so redirection works inside the wrapper.

:: Change to project root (two levels up from scripts/setup)
cd /d "%~dp0\..\.."
set "ROOT_DIR=%CD%"

:: Determine python executable (prefer venv)
if exist "%ROOT_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%ROOT_DIR%\.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_EXE=python"
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] Python executable not found. Run setup.bat to create the venv or install Python and try again.
    pause
    exit /b 1
)

set "LOG_DIR=%ROOT_DIR%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set "BACKEND_LOG=%LOG_DIR%\pcbot-backend.log"

echo [INFO] Starting backend with: %PYTHON_EXE%

:: Ensure Python prefers UTF-8 for I/O
set PYTHONUTF8=1

:: If SHOW_CONSOLE is set, run without redirect so output appears in the started window
if defined SHOW_CONSOLE (
    echo [INFO] SHOW_CONSOLE detected - printing backend output to console (no log redirection)
    "%PYTHON_EXE%" "%ROOT_DIR%\widget_api.py"
) else (
    :: Run the backend (this process handles redirection so START won't need to do it)
    "%PYTHON_EXE%" "%ROOT_DIR%\widget_api.py" > "%BACKEND_LOG%" 2>&1
)

echo [INFO] Backend process ended. See log: %BACKEND_LOG%