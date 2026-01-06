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

echo [1/3] Building widget...
cd frontend-widget
call npm run build
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Widget build failed!
    echo Make sure you have run: npm install
    pause
    exit /b 1
)

cd ..
echo [DONE] Widget built successfully!
echo.

echo [2/3] Starting Flask backend on port 5000...
start "PCBot Backend" cmd /c "python widget_api.py"
timeout /t 3 /nobreak >nul

echo [DONE] Backend started!
echo.

echo [3/3] Creating public tunnel...
echo.
echo ==========================================
echo   SHARE THIS URL TO ACCESS WIDGET
echo ==========================================
echo.
echo Once the tunnel starts, add /widget-standalone.html to the URL
echo Example: https://your-url.trycloudflare.com/widget-standalone.html
echo.

cloudflared tunnel --url http://localhost:5000

REM When tunnel is closed, cleanup
taskkill /F /FI "WINDOWTITLE eq PCBot Backend*" >nul 2>nul
echo.
echo Backend stopped. Goodbye!
