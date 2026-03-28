@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo   KODYS Foot Clinik - Definitive Launcher (v2.2.28)
echo ======================================================

:: 1. SET ZERO-WRITE POLICY IMMEDIATELY
set "PYTHONDONTWRITEBYTECODE=1"

:: 2. DETECT DIRECTORIES
set "INSTALL_DIR=%~dp0"
set "PY_DIST=%INSTALL_DIR%py-dist"
set "WINPYDIR=%PY_DIST%\python-2.7.10"

:: 3. HARDEN ENVIRONMENT PATHS (Fixes DLL Load Failed)
:: Prepend bundled paths to avoid picking up system-wide Python 3
set "PATH=%PY_DIST%;%WINPYDIR%;%WINPYDIR%\DLLs;%WINPYDIR%\Lib\site-packages\PyQt4;%WINPYDIR%\Lib\site-packages\numpy\core;%WINPYDIR%\Lib\site-packages\scipy\special;%PATH%"

:: 4. FORCE MODULE RESOLUTION (Fixes ImportError)
set "PYTHONPATH=%PY_DIST%;%WINPYDIR%\Lib;%WINPYDIR%\Lib\site-packages"

:: 5. CONFIGURE WRITABLE LOGGING
set "LOG_DIR=%TEMP%\KodysFootClinikV2"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo [INFO] Using Bundled Python: %WINPYDIR%
echo [INFO] Zero-Write Mode: ACTIVE
echo.

:: 6. LAUNCH WITH -B FLAG (Double Protection)
cd /d "%PY_DIST%"
"%WINPYDIR%\python.exe" -B run.py > "%LOG_DIR%\launch_log.txt" 2> "%LOG_DIR%\launch_error.log"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Application failed to start (Level %ERRORLEVEL%).
    echo --------------------------------------------------
    echo Please check these logs for details:
    echo 1. %LOG_DIR%\kodys_boot_debug.log
    echo 2. %LOG_DIR%\launch_error.log
    echo --------------------------------------------------
    if exist "%LOG_DIR%\kodys_boot_debug.log" (
        echo [Last Boot Log]:
        type "%LOG_DIR%\kodys_boot_debug.log"
    )
    pause
)
endlocal