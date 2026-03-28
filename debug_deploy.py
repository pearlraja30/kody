import os, sys, ctypes

def check_env():
    print("=== KODYS Runtime Diagnostic ===")
    print("Python Version: %s" % sys.version)
    print("Executable: %s" % sys.executable)
    print("CWD: %s" % os.getcwd())
    
    # Check DLL Paths
    path = os.environ.get('PATH', '')
    print("\n[PATH Audit]")
    paths = path.split(os.pathsep)
    py_dist_paths = [p for p in paths if 'py-dist' in p.lower()]
    print("Found %d py-dist paths in PATH" % len(py_dist_paths))
    for p in py_dist_paths[:5]:
        print("  - %s" % p)
    
    # Try loading critical DLLs
    print("\n[DLL Load Tests]")
    critical_dlls = ['sqlite3.dll', 'libcef.dll', 'QtGui4.dll']
    for dll in critical_dlls:
        try:
            handle = ctypes.windll.kernel32.GetModuleHandleW(unicode(dll))
            if handle:
                print("✅ %s: ALREADY LOADED" % dll)
            else:
                # Try locating it
                found = False
                for p in paths:
                    if os.path.exists(os.path.join(p, dll)):
                        print("✅ %s: FOUND in %s" % (dll, p))
                        found = True
                        break
                if not found:
                    print("❌ %s: NOT FOUND in PATH" % dll)
        except Exception as e:
            print("❓ %s: Error checking (%s)" % (dll, str(e)))

    # Check Static Folders
    print("\n[Static Folder Audit]")
    # Try finding gstatic relative to current run.py location
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Check source structure
        p1 = os.path.join(base, "app", "appsource", "kodys", "templates", "gstatic")
        p2 = os.path.join(base, "app", "kodys", "templates", "gstatic")
        
        print("Source path exists: %s (%s)" % (os.path.exists(p1), p1))
        print("Dist path exists:   %s (%s)" % (os.path.exists(p2), p2))
    except:
        pass

if __name__ == "__main__":
    check_env()
    raw_input("\nPress Enter to exit...")
