#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # --- ROBUST DLL PRE-FLIGHT (v2.2.36) ---
    if os.name == 'nt':
        import ctypes
        try:
            # Find py-dist accurately
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            py_dist = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(base)), 'py-dist'))
            
            if os.path.exists(py_dist):
                # 1. Recursive Search for Binary Fragments
                dll_dirs = set([py_dist])
                for root, dirs, files in os.walk(py_dist):
                    if any(f.lower().endswith(('.dll', '.pyd')) for f in files):
                        dll_dirs.add(root)
                
                # 2. Path Injection (Safe Unicode Handling)
                current_path_list = [p.strip() for p in os.environ.get('PATH', '').split(os.pathsep) if p.strip()]
                final_paths = []
                added_paths = set()
                
                # Priority: py-dist binaries
                for d in sorted(list(dll_dirs)):
                    if d not in added_paths:
                        final_paths.append(d)
                        added_paths.add(d)
                        # Also register with Kernel32 for deep resolution
                        try:
                            ctypes.windll.kernel32.SetDllDirectoryW(unicode(d))
                        except: pass
                
                # Append original paths
                for p in current_path_list:
                    if p not in added_paths:
                        final_paths.append(p)
                        added_paths.add(p)
                
                # Final stringification for os.environ (Python 2.7 requires byte-strings)
                try:
                    os.environ['PATH'] = os.pathsep.join(final_paths).encode('mbcs')
                except:
                    os.environ['PATH'] = os.pathsep.join(final_paths).encode('utf-8', 'ignore')
        except Exception as e:
            sys.stderr.write("DLL Pre-flight Error: %s\n" % str(e))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
