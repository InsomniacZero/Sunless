@echo off
setlocal enabledelayedexpansion

:: ==============================================================================
:: Janitor AI x Gemini Proxy - Windows 1-Click Launcher
:: ==============================================================================

cd /d "%~dp0"
title Sunless (Gemini Gateway)

echo.
echo  ======================================================================
echo                                SUNLESS
echo                 Gemini Gateway for Janitor AI Roleplay
echo  ======================================================================
echo.

:: ── Auto-Update from GitHub ─────────────────────────────────────────────
:: Silently pulls latest changes every startup. Fails gracefully if offline.
if exist ".git" (
    where git >nul 2>nul
    if !errorlevel! equ 0 (
        git stash -q >nul 2>nul
        for /f "tokens=*" %%A in ('git rev-parse HEAD 2^>nul') do set "BEFORE=%%A"
        git pull --ff-only origin main -q >nul 2>nul
        for /f "tokens=*" %%A in ('git rev-parse HEAD 2^>nul') do set "AFTER=%%A"
        git stash pop -q >nul 2>nul
        if not "!BEFORE!"=="!AFTER!" (
            echo  [*] Auto-updated to latest version!
            echo      Changelog: https://github.com/InsomniacZero/Sunless/commits/main
            echo.
        )
    )
)

:: 1. Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo IMPORTANT: Make sure to check 'Add python.exe to PATH' during install.
    echo.
    pause
    exit /b 1
)

:: 2. Setup Virtual Environment
if not exist ".venv" (
    echo [*] Creating lightweight virtual environment [.venv]...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [WARNING] Could not create venv. Using system Python instead.
        set "PY_CMD=python"
        goto :check_deps
    )
)

if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
) else (
    set "PY_CMD=python"
)

:check_deps
:: 3. Check and install minimal dependencies
"%PY_CMD%" -c "import starlette, uvicorn, httpx, curl_cffi" >nul 2>nul
if %errorlevel% neq 0 (
    echo [*] Installing required lightweight packages [takes ~5 seconds]...
    "%PY_CMD%" -m pip install -q -r requirements.txt
    if %errorlevel% neq 0 (
        "%PY_CMD%" -m pip install starlette uvicorn httpx curl_cffi
    )
    echo [*] Packages installed successfully.
    echo.
)

:: 4. Auto-register global 'nephis' command for Windows (CMD & PowerShell)
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps" (
    (
        echo @echo off
        echo cd /d "%~dp0"
        echo call "%~dp0start.bat" %%*
    ) > "%LOCALAPPDATA%\Microsoft\WindowsApps\nephis.cmd" 2>nul
    (
        echo @echo off
        echo cd /d "%~dp0"
        echo call "%~dp0start.bat" %%*
    ) > "%LOCALAPPDATA%\Microsoft\WindowsApps\nephis.bat" 2>nul
)
if not exist "%USERPROFILE%\bin" mkdir "%USERPROFILE%\bin" 2>nul
(
    echo @echo off
    echo cd /d "%~dp0"
    echo call "%~dp0start.bat" %%*
) > "%USERPROFILE%\bin\nephis.cmd" 2>nul

:: 5. Launch proxy
"%PY_CMD%" -m proxy.cli %*

if %errorlevel% neq 0 (
    echo.
    echo [Proxy exited with code %errorlevel%]
    pause
)
