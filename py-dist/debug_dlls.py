import os, sys, ctypes, platform, traceback

def log_diag(msg):
    print("[DIAG] %s" % msg)

def test_load_dll(name):
    try:
        ctypes.WinDLL(name)
        log_diag("  - %s: LOAD SUCCESS" % name)
        return True
    except Exception as e:
        log_diag("  - %s: LOAD FAILED: %s" % (name, str(e)))
        return False

def test_import(module_name):
    try:
        __import__(module_name)
        log_diag("  - Import %s: SUCCESS" % module_name)
    except Exception as e:
        log_diag("  - Import %s: FAILED" % module_name)
        log_diag(traceback.format_exc())

if __name__ == "__main__":
    log_diag("Starting DLL Diagnostic Audit...")
    log_diag("Python Version: %s" % sys.version)
    log_diag("Platform: %s" % platform.platform())
    log_diag("CWD: %s" % os.getcwd())
    log_diag("PATH: %s" % os.environ.get('PATH', ''))
    
    log_diag("\n--- 1. Testing Core Runtime DLLs ---")
    # Python 2.7 core
    test_load_dll("python27.dll")
    # VC++ 2008 (Required for Python 2.7)
    test_load_dll("msvcr90.dll")
    test_load_dll("msvcp90.dll")
    # VC++ 2010 (Required by some newer binary wheels)
    test_load_dll("msvcr100.dll")
    test_load_dll("msvcp100.dll")
    # SQLite
    test_load_dll("sqlite3.dll")

    log_diag("\n--- 2. Testing Component Imports ---")
    test_import("PyQt4.QtCore")
    test_import("numpy")
    test_import("scipy")
    test_import("spectrum")
    test_import("django")

    log_diag("\n--- 3. Testing NumPy/SciPy specific DLLs ---")
    # Find numpy core pyd
    try:
        import numpy
        nc_path = os.path.dirname(numpy.__file__)
        log_diag("NumPy location: %s" % nc_path)
    except: pass
    
    log_diag("\nDiagnostic Audit Finished.")
