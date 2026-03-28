#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # --- FORENSIC DLL PRE-FLIGHT (v2.2.35) ---
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        try:
            # Find py-dist by walking up from appsource/app_config/manage.py
            # appsource (parent) -> kody (grandparent) -> py-dist
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            py_dist = os.path.join(os.path.dirname(os.path.dirname(base)), 'py-dist')
            
            if os.path.exists(py_dist):
                # 1. Recursive Search for Binary Fragments
                dll_dirs = [py_dist]
                for root, dirs, files in os.walk(py_dist):
                    if any(f.lower().endswith(('.dll', '.pyd')) for f in files):
                        dll_dirs.append(root)
                
                # 2. Path Injection
                current_path = os.environ.get('PATH', '')
                for d in dll_dirs:
                    if d not in current_path:
                        current_path = d + os.pathsep + current_path
                os.environ['PATH'] = current_path.encode('ascii', 'ignore') if isinstance(current_path, unicode) else current_path
                
                # 3. Kernel Search Mode Override
                kernel32 = ctypes.windll.kernel32
                for d in dll_dirs:
                    try:
                        kernel32.SetDllDirectoryW(unicode(d))
                    except:
                        pass
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
