import os
import sys
import datetime

def log(msg):
    print("[DIAG] %s" % msg)

log("--- SANITY CHECK START ---")
log("Python Executable: %s" % sys.executable)
log("Python Version: %s" % sys.version)
log("Platform: %s" % sys.platform)
log("Current Dir: %s" % os.getcwd())

# 1. Test distutils (to confirm Python version)
try:
    from distutils import util
    log("SUCCESS: distutils imported correctly (Confirmed Python 2.7 standard library)")
except Exception as e:
    log("FAILED: distutils import: %s" % str(e))

# 2. Test PyQt4 / DLL Load
try:
    import PyQt4
    log("SUCCESS: PyQt4 base package loaded from: %s" % PyQt4.__file__)
    from PyQt4 import QtGui, QtCore
    log("SUCCESS: QtGui/QtCore loaded correctly (DLLs found)")
except Exception as e:
    log("FAILED: PyQt4 import (Check DLLs/Path): %s" % str(e))
    import traceback
    traceback.print_exc()

# 3. Test AppData Writable
temp_dir = os.environ.get('TEMP', os.environ.get('TMP', 'C:\\Temp'))
test_file = os.path.join(temp_dir, "kodys_write_test.txt")
try:
    with open(test_file, "w") as f:
        f.write("test %s" % datetime.datetime.now())
    log("SUCCESS: Writable AppData/Temp: %s" % test_file)
    os.remove(test_file)
except Exception as e:
    log("FAILED: Write to Temp: %s" % str(e))

# 4. Check Config
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.json"))
if os.path.exists(config_path):
    log("SUCCESS: Config found at %s" % config_path)
    try:
        import json
        with open(config_path) as f:
            json.load(f)
        log("SUCCESS: Config is valid JSON and readable")
    except Exception as e:
        log("FAILED: Config read/parse: %s" % str(e))
else:
    log("FAILED: Config NOT FOUND at %s" % config_path)

log("--- SANITY CHECK COMPLETE ---")
