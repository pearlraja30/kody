import os, sys, math
import datetime

# --- ULTRA EARLY LOGGING ---
def log_boot(msg):
    # Definitive writable log in AppData/Local/Temp
    temp_dir = os.environ.get('TEMP', os.environ.get('TMP', '/tmp'))
    log_path = os.path.join(temp_dir, "kodys_boot_debug.log")
    try:
        with open(log_path, "a") as f:
            f.write("[%s] %s\n" % (datetime.datetime.now(), msg))
    except:
        pass

log_boot("--- BOOT START ---")
log_boot("Python Executable: %s" % sys.executable)
log_boot("Python Version: %s" % sys.version)
log_boot("Current Dir: %s" % os.getcwd())
log_boot("Path: %s" % sys.path)

def show_fatal_error(title, message):
    log_boot("FATAL [%s]: %s" % (title, message))
    try:
        from PyQt4 import QtGui, QtCore
        temp_app = QtGui.QApplication.instance()
        if not temp_app:
            temp_app = QtGui.QApplication([])
        QtGui.QMessageBox.critical(None, title, message)
    except:
        print("ERROR [%s]: %s" % (title, message))

import subprocess, time, socket

# --- PYQT4 DIAGNOSTIC & ROBUST PATHING ---
log_boot("Checking PyQt4 environment...")
try:
    import imp
    sp_path = os.path.join(os.getcwd(), "python-2.7.10", "Lib", "site-packages")
    if not os.path.exists(sp_path):
        sp_path = os.path.join(os.getcwd(), "python-2.7.10", "lib", "site-packages")
    
    pyqt4_path = os.path.join(sp_path, "PyQt4")
    sip_pyd_path = os.path.join(sp_path, "sip.pyd")
    
    log_boot("Site-packages: %s" % sp_path)
    log_boot("PyQt4 path: %s" % pyqt4_path)
    
    # 1. Force PATH for DLLs
    if os.path.exists(pyqt4_path):
        os.environ['PATH'] = pyqt4_path + os.pathsep + os.environ['PATH']
    
    # 2. Force sys.path
    if sp_path not in sys.path:
        sys.path.insert(0, sp_path)

    # 3. FORCE sip LOAD (The critical fix)
    try:
        import sip
        log_boot("Found existing sip: %s" % sip.__file__)
    except ImportError:
        log_boot("Standard sip import failed. Attempting manual load from %s" % sip_pyd_path)
        if os.path.exists(sip_pyd_path):
            sip = imp.load_dynamic('sip', sip_pyd_path)
            sys.modules['sip'] = sip
            log_boot("Successfully force-loaded sip.")
        else:
            log_boot("ERROR: sip.pyd NOT FOUND at %s" % sip_pyd_path)

    log_boot("Attempting PyQt4 import...")
    import PyQt4
    log_boot("PyQt4 base package loaded from: %s" % PyQt4.__file__)
    
    log_boot("Importing QtGui...")
    from PyQt4 import QtGui
    log_boot("QtGui loaded successfully.")
    
    from PyQt4 import QtCore
    from PyQt4 import QtWebKit
    log_boot("PyQt4 all modules imported successfully.")
except Exception as e:
    import traceback
    log_boot("CRITICAL ERROR: Failed to import PyQt4: %s" % str(e))
    log_boot("Traceback: %s" % traceback.format_exc())

import json
import compileall
from distutils import util
import re
from serial import SerialException, SerialTimeoutException
import winreg
import datetime
from dateutil.relativedelta import relativedelta

# --- Setup finished ---
log_boot("Setup finished. Entering main GUI loop...")
from scipy import signal

fs = 250.0  # Sample frequency (Hz)
f0 = 50.0  # Frequency to be removed from signal (Hz)
N = 2 #order
wn = f0/fs  # Normalized Frequency
# Design notch filter
# B, A = signal.iirnotch(w0, Q)
B, A = signal.butter(N,wn)
device = None
thread_connection = None
browser_func = None
ser = None
vpt_ser = None
proc = None
web_view = None
dialog = None
printer = None
config = None
device_status = "DISCONNECTED"
hcp_device_status = "DISCONNECTED"
hcp_usb_device_status = "DISCONNECTED"
can_device_status = "DISCONNECTED"
can_blu_device_status = "DISCONNECTED"
initial_width = 800
initial_height = 600
max_width = 0
max_height = 0
min_width = 800
min_height = 600
window_title = "My Django App"
icon_name = "icon.png"
fullscreen_allowed = True
project_dir_name="app"
project_dir_path="../app/"
assets_dir_name="app"
assets_dir_path="../app/"
dev_tools_menu_enabled = True
dev = None
endpoint = None
can_data_type = ""
can_password_ok = False
can_blu_password_ok = False
lead_off = False
air_leak = False
prev_time = datetime.datetime.now()
hcp_blu_time = datetime.datetime.now()
data_time = datetime.datetime.now()
error_1 = False
error_2 = False
error_3 = False
hcp_usb_passcode = ""
can_passcode = ""
can_mode = "monitor"
can_gain = "gain_3"
stop_999_check = False
list_data = list()
ecg_level_1 = list()
ecg_level_2 = list()
ecg_level_3 = list()

# Lifecycle flags & counters
browser_count = 0
is_running_loop = False
is_shutting_down = False
splash = None
mw = None

libcef_dll = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        'libcef.dll')

if os.path.exists(libcef_dll):
    if (2,7) <= sys.version_info < (2,8):
        import cefpython_py27 as cefpython
    elif (3,4) <= sys.version_info < (3,4):
        import cefpython_py34 as cefpython
    else:
        raise Exception("Unsupported python version: %s" % sys.version)
else:
    from cefpython3 import cefpython


def GetApplicationPath(file=None):
    import re, os, platform
    if not hasattr(GetApplicationPath, "dir"):
        if hasattr(sys, "frozen"):
            dir = os.path.dirname(sys.executable)
        elif "__file__" in globals():
            dir = os.path.dirname(os.path.realpath(__file__))
        else:
            dir = os.getcwd()
        GetApplicationPath.dir = dir

    if file is None:
        file = ""

    if not file.startswith("/") and not file.startswith("\\") and (
            not re.search(r"^[\w-]+:", file)):
        path = GetApplicationPath.dir + os.sep + file
        if platform.system() == "Windows":
            path = re.sub(r"[/\\]+", re.escape(os.sep), path)
        path = re.sub(r"[/\\]+$", "", path)
        return path
    return str(file)


def GetWritableAppDataPath(folder=None):
    """Returns a writable path in the user's TEMP directory to avoid permission issues."""
    import os
    # Use TEMP/KodysFootClinikV2 as a guaranteed writable base
    base = os.path.join(os.environ.get('TEMP', os.environ.get('TMP', os.path.expanduser('~'))), "KodysFootClinikV2")
    if not os.path.exists(base):
        try:
            os.makedirs(base)
        except:
            pass
    
    # Pre-create standard subdirectories to avoid "No such file" errors in services
    for sub in ["logs", "cache", "app_assets", "app_assets/media", "app_assets/DATA"]:
        sub_path = os.path.join(base, sub)
        if not os.path.exists(sub_path):
            try:
                os.makedirs(sub_path)
            except:
                pass

    if folder:
        path = os.path.join(base, folder)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                pass
        return path
    return base


def ExceptHook(excType, excValue, traceObject):
    global is_shutting_down, is_running_loop
    import traceback, os, time, codecs
    errorMsg = "\n".join(traceback.format_exception(excType, excValue,
            traceObject))
    errorFile = os.path.join(GetWritableAppDataPath(), "error.log")
    try:
        appEncoding = cefpython.g_applicationSettings["string_encoding"]
    except:
        appEncoding = "utf-8"
    if type(errorMsg) == bytes:
        errorMsg = errorMsg.decode(encoding=appEncoding, errors="replace")
    try:
        with codecs.open(errorFile, mode="a", encoding=appEncoding) as fp:
            fp.write("\n[%s] %s\n" % (
                    time.strftime("%Y-%m-%d %H:%M:%S"), errorMsg))
    except:
        print("[run.py] WARNING: failed writing to error file: %s" % (
                errorFile))
    errorMsg = errorMsg.encode("ascii", errors="replace")
    errorMsg = errorMsg.decode("ascii", errors="replace")
    print("\n"+errorMsg+"\n")

    if not is_shutting_down:
        is_shutting_down = True
        try:
            if is_running_loop:
                cefpython.QuitMessageLoop()
            cefpython.Shutdown()
        except:
            pass
    os._exit(1)


class MainWindow(QtGui.QMainWindow):
    mainFrame = None

    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.mainFrame = MainFrame(self)
        self.setCentralWidget(self.mainFrame)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMenuBar(None)
        self.setStatusBar(None)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle(window_title)
        self.setWindowIcon(QtGui.QIcon(icon_name))
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        # Ensure we start with the config size but allow resizing
        self.resize(initial_width, initial_height)
        if min_width > 0 and min_height > 0:
            self.setMinimumSize(min_width, min_height)
        
        # Initial position
        self.center()
        self.is_closing = False

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def focusInEvent(self, event):
        if self.mainFrame and self.mainFrame.browser:
            cefpython.WindowUtils.OnSetFocus(int(self.mainFrame.winId()), 0, 0, 0)

    def resizeEvent(self, event):
        if self.mainFrame:
            self.mainFrame.resize(self.centralWidget().size())

    def closeEvent(self, event):
        global is_shutting_down, is_running_loop
        if self.is_closing:
            event.accept()
            return
            
        url = self.mainFrame.browser.GetUrl()
        if url.startswith("http://127.0.0.1:5427/APP"):
            reply = QtGui.QMessageBox.question(self, 'Alert',"You should Close the test window first to quit application?", QtGui.QMessageBox.Ok)
            if reply == QtGui.QMessageBox.Ok:
                event.ignore()
        else:
            reply = QtGui.QMessageBox.question(self, 'Alert',"Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.is_closing = True
                # Stop timer first
                try:
                    app.timer.stop()
                except:
                    pass
                # Stop backend cleanly
                try:
                    import platform
                    if platform.system() == "Windows":
                        subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)], 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        proc.terminate()
                        proc.wait()
                except:
                    pass
                # Mark shutting down
                if not is_shutting_down:
                    is_shutting_down = True
                # Tell CEF to close. OnBeforeClose will call QuitMessageLoop.
                self.mainFrame.browser.CloseBrowser(True)
                event.accept()
            else:
                event.ignore()


class MainFrame(QtGui.QWidget):
    browser = None

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)
        windowInfo = cefpython.WindowInfo()
        # Initialize with 0,0,0,0 rect and let resizeEvent handle the actual sizing
        # This prevents initial white-space offsets on many systems
        rect = [0, 0, 0, 0]
        windowInfo.SetAsChild(int(self.winId()), rect)
        self.parent = parent 
        
        # Robust backend health check with timeout
        start_time = time.time()
        backend_ready = False
        log_boot("Waiting for backend on localhost:5427...")
        while time.time() - start_time < 30:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            result = sock.connect_ex(('127.0.0.1', 5427))
            sock.close()
            if result == 0:
                backend_ready = True
                log_boot("Backend is online.")
                break
            time.sleep(0.5)
            
        if not backend_ready:
            log_boot("CRITICAL: Backend failed to start after 30 seconds.")
            show_fatal_error("Startup Failure", "The backend server failed to respond on port 5427. Please check the logs.")
            os._exit(1)

        self.browser = cefpython.CreateBrowserSync(windowInfo,
                browserSettings={},
                navigateUrl=GetApplicationPath("http://127.0.0.1:5427"))

        global browser_count
        browser_count += 1
        
        self.browser.SetClientHandler(LoadHandler())
        self.set_javascript_bindings()



    def resizeEvent(self, event):
        if self.browser:
            # Explicitly sync CEF size with widget size to eliminate offsets
            cefpython.WindowUtils.OnSize(int(self.winId()), 0, 0, 0)

    def set_javascript_bindings(self):
        external = External(self.browser)
        bindings = cefpython.JavascriptBindings(bindToFrames=False, bindToPopups=False)
        bindings.SetObject("external", external)
        self.browser.SetJavascriptBindings(bindings)


class LoadHandler():
    def __init__(self):
        self.initial_app_loading = True

    def OnLoadStart(self, browser, frame, *args, **kwargs):
        if self.initial_app_loading:
            self.initial_app_loading = False
    def OnLoadingStateChange(self, browser, is_loading, *args, **kwargs):
        if not is_loading:
            pass
    def OnLoadEnd(self, browser, frame, *args, **kwargs):
        if frame.IsMain():
            def show_main():
                global splash, mw
                if splash:
                    splash.finish(mw)
                    splash = None
                if fullscreen_allowed:
                    mw.setWindowState(QtCore.Qt.WindowMaximized)
                    mw.show()
                else:
                    mw.show()
            QtCore.QTimer.singleShot(0, show_main)
    def OnLoadError(self, browser, frame, error_code, error_text_str, failed_url, *args, **kwargs):
        pass
    
    def OnBeforeClose(self, browser, **kwargs):
        global browser_count, is_running_loop
        browser_count -= 1
        if browser_count == 0:
            if is_running_loop:
                cefpython.QuitMessageLoop()


def ToByteArray(hex_string):
    chArray = list(hex_string.encode())
    buffer = [0]*17
    buffer[0] = 0
    for i in range(len(chArray)):
        num2 = hex(ord(chArray[i]))
        s = "%s"%(num2)
        num3 = int(s, 16)
        buffer[i+1] = num3
    return buffer


def ToByteArrayVpt(hex_string):
    chArray = list(hex_string.encode())
    buffer = [0]*13
    buffer[0] = 1
    for i in range(len(chArray)):
        num2 = hex(ord(chArray[i]))
        s = "%s"%(num2)
        num3 = int(s, 16)
        buffer[i+1] = num3
    return buffer


def ToByteArrayVptBlu(hex_string,byte_length):
    chArray = list(hex_string.encode())
    buffer = [0]*byte_length
    for i in range(len(chArray)):
        num2 = hex(ord(chArray[i]))
        s = "%s"%(num2)
        num3 = int(s, 16)
        buffer[i] = num3
    return buffer


def calculateCRC(data,numBytes_U):
    crcTab16_U = [0]*256
    try:
        for i_U in range(0,256):
            crc_U = 0
            c_U = i_U
            for  j_U in range(0,8):
                if ((crc_U ^ c_U) & 1) != 0:
                    crc_U = (crc_U >> 1) ^ 40961
                else: 
                    crc_U = crc_U >> 1
                c_U = (c_U >> 1)
            crcTab16_U[i_U] = crc_U
        crc_U =  0
        ptr_U = data
        if ptr_U != None:
            for a_U in range(0,numBytes_U):
                crc_U = (crc_U >> 8) ^ (crcTab16_U[( ((crc_U) ^ ((((ptr_U[a_U])) & 255)))) & 255])
    except Exception,e:
        pass
    return crc_U


def continuous_connect():
    global device
    global hcp_usb_device_status
    while True:
        if hcp_usb_device_status == "CONNECTED":
            try:
                hex_string = "A"
                buffer = ToByteArray(hex_string)
                device.send_output_report(buffer)
                time.sleep(1)
            except:
                break

def hcp_device_status_check():
    global browser_func
    global device
    global hcp_usb_device_status
    while True:
        time.sleep(1)
        if device.is_plugged():
            if hcp_usb_device_status == "CONNECTED":
                browser_func.ExecuteFunction("device_status","ON")
            elif hcp_usb_device_status == "DISCONNECTED":
                browser_func.ExecuteFunction("device_status","OFF")
                break 
        else:
            hcp_usb_device_status = "DISCONNECTED"
            browser_func.ExecuteFunction("device_shutdown")
            device.close()
            break

def hcp_blu_device_check_status():
    global ser
    global hcp_device_status
    global browser_func
    global hcp_blu_time
    while True:
        time.sleep(1)
        current_time = datetime.datetime.now()
        diff_time = relativedelta(current_time,hcp_blu_time)
        if hcp_device_status == "CONNECTED":
            if  diff_time.seconds > 6:
                hcp_device_status = "DISCONNECTED"
                browser_func.ExecuteFunction("device_shutdown")
                ser.close()
                ser = None
                break
            browser_func.ExecuteFunction("device_status","ON")
        elif hcp_device_status == "DISCONNECTED":
            browser_func.ExecuteFunction("device_status","OFF")
            break

def data_handler(data):
    global browser_func
    global device
    global hcp_usb_device_status
    global hcp_usb_passcode
    import threading
    try:
        data = ''.join(chr(i) for i in data)
        if data:
            data = data.split(" ")[0]
            data = data[1:]
            if "SERIAL?" in data:
                buffer = ToByteArray(hcp_usb_passcode)
                device.send_output_report(buffer)
            elif "NOT" in data:
                browser_func.ExecuteFunction("password_show")
                browser_func.ExecuteFunction("device_status","OFF")
                browser_func.ExecuteFunction("pleasewait_loader_end")
                device.close()
            elif "OK" in data:
                hcp_usb_device_status = "CONNECTED"
                browser_func.ExecuteFunction("device_status","ON")
                thread_connection1 = threading.Thread(target=hcp_device_status_check)
                thread_connection1.daemon = True
                thread_connection1.start()
                browser_func.ExecuteFunction("pleasewait_loader_end")
            else:
                data = data.replace(" ","").strip()
                browser_func.ExecuteFunction("js_print",str(data))
                browser_func.ExecuteFunction("device_status","ON")
        else:
            pass
    except Exception,e:
        pass


def data_handler_blu(pass_code_):
    global ser
    global browser_func
    global hcp_device_status
    global hcp_blu_time
    import threading
    while True:
        try:
            data = ser.read_until()
            if data:
                hcp_blu_time = datetime.datetime.now()
            if data.strip() == "SERIAL?":
                for pcode in pass_code_:
                    time.sleep(0.2)
                    ser.write(pcode)
            elif data.strip() == "OK":
                hcp_device_status = "CONNECTED"
                browser_func.ExecuteFunction("device_status","ON")
                thread_connection1 = threading.Thread(target=hcp_blu_device_check_status)
                thread_connection1.daemon = True
                thread_connection1.start()
                browser_func.ExecuteFunction("pleasewait_loader_end")
            elif data.strip() == "NOT OK":
                ser.close()
                hcp_device_status = "DISCONNECTED"
                browser_func.ExecuteFunction("password_show")
                time.sleep(1)
                browser_func.ExecuteFunction("device_status","OFF")
                browser_func.ExecuteFunction("pleasewait_loader_end")
            elif data.strip() == "SLEEP":
                hcp_device_status = "DISCONNECTED"
                ser.close()
                browser_func.ExecuteFunction("device_shutdown")
            else:
                if re.search(r'^\d+\.\d+',data) or re.search(r'\w+',data):
                    data = data.replace(" ","").strip()
                    browser_func.ExecuteFunction("js_print",str(data))
        except SerialException:
            break
        except Exception,e:
            break


def data_handler_vpt(data):
    global browser_func
    try:
        if data:
            value = data[1]
            code = data[0]
            inc = data[2]
            if code == 2:
                browser_func.ExecuteFunction("device_status","OFF")
            elif code == 4:
                if inc == 1:
                    value = value + 256
                elif inc == 2:
                    value = value + 256 + 256
                value = str(value)
                if len(value) == 1:
                    value = "0."+value[-1:]
                else:
                    value = value[:-1]+"."+value[-1:]
                browser_func.ExecuteFunction("js_print",str(value))
                browser_func.ExecuteFunction("device_status","ON")
            elif code == 3:
                if value == 1:
                    value = "NEXT"
                elif value == 2:
                    value = "PREV"
                elif value == 4:
                    value = "RECORD"
                elif value == 8:
                    value = "DEL"
                browser_func.ExecuteFunction("js_print",str(value))
        else:
            browser_func.ExecuteFunction("device_status","OFF")
    except Exception,e:
        browser_func.ExecuteFunction("device_status","OFF")


def data_handler_blu_vpt():
    global vpt_ser
    global browser_func
    global device_status
    data = ""
    while True:
        try:
            data += vpt_ser.read()
            if data:
                if len(data) > 4:
                    code = int(hex(ord(data[4])), 16)
                    if code == 2:
                        if len(data) > 15:
                            value = data[0:15]
                            data =  data[15:]
                            if value[11] == "C" and value[12] == "A":
                                browser_func.ExecuteFunction("device_status","ON")
                                device_status = "CONNECTED"
                            else:
                                #wrong passcode
                                browser_func.ExecuteFunction("password_show")
                                device_status = "DISCONNECTED"
                                vpt_ser.close()
                                vpt_ser = None
                                browser_func.ExecuteFunction("device_status","OFF")
                                browser_func = None
                                break
                    elif code == 4:
                        if len(data) > 17:
                            value = data[0:17]
                            data =  data[17:]
                            num2 = hex(ord(value[14]))
                            inc = hex(ord(value[13]))
                            s = "%s"%(num2)
                            voltage = int(s, 16)
                            inc = int(inc, 16)
                            if inc == 1:
                                voltage = voltage + 256
                            elif inc == 2:
                                voltage = voltage + 256 + 256
                            voltage = str(voltage)
                            if len(voltage) == 1:
                                voltage = "0."+voltage[-1:]
                            else:
                                voltage = voltage[:-1]+"."+voltage[-1:]
                            browser_func.ExecuteFunction("js_print",str(voltage))
                            browser_func.ExecuteFunction("device_status","ON")
                    elif code == 3:
                        if len(data) > 16:
                            value = data[0:16]
                            data = data[16:]
                            if value[11] == "K" and value[12] == "P":
                                num2 = hex(ord(value[13]))
                                s = "%s"%(num2)
                                command = int(s, 16)
                                if command == 1:
                                    command = "NEXT"
                                elif command == 2:
                                    command = "PREV"
                                elif command == 4:
                                    command = "RECORD"
                                elif command == 8:
                                    command = "DEL"
                                elif command == 3:
                                    command = 0
                                if command:
                                    browser_func.ExecuteFunction("js_print",str(command))
                                    browser_func.ExecuteFunction("device_status","ON")
        except SerialException:
            browser_func.ExecuteFunction("device_status","OFF")
            vpt_ser = None
            browser_func = None
            device_status = "DISCONNECTED"
            break
        except SerialTimeoutException:
            browser_func.ExecuteFunction("device_status","OFF")
            vpt_ser = None
            browser_func = None
            device_status = "DISCONNECTED"
            break
        except Exception,e:
            break


def data_handler_can_blu(passcode):
    global ser
    global browser_func
    global prev_time
    global can_data_type
    global lead_off
    global air_leak
    global can_blu_password_ok
    global can_blu_device_status
    global can_mode
    global can_gain
    global can_blu_time
    global data_time
    global stop_999_check
    global B
    global A
    import threading
    list_data = list()
    ecg_level_1 = list()
    ecg_level_2 = list()
    ecg_level_3 = list()
    while True:
        if can_blu_password_ok == False:
            try:
                data = ser.read_until()

                if data.strip() == "SERIAL?":
                    for pcode in passcode:
                        time.sleep(0.2)
                        ser.write(pcode)
                if data.strip() == "OK":
                    can_blu_password_ok = True
                    can_blu_device_status = "CONNECTED"
                    browser_func.ExecuteFunction("device_status","ON")
                    thread_connection1 = threading.Thread(target=arrhytmia_check)
                    thread_connection1.daemon = True
                    thread_connection1.start()
                    data_time = datetime.datetime.now()
                    thread_connection3 = threading.Thread(target=can_blu_device_status_check)
                    thread_connection3.daemon = True
                    thread_connection3.start()
                    if can_mode == "operation":
                        ser.write("^")
                    elif can_mode == "monitor":
                        ser.write("&")
                    elif can_mode == "diagnose":
                        ser.write("*")
                    else:
                        pass
                    if can_gain == "gain_1":
                        ser.write("!")
                    elif can_gain == "gain_2":
                        ser.write("#")
                    elif can_gain == "gain_3":
                        ser.write("$")
                    elif can_gain == "gain_4":
                        ser.write("@")
                    else:
                        pass
                    browser_func.ExecuteFunction("pleasewait_loader_end")
                if data.strip() == "NOT OK":
                    browser_func.ExecuteFunction("password_show")
                    can_blu_password_ok = False
                    can_blu_device_status = "DISCONNECTED"
                    browser_func.ExecuteFunction("pleasewait_loader_end")
                    ser = None
                    browser_func = None
                    break
            except:
                can_blu_password_ok = False
                can_blu_device_status = "DISCONNECTED"
                break
        else:
            if can_data_type == "PARA":
                try:
                    data = ser.read(1)
                    if data:
                        data_time = datetime.datetime.now()
                    val  = int(hex(ord(data)),16)
                    list_data.append(val)
                    if val == 251:
                        data1 = ser.read(1)
                        data2 = ser.read(1)
                        data3 = ser.read(1)
                        ecg_level_1.append(int(hex(ord(data1)),16))
                        ecg_level_2.append(int(hex(ord(data2)),16))
                        ecg_level_3.append(int(hex(ord(data3)),16))
                        list_data.append(int(hex(ord(data1)),16))
                        list_data.append(int(hex(ord(data2)),16))
                        list_data.append(int(hex(ord(data3)),16))
                    if val == 254:
                        data_1 = ser.read(7)
                        cdata = list()
                        for i in data_1:
                            cdata.append(int(hex(ord(i)),16))
                            list_data.append(int(hex(ord(i)),16))
                        try:
                            binary_data = bin(cdata[2]).replace("0b", "")
                            if str(binary_data[-2]) == "1":
                                if not lead_off:
                                    lead_off = True
                                    browser_func.ExecuteFunction('js_lead_off_alert',"ON")
                                    ser.write('4')
                            elif str(binary_data[-2]) == "0":
                                if lead_off:
                                    lead_off = False
                                    browser_func.ExecuteFunction('js_lead_off_alert',"OFF")
                                    ser.write('5')
                        except:
                            pass
                    if val == 252:
                        prev_time = datetime.datetime.now()
                    if can_mode == "diagnose":
                        display_len = 1000
                    else:
                        display_len = 45
                    if len(ecg_level_1) > display_len:
                        if can_mode == "diagnose":
                            smooth_data_1 = signal.filtfilt(B,A,ecg_level_1,method='gust')
                            smooth_data_2 = signal.filtfilt(B,A,ecg_level_2,method='gust')
                            browser_func.ExecuteFunction('js_print',str(list(smooth_data_1)).replace("[","").replace("]",""),str(list(smooth_data_2)).replace("[","").replace("]",""),str(ecg_level_3).replace("[","").replace("]",""),str(list_data).replace("[","").replace("]",""),str(ecg_level_1).replace("[","").replace("]",""),str(ecg_level_2).replace("[","").replace("]",""))
                        else:
                            browser_func.ExecuteFunction('js_print',str(ecg_level_1).replace("[","").replace("]",""),str(ecg_level_2).replace("[","").replace("]",""),str(ecg_level_3).replace("[","").replace("]",""),str(list_data).replace("[","").replace("]",""),str(ecg_level_1).replace("[","").replace("]",""),str(ecg_level_2).replace("[","").replace("]",""))
                        list_data = []
                        ecg_level_1 = []
                        ecg_level_2 = []
                        ecg_level_3 = []
                except Exception,e:
                    pass
            elif can_data_type == "SYM":
                try:
                    data = ser.read_until('\x03')
                    check_data = data.replace("\x00","").replace("0","")
                    if check_data:
                        data_time = datetime.datetime.now()
                    if "999" in data :
                        stop_999_check = True
                        ser.write('8')
                    elif "S1" in data:
                        stop_999_check = True
                        pulse_rate = ""
                        systolic = ""
                        diastolic = ""
                        message_code = ""
                        for i in range(len(data)):
                            if data[i] == "P":
                                systolic = data[i+1:i+4]
                                diastolic = data[i+4:i+7]
                            if data[i] == "R":
                                pulse_rate = data[i+1:i+4]
                        browser_func.ExecuteFunction('js_bp_print',systolic,diastolic,pulse_rate)
                    elif "S0" in data:
                        stop_999_check = True
                        is_error = False
                        for i in range(len(data)):
                            if data[i] == "M":
                                message_code = data[i+1:i+3]
                                if message_code == "00" or message_code == "03":
                                    is_error = False
                                else:
                                    ser.write('6')
                                    is_error = True
                        if is_error:
                            browser_func.ExecuteFunction('js_bp_error',message_code)
                    elif "S2" in data:
                        stop_999_check = True
                        is_error = False
                        for i in range(len(data)):
                            if data[i] == "M":
                                message_code = data[i+1:i+3]
                                if message_code == "00" or message_code == "03":
                                    is_error = False
                                else:
                                    ser.write('6')
                                    is_error = True
                        if is_error:
                            browser_func.ExecuteFunction('js_bp_error',message_code)
                    elif "BP EMR STOP" in data:
                        stop_999_check = True
                        browser_func.ExecuteFunction('emergency_stop_for_device')
                    else:
                        data = data.split("\x02")
                        if len(data) > 1:
                            browser_func.ExecuteFunction('js_print',str(data[1][:3]))
                    
                except Exception, e:
                    print(e)


def data_handler_can(data):
    global browser_func
    global device
    global prev_time
    global data_time
    global can_password_ok
    global can_data_type
    global lead_off
    global air_leak
    global error_1
    global error_2
    global error_3
    global can_passcode
    global can_device_status
    global can_mode
    global can_gain
    global stop_999_check
    global list_data
    global ecg_level_1
    global ecg_level_2 
    global ecg_level_3 
    global A
    global B
    try:

        if can_password_ok == False:
            try:
                response = ''.join(chr(i) for i in data[:10])
                if response.replace("\x00","").strip().startswith("SERIAL?"):
                    buffer = ToByteArray(can_passcode)
                    device.send_output_report(buffer)
                elif response.replace("\x00","").strip().startswith("OK"):
                    can_password_ok = True
                    can_device_status = "CONNECTED"
                    import threading
                    browser_func.ExecuteFunction("device_status","ON")
                    thread_connection1 = threading.Thread(target=can_device_status_check)
                    thread_connection1.daemon = True
                    thread_connection1.start()
                    thread_connection2 = threading.Thread(target=usb_arrhytmia_check)
                    thread_connection2.daemon = True
                    thread_connection2.start()
                    if can_mode == "operation":
                        send_command_to_device("^")
                    elif can_mode == "monitor":
                        send_command_to_device("&")
                    elif can_mode == "diagnose":
                        send_command_to_device("*")
                    else:
                        pass
                    if can_gain == "gain_1":
                        send_command_to_device("!")
                    elif can_gain == "gain_2":
                        send_command_to_device("#")
                    elif can_gain == "gain_3":
                        send_command_to_device("$")
                    elif can_gain == "gain_4":
                        send_command_to_device("@")
                    else:
                        pass
                    browser_func.ExecuteFunction("pleasewait_loader_end")
                elif response.replace("\x00","").strip().startswith("NOT OK"):
                    can_device_status = "DISCONNECTED"
                    can_password_ok = False
                    browser_func.ExecuteFunction("password_show")
                    browser_func.ExecuteFunction("device_status","OFF")
                    browser_func.ExecuteFunction("pleasewait_loader_end")
                    device.close()
            except Exception,e:
                can_device_status = "DISCONNECTED"
                can_password_ok = False
                browser_func.ExecuteFunction("pleasewait_loader_end")
                device.close()
        else:
            if can_data_type == "PARA":
                for i in range(len(data)):
                    list_data.append(data[i])
                    if error_1:
                        if i < 7:
                            ecg_level_1.append(int(data[i+1]))
                            ecg_level_2.append(int(data[i+2]))
                            ecg_level_3.append(int(data[i+3]))
                            error_1 = False
                            error_2 = False
                            error_3 = False
                    if error_2:
                        if i < 7:
                            ecg_level_2.append(int(data[i+1]))
                            ecg_level_3.append(int(data[i+2]))
                            error_2 = False
                            error_3 = False
                    if error_3:
                        if i < 7:
                            ecg_level_3.append(int(data[i+1]))
                            error_3 = False
                    if data[i] == 251:
                        try:
                            ecg_level_1.append(int(data[i+1]))
                        except Exception,e:
                            error_1 = True
                        try:
                            ecg_level_2.append(int(data[i+2]))
                        except Exception,e:
                            error_2 = True
                        try:
                            ecg_level_3.append(int(data[i+3]))
                        except Exception,e:
                            error_3 = True
                    if data[i] == 254:
                        try:
                            binary_data = bin(data[i+3:i+4][0]).replace("0b", "")
                            if str(binary_data[-2]) == "1":
                                if not lead_off:
                                    lead_off = True
                                    browser_func.ExecuteFunction('js_lead_off_alert',"ON")
                                    send_command_to_device("4")
                            elif str(binary_data[-2]) == "0":
                                if lead_off:
                                    lead_off = False
                                    browser_func.ExecuteFunction('js_lead_off_alert',"OFF")
                                    send_command_to_device("5")
                        except:
                            pass
                    if data[i] == 252:
                        prev_time = datetime.datetime.now()
                if can_mode == "diagnose":
                    display_len = 1000
                else:
                    display_len = 45
                if len(ecg_level_1) > display_len:
                    if can_mode == "diagnose":
                        smooth_data_1 = signal.filtfilt(B,A,ecg_level_1,method='gust')
                        smooth_data_2 = signal.filtfilt(B,A,ecg_level_2,method='gust')
                        browser_func.ExecuteFunction('js_print',str(list(smooth_data_1)).replace("[","").replace("]",""),str(list(smooth_data_2)).replace("[","").replace("]",""),str(ecg_level_3).replace("[","").replace("]",""),str(list_data).replace("[","").replace("]",""),str(ecg_level_1).replace("[","").replace("]",""),str(ecg_level_2).replace("[","").replace("]",""))
                    else:
                        browser_func.ExecuteFunction('js_print',str(ecg_level_1).replace("[","").replace("]",""),str(ecg_level_2).replace("[","").replace("]",""),str(ecg_level_3).replace("[","").replace("]",""),str(list_data).replace("[","").replace("]",""),str(ecg_level_1).replace("[","").replace("]",""),str(ecg_level_2).replace("[","").replace("]",""))
                    list_data = list()
                    ecg_level_1 = list()
                    ecg_level_2 = list()
                    ecg_level_3 = list()
            elif can_data_type == "SYM":
                data = ''.join(map(chr,data))
                if data and str(data[2:5]).strip() != "":
                    data_time = datetime.datetime.now()
                if '999' in data:
                    stop_999_check = True
                    send_command_to_device("8")
                elif 'BP EMR STOP' in data:
                    stop_999_check = True
                    browser_func.ExecuteFunction('emergency_stop_for_device')
                elif 'S0' in data:
                    stop_999_check = True
                    message_code = ""
                    for i in range(len(data)):
                        if data[i] == "M":
                            message_code = data[i+1:i+3]
                            if message_code == "00" or message_code == "03":
                                is_error = False
                            else:
                                send_command_to_device("6")
                                air_leak = True
                                is_error = True
                    if is_error:
                        browser_func.ExecuteFunction('js_bp_error',message_code)
                elif 'S1' in data:
                    stop_999_check = True
                    pulse_rate = ""
                    systolic = ""
                    diastolic = ""
                    message_code = ""
                    for i in range(len(data)):
                        if data[i] == "P":
                            systolic = data[i+1:i+4]
                            diastolic = data[i+4:i+7]
                        if data[i] == "R":
                            pulse_rate = data[i+1:i+4]
                    browser_func.ExecuteFunction('js_bp_print',systolic,diastolic,pulse_rate)
                elif 'S2' in data:
                    stop_999_check = True
                    message_code = ""
                    for i in range(len(data)):
                        if data[i] == "M":
                            message_code = data[i+1:i+3]
                            if message_code == "00" or message_code == "03":
                                is_error = False
                            else:
                                send_command_to_device("6")
                                air_leak = True
                                is_error = True
                    if is_error:
                        browser_func.ExecuteFunction('js_bp_error',message_code)
                else:
                    browser_func.ExecuteFunction('js_print',str(data[2:5]))     
    except Exception as e:
        print(e)
        pass


def send_command_to_device(command):
    global device
    try:
        buffer = ToByteArray(command)
        device.send_output_report(buffer)
    except:
        pass


def send_command_to_device_via_blu(command):
    global ser
    try:
        if ser:
            ser.write(command)
    except:
        pass


def send_command_to_device_vpt(command):
    global device
    global browser_func
    try:
        buffer = ToByteArrayVpt(command)
        device.send_output_report(buffer)
        if command == "Z":
            device.close()
            browser_func.ExecuteFunction("device_status","OFF")
    except:
        pass


def send_command_to_device_vpt_via_blu(command):
    global vpt_ser
    global browser_func
    try:
        if vpt_ser:
            if command == "Z":
                hex_string = "OCP14VBDVBACCCR"
                buffer = ToByteArrayVptBlu(hex_string,15)
                buffer[3] = 0x00
                buffer[4] = 0x02
                crc_array = calculateCRC(buffer,13)
                s = crc_array >> 8
                buffer[13] = s
                buffer[14] = int(hex(crc_array & 0xFF), 16)
                vpt_ser.write(buffer)
                browser_func.ExecuteFunction("device_status","OFF")
                vpt_ser.close()
                vpt_ser = None
                browser_func = None
    except Exception,e:
        browser_func.ExecuteFunction("device_status","OFF")
        vpt_ser = None
        browser_func = None


def voltage_enquriy():
    global vpt_ser
    global device_status
    global browser_func
    data = ""
    while True:
        try:
            hex_string = "OCP02VBAVBDVE04"
            buffer = ToByteArrayVptBlu(hex_string,15)
            buffer[3] = 0
            buffer[4] = 2
            crc_array = calculateCRC(buffer,13)
            s = crc_array >> 8
            buffer[13] = s
            buffer[14] = int(hex(crc_array & 0xFF), 16)
            vpt_ser.write(buffer)
            time.sleep(0.1)
        except SerialException:
            browser_func.ExecuteFunction("device_status","OFF")
            vpt_ser.close()
            vpt_ser = None
            browser_func = None
            device_status = "DISCONNECTED"
            break
        except Exception,e:
            break


def device_status_check():
    global browser_func
    global device
    while True:
        if device.is_plugged():
            time.sleep(1)
        else:
            browser_func.ExecuteFunction("device_status","OFF")
            break


def can_device_status_check():
    global browser_func
    global device
    global can_device_status
    global can_password_ok
    global can_data_type
    global data_time
    global stop_999_check
    while True:
        time.sleep(1)
        if device.is_plugged():
            if can_device_status == "CONNECTED":
                try:
                    if can_data_type == "SYM" and stop_999_check == False:
                        current_time = datetime.datetime.now()
                        diff_time = relativedelta(current_time,data_time)
                        if diff_time.seconds > 5:
                            stop_999_check = True
                            browser_func.ExecuteFunction('bp_not_responding')
                    browser_func.ExecuteFunction("device_status","ON")
                except:
                    pass
            elif can_device_status == "DISCONNECTED":
                can_password_ok = False
                browser_func.ExecuteFunction("device_status","OFF")
                break 
        else:
            can_password_ok = False
            can_device_status = "DISCONNECTED"
            browser_func.ExecuteFunction("device_shutdown")
            device.close()
            break

def can_blu_device_status_check():
    global ser
    global can_blu_device_status
    global browser_func
    global can_blu_password_ok
    global can_data_type
    global data_time
    global stop_999_check
    while True:
        try:
            if can_blu_device_status == "CONNECTED":
                if can_data_type == "":
                    try:
                        if can_data_type == "":
                            ser.write('0')
                    except:
                        ser.close()
                        can_data_type = ""
                        can_blu_device_status = "DISCONNECTED"
                        can_blu_password_ok = False
                        browser_func.ExecuteFunction("device_shutdown")
                        break
                elif can_data_type == "SYM":
                    if  stop_999_check == False:
                        current_time = datetime.datetime.now()
                        diff_time = relativedelta(current_time,data_time)
                        if diff_time.seconds > 7:
                            ser.write('8')
                        if diff_time.seconds > 12:
                            try:
                                for i in range(0,10):
                                    ser.write('0')
                                stop_999_check = True
                                browser_func.ExecuteFunction('bp_not_responding')
                            except:
                                can_data_type= ""
                                can_blu_password_ok=False
                                can_blu_device_status = "DISCONNECTED"
                                browser_func.ExecuteFunction("device_shutdown")
                                break
                elif can_data_type == "PARA":
                    current_time = datetime.datetime.now()
                    diff_time = relativedelta(current_time,data_time)
                    if diff_time.seconds > 3:
                        can_data_type= ""
                        can_blu_password_ok=False
                        can_blu_device_status = "DISCONNECTED"
                        browser_func.ExecuteFunction("device_shutdown")
                        break
                browser_func.ExecuteFunction("device_status","ON")
            elif can_blu_device_status == "DISCONNECTED":
                can_blu_password_ok = False
                can_data_type= ""
                browser_func.ExecuteFunction("device_status","OFF")
                break
        except:
            pass
        time.sleep(1)


def arrhytmia_check():
    global prev_time
    global browser_func
    global can_data_type
    global can_blu_device_status
    global lead_off
    prev_time = datetime.datetime.now()
    while True:
        if can_data_type == "PARA" and can_blu_device_status == "CONNECTED" and lead_off == False:
            try:
                current_time = datetime.datetime.now()
                diff_time = relativedelta(current_time,prev_time)
                if diff_time.seconds > 20:
                    browser_func.ExecuteFunction('arrhythmia_alert')
                    break
            except Exception,e:
                break
        elif can_blu_device_status == "CONNECTED" and lead_off == True:
            prev_time = datetime.datetime.now()
        elif can_blu_device_status != "CONNECTED" or can_data_type == "SYM":
            break
        else:
            pass
        time.sleep(3)

def usb_arrhytmia_check():
    global prev_time
    global browser_func
    global can_data_type
    global device
    global can_device_status
    global lead_off
    prev_time = datetime.datetime.now()
    while True:
        if can_data_type == "PARA" and device.is_plugged() and can_device_status == "CONNECTED" and lead_off == False:
            try:
                current_time = datetime.datetime.now()
                diff_time = relativedelta(current_time,prev_time)
                if diff_time.seconds > 20:
                    browser_func.ExecuteFunction('arrhythmia_alert')
                    break
            except Exception,e:
                break
        elif can_device_status == "CONNECTED" and lead_off == True:
            prev_time = datetime.datetime.now()
        elif can_device_status != "CONNECTED" or can_data_type == "SYM":
            break
        else:
            pass
        time.sleep(3)


class BluetoothSpp:
    key_bthenum = r"SYSTEM\CurrentControlSet\Enum\BTHENUM"

    def get_spp_com_port(self, bt_mac_addr):
        bt_mac_addr = bt_mac_addr.replace(':', '').upper()
        for i in self.gen_enum_key('', 'LOCALMFG'):
            for j in self.gen_enum_key(i, bt_mac_addr):
                subkey = self.key_bthenum+'\\'+ i+'\\'+j
                port = self.get_reg_data(subkey, 'FriendlyName')
                assert('Standard Serial over Bluetooth link' in port[0])
                items = port[0].split()
                port = items[5][1:-1]
                return port

    def gen_enum_key(self, subkey, search_str):
        hKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.key_bthenum + '\\' + subkey)

        try:
            i = 0
            while True:
                output = winreg.EnumKey(hKey, i)
                if search_str in output:
                    yield output
                i += 1

        except:
            pass

        winreg.CloseKey(hKey)

    def get_reg_data(self, subkey, name):
        hKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            subkey)
        output = winreg.QueryValueEx(hKey, name) 
        winreg.CloseKey(hKey)
        return output


def monitor_scanner(side):
    global browser_func
    count = 0
    while True:
        try:
            if os.path.exists(r'C:\\temp\\kodys\\podo_i_mat\\final-output.jpeg'):
                cur_file = open(r'C:\\temp\\kodys\\podo_i_mat\\final-output.jpeg','rb')
                import uuid
                uid = uuid.uuid4().hex[:5]
                temp_file = open(assets_media_dir_path+'\\podo_i_mat\\podo_i_mat-'+uid+'.'+'jpeg','wb')
                temp_file.write(cur_file.read())
                cur_file.close()
                try:
                    if os.path.exists(r'C:\\temp\\kodys\\podo_i_mat\\output.jpeg'):
                        os.remove(r"C:\\temp\\kodys\\podo_i_mat\\output.jpeg")
                except:
                    pass
                os.remove(r'C:\\temp\\kodys\\podo_i_mat\\final-output.jpeg')
                browser_func.ExecuteFunction("load_image",str('http://127.0.0.1:5423/site_media/podo_i_mat/'+'podo_i_mat-'+uid+'.'+'jpeg'),side)
            if os.path.exists(r'C:\\temp\\kodys\\podo_i_mat\\lock.txt'):
                browser_func.ExecuteFunction("pleasewait_loader_start")
            else:
                browser_func.ExecuteFunction("pleasewait_loader_end")
                break
            time.sleep(0.2)
        except Exception as e:
            print(e)


def convertIt():
    global dialog
    global web_view
    global printer
    dialog.paintRequested.connect(lambda p: web_view.page().currentFrame().print_(printer))
    web_view.close()
    dialog.exec_()


class External(object):
    def __init__(self, browser):
        self.browser = browser
    def connection(self, js_callback):
        def connect(device_type,pass_code,connection_type):
            global browser_func
            global thread_connection
            global device
            global ser
            global vpt_ser
            global device_status
            global hcp_device_status
            global hcp_usb_device_status
            global can_device_status
            global can_blu_device_status
            global can_data_type
            global dev
            global endpoint
            global lead_off
            global error_1
            global error_2
            global error_3
            global air_leak
            global hcp_usb_passcode
            global can_passcode
            global can_mode
            global can_gain
            global prev_time
            global data_time
            global stop_999_check
            global list_data
            global ecg_level_1
            global ecg_level_2
            global ecg_level_3
            if str(device_type) == "HCP":
                if str(connection_type) == "USB":
                    if hcp_usb_device_status != "CONNECTED":
                        import pywinusb.hid as hid
                        import threading
                        browser_func = self.browser
                        vendor_id = 0x04d2
                        product_id = 0x0001
                        hidfilter = hid.HidDeviceFilter(vendor_id=vendor_id,product_id=product_id)
                        devices = hidfilter.get_devices()
                        if devices:
                            try:
                                device = devices[0]
                                device.open()
                                hex_string = "Q"
                                hcp_usb_passcode = 'K'+str(pass_code)
                                buffer = ToByteArray(hex_string)
                                device.send_output_report(buffer)
                                device.set_raw_data_handler(data_handler)
                                thread_connection = threading.Thread(target=continuous_connect)
                                thread_connection.daemon = True
                                thread_connection.start()
                            except:
                                self.browser.ExecuteFunction("pleasewait_loader_end")
                                widget = QtGui.QWidget()
                                widget.setWindowTitle(window_title)
                                widget.setWindowIcon(QtGui.QIcon(icon_name))
                                QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device, Please reboot device and try again.",QtGui.QMessageBox.Ok)
                        else:
                            self.browser.ExecuteFunction("pleasewait_loader_end")
                            widget = QtGui.QWidget()
                            widget.setWindowTitle(window_title)
                            widget.setWindowIcon(QtGui.QIcon(icon_name))
                            QtGui.QMessageBox.question(widget,'Alert',"Please check device USB is connected with PC?",QtGui.QMessageBox.Ok)
                    else:
                        self.browser.ExecuteFunction("pleasewait_loader_end")
                elif str(connection_type) == "BLU":     
                    import serial
                    import threading
                    browser_func = self.browser
                    try:
                        port_available = False
                        if hcp_device_status != "CONNECTED":
                            pass_code_ = pass_code.split(":")[0]
                            bt_mac_addr = pass_code.split(":")[1]
                            bt_spp = BluetoothSpp()
                            port = bt_spp.get_spp_com_port(bt_mac_addr)
                            if port:
                                try:
                                    ser = serial.Serial(str(port),9600,bytesize=8, parity='N', stopbits=1,xonxoff=0,write_timeout=0.3,timeout=2)
                                    ser.write('Q')
                                    thread_connection = threading.Thread(target=data_handler_blu, args = ("K"+pass_code_,))
                                    thread_connection.daemon = True
                                    thread_connection.start()
                                    port_available = True
                                except Exception,e:
                                    self.browser.ExecuteFunction("pleasewait_loader_end")
                                    widget = QtGui.QWidget()
                                    widget.setWindowTitle(window_title)
                                    widget.setWindowIcon(QtGui.QIcon(icon_name))
                                    QtGui.QMessageBox.question(widget,'Alert',"Please check Device is ON and Blutooth is paired with PC?",QtGui.QMessageBox.Ok)
                            else:
                                self.browser.ExecuteFunction("pleasewait_loader_end")
                                widget = QtGui.QWidget()
                                widget.setWindowTitle(window_title)
                                widget.setWindowIcon(QtGui.QIcon(icon_name))
                                QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device,Com port not available!",QtGui.QMessageBox.Ok)
                        else:
                            self.browser.ExecuteFunction("pleasewait_loader_end")
                    except Exception,e:
                        self.browser.ExecuteFunction("pleasewait_loader_end")
                        widget = QtGui.QWidget()
                        widget.setWindowTitle(window_title)
                        widget.setWindowIcon(QtGui.QIcon(icon_name))
                        QtGui.QMessageBox.question(widget,'Alert',"Please check Device is ON and Blutooth is paired with PC?",QtGui.QMessageBox.Ok)
            elif str(device_type) == "VPT-ULTRA":
                if str(connection_type) == "USB":
                    import pywinusb.hid as hid
                    import threading
                    vendor_id =  0x0483
                    product_id = 0xA2B0
                    hidfilter = hid.HidDeviceFilter(vendor_id=vendor_id,product_id=product_id)
                    devices = hidfilter.get_devices()
                    browser_func = self.browser
                    if devices:
                        try:
                            device = devices[0]
                            device.open()
                            buffer = ToByteArrayVpt(str(pass_code))
                            device.send_output_report(buffer)
                            device.set_raw_data_handler(data_handler_vpt)
                            thread_connection1 = threading.Thread(target=device_status_check)
                            thread_connection1.daemon = True
                            thread_connection1.start()
                        except Exception,e:
                            widget = QtGui.QWidget()
                            widget.setWindowTitle(window_title)
                            widget.setWindowIcon(QtGui.QIcon(icon_name))
                            QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device, Please reboot device and try again.",QtGui.QMessageBox.Ok)
                    else:
                        widget = QtGui.QWidget()
                        widget.setWindowTitle(window_title)
                        widget.setWindowIcon(QtGui.QIcon(icon_name))
                        QtGui.QMessageBox.question(widget,'Alert',"Please check device USB is connected with PC?",QtGui.QMessageBox.Ok)
                elif str(connection_type) == "BLU":
                    import serial
                    import threading
                    pass_code = str(pass_code)
                    browser_func = self.browser
                    try:
                        if device_status != "CONNECTED": 
                            import serial.tools.list_ports
                            ports = []
                            comlist = list(serial.tools.list_ports.comports())
                            for element in comlist:
                                if "VID&00010039_PID&5056" in str(element.hwid):
                                    ports.append(element.device)
                            for port in ports:
                                try:
                                    vpt_ser = serial.Serial(port,9600,parity='N',write_timeout=3)
                                    hex_string = "OCP14VBAVBDCR"+pass_code+"CR"
                                    buffer = ToByteArrayVptBlu(hex_string,27)
                                    buffer[3] = 0
                                    buffer[4] = 14
                                    crc_array = calculateCRC(buffer,25)
                                    s = crc_array >> 8
                                    buffer[25] = s
                                    buffer[26] = int(hex(crc_array & 0xFF), 16)
                                    vpt_ser.write(buffer)
                                    thread_connection1 = threading.Thread(target=data_handler_blu_vpt)
                                    thread_connection1.daemon = True
                                    thread_connection1.start()
                                    thread_connection = threading.Thread(target=voltage_enquriy)
                                    thread_connection.daemon = True
                                    thread_connection.start()
                                    break
                                except Exception,e:
                                    vpt_ser = None
                                    browser_func = None
                                    device_status = "DISCONNECTED"
                                    pass
                            if not ports:
                                device_status = "DISCONNECTED"
                                vpt_ser = None
                                browser_func = None
                                widget = QtGui.QWidget()
                                widget.setWindowTitle(window_title)
                                widget.setWindowIcon(QtGui.QIcon(icon_name))
                                QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device,Com port not available!",QtGui.QMessageBox.Ok)
                    except Exception,e:
                        vpt_ser = None
                        browser_func = None
                        widget = QtGui.QWidget()
                        widget.setWindowTitle(window_title)
                        widget.setWindowIcon(QtGui.QIcon(icon_name))
                        QtGui.QMessageBox.question(widget,'Alert',"Please check Device Blutooth is paired with PC?",QtGui.QMessageBox.Ok)
            elif str(device_type) == "VPT":
                if str(connection_type) == "USB":
                    import pywinusb.hid as hid
                    import threading
                    vendor_id = 0x10c4
                    product_id = 0x881f
                    hidfilter = hid.HidDeviceFilter(vendor_id=vendor_id,product_id=product_id)
                    devices = hidfilter.get_devices()
                    browser_func = self.browser
                    if devices:
                        try:
                            device = devices[0]
                            device.open()
                            buffer = ToByteArrayVpt(str(pass_code))
                            device.send_output_report(buffer)
                            device.set_raw_data_handler(data_handler_vpt)
                            thread_connection1 = threading.Thread(target=device_status_check)
                            thread_connection1.daemon = True
                            thread_connection1.start()
                        except Exception,e:
                            widget = QtGui.QWidget()
                            widget.setWindowTitle(window_title)
                            widget.setWindowIcon(QtGui.QIcon(icon_name))
                            QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device, Please reboot device and try again.",QtGui.QMessageBox.Ok)
                    else:
                        widget = QtGui.QWidget()
                        widget.setWindowTitle(window_title)
                        widget.setWindowIcon(QtGui.QIcon(icon_name))
                        QtGui.QMessageBox.question(widget,'Alert',"Please check device USB is connected with PC?",QtGui.QMessageBox.Ok)
            elif str(device_type) == "CAN":
                if str(connection_type) == "USB":
                    import pywinusb.hid as hid
                    import threading
                    browser_func = self.browser
                    vendor_id = 0x04d3
                    product_id = 0x0005
                    hidfilter = hid.HidDeviceFilter(vendor_id=vendor_id,product_id=product_id)
                    devices = hidfilter.get_devices()
                    if devices:
                        try:
                            if can_device_status != "CONNECTED":
                                pass_code_ = pass_code.split(":")[0]
                                can_mode = pass_code.split(":")[1]
                                can_gain = pass_code.split(":")[2]
                                device = devices[0]
                                device.open()
                                hex_string = "Q"
                                can_passcode = 'K'+str(pass_code_)
                                buffer = ToByteArray(hex_string)
                                device.send_output_report(buffer)
                                list_data = list()
                                ecg_level_1 = list()
                                ecg_level_2 = list()
                                ecg_level_3 = list()
                                lead_off = False
                                air_leak = False
                                error_1 = False
                                error_2 = False
                                error_3 = False
                                prev_time = datetime.datetime.now()
                                data_time = datetime.datetime.now()
                                can_data_type = ""
                                stop_999_check = False
                                device.set_raw_data_handler(data_handler_can)
                            else:
                                self.browser.ExecuteFunction("pleasewait_loader_end")
                        except Exception,e:
                            self.browser.ExecuteFunction("pleasewait_loader_end")
                            widget = QtGui.QWidget()
                            widget.setWindowTitle(window_title)
                            widget.setWindowIcon(QtGui.QIcon(icon_name))
                            QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device, Please reboot device and try again.",QtGui.QMessageBox.Ok)
                    else:
                        self.browser.ExecuteFunction("pleasewait_loader_end")
                        widget = QtGui.QWidget()
                        widget.setWindowTitle(window_title)
                        widget.setWindowIcon(QtGui.QIcon(icon_name))
                        QtGui.QMessageBox.question(widget,'Alert',"Please check device USB is connected with PC?",QtGui.QMessageBox.Ok)
                elif str(connection_type) == "BLU":     
                    import serial
                    import threading
                    browser_func = self.browser
                    try:
                        if can_blu_device_status != "CONNECTED":
                            pass_code_ = pass_code.split(":")[0]
                            bt_mac_addr = pass_code.split(":")[1]
                            can_mode = pass_code.split(":")[2]
                            can_gain = pass_code.split(":")[3]
                            bt_spp = BluetoothSpp()
                            port = bt_spp.get_spp_com_port(bt_mac_addr)
                            if port:
                                try:
                                    ser = serial.Serial(str(port),9600 ,bytesize=8, parity='N', stopbits=1,xonxoff=0,write_timeout=0.3,timeout=2)
                                    ser.write('Q')
                                    lead_off = False
                                    air_leak = False
                                    prev_time = datetime.datetime.now()
                                    data_time = datetime.datetime.now()
                                    can_data_type = ""
                                    stop_999_check = False
                                    thread_connection2 = threading.Thread(target=data_handler_can_blu, args = ("K"+pass_code_,))
                                    thread_connection2.daemon = True
                                    thread_connection2.start()
                                except Exception,e:
                                    self.browser.ExecuteFunction("pleasewait_loader_end")
                                    ser = None
                                    browser_func = None
                                    widget = QtGui.QWidget()
                                    widget.setWindowTitle(window_title)
                                    widget.setWindowIcon(QtGui.QIcon(icon_name))
                                    QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device,Com port not available!",QtGui.QMessageBox.Ok)
                            else:
                                self.browser.ExecuteFunction("pleasewait_loader_end")
                                widget = QtGui.QWidget()
                                widget.setWindowTitle(window_title)
                                widget.setWindowIcon(QtGui.QIcon(icon_name))
                                QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device,Com port not available!",QtGui.QMessageBox.Ok)
                        else:
                            self.browser.ExecuteFunction("pleasewait_loader_end")
                            widget = QtGui.QWidget()
                            widget.setWindowTitle(window_title)
                            widget.setWindowIcon(QtGui.QIcon(icon_name))
                            QtGui.QMessageBox.question(widget,'Alert',"Device already connected!",QtGui.QMessageBox.Ok)
                    except Exception,e:
                        self.browser.ExecuteFunction("pleasewait_loader_end")
                        widget = QtGui.QWidget()
                        widget.setWindowTitle(window_title)
                        widget.setWindowIcon(QtGui.QIcon(icon_name))
                        QtGui.QMessageBox.question(widget,'Alert',"Please check Device Blutooth is paired with PC?",QtGui.QMessageBox.Ok)
        js_callback.Call("string",connect)

    def test_mode_change(self, js_callback):
        def mode_change(test_type,connect_type):
            if connect_type == "USB":
                if test_type == "HEAT":
                    send_command_to_device('H')
                else:
                    send_command_to_device('C')
            elif connect_type == "BLU":
                if test_type == "HEAT":
                    send_command_to_device_via_blu('H')
                else:
                    send_command_to_device_via_blu('C')
        js_callback.Call("str",mode_change)

    def can_test_command(self,js_callback):
        def command_send(connect_type,command):
            global can_data_type
            global prev_time
            global data_time
            global air_leak
            global stop_999_check
            try:
                if command == "A" or command == "C" or command == "E" or command == "G" or command == "I" or command == "W":
                    prev_time = datetime.datetime.now()
                    data_time = datetime.datetime.now()
                    can_data_type = "PARA"
                elif command == "L" or command == "N" or command == "P" or command == "S" or command == "U":
                    stop_999_check = False
                    data_time = datetime.datetime.now()
                    can_data_type = "SYM"
                elif command == "B" or command == "D" or command == "F" or command == "H" or command == "J" or command == "X" or command == "T" or command == "V" or command == "s" or command == "r" or command == "h":
                    can_data_type = ""
                elif command == "7":
                    air_leak = False
                elif command == "K":
                    stop_999_check = False
                    can_data_type = ""
                if connect_type == "BLU":
                    send_command_to_device_via_blu(command)
                else:
                    send_command_to_device(command)
            except Exception,e:
                print(e)
        js_callback.Call(command_send)

    def scan_img(self,js_callback):
        def scan_img_file(side):
            import threading
            global browser_func
            global thread_connection
            if not os.path.exists(r'C:\\temp\\kodys\\podo_i_mat\\'):
                os.makedirs(r'C:\\temp\\kodys\\podo_i_mat\\')
            if not os.path.exists(r'C:\\temp\\kodys\\podo_i_mat\\lock.txt'):
                f = open(r'C:\\temp\\kodys\\podo_i_mat\\lock.txt','wb')
                f.write('locked')
                f.close()
            if os.path.exists(r'C:\\temp\\kodys\\podo_i_mat\\final-output.jpeg'):
                os.remove(r"C:\\temp\\kodys\\podo_i_mat\\final-output.jpeg")
            browser_func = self.browser
            thread_connection = threading.Thread(target=monitor_scanner,args = (side,))
            thread_connection.daemon = True
            thread_connection.start()            
        js_callback.Call(scan_img_file)

    def open_app(self,js_callback):
        def open_scan_app():
            import subprocess
            file = app_dir_path+'\\WIAScanner\\WIAScannerApp.exe'
            subprocess.call([file])
        js_callback.Call(open_scan_app)

    def convert_img(self, js_callback):
        def convert_img_file(img_src,side):
            img_src = img_src.replace('http://127.0.0.1:5423/site_media/podo_i_mat/',assets_media_dir_path+"\\podo_i_mat\\")
            from PIL import Image
            import cv2
            img = cv2.imread(img_src) 
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            cv2.imwrite(img_src,gray)

            cv2.waitKey(0)

            img = cv2.imread(img_src) 

            avging = cv2.blur(img,(10,10))

            cv2.imwrite(img_src,avging)

            im = Image.open(img_src)

            width, height = im.size

            for x in range(width):
                for y in range(height):
                    r,g,b = im.getpixel((x,y))
                    num1 = 0
                    if (r >= 80 or g >= 80):
                        num1 = 1
                    else:
                        if (b >= 80):
                            num1 = 1
                        else:
                            num1 = 0
                    if num1 == 0:
                        im.putpixel((x,y), (255, 52, 0))
                    else:
                        num2 = 0
                        if ((r >= 110 or (r <= 80 or g >= 110)) or (g <= 80)):
                            num2 = 1
                        else:
                            if b >= 110:
                                num2 = 1
                            else:
                                if (b <= 80):
                                    num2 = 1
                                else:
                                    num2 = 0
                        if num2 == 0:
                            im.putpixel((x,y), (248, 146, 103))
                        else:
                            num3 = 0
                            if ((r >= 150 or (r <= 110 or g >= 150)) or (g <= 110)):
                                num3 = 1
                            else:
                                if b >= 150:
                                    num3 = 1
                                else:
                                    if b <= 110:
                                        num3 = 1
                                    else:
                                        num3 = 0
                            if num3 == 0:
                                im.putpixel( (x,y),(238, 231, 84))
                            else:
                                num4 = 0
                                if ((r >= 200 or (r <= 150 or g >= 200)) or (g <= 150)):
                                    num4 = 1
                                else:
                                    if b >= 200:
                                        num4 = 1 
                                    else:
                                        if b <= 150:
                                            num4 = 1
                                        else:
                                            num4 =0
                                if num4 == 0:
                                    im.putpixel( (x,y), (106, 231, 81))
                                else:
                                    num5 = 0
                                    if ((r >= 230 or (r <= 190 or g >= 230)) or (g <= 190)):
                                        num5 = 1
                                    else:
                                        if b >= 230: 
                                            num5 = 1 
                                        else: 
                                            if b <= 190:
                                                num5 = 1
                                            else:
                                                num5 = 0
                                    if num5 == 0:
                                        im.putpixel( (x,y), (131, 110, 177))
                                    else:
                                        num6 = 0
                                        if ((r >= 255 or (r <= 210 or g >= 255)) or (g <= 210)):
                                            num6 = 1
                                        else:
                                            if b >= 255 :
                                                num6 = 1 
                                            else:
                                                if b <= 210 :
                                                    num6 = 1
                                                else:
                                                    num6 = 0
                                        if num6 == 0:
                                            im.putpixel( (x,y), (255, 255, 255))

            im.save(img_src)
            self.browser.ExecuteFunction("load_image",str(img_src.replace(assets_media_dir_path+"\\podo_i_mat\\",'http://127.0.0.1:5423/site_media/podo_i_mat/'))+"?t=101",'con-'+side)
        js_callback.Call(convert_img_file)

    def browser_file(self, js_callback):
        def browser_img_file(side):
            from PIL import Image
            from PIL import ImageFile
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            selected_file = QtGui.QFileDialog.getOpenFileName(caption='Open file',filter="Image files (*.jpg *.jpeg *.png)")
            if selected_file:
                extension = selected_file.split(".")[-1]
                cur_file = open(str(selected_file),'rb')
                import uuid
                uid = uuid.uuid4().hex[:5]
                temp_file = open(assets_media_dir_path+'\\podo_i_mat\\podo_i_mat-BrowserImage'+uid+'.'+extension,'wb')
                temp_file.write(cur_file.read())
                self.browser.ExecuteFunction("load_image",str('http://127.0.0.1:5423/site_media/podo_i_mat/'+'podo_i_mat-BrowserImage'+uid+'.'+extension),'browser-'+side)
        js_callback.Call(browser_img_file)

    def connection_close(self,js_callback):
        def close_device(test_type,connect_type):
            global hcp_device_status
            global hcp_usb_device_status
            global can_device_status
            global can_blu_device_status
            global device_status
            global vpt_ser
            global browser_func
            global device
            global dev
            global ser
            global can_password_ok
            global can_blu_password_ok
            try:
                if test_type == "VPT":
                    if connect_type == "USB":
                        if device and device.is_plugged():
                            buffer = [1]*13
                            device.send_output_report(buffer)
                            device.close()
                            browser_func.ExecuteFunction("device_status","OFF")
                        browser_func = None
                        device = None
                    elif connect_type == "BLU":
                        if vpt_ser and browser_func:
                            device_status = "DISCONNECTED"
                            browser_func.ExecuteFunction("device_status","OFF")
                            vpt_ser.close()
                        vpt_ser = None
                        browser_func = None
                elif test_type == "HCP":
                    if connect_type == "USB":
                        if hcp_usb_device_status == "CONNECTED":
                            send_command_to_device('Z')
                            device.close()
                        hcp_usb_device_status = "DISCONNECTED"
                    elif connect_type == "BLU":
                        if hcp_device_status == "CONNECTED":
                            ser.write('Z')
                            ser.close()
                            ser = None
                        hcp_device_status = "DISCONNECTED"
                    elif connect_type == "BLU-H":
                        if hcp_device_status == "CONNECTED":
                            ser.write('Z')
                        hcp_device_status = "DISCONNECTED"
                        browser_func.ExecuteFunction("redirct_to_home")
                    elif connect_type == "BLU-S":
                        if hcp_device_status == "CONNECTED":
                            ser.write('Z')
                        hcp_device_status = "DISCONNECTED"
                        browser_func.ExecuteFunction("redirect_to_signout")
                elif test_type == "CAN":
                    if connect_type == "USB":
                        if can_device_status == "CONNECTED":
                            send_command_to_device('Z')
                            device.close()
                        can_password_ok = False
                        can_device_status = "DISCONNECTED"
                    elif connect_type == "BLU":
                        if can_blu_device_status == "CONNECTED":
                            ser.write('Z')
                            ser.close()
                            ser = None
                        can_blu_password_ok = False
                        can_blu_device_status = "DISCONNECTED"
            except:
                pass
        js_callback.Call("str",close_device)

    def export_as_pdf(self,js_callback):
        def save_file(ele):
            try:
                import string
                ele = filter(lambda x: x in string.printable, ele)
                html_string = """
                <html>
                <head>
                <link href="http://127.0.0.1:5423/site_media/css/kodys1.css" rel="stylesheet">
                <link href="http://127.0.0.1:5423/site_media/css/kodysreports.css" rel="stylesheet">
                <link href="http://127.0.0.1:5423/site_media/css/roboto.css" rel="stylesheet">
                <style>
                </style>
                </head>
                <body style="font-family: 'Times_New_Roman'!important;">
                {0}
                </body>
                </html>
                """.format(ele)
                options = {
                'page-size':'A4',
                'dpi':400,
                'zoom':1.23,
                'margin-top': '0in',
                'margin-bottom': '0in',
                'margin-left': '0in',
                'margin-right': '0in',
                'quiet':'',
                }                    
                name = QtGui.QFileDialog.getSaveFileName(caption='Save File', filter="PDF Files (*.pdf *.PDF)")
                import pdfkit
                path_wkthmltopdf = app_dir_path+'\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
                config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                pdfkit.from_string(html_string, str(name), configuration=config,options=options)
                widget = QtGui.QWidget()
                widget.setWindowTitle(window_title)
                widget.setWindowIcon(QtGui.QIcon(icon_name))
                QtGui.QMessageBox.question(widget,'Message',"PDF Exported Successfully.",QtGui.QMessageBox.Ok)
            except Exception,e:
                widget = QtGui.QWidget()
                widget.setWindowTitle(window_title)
                widget.setWindowIcon(QtGui.QIcon(icon_name))
                QtGui.QMessageBox.question(widget,'Message',"Something went wrong. Please try again later.",QtGui.QMessageBox.Ok)
        js_callback.Call(save_file)

    def print_pdf(self,js_callback):
        def print_file(ele):
            try:
                html_string = """
                <html>
                <head>
                <link href="http://127.0.0.1:5423/site_media/css/kodys1.css" rel="stylesheet">
                <link href="http://127.0.0.1:5423/site_media/css/kodysreports.css" rel="stylesheet">
                <link href="http://127.0.0.1:5423/site_media/css/roboto.css" rel="stylesheet">
                </head>
                <body style="font-family: 'Times_New_Roman'!important;width:100%;height:100%;margin: 0px;margin-top:-40px;">
                {0}
                </body>
                </html>
                """.format(ele)
                html_string = html_string.encode('ascii', 'ignore')
                web_view = QtWebKit.QWebView() 
                web_view.setHtml(html_string)
                web_view.setZoomFactor(1.22)
                dialog = QtGui.QPrintDialog()
                dialog.setWindowTitle(window_title)
                dialog.setWindowIcon(QtGui.QIcon(icon_name))
                printer = dialog.printer()
                printer.setPaperSize(QtGui.QPrinter.A4)
                printer.setOrientation(QtGui.QPrinter.Portrait)
                printer.setFullPage(True)
                printer.setPageMargins(5, 0, 0, 0, QtGui.QPrinter.Millimeter)
                if dialog.exec_() == QtGui.QDialog.Accepted:
                    web_view.page().currentFrame().print_(printer)
                    widget = QtGui.QWidget()
                    widget.setWindowTitle(window_title)
                    widget.setWindowIcon(QtGui.QIcon(icon_name))
                    QtGui.QMessageBox.question(widget,'Message',"Report Printed Successfully.",QtGui.QMessageBox.Ok)
            except Exception,e:
                widget = QtGui.QWidget()
                widget.setWindowTitle(window_title)
                widget.setWindowIcon(QtGui.QIcon(icon_name))
                QtGui.QMessageBox.question(widget,'Message',"Something went wrong. Please try again later.",QtGui.QMessageBox.Ok)
        js_callback.Call(print_file)

    def email_pdf(self,js_callback):
        def email_file(ele):
            try:
                import string
                ele = filter(lambda x: x in string.printable, ele)
                html_string = """
                <html>
                <head>
                <link href="http://127.0.0.1:5423/site_media/css/kodys1.css" rel="stylesheet">
                <link href="http://127.0.0.1:5423/site_media/css/kodysreports.css" rel="stylesheet">
                <link href="http://127.0.0.1:5423/site_media/css/roboto.css" rel="stylesheet">
                <style>
                </style>
                </head>
                <body style="font-family: 'Times_New_Roman'!important;">
                {0}
                </body>
                </html>
                """.format(ele)
                html_string = html_string.encode('ascii', 'ignore')
                options = {
                'page-size':'A4',
                'dpi':400,
                'zoom':1.23,
                'margin-top': '0in',
                'margin-right': '0in',
                'margin-bottom': '0in',
                'margin-left': '0in',
                'quiet': '',
                }                    
                import pdfkit
                path_wkthmltopdf = app_dir_path+'\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
                config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                import uuid
                uid = uuid.uuid4().hex[:5]
                pdfkit.from_string(html_string, assets_dir_path+'\\report\\Report-'+uid+'.pdf', configuration=config,options=options)
                self.browser.ExecuteFunction("pdf_file_name",'Report-'+uid+'.pdf')
            except Exception,e:
                self.browser.ExecuteFunction("pdf_file_error")
        js_callback.Call(email_file)

    def preview_pdf(self,js_callback):
        def preview_file(ele):
            global dialog
            global web_view
            global printer
            html_string = """
            <html>
            <head>
            <link href="http://127.0.0.1:5423/site_media/css/kodys1.css" rel="stylesheet">
            <link href="http://127.0.0.1:5423/site_media/css/kodysreports.css" rel="stylesheet">
            <link href="http://127.0.0.1:5423/site_media/css/roboto.css" rel="stylesheet">
            </head>
            <body style="font-family: 'Times_New_Roman'!important;width:100%;height:100%;margin: 0px;margin-top:-50px;">
            {0}
            </body>
            </html>
            """.format(ele)
            html_string = html_string.encode('ascii', 'ignore')
            web_view = QtWebKit.QWebView() 
            web_view.setHtml(html_string)
            web_view.setZoomFactor(1.235)
            web_view.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            frame = web_view.page().mainFrame()
            web_view.page().setViewportSize(frame.contentsSize())
            web_view.resize(frame.contentsSize())
            dialog = QtGui.QPrintPreviewDialog()
            dialog.setWindowTitle(window_title)
            dialog.setWindowIcon(QtGui.QIcon(icon_name))
            printer = dialog.printer()
            printer.setPaperSize(QtGui.QPrinter.A4)
            printer.setOrientation(QtGui.QPrinter.Portrait)
            printer.setFullPage(True)
            web_view.loadFinished.connect(convertIt)
        js_callback.Call(preview_file)


class CefApplication(QtGui.QApplication):
    timer = None

    def __init__(self, args):
        super(CefApplication, self).__init__(args)
        self.createTimer()

    def createTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(1)

    def onTimer(self):
        if is_cef_initialized:
            cefpython.MessageLoopWork()

is_cef_initialized = False

if __name__ == '__main__':
    # --- STEP 1: INSTANT SPLASH ---
    app = CefApplication(sys.argv)
    
    splash = None
    splash_path = GetApplicationPath("../config/splash.png")
    if os.path.exists(splash_path):
        splash = QtGui.QSplashScreen(QtGui.QPixmap(splash_path))
        splash.show()
        # Ensure it stays on top and visible
        splash.raise_()
        app.processEvents()
        splash.showMessage("Starting KODYS...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, QtGui.QColor(QtCore.Qt.white))
        app.processEvents()
        app.processEvents()

    # --- STEP 2: LOAD CONFIG & ENV ---
    config_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config','config.json'))
    try:
        if splash:
            splash.showMessage("Loading Configuration...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, QtGui.QColor(QtCore.Qt.white))
            app.processEvents()
            app.processEvents()
        with open(config_file_path) as data_file:    
            data = json.load(data_file)
            django_app_data = data["application"]
            project_dir_name = django_app_data["project_dir_name"].replace('\\', os.sep)
            assets_dir_name = django_app_data["assets_dir_name"].replace('\\', os.sep)
            assets_media_dir_name = django_app_data["assets_media_dir_name"].replace('\\', os.sep)
            project_dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..',project_dir_name))
            assets_dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..',assets_dir_name))
            assets_media_dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..',assets_media_dir_name))
            window_data= data["window"]
            dev_tools_menu_enabled = bool(util.strtobool(window_data["dev_tools_menu_enabled"].lower()))
            initial_width = int(window_data["width"])
            initial_height = int(window_data["height"])
            min_width = int(window_data["min_width"])
            min_height = int(window_data["min_height"])
            window_title = window_data["title"]
            icon_name = window_data["icon"]
            icon_name = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config',icon_name))
            fullscreen_allowed =  bool(util.strtobool(window_data["fullscreen_allowed"].lower()))
            max_width = int(window_data["max_width"])
            max_height = int(window_data["max_height"])
    except:
        print("Failed Reading Config")
    app.processEvents()
    
    # Ensure logging directory exists for Django
    log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "app", "appsource", "logs")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
            print("Created missing logs directory: %s" % log_dir)
        except:
            pass

    # --- DATA MIGRATION & WRITE CHECK ---
    data_root = GetWritableAppDataPath()
    log_boot("Data Root: %s" % data_root)
    
    # Migrate DB if needed
    src_db = os.path.join(project_dir_path, "db.sqlite3")
    dest_db = os.path.join(data_root, "db.sqlite3")
    if os.path.exists(src_db) and not os.path.exists(dest_db):
        try:
            import shutil
            shutil.copy2(src_db, dest_db)
            log_boot("Migrated database to AppData")
        except Exception as e:
            log_boot("Warning: Failed to migrate database: %s" % str(e))

    # Migrate Assets if needed
    src_assets = os.path.abspath(os.path.join(project_dir_path, "..", "app_assets"))
    dest_assets = os.path.join(data_root, "app_assets")
    if os.path.exists(src_assets) and not os.path.exists(dest_assets):
        try:
            import shutil
            shutil.copytree(src_assets, dest_assets)
            log_boot("Migrated assets to AppData")
        except Exception as e:
            log_boot("Warning: Failed to migrate assets: %s" % str(e))

    if splash:
        splash.showMessage("Compiling Assets...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, QtGui.QColor(QtCore.Qt.white))
        app.processEvents()
        app.processEvents()
    
    # Defensive compile - skip if read-only, and don't force
    try:
        # Don't use force=True to avoid permission denied spam for existing files
        compileall.compile_dir(project_dir_path, quiet=1)
    except:
        log_boot("Info: Skipping asset compilation (directory is read-only)")
    app.processEvents()
    
    # Ensure admin credentials are set using the current python executable
    try:
        if splash:
            splash.showMessage("Verifying Admin Credentials...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, QtGui.QColor(QtCore.Qt.white))
            app.processEvents()
            app.processEvents()
        admin_script = os.path.join(project_dir_path, "create_admin.py")
        if os.path.exists(admin_script):
            subprocess.check_call([sys.executable, admin_script])
            print("Successfully verified admin credentials.")
    except Exception as e:
        print("Warning: Failed to verify admin credentials: %s" % str(e))
    app.processEvents()

    if splash:
        splash.showMessage("Starting Backend Services...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, QtGui.QColor(QtCore.Qt.white))
        app.processEvents()
        app.processEvents()
    
    manage_path = os.path.join(project_dir_path, 'manage.pyc')
    if not os.path.exists(manage_path):
        manage_path = os.path.join(project_dir_path, 'manage.py')
    
    # Ensure subprocess inherits the correct environment (esp. PATH for DLLs)
    env = os.environ.copy()
    python_root = os.path.dirname(sys.executable)
    # Add python root and its DLL directories to PATH
    env['PATH'] = python_root + os.pathsep + os.path.join(python_root, "DLLs") + os.pathsep + os.environ.get('PATH', '')
    # Prevent Permission Denied errors for .pyc files in Program Files
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    # Redirect Matplotlib cache/config to a writable location
    mpl_config_dir = os.path.join(data_root, 'mpl_config')
    if not os.path.exists(mpl_config_dir):
        os.makedirs(mpl_config_dir)
    env['MPLCONFIGDIR'] = mpl_config_dir
    
    try:
        # 1. First, ensure migrations are applied (fixes "no such table: auth_user")
        log_boot("Running database migrations...")
        # Capture output to show in popup if it fails
        p = subprocess.Popen([sys.executable, manage_path, 'migrate', '--noinput'], 
                             env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            error_details = (out + "\n" + err).strip()
            # Show last 10 lines of error for relevance
            error_msg = "\n".join(error_details.splitlines()[-10:])
            log_boot("CRITICAL: Migration failed:\n%s" % error_details)
            show_fatal_error("Database Error", "Migrations failed. This usually means the environment is not ready or the DB is locked.\n\nError Summary:\n%s" % error_msg)
            # We continue anyway as the DB might already be ready
        
        # 2. Start the actual server
        log_boot("Starting Django on port 5427 via %s" % manage_path)
        # Use --noreload to avoid issues in packaged environments
        if sys.platform == "win32":
            import win32process
            proc = subprocess.Popen([sys.executable, manage_path, 'runserver', '127.0.0.1:5427', '--noreload'], 
                                   env=env,
                                   creationflags=win32process.CREATE_NO_WINDOW)
        else:
            proc = subprocess.Popen([sys.executable, manage_path, 'runserver', '127.0.0.1:5427', '--noreload'], env=env)
    except Exception as e:
        show_fatal_error("Backend Error", "Could not start Django server: %s" % str(e))
        sys.exit(1)

    print("[pyqt.py] PyQt version: %s" % QtCore.PYQT_VERSION_STR)
    print("[pyqt.py] QtCore version: %s" % QtCore.qVersion())

    sys.excepthook = ExceptHook

    # Application settings
    settings = {
        "debug": True,
        "log_severity": cefpython.LOGSEVERITY_INFO,
        "log_file": os.path.join(GetWritableAppDataPath(), "cef_debug.log"),
        "auto_zooming": "1",
        "release_dcheck_enabled": True,
        "cache_path": GetWritableAppDataPath("cache"),
        "locales_dir_path": os.path.join(cefpython.GetModuleDirectory(), "locales"),
        "resources_dir_path": cefpython.GetModuleDirectory(),
        "browser_subprocess_path": os.path.join(cefpython.GetModuleDirectory(), "subprocess.exe"),
        "context_menu":{"enabled" : dev_tools_menu_enabled},
    }

    # Command line switches set programmatically
    switches = {
        "remote-debugging-port": "5424",
        "no-proxy-server": "",
        "disable-gpu": "",
        "disable-gpu-compositing": "",
        "enable-begin-frame-scheduling": "",
    }

    # --- STEP 4: CEF & Main Window ---
    try:
        if splash:
            splash.showMessage("Initializing Browser Engine...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, QtGui.QColor(QtCore.Qt.white))
            app.processEvents()
            app.processEvents()
        log_boot("Initializing CEF...")
        cefpython.Initialize(settings, switches)
        is_cef_initialized = True
    except Exception as e:
        show_fatal_error("CEF Error", "Could not initialize Browser Engine: %s" % str(e))
        sys.exit(1)
    
    if splash:
        splash.showMessage("Launching Application...", QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter, QtGui.QColor(QtCore.Qt.white))
        app.processEvents()
        app.processEvents()
    
    try:
        log_boot("Creating MainWindow...")
        mw = MainWindow()
    except Exception as e:
        import traceback
        show_fatal_error("UI Error", "Could not create Main Window: %s\n\n%s" % (str(e), traceback.format_exc()))
        sys.exit(1)

    if splash:
        splash.finish(mw)
    
    # Run CEF Message Loop
    log_boot("Entering MessageLoop")
    is_running_loop = True
    cefpython.MessageLoop()
    is_running_loop = False
    
    # --- DEFINITIVE SHUTDOWN ---
    log_boot("Shutting down...")
    app.timer.stop()
    app.closeAllWindows()
    app.processEvents()
