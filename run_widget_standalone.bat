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

echo [1/5] Checking required services...
echo.

REM Check if Qdrant is running
echo Checking Qdrant...
curl -s http://localhost:6338/health >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Qdrant not running - attempting to start...
    where qdrant >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        start "Qdrant Vector DB" cmd /c "qdrant"
        timeout /t 3 /nobreak >nul
        echo Qdrant started!
    ) else (
        echo [WARNING] Qdrant not found. Install from: https://qdrant.tech/documentation/guides/installation/
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

echo [4/5] Starting Flask backend on port 5000...
start "PCBot Backend" cmd /c "cd /d "%~dp0" && if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) && python widget_api.py"

echo Waiting for backend to start...
timeout /t 8 /nobreak >nul

REM Open browser automatically
echo [5/5] Opening browser...
start http://localhost:5000
timeout /t 2 /nobreak >nul

echo [DONE] Backend started and browser opened!
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
