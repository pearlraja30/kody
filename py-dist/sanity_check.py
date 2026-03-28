import os, sys, socket, subprocess

def run_check():
    print("--- KODYS SANITY CHECK (v1.0) ---")
    print("Python Executable: %s" % sys.executable)
    print("Python Version: %s" % sys.version)
    print("Current Dir: %s" % os.getcwd())
    
    # 1. Check AppData Access
    data_root = os.path.join(os.environ.get('TEMP', os.environ.get('TMP', '/tmp')), 'KodysFootClinikV2')
    print("\n[1] Checking AppData: %s" % data_root)
    if not os.path.exists(data_root):
        try: os.makedirs(data_root); print("    -> Created Data Root successfully.")
        except Exception as e: print("    -> FAILED to create Data Root: %s" % e)
    else:
        print("    -> Data Root exists.")
    
    # 2. Check Port 5427
    print("\n[2] Checking Port 5427 availability...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    result = sock.connect_ex(('127.0.0.1', 5427))
    if result == 0:
        print("    -> Port 5427 is BUSY (another instance running?)")
    else:
        print("    -> Port 5427 is FREE.")
    sock.close()

    # 3. Check SQLite/Django Imports
    print("\n[3] Checking Library Imports...")
    try:
        import sqlite3
        print("    -> sqlite3: OK (%s)" % sqlite3.__file__)
    except Exception as e:
        print("    -> sqlite3: FAILED (%s)" % e)

    try:
        import PyQt4
        from PyQt4 import QtGui
        print("    -> PyQt4: OK (%s)" % PyQt4.__file__)
    except Exception as e:
        print("    -> PyQt4: FAILED (%s)" % e)

    # 4. Environment Check (PATH)
    print("\n[4] Checking PATH for DLLs...")
    python_root = os.path.dirname(sys.executable)
    print("    -> Python Root: %s" % python_root)
    dll_dir = os.path.join(python_root, "DLLs")
    if os.path.exists(dll_dir):
        print("    -> DLLs Directory: OK")
    else:
        print("    -> DLLs Directory: MISSING!")

    print("\n--- CHECK COMPLETE ---")
    print("If all OK, please run the app. If backend fails, check %TEMP%\\KodysFootClinikV2\\logs\\app.log")

if __name__ == "__main__":
    run_check()
    raw_input("\nPress Enter to exit...")
