@echo off
REM PCBot All-in-One Setup & Launcher v4.0.0
REM Single-file installer + runtime launcher for Windows RDP servers

title PCBot Full Setup and Launcher
cd /d "%~dp0"
setlocal EnableDelayedExpansion

:: Default configuration
set "PORT=5001"
set "ROOT=%CD%"
set "LOG_DIR=%ROOT%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo.
echo ==========================================
echo   PCBot - Full Setup & Launcher v4.0.0
echo ==========================================
echo.
echo Select an option:
echo  1. Full Setup (create venv, install deps, start services)
echo  2. Start Backend (run_widget backend only)
echo  3. Start Widget (backend + open browser + tunnel)
echo  4. Start Cloudflare Tunnel only
echo  5. Run Calibration Test (300-question)
echo  6. Check status (health, port, processes)
echo  7. Exit
echo.
set /p choice="Enter choice (1-7): "

if "%choice%"=="1" goto FULL_SETUP
if "%choice%"=="2" goto START_BACKEND
if "%choice%"=="3" goto START_WIDGET
if "%choice%"=="4" goto START_TUNNEL
if "%choice%"=="5" goto RUN_CAL_TEST
if "%choice%"=="6" goto CHECK_STATUS
if "%choice%"=="7" goto :EOF

echo Invalid choice.
pause
goto :EOF

:FULL_SETUP
echo [STEP] Checking Python...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ and add to PATH.
    pause
    goto :EOF
)
python --version
echo [OK]

echo [STEP] Creating virtual environment (if missing)...
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create .venv
        pause
        goto :EOF
    )
    echo [OK] .venv created
) else (
    echo [OK] .venv already exists
)

echo [STEP] Activating virtual environment and installing Python packages...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [WARN] Some packages failed. Installing core packages explicitly...
    python -m pip install flask flask-cors waitress --quiet
    python -m pip install qdrant-client sentence-transformers --quiet
    python -m pip install langchain PyMuPDF nltk requests python-dotenv psutil transformers torch --quiet
)
echo [OK] Python dependencies installed (check logs for errors)

echo [STEP] Check Node.js (optional for building frontend)...
where node >nul 2>nul
if %ERRORLEVEL% equ 0 (
    node --version
    echo Installing frontend dependencies (frontend-widget)...
    pushd frontend-widget
    call npm install --silent
    if %ERRORLEVEL% neq 0 (
        echo [WARN] npm install had issues. Try running npm install manually in frontend-widget.
    )
    popd
) else (
    echo [INFO] Node.js not found - skipping frontend install. You can build frontend later.
)

echo [STEP] Docker / Qdrant check (optional)
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARN] Docker not found. Qdrant will not be installed automatically. Install Docker and re-run if you need Qdrant locally.
) else (
    echo Docker detected. Ensuring pndbot-qdrant container is running...
    docker ps -a --filter "name=pndbot-qdrant" --format "{{.Names}}" | findstr /I "pndbot-qdrant" >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        echo Starting existing container...
        docker start pndbot-qdrant >nul 2>&1 || (
            echo Failed to start existing container. Attempting to create a new one...
            docker run -d -p 6338:6333 -p 6334:6334 --name pndbot-qdrant qdrant/qdrant
        )
    ) else (
        echo Creating Qdrant container (this may download an image)...
        docker run -d -p 6338:6333 -p 6334:6334 --name pndbot-qdrant qdrant/qdrant
    )
    timeout /t 3 /nobreak >nul
    echo [OK] Qdrant start attempted. Check docker ps to confirm.
)

echo [STEP] Check Ollama (optional)
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Ollama not found. Skipping Ollama setup.
) else (
    echo Ollama found. Ensuring service is running...
    curl -s http://127.0.0.1:11434/api/version >nul 2>1
    if %ERRORLEVEL% neq 0 (
        echo Starting Ollama (this may open a new window)...
        start "Ollama Server" cmd /c "ollama serve"
        timeout /t 5 /nobreak >nul
    )
    echo [OK] Ollama check complete.
)

echo [STEP] Initial backend warmup (runs using wrapper and logs output)
start "PCBot Initial Setup" "%~dp0\scripts\setup\run_backend.bat"
echo Waiting for warmup (45s)...
timeout /t 45 /nobreak >nul
echo Attempting to stop initial warmup window...
taskkill /FI "WINDOWTITLE eq PCBot Initial Setup*" /F >nul 2>nul

echo [COMPLETE] Full Setup finished. Starting widget launcher now...
start "PCBot Widget Launcher" "%~dp0\run_widget_standalone.bat"
echo Done. Press any key to exit.
pause >nul
goto :EOF

:START_BACKEND
echo Starting backend (wrapper will choose .venv python if present)...
start "PCBot Backend" "%~dp0\scripts\setup\run_backend.bat"
echo Backend started. Check logs in %LOG_DIR%\pcbot-backend.log
timeout /t 2 /nobreak >nul
goto :EOF

:START_WIDGET
echo Starting widget (backend + open browser + tunnel)...
start "PCBot Widget" "%~dp0\run_widget_standalone.bat"
echo Widget launcher started.
timeout /t 2 /nobreak >nul
goto :EOF

:START_TUNNEL
echo Starting Cloudflare Tunnel (will open a new window)...
start "PCBot Tunnel" cmd /k "cloudflared tunnel --url http://127.0.0.1:%PORT%"
timeout /t 2 /nobreak >nul
goto :EOF

:RUN_CAL_TEST
echo Running calibration test (300-question)...
REM Ensure we run from repo root so tests path resolves correctly
cd /d "%~dp0"
echo Checking API health...
curl -s http://127.0.0.1:%PORT%/health >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo API not responding. Starting backend wrapper...
    start "PDBOT API" "%~dp0\scripts\setup\run_backend.bat"
    echo Waiting 45 seconds for backend to initialize...
    timeout /t 45 /nobreak >nul
)
echo Running test script from %CD%\tests\comprehensive_300_test.py
if not exist "tests\comprehensive_300_test.py" (
    echo [ERROR] tests\comprehensive_300_test.py not found in %CD%
    pause
    goto :EOF
)
python tests\comprehensive_300_test.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Calibration test failed. Check backend log and test output.
) else (
    echo [OK] Calibration test completed.
)
pause
goto :EOF

n:CHECK_STATUS
echo Backend health:
curl -s http://127.0.0.1:%PORT%/health || echo "Health check failed"
echo.
echo Listening sockets for port %PORT%:
netstat -ano | findstr ":%PORT%"
echo.
echo Python processes (first 20 lines):
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE

echo Log tail (last 200 lines):
if exist "%LOG_DIR%\pcbot-backend.log" (
    powershell -Command "Get-Content -Path '%LOG_DIR%\\pcbot-backend.log' -Tail 200"
) else (
    echo No backend log found at %LOG_DIR%\pcbot-backend.log
)
pause
goto :EOF