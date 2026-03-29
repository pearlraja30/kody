#!/bin/bash
# ======================================================
#   KODYS Foot Clinik - macOS Native Launcher (No Docker)
# ======================================================

# 1. SET ZERO-WRITE POLICY
export PYTHONDONTWRITEBYTECODE=1

# 2. DETECT DIRECTORIES
# If running inside a KODYS.app bundle, the layout is:
# KODYS.app/Contents/MacOS/launchapp_mac.sh
# KODYS.app/Contents/Resources/py-dist/
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ "$SCRIPT_DIR" == *"/Contents/MacOS" ]]; then
    # Production Mode (inside .app bundle)
    APP_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
    PY_DIST="$APP_ROOT/Contents/Resources/py-dist"
else
    # Development Mode
    PY_DIST="$SCRIPT_DIR/py-dist"
fi

MAC_PYDIR="$PY_DIST/python-2.7.10-mac"

# 3. CONFIGURE ENVIRONMENT
# Ensure we pick up bundled libraries first
export PATH="$MAC_PYDIR/bin:$PATH"
export PYTHONPATH="$PY_DIST:$MAC_PYDIR/lib/python2.7/site-packages"
export DYLD_LIBRARY_PATH="$MAC_PYDIR/lib:$DYLD_LIBRARY_PATH"

# 4. DATA DIRECTORY (Standard macOS Application Support)
DATA_DIR="$HOME/Library/Application Support/KodysFootClinikV2"
mkdir -p "$DATA_DIR/logs"

echo "[INFO] Launching KODYS Native (macOS)..."
echo "[INFO] Python Dist: $MAC_PYDIR"
echo "[INFO] Data Root: $DATA_DIR"

# 5. EXECUTE
cd "$PY_DIST"

# Check if bundled python exists, otherwise fallback to system (if compatible)
if [ -f "$MAC_PYDIR/bin/python" ]; then
    "$MAC_PYDIR/bin/python" -B run.py > "$DATA_DIR/logs/launch_log.txt" 2> "$DATA_DIR/logs/launch_error.log" &
else
    # Fallback/Development mode
    python -B run.py > "$DATA_DIR/logs/launch_log.txt" 2> "$DATA_DIR/logs/launch_error.log" &
fi

# 6. ERROR HANDLING
if [ $? -ne 0 ]; then
    osascript -e 'display alert "KODYS Launch Error" message "Please verify that the application and its dependencies are correctly installed." as critical'
fi
