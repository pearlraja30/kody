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
    echo ERROR: Application failed to start.
    echo Please check 'launch_error.log' in the installation folder.
    echo.
    type ..\launch_error.log
    pause
)