@echo off
echo Starting Kodys Foot Clinik...
echo.
call py-dist\scripts\env.bat
cd py-dist\
echo Current directory: %cd%
echo Using Python:
python --version
echo.
echo Launching GUI...
python run.py > ..\launch_log.txt 2> ..\launch_error.log
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Application failed to start.
    echo --------------------------------------------------
    echo Please check these files for details:
    echo 1. boot_debug.log  (Technical startup log)
    echo 2. launch_error.log (Python error details)
    echo --------------------------------------------------
    echo.
    if exist boot_debug.log (
        echo [Recent Boot Log Contents]:
        type boot_debug.log
    )
    pause
)