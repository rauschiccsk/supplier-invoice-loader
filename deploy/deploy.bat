@echo off
REM Supplier Invoice Loader - Docker Deployment Script for Windows
REM Version: 2.0.0

setlocal enabledelayedexpansion

REM Colors don't work well in batch, so using simple text
echo ============================================
echo   Supplier Invoice Loader - Docker Deploy
echo   Version: 2.0.0
echo   Platform: Windows
echo ============================================
echo.

REM Check Docker
echo Kontrolujem Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker nie je nainstalovany!
    echo Prosim nainstalujte Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker je nainstalovany

REM Check Docker Compose
echo Kontrolujem Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    REM Try docker compose v2
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Docker Compose nie je nainstalovany!
        pause
        exit /b 1
    )
    set DOCKER_COMPOSE=docker compose
) else (
    set DOCKER_COMPOSE=docker-compose
)
echo [OK] Docker Compose je nainstalovany

REM Check if Docker is running
echo Kontrolujem Docker daemon...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker daemon nebezi!
    echo Prosim spustite Docker Desktop
    pause
    exit /b 1
)
echo [OK] Docker daemon bezi
echo.

REM Check for .env file
if exist .env (
    echo [WARNING] .env subor uz existuje
    set /p OVERWRITE=Chcete ho prepisat? (y/n):
    if /i "!OVERWRITE!"=="n" (
        echo Pouzijem existujuci .env subor
        goto :create_dirs
    )
    REM Backup existing .env
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "timestamp=!dt:~0,8!_!dt:~8,6!"
    copy .env .env.backup.!timestamp! >nul
    echo [OK] Existujuci .env zalohovany
)

REM Create .env from template
if not exist .env.example (
    echo [ERROR] .env.example subor neexistuje!
    pause
    exit /b 1
)

copy .env.example .env >nul
echo [OK] .env subor vytvoreny
echo.

REM Interactive configuration
echo === KONFIGURACIA ZAKAZNIKA ===
echo.
set /p CUSTOMER_NAME=Nazov zakaznika (napr. MAGERSTAV):
set /p CUSTOMER_FULL_NAME=Plny nazov firmy:
set /p NEX_API_URL=NEX Genesis API URL:
set /p NEX_API_KEY=NEX Genesis API Key:
set /p OPERATOR_EMAIL=Email operatora:
set /p AUTOMATION_EMAIL=Automation email:
set /p ALERT_EMAIL=Alert email:

REM Generate random API key (using PowerShell)
for /f "delims=" %%a in ('powershell -Command "[System.Web.Security.Membership]::GeneratePassword(32, 10)"') do set API_KEY=%%a

REM Update .env file using PowerShell
echo Ukladam konfiguraciu...
powershell -Command "(gc .env) -replace 'CUSTOMER_NAME=.*', 'CUSTOMER_NAME=%CUSTOMER_NAME%' | Out-File -encoding ASCII .env"
powershell -Command "(gc .env) -replace 'CUSTOMER_FULL_NAME=.*', 'CUSTOMER_FULL_NAME=%CUSTOMER_FULL_NAME%' | Out-File -encoding ASCII .env"
powershell -Command "(gc .env) -replace 'NEX_GENESIS_API_URL=.*', 'NEX_GENESIS_API_URL=%NEX_API_URL%' | Out-File -encoding ASCII .env"
powershell -Command "(gc .env) -replace 'NEX_GENESIS_API_KEY=.*', 'NEX_GENESIS_API_KEY=%NEX_API_KEY%' | Out-File -encoding ASCII .env"
powershell -Command "(gc .env) -replace 'OPERATOR_EMAIL=.*', 'OPERATOR_EMAIL=%OPERATOR_EMAIL%' | Out-File -encoding ASCII .env"
powershell -Command "(gc .env) -replace 'AUTOMATION_EMAIL=.*', 'AUTOMATION_EMAIL=%AUTOMATION_EMAIL%' | Out-File -encoding ASCII .env"
powershell -Command "(gc .env) -replace 'ALERT_EMAIL=.*', 'ALERT_EMAIL=%ALERT_EMAIL%' | Out-File -encoding ASCII .env"
powershell -Command "(gc .env) -replace 'LS_API_KEY=.*', 'LS_API_KEY=%API_KEY%' | Out-File -encoding ASCII .env"

echo [OK] Konfiguracia ulozena
echo.

:create_dirs
REM Create directories
echo Vytvoram adresare...
if not exist data\pdf mkdir data\pdf
if not exist data\xml mkdir data\xml
if not exist data\db mkdir data\db
if not exist logs mkdir logs
if not exist backups mkdir backups
echo [OK] Adresare vytvorene
echo.

REM Build Docker image
set /p BUILD=Chcete vybuildovat Docker image? (y/n):
if /i "%BUILD%"=="y" (
    echo Buildujem Docker image...
    %DOCKER_COMPOSE% build --no-cache
    if %errorlevel% neq 0 (
        echo [ERROR] Build Docker image zlyhal!
        pause
        exit /b 1
    )
    echo [OK] Docker image vytvoreny
    echo.
)

REM Start application
set /p START=Chcete spustit aplikaciu? (y/n):
if /i "%START%"=="y" (
    echo Spustam aplikaciu...
    %DOCKER_COMPOSE% up -d
    if %errorlevel% neq 0 (
        echo [ERROR] Spustenie aplikacie zlyhalo!
        pause
        exit /b 1
    )
    echo [OK] Aplikacia spustena
    echo.

    REM Wait for application
    echo Cakam na start aplikacie...
    timeout /t 10 /nobreak >nul

    REM Test application
    echo Testujem aplikaciu...
    curl -f http://localhost:8000/health >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] Health check zlyhal - aplikacia mozno este startuje
    ) else (
        echo [OK] Health check OK
    )
    echo.

    REM Show info
    echo ============================================
    echo   DEPLOYMENT DOKONCENY!
    echo ============================================
    echo.
    echo Aplikacia bezi na: http://localhost:8000
    echo Health check: http://localhost:8000/health
    echo API dokumentacia: http://localhost:8000/docs
    echo.
    echo Dolezite prikazy:
    echo   Zobrazenie logov:    %DOCKER_COMPOSE% logs -f invoice-loader
    echo   Restart aplikacie:   %DOCKER_COMPOSE% restart
    echo   Zastavenie aplikacie: %DOCKER_COMPOSE% down
    echo   Status:              %DOCKER_COMPOSE% ps
    echo.
    echo API Key pre n8n workflow:
    findstr "LS_API_KEY=" .env
    echo.
    echo Nezabudnite:
    echo   1. Nastavit n8n workflow s tymto API key
    echo   2. Nakonfigurovat Gmail pre automation email
    echo   3. Nastavit pravidelne zalohovanie
    echo   4. Skontrolovat firewall pravidla
    echo.
)

pause
