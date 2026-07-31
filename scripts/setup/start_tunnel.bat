@echo off
REM PDBOT Cloudflare Tunnel v3.3.9
REM Creates 1 tunnel: Everything served from API (5001)
title PDBOT External Tunnel
cd /d "%~dp0"

echo.
echo  ========================================
echo    PDBOT External Access via Cloudflare
echo    Creating 1 Shareable Link
echo  ========================================
echo.

where cloudflared >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo   [ERROR] cloudflared not found!
    echo   Install: winget install Cloudflare.cloudflared
    pause
    exit /b 1
)

REM Check and start API service
echo [1/2] Checking Widget API (port 5001)...
powershell -Command "try { Invoke-RestMethod -Uri 'http://localhost:5001/health' -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"
if %ERRORLEVEL% neq 0 (
    echo       Starting API...
    REM Use backend wrapper for consistent startup and logging
start "PDBOT API" /min "%~dp0\run_backend.bat"
    timeout /t 15 /nobreak >nul
)
echo       [OK] API running on port 5001

echo [2/2] Starting Cloudflare Tunnel...
echo.
echo  ========================================
echo    STARTING TUNNEL - Watch for URL!
echo  ========================================
echo.
echo  ONE URL for everything:
echo.
echo    /           - Mobile Chat UI
echo    /widget     - Full Widget UI  
echo    /chat       - API endpoint
echo    /health     - Health check
echo.
echo  ========================================
echo.

REM Start tunnel
start "PDBOT Tunnel" cmd /k "echo ======== PDBOT TUNNEL ======== && echo. && echo Share this URL for external access: && echo. && cloudflared tunnel --url http://127.0.0.1:5001"

echo.
echo  ========================================
echo   Tunnel starting...
echo   Check the popup window for the URL!
echo.
echo   On phone/external device:
echo   - Mobile UI:  [tunnel-url]/
echo   - Full Widget: [tunnel-url]/widget
echo  ========================================
echo.
pause
echo.
echo   API URL (5001): For mobile.html backend
echo   Widget URL (3000): React chatbot widget
echo   Streamlit URL (8501): Full desktop UI
echo  ========================================
echo.
pause
