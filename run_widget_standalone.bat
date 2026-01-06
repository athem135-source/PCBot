@echo off
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

echo [1/2] Standalone widget ready (no build needed)!
echo.

echo [2/2] Starting Flask backend on port 5000...
start "PCBot Backend" cmd /c "python widget_api.py"
timeout /t 3 /nobreak >nul

echo [DONE] Backend started!
echo.

echo Creating public tunnel...
echo.
echo ==========================================
echo   SHARE THIS URL TO ACCESS PCBOT
echo ==========================================
echo.
echo The tunnel URL will show a landing page with all options
echo Example: https://your-url.trycloudflare.com
echo.
echo Available pages:
echo   /                        Landing page (default)
echo   /widget-standalone.html  Widget interface
echo   /mobile.html             Mobile interface
echo.

cloudflared tunnel --url http://localhost:5000

REM When tunnel is closed, cleanup
taskkill /F /FI "WINDOWTITLE eq PCBot Backend*" >nul 2>nul
echo.
echo Backend stopped. Goodbye!
