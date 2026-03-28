@echo off
echo Starting Kodys Foot Clinik...
echo.
call py-dist\scripts\env.bat
cd py-dist\
echo Current directory: %cd%
echo Using Bundled Python Environment...
set "PYTHON_EXE=%WINPYDIR%\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

"%PYTHON_EXE%" --version
echo.
echo Launching KODYS GUI...
set "LOG_DIR=%TEMP%\KodysFootClinikV2"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
"%PYTHON_EXE%" -B run.py > "%LOG_DIR%\launch_log.txt" 2> "%LOG_DIR%\launch_error.log"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Application failed to start.
    echo --------------------------------------------------
    echo Please check these files for details:
    echo 1. %TEMP%\KodysFootClinikV2\kodys_boot_debug.log  (Technical startup log)
    echo 2. %TEMP%\KodysFootClinikV2\launch_error.log (Python error details)
    echo --------------------------------------------------
    echo.
    if exist "%TEMP%\KodysFootClinikV2\kodys_boot_debug.log" (
        echo [Recent Boot Log Contents]:
        type "%TEMP%\KodysFootClinikV2\kodys_boot_debug.log"
    )
    pause
)