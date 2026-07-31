@echo on
REM PCBot Widget Standalone - Quick Share
title PCBot Widget Standalone
cd /d "%~dp0"

echo.
echo  ==========================================
echo    PCBot Widget Standalone - Quick Share
echo  ==========================================
echo.

REM Check if cloudflared is installed
where cloudflared >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] cloudflared not found!
    echo.
    echo Install with:
    echo   winget install Cloudflare.cloudflared
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking required services...
echo.

REM Check if Qdrant is running
echo Checking Qdrant...
curl -s http://127.0.0.1:6338/health >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Qdrant not running - attempting to start - if available...
    where qdrant >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        start "Qdrant Vector DB" cmd /c "qdrant"
        timeout /t 3 /nobreak >nul
        echo Qdrant started!
    ) else (
        rem Try to use Docker if present to run Qdrant automatically
        where docker >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            echo Docker detected - attempting to start Qdrant container pcbot-qdrant...
            docker ps -a --filter "name=pcbot-qdrant" --format "{{.Names}}" | findstr /R /C:"pcbot-qdrant" >nul 2>&1
            if %ERRORLEVEL% equ 0 (
                echo Container exists, starting...
                docker start pcbot-qdrant >nul 2>&1 || echo Failed to start existing container
            ) else (
                echo Pulling and running container...
                docker run -d --name pcbot-qdrant -p 6338:6338 qdrant/qdrant >nul 2>&1 || echo Failed to run container
            )
            timeout /t 6 /nobreak >nul
            echo If Docker started Qdrant, give it a few seconds to initialize and re-run the launcher if needed.
        ) else (
            echo [WARNING] Qdrant not found and Docker not available. Install Qdrant or Docker. See: https://qdrant.tech/documentation/guides/installation/
        )
    )
) else (
    echo Qdrant is running!
)

REM Check if Ollama is running
echo Checking Ollama...
curl -s http://localhost:11434/api/version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Ollama not running - attempting to start...
    where ollama >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        start "Ollama LLM Server" cmd /c "ollama serve"
        timeout /t 3 /nobreak >nul
        echo Ollama started!
    ) else (
        echo [WARNING] Ollama not found. Install from: https://ollama.ai/download
    )
) else (
    echo Ollama is running!
)

echo.
echo [2/5] Standalone widget ready (no build needed)!
echo.

echo [3/5] Activating Python environment...
REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated!
) else (
    echo [WARNING] Virtual environment not found. Run setup.bat first.
    echo Continuing with system Python...
)
echo.

set "PORT=5001"
echo [4/5] Starting Flask backend on port %PORT%...
REM Use wrapper to start backend and capture logs
set "SHOW_CONSOLE=1"
start "PCBot Backend" "%~dp0scripts\setup\run_backend.bat"
set "SHOW_CONSOLE="

echo Waiting for backend to start (checking /health)...
set "HEALTH_URL=http://127.0.0.1:%PORT%/health"
set /a attempts=0
set /a max_attempts=20
:wait_health
curl -s %HEALTH_URL% >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Backend is responding.
    goto health_ok
) else (
    set /a attempts+=1
    if %attempts% geq %max_attempts% (
        echo [ERROR] Backend did not respond after %max_attempts% attempts. Check logs: %LOG_DIR%\pcbot-backend.log
        pause
        goto :EOF
    )
    echo Waiting for backend... (attempt %attempts%/%max_attempts%)
    timeout /t 3 /nobreak >nul
    goto wait_health
)

:health_ok
echo [5/5] Backend started and responding.
echo.

echo Creating public tunnel (capturing public URL)...
echo.
set "TUNNEL_OUTPUT=%TEMP%\pcbot_tunnel_output.txt"
if exist "%TUNNEL_OUTPUT%" del "%TUNNEL_OUTPUT%" >nul 2>nul

echo Creating tunnel output file: %TUNNEL_OUTPUT%
echo. > "%TUNNEL_OUTPUT%"
echo Starting cloudflared quick tunnel in background (output -> %TUNNEL_OUTPUT%)...
echo Starting cloudflared quick tunnel in a new PowerShell window (output -> %TUNNEL_OUTPUT%)...
start "PCBot Tunnel" powershell -NoExit -Command "cloudflared tunnel --url 'http://127.0.0.1:5001' --no-autoupdate 2>&1 | Tee-Object -FilePath '%TUNNEL_OUTPUT%'"

echo Waiting for tunnel URL (60s timeout)...

set /a attempts=0
set /a max_attempts=40
set "TUNNEL_URL="
:wait_tunnel
set /a attempts+=1
set "TUNNEL_URL="
if exist "%TUNNEL_OUTPUT%" (
    rem Use PowerShell to read output and extract the trycloudflare URL (handles Unicode/UTF-16/UTF-8)
    for /f "usebackq delims=" %%U in (`powershell -NoProfile -Command "if (Test-Path -Path '%TUNNEL_OUTPUT%') { $txt = Get-Content -Raw -Path '%TUNNEL_OUTPUT%'; if ($txt -match 'https://[A-Za-z0-9\-\.]+trycloudflare.com[^\s\"]*') { Write-Output $Matches[0]; exit 0 } else { exit 1 } } else { exit 2 }"`) do set "TUNNEL_URL=%%U"
)
if defined TUNNEL_URL (
    echo [TUNNEL] Public URL detected: %TUNNEL_URL%
    echo Opening public landing page in browser...
    start "" "%TUNNEL_URL%"
    goto tunnel_done
)
if %attempts% geq %max_attempts% (
    echo [WARN] Tunnel URL not detected after %max_attempts% attempts. Falling back to local host.
    echo Local: http://127.0.0.1:%PORT%
    start http://127.0.0.1:%PORT%
    goto tunnel_done
)
echo Waiting for tunnel... (attempt %attempts%/%max_attempts%)
timeout /t 3 /nobreak >nul
goto wait_tunnel

:tunnel_done
echo Tunnel process started (check %TUNNEL_OUTPUT% for details). When tunnel is closed, close the tunnel window to shutdown.
echo.
REM Do not force-close backend here; let user stop it manually.
pause
goto :EOF



