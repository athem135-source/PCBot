@echo off
REM PCBot Main Launcher
REM Quick access to all deployment scripts
title PCBot Launcher
cd /d "%~dp0"

echo.
echo  ==========================================
echo    PCBot - Planning Commission Chatbot
echo    Main Launcher v3.4
echo  ==========================================
echo.
echo  Select an option:
echo.
echo  1. Start Widget (Standalone + Tunnel)
echo  2. Start Calibration Test
echo  3. View Statistics Dashboard
echo  4. Setup Environment
echo  5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Starting Widget Standalone...
    call scripts\setup\run_widget_standalone.bat
) else if "%choice%"=="2" (
    echo Starting Calibration Test...
    call scripts\setup\run_calibration_test.bat
) else if "%choice%"=="3" (
    echo Opening Statistics Dashboard...
    powershell -ExecutionPolicy Bypass -File "scripts\setup\stats_dashboard.ps1"
) else if "%choice%"=="4" (
    echo Running Setup...
    call scripts\setup\setup.bat
) else if "%choice%"=="5" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please run again.
    pause
)
