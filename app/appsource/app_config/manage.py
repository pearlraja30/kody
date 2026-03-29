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
                
                # 2. Path Injection
                # We prioritize py-dist and python-root for binary stability
                python_root = os.path.dirname(sys.executable)
                priority_paths = [
                    python_root,
                    os.path.join(python_root, "DLLs"),
                    os.path.join(python_root, "Lib", "site-packages"),
                ] + sorted(list(dll_dirs))
                
                current_paths = [p.strip() for p in os.environ.get('PATH', '').split(os.pathsep) if p.strip()]
                final_paths = []
                added = set()
                
                for p in priority_paths:
                    if p and os.path.isdir(p) and p not in added:
                        final_paths.append(p)
                        added.add(p)
                        try:
                            ctypes.windll.kernel32.SetDllDirectoryW(unicode(p))
                        except: pass
                        
                for p in current_paths:
                    if p and p not in added:
                        final_paths.append(p)
                        added.add(p)
                
                # 3. Final stringification (Python 2.7 requires byte-strings)
                path_str = os.pathsep.join(final_paths)
                try:
                    os.environ['PATH'] = path_str.encode('mbcs')
                except:
                    os.environ['PATH'] = path_str.encode('utf-8', 'ignore')
        except Exception as e:
            sys.stderr.write("DLL Pre-flight Error: %s\n" % str(e))

    # --- DATA CORRECTION (v2.2.46) ---
    if 'runserver' in sys.argv or 'kodys_app' in sys.argv or len(sys.argv) <= 1:
        try:
            import django
            django.setup()
            from kodys.models import MA_MEDICALAPPS, MA_APPLICATION
            
            # 1. Fix Medical Apps Icons
            for app in MA_MEDICALAPPS.objects.filter(ICON_PATH__startswith='/site_media/'):
                app.ICON_PATH = app.ICON_PATH.replace('/site_media/', '', 1)
                app.save()
            
            # 2. Fix Application Logo
            for app_meta in MA_APPLICATION.objects.filter(LOGO__startswith='/site_media/'):
                app_meta.LOGO = app_meta.LOGO.replace('/site_media/', '', 1)
                app_meta.save()
                
            sys.stdout.write("Data Correction: Redundant /site_media/ prefixes stripped.\n")
        except Exception as e:
            sys.stderr.write("Data Correction Error: %s\n" % str(e))

    execute_from_command_line(sys.argv)
