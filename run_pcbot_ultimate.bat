@echo off
REM PCBot Ultimate Launcher & Test Runner v4.0.0
REM Single entrypoint: setup, backend, widget, tests, archive old .bat files

title PCBot Ultimate Launcher
cd /d "%~dp0"
setlocal EnableDelayedExpansion

set "PORT=5001"
set "ROOT=%CD%"
set "LOG_DIR=%ROOT%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo.
echo ==========================================
echo   PCBot - Ultimate Launcher v4.0.0
echo ==========================================
echo.
echo Select an option:
echo  1. Full Setup (create venv, install deps, start services)
echo  2. Start Backend (run_backend wrapper)
echo  3. Start Widget (backend + open browser + tunnel)
echo  4. Start Cloudflare Tunnel only (127.0.0.1:%PORT%)
echo  5. Run Quick 25-Question Test (smoke test)
echo  6. Run Comprehensive 300-Question Test (background)
echo  7. Archive non-core .bat files (keep core files)
echo  8. Check status (health, port, processes)
echo  9. Exit
echo.
set "CMD_ARG=%~1"
if /I "%CMD_ARG%"=="auto" goto AUTO_RUN
set /p choice="Enter choice (1-9): "

if "%choice%"=="1" goto FULL_SETUP
if "%choice%"=="2" goto START_BACKEND
if "%choice%"=="3" goto START_WIDGET
if "%choice%"=="4" goto START_TUNNEL
if "%choice%"=="5" goto RUN_QUICK_TEST
if "%choice%"=="6" goto RUN_COMPREHENSIVE
if "%choice%"=="7" goto ARCHIVE_BATS
if "%choice%"=="8" goto CHECK_STATUS
if "%choice%"=="9" goto :EOF

echo Invalid choice.
pause
goto :EOF

goto :FULL_SETUP

:AUTO_RUN
echo Running in automatic mode (non-interactive). This will perform full setup and start widget.
goto FULL_SETUP

:FULL_SETUP
echo Launching full setup (non-interactive)...
call "%~dp0\scripts\setup\setup.bat"
echo Full setup launched.
pause
goto :EOF

:START_BACKEND
echo Starting backend (wrapper will prefer .venv python)...
start "PCBot Backend" "%~dp0\scripts\setup\run_backend.bat"
echo Backend start requested. Give it a few seconds to initialize.
timeout /t 6 /nobreak >nul
echo You can check logs at %LOG_DIR%\pcbot-backend.log
pause
goto :EOF

:START_WIDGET
echo Starting widget launcher (will also attempt backend via wrapper if needed)...
start "PCBot Widget Launcher" "%~dp0\run_widget_standalone.bat"
echo Widget launcher started.
timeout /t 2 /nobreak >nul
goto :EOF

:START_TUNNEL
echo Starting Cloudflare Tunnel (127.0.0.1:%PORT%)
REM Ensure backend health before starting tunnel
set "HEALTH_URL=http://127.0.0.1:%PORT%/health"
set /a attempts=0
set /a max_attempts=20
:wait_health_tunnel
curl -s %HEALTH_URL% >nul 2>&1
if %ERRORLEVEL% neq 0 (
    set /a attempts+=1
    if %attempts% geq %max_attempts% (
        echo [ERROR] Backend not responding; cannot start tunnel. Start backend and retry.
        pause
        goto :EOF
    )
    echo Waiting for backend to respond before starting tunnel... (%attempts%/%max_attempts%)
    timeout /t 3 /nobreak >nul
    goto wait_health_tunnel
)
start "PCBot Tunnel" cmd /k "cloudflared tunnel --url http://127.0.0.1:%PORT%"
timeout /t 2 /nobreak >nul
goto :EOF

:RUN_QUICK_TEST
echo Running Quick 25-Question Smoke Test...
REM Ensure API is running or start wrapper
curl -s http://127.0.0.1:%PORT%/health >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo API not responding. Starting backend wrapper...
    start "PDBOT API" "%~dp0\scripts\setup\run_backend.bat"
    echo Waiting 20 seconds for backend to initialize...
    timeout /t 20 /nobreak >nul
)
if not exist "%~dp0\tests\quick_25_test.py" (
    echo [ERROR] tests\quick_25_test.py missing. Aborting.
    pause
    goto :EOF
)
python "%~dp0\tests\quick_25_test.py"
echo Quick test finished. See tests\quick_25_results.json
pause
goto :EOF

:RUN_COMPREHENSIVE
echo Launching comprehensive 300-question test in background (detached)...
REM Ensure API running
curl -s http://127.0.0.1:%PORT%/health >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo API not responding. Starting backend wrapper...
    start "PDBOT API" "%~dp0\scripts\setup\run_backend.bat"
    echo Waiting 30 seconds for backend to initialize...
    timeout /t 30 /nobreak >nul
)
if not exist "%~dp0\tests\comprehensive_300_test.py" (
    echo [ERROR] tests\comprehensive_300_test.py missing. Aborting.
    pause
    goto :EOF
)
start "Comprehensive Test" cmd /c "python "%~dp0\tests\comprehensive_300_test.py" && pause"
echo Comprehensive test started in a new window. It runs detached so you can continue other tasks.
pause
goto :EOF

:ARCHIVE_BATS
echo Archiving non-core .bat files to scripts\bak (preserves core files)...
if not exist "%~dp0\scripts\bak" mkdir "%~dp0\scripts\bak"
REM Keep these core files: run_pcbot_ultimate.bat, scripts\setup\run_backend.bat, scripts\setup\setup.bat, run_widget_standalone.bat, scripts\setup\run_widget_standalone.bat, full_setup.bat
for %%F in ("%~dp0\*.bat") do (
    set "fname=%%~nxF"
    if /I not "!fname!"=="run_pcbot_ultimate.bat" if /I not "!fname!"=="full_setup.bat" if /I not "!fname!"=="run_widget_standalone.bat" (
        move "%%~fF" "%~dp0\scripts\bak\" >nul 2>nul || echo "Could not move %%~nxF"
    )
)
for /R "%~dp0\scripts" %%G in (*.bat) do (
    REM Don't archive run_backend.bat or setup.bat or run_widget_standalone.bat in scripts\setup
    set "sub=%%~fG"
    setlocal enabledelayedexpansion
    set "bn=%%~nxG"
    if /I not "!bn!"=="run_backend.bat" if /I not "!bn!"=="setup.bat" if /I not "!bn!"=="run_widget_standalone.bat" (
        move "%%~fG" "%~dp0\scripts\bak\" >nul 2>nul || echo "Could not move %%~nxG"
    )
    endlocal
)
echo Archive complete. Check scripts\bak for archived files.
pause
goto :EOF

:CHECK_STATUS
echo Backend health:
curl -s http://127.0.0.1:%PORT%/health || echo "Health check failed"
echo.
echo Listening sockets for port %PORT%:
netstat -ano | findstr ":%PORT%"
echo.
echo Python processes (first 20 lines):
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
echo.
echo Log tail (last 200 lines):
if exist "%LOG_DIR%\pcbot-backend.log" (
    powershell -Command "Get-Content -Path '%LOG_DIR%\\pcbot-backend.log' -Tail 200"
) else (
    echo No backend log found at %LOG_DIR%\pcbot-backend.log
)
pause
goto :EOF