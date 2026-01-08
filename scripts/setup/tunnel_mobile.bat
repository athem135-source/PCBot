@echo off
REM PDBOT Mobile Tunnel - Simple Version
title PDBOT Mobile Tunnel
cd /d "%~dp0"

echo.
echo  ================================
echo    PDBOT Mobile Chat - Tunnel
echo  ================================
echo.

where cloudflared >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] cloudflared not found!
    echo Install: winget install Cloudflare.cloudflared
    pause
    exit /b 1
)

echo Starting tunnel to localhost:5000...
echo.
echo Share the URL below to access on phone!
echo.

cloudflared tunnel --url http://localhost:5000
