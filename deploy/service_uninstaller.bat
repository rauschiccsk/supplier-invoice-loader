@echo off
REM ===============================================================================
REM Supplier Invoice Loader - Windows Service Uninstaller
REM Quick uninstall script for Windows service
REM ===============================================================================

setlocal enabledelayedexpansion

REM Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires Administrator privileges.
    echo Please run as Administrator.

    REM Try to elevate
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ==========================================
echo Supplier Invoice Loader - Service Uninstaller
echo ==========================================
echo.

set SERVICE_NAME=SupplierInvoiceLoader

REM Check if service exists
sc query %SERVICE_NAME% >nul 2>&1
if %errorlevel% neq 0 (
    echo Service %SERVICE_NAME% is not installed.
    pause
    exit /b
)

echo This will completely remove the %SERVICE_NAME% service.
echo.
set /p confirm=Are you sure? (Type YES to continue):

if /i not "%confirm%"=="YES" (
    echo Uninstall cancelled.
    pause
    exit /b
)

echo.
echo Stopping service...
net stop %SERVICE_NAME% >nul 2>&1
timeout /t 2 /nobreak >nul

REM Try NSSM first
where nssm >nul 2>&1
if %errorlevel% equ 0 (
    echo Removing service using NSSM...
    nssm remove %SERVICE_NAME% confirm
) else (
    REM Check in tools directory
    if exist "%~dp0..\tools\nssm\win64\nssm.exe" (
        echo Removing service using NSSM...
        "%~dp0..\tools\nssm\win64\nssm.exe" remove %SERVICE_NAME% confirm
    ) else if exist "%~dp0..\tools\nssm\win32\nssm.exe" (
        echo Removing service using NSSM...
        "%~dp0..\tools\nssm\win32\nssm.exe" remove %SERVICE_NAME% confirm
    ) else (
        echo Removing service using SC...
        sc delete %SERVICE_NAME%
    )
)

if %errorlevel% equ 0 (
    echo.
    echo Service removed successfully!

    REM Clean up service info file
    if exist "%~dp0..\service_info.json" (
        del "%~dp0..\service_info.json"
    )
) else (
    echo.
    echo Failed to remove service.
    echo Please check Event Viewer for details.
)

echo.
pause