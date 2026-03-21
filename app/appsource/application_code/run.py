# An example of embedding CEF browser in a PyQt4 application.
# Tested with PyQt 4.10.3 (Qt 4.8.5).
import os, sys,math
import subprocess,time,socket
import json
import compileall
from distutils import util
import re
from serial import SerialException,SerialTimeoutException
import winreg
import datetime
from dateutil.relativedelta import relativedelta
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtWebKit

device = None
thread_connection = None
browser_func = None
ser = None
vpt_ser = None
proc = None
web_view = None
dialog = None
printer = None
device_status = "DISCONNECTED"
hcp_device_status = "DISCONNECTED"
hcp_usb_device_status = "DISCONNECTED"
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
lead_off = False
air_leak = False
prev_time = datetime.datetime.now()
hcp_blu_time = datetime.datetime.now()
error_1 = False
error_2 = False
error_3 = False
hcp_usb_passcode = ""

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


def ExceptHook(excType, excValue, traceObject):
    import traceback, os, time, codecs
    errorMsg = "\n".join(traceback.format_exception(excType, excValue,
            traceObject))
    errorFile = GetApplicationPath("error.log")
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
    cefpython.QuitMessageLoop()
    cefpython.Shutdown()
    os._exit(1)


class MainWindow(QtGui.QMainWindow):
    mainFrame = None

    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.mainFrame = MainFrame(self)
        self.setCentralWidget(self.mainFrame)
        self.setMinimumSize(min_width,min_height)
        if fullscreen_allowed == False and max_height != 0 and max_width != 0: 
            self.setFixedSize(max_width,max_height)
        self.resize(initial_width, initial_height)
        self.setWindowTitle(window_title)
        self.setWindowIcon(QtGui.QIcon(icon_name))
        self.setWindowFlags(QtCore.Qt.WindowCancelButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.center()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def focusInEvent(self, event):
        cefpython.WindowUtils.OnSetFocus(int(self.centralWidget().winId()), 0, 0, 0)

    def closeEvent(self, event):
        url = self.mainFrame.browser.GetUrl()
        if url.startswith("http://127.0.0.1:5423/APP"):
            reply = QtGui.QMessageBox.question(self, 'Alert',"You should Close the test window first to quit application?", QtGui.QMessageBox.Ok)
            if reply == QtGui.QMessageBox.Ok:
                event.ignore()
        else:
            reply = QtGui.QMessageBox.question(self, 'Alert',"Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)])
                event.accept()
            else:
                event.ignore()


class MainFrame(QtGui.QWidget):
    browser = None

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)
        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsChild(int(self.winId()))   
        self.parent = parent 
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1',5423))
            sock.close()
            if result == 0:
                break
        self.browser = cefpython.CreateBrowserSync(windowInfo,
                browserSettings={},
                navigateUrl=GetApplicationPath("http://127.0.0.1:5423"))

        self.browser.SetClientHandler(LoadHandler())
        self.set_javascript_bindings()


    def moveEvent(self, event):
        cefpython.WindowUtils.OnSize(int(self.winId()), 0, 0, 0)

    def resizeEvent(self, event):
        cefpython.WindowUtils.OnSize(int(self.winId()), 0, 0, 0)

    def set_javascript_bindings(self):
        external = External(self.browser)
        bindings = cefpython.JavascriptBindings(bindToFrames=False, bindToPopups=False)
        bindings.SetObject("external", external)
        self.browser.SetJavascriptBindings(bindings)


class LoadHandler():
    def __init__(self):
        self.initial_app_loading = True

    def OnLoadStart(self, browser, **_):
        if self.initial_app_loading:
            self.initial_app_loading = False
    def OnLoadingStateChange(self, browser, is_loading, **_):
        if not is_loading:
            pass  
    def OnLoadEnd(self, browser, **_):
        pass
    def OnLoadError(self, browser, **_):
        pass


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
    crcTab16_U = [0]*255
    for i_U in range(0,255):
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
    return crc_U


def continuous_connect():
    global device
    global hcp_usb_device_status
    global browser_func
    while True:
        if hcp_usb_device_status == "CONNECTED":
            try:
                hex_string = "A"
                buffer = ToByteArray(hex_string)
                device.send_output_report(buffer)
                time.sleep(1)
            except:
                hcp_usb_device_status = "DISCONNECTED"
                hex_string = "Z"
                buffer = ToByteArray(hex_string)
                device.send_output_report(buffer)
                device.close()
                browser_func.ExecuteFunction("device_status","OFF")
                break


def data_handler(data):
    global browser_func
    global device
    global hcp_usb_device_status
    global hcp_usb_passcode
    try:
        if not device.is_plugged and not device.is_opened:
            hcp_usb_device_status = "DISCONNECTED"
            browser_func.ExecuteFunction("device_status","OFF")
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
            elif "OK" in data:
                hcp_usb_device_status = "CONNECTED"
                browser_func.ExecuteFunction("device_status","ON")
            else:
                data = data.replace(" ","").strip()
                browser_func.ExecuteFunction("js_print",str(data))
                browser_func.ExecuteFunction("device_status","ON")
        else:
            pass
    except Exception,e:
        hcp_usb_device_status = "DISCONNECTED"
        browser_func.ExecuteFunction("device_status","OFF")
        hex_string = "Z"
        buffer = ToByteArray(hex_string)
        device.send_output_report(buffer)


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
                thread_connection1 = threading.Thread(target=hcp_blu_device_check_status)
                thread_connection1.daemon = True
                thread_connection1.start()
                browser_func.ExecuteFunction("device_status","ON")
            elif data.strip() == "NOT OK":
                ser.close()
                hcp_device_status = "DISCONNECTED"
                browser_func.ExecuteFunction("password_show")
                time.sleep(1)
                browser_func.ExecuteFunction("device_status","OFF")
            elif data.strip() == "SLEEP":
                hcp_device_status = "DISCONNECTED"
                ser.close()
                browser_func.ExecuteFunction("device_status","OFF")
            else:
                if re.search(r'^\d+\.\d+',data) or re.search(r'\w+',data):
                    data = data.replace(" ","").strip()
                    browser_func.ExecuteFunction("js_print",str(data))
                if hcp_device_status == "CONNECTED":
                    browser_func.ExecuteFunction("device_status","ON")
        except SerialException:
            hcp_device_status = "DISCONNECTED"
            browser_func.ExecuteFunction("device_status","OFF")
            command = "Z"
            ser.write(command)
            ser.close()
            ser = None
            break
        except Exception,e:
            hcp_device_status = "DISCONNECTED"
            browser_func.ExecuteFunction("device_status","OFF")
            ser.close()
            ser = None
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


def can_blu_connection(passcode):
    global ser
    global browser_func
    global can_blu_device_status
    while True:
        data = ser.read_until()
        if data.strip() == "SERIAL?":
            ser.write(str(passcode))
        if data.strip() == "OK":
            browser_func.ExecuteFunction("device_status","ON")
            can_blu_device_status = "CONNECTED"
            break
        if data.strip() == "NOT OK":
            can_blu_device_status = "DISCONNECTED"
            browser_func.ExecuteFunction("password_show")
            time.sleep(1)
            browser_func.ExecuteFunction("device_status","OFF")
            ser = None
            browser_func = None
            break


def data_handler_can_blu():
    global ser
    global browser_func
    global prev_time
    global can_data_type
    global lead_off
    global air_leak
    list_data = list()
    ecg_level_1 = list()
    ecg_level_2 = list()
    ecg_level_3 = list()
    while True:
        if can_data_type == "PARA":
            data = ser.read(1)
            try:
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
                    data_1 = ser.read(1)
                    data_2 = ser.read(1)
                    data_3 = ser.read(1)
                    list_data.append(int(hex(ord(data_1)),16))
                    list_data.append(int(hex(ord(data_2)),16))
                    list_data.append(int(hex(ord(data_3)),16))
                    try:
                        if str(int(hex(ord(data_3)),16)).startswith("1"):
                            if not lead_off:
                                lead_off = True
                                ser.write('4')
                        elif str(int(hex(ord(data_3)),16)).startswith("2"):
                            if lead_off:
                                lead_off = False
                                ser.write('5')
                    except:
                        pass
                if val == 252:
                    prev_time = datetime.datetime.now()
                if len(list_data) > 45:
                    browser_func.ExecuteFunction('js_print',str(ecg_level_1).replace("[","").replace("]",""),str(ecg_level_2).replace("[","").replace("]",""),str(ecg_level_3).replace("[","").replace("]",""),str(list_data).replace("[","").replace("]",""))
                    list_data = []
                    ecg_level_1 = []
                    ecg_level_2 = []
                    ecg_level_3 = []
            except Exception,e:
                pass
        elif can_data_type == "SYM":
            data = ser.read(1)
            try:
                data = str(int(hex(ord(data)),16))
                if data == "2":
                    bp_data = ser.read(3)
                    if bp_data == "999":
                        ser.write('8')
                        final_data = ser.read(42)
                        pulse_rate = ""
                        systolic = ""
                        diastolic = ""
                        message_code = ""
                        for i in range(len(final_data)):
                            if final_data[i] == "M":
                                message_code = final_data[i+1:i+3]
                                if message_code == "00" or message_code == "03":
                                    is_error = False
                                else:
                                    ser.write('6')
                                    is_error = True
                            if final_data[i] == "P":
                                systolic = final_data[i+1:i+4]
                                diastolic = final_data[i+5:i+7]
                            if final_data[i] == "R":
                                pulse_rate = final_data[i+1:i+4]
                        if is_error:
                            browser_func.ExecuteFunction('js_bp_error',message_code)
                        else:
                            browser_func.ExecuteFunction('js_bp_print',systolic,diastolic,pulse_rate)
                    else:
                        browser_func.ExecuteFunction('js_print',str(bp_data))
            except Exception, e:
                print(e)


def data_handler_can(data):
    global browser_func
    global device
    global prev_time
    global can_password_ok
    global can_data_type
    global lead_off
    global air_leak
    global error_1
    global error_2
    global error_3
    list_data = list()
    
    try:
        ecg_level_1 = list()
        ecg_level_2 = list()
        ecg_level_3 = list()
        if can_password_ok == False:
            try:
                response = ''.join(chr(i) for i in data)
                if response.replace("\x00","").strip().startswith("OK"):
                    can_password_ok = True
                    import threading
                    thread_connection1 = threading.Thread(target=can_device_status_check)
                    thread_connection1.daemon = True
                    thread_connection1.start()
                    thread_connection2 = threading.Thread(target=usb_arrhytmia_check)
                    thread_connection2.daemon = True
                    thread_connection2.start()
                    browser_func.ExecuteFunction("device_status","ON")
                elif response.replace("\x00","").strip().startswith("NOT OK"):
                    can_password_ok = False
                    browser_func.ExecuteFunction("password_show")
                    time.sleep(1)
                    browser_func.ExecuteFunction("device_status","OFF")
                    browser_func = None
            except Exception,e:
                can_password_ok = False
        else:
            if can_data_type == "PARA":
                list_data = data
                for i in range(len(data)):
                    if error_1:
                        if i < 7:
                            ecg_level_1.append(list_data[i+1])
                            ecg_level_2.append(list_data[i+2])
                            ecg_level_3.append(list_data[i+3])
                            error_1 = False
                            error_2 = False
                            error_3 = False
                    if error_2:
                        if i < 7:
                            ecg_level_2.append(list_data[i+1])
                            ecg_level_3.append(list_data[i+2])
                            error_2 = False
                            error_3 = False
                    if error_3:
                        if i < 7:
                            ecg_level_3.append(list_data[i+1])
                            error_3 = False
                    if list_data[i] == 251:
                        try:
                            ecg_level_1.append(list_data[i+1])
                        except Exception,e:
                            error_1 = True
                        try:
                            ecg_level_2.append(list_data[i+2])
                        except Exception,e:
                            error_2 = True
                        try:
                            ecg_level_3.append(list_data[i+3])
                        except Exception,e:
                            error_3 = True
                    if list_data[i] == 254:
                        try:
                            if str(list_data[i+3]).startswith("1"):
                                if not lead_off:
                                    lead_off = True
                                    buffer = ToByteArray(str('4'))
                                    device.send_output_report(buffer)
                            elif str(list_data[i+3]).startswith("2"):
                                if lead_off:
                                    lead_off = False
                                    buffer = ToByteArray(str('5'))
                                    device.send_output_report(buffer)
                        except:
                            pass
                    if list_data[i] == 252:
                        prev_time = datetime.datetime.now()
                browser_func.ExecuteFunction('js_print',str(ecg_level_1).replace("[","").replace("]",""),str(ecg_level_2).replace("[","").replace("]",""),str(ecg_level_3).replace("[","").replace("]",""),str(list_data).replace("[","").replace("]",""))
            elif can_data_type == "SYM":
                if data[1] == 2: 
                    data = ''.join(chr(i) for i in data)
                    if '999' in data:
                        send_command_to_device("8")
                    elif 'P' in data:
                        pulse_rate = ""
                        systolic = ""
                        diastolic = ""
                        message_code = ""
                        for i in range(len(data)):
                            if data[i] == "M":
                                message_code = data[i+1:i+3]
                                if message_code == "00" or message_code == "03":
                                    is_error = False
                                else:
                                    buffer = ToByteArray(str('6'))
                                    device.send_output_report(buffer)
                                    air_leak = True
                                    is_error = True
                            if data[i] == "P":
                                systolic = data[i+1:i+4]
                                diastolic = data[i+5:i+7]
                            if data[i] == "R":
                                pulse_rate = data[i+1:i+4]
                        if is_error:
                            browser_func.ExecuteFunction('js_bp_error',message_code)
                        else:
                            browser_func.ExecuteFunction('js_bp_print',systolic,diastolic,pulse_rate)
                    else:
                        browser_func.ExecuteFunction('js_print',str(data[2:5]))
    except Exception,e:
        pass


def send_command_to_device(command):
    global device
    global browser_func
    try:
        buffer = ToByteArray(command)
        device.send_output_report(buffer)
        if command == "Z":
            device.close()
            browser_func.ExecuteFunction("device_status","OFF")
    except:
        pass


def send_command_to_device_via_blu(command):
    global ser
    global browser_func
    try:
        if ser:
            ser.write(command)
            if command == "Z":
                browser_func.ExecuteFunction("device_status","OFF")
                browser_func = None
                ser.close()
                ser = None
    except:
        browser_func = None
        ser = None
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
        print(e)


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


def hcp_blu_device_check_status():
    global ser
    global hcp_device_status
    global browser_func
    global hcp_blu_time
    while True:
        current_time = datetime.datetime.now()
        diff_time = relativedelta(current_time,hcp_blu_time)
        if hcp_device_status == "CONNECTED" and  diff_time.seconds < 6:
            time.sleep(2)
        else:
            browser_func.ExecuteFunction("device_status","OFF")
            ser.close()
            hcp_device_status = "DISCONNECTED"
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
    global can_password_ok
    while True:
        try:
            if can_password_ok == True and device.is_plugged():
                time.sleep(1)
                browser_func.ExecuteFunction("device_status","ON")
            else:
                browser_func.ExecuteFunction("device_status","OFF")
        except Exception,e:
            pass


def can_blu_device_check_status():
    global ser
    global can_blu_device_status
    global browser_func
    while True:
        if can_blu_device_status == "CONNECTED":
            try:
                ser.write("0")
                time.sleep(2)
                browser_func.ExecuteFunction("device_status","ON")
            except SerialException:
                browser_func.ExecuteFunction("device_status","OFF")
                ser.close()
                can_blu_device_status = "DISCONNECTED"
                break
            except Exception,e:
                break


def hcp_device_status_check():
    global browser_func
    global device
    global hcp_usb_device_status
    while True:
        if device.is_plugged() and hcp_usb_device_status == "CONNECTED":
            time.sleep(3)
            browser_func.ExecuteFunction("device_status","ON")
        else:
            hcp_usb_device_status = "DISCONNECTED"
            browser_func.ExecuteFunction("device_status","OFF")
            break


def arrhytmia_check():
    global prev_time
    global browser_func
    global can_data_type
    prev_time = datetime.datetime.now()
    while True:
        if can_data_type == "PARA":
            try:
                current_time = datetime.datetime.now()
                diff_time = relativedelta(current_time,prev_time)
                if diff_time.seconds > 30:
                    browser_func.ExecuteFunction('arrhythmia_alert')
                    break
                time.sleep(3)
            except Exception,e:
                break
        else:
            pass


def usb_arrhytmia_check():
    global prev_time
    global browser_func
    global can_data_type
    global device
    prev_time = datetime.datetime.now()
    while True:
        if can_data_type == "PARA" and device.is_plugged():
            try:
                current_time = datetime.datetime.now()
                diff_time = relativedelta(current_time,prev_time)
                if diff_time.seconds > 30:
                    browser_func.ExecuteFunction('arrhythmia_alert')
                    break
                time.sleep(3)
            except Exception,e:
                break
        else:
            pass


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
        except Exception,e:
            print e


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
                                thread_connection1 = threading.Thread(target=hcp_device_status_check)
                                thread_connection1.daemon = True
                                thread_connection1.start()
                            except:
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
                                    ser = serial.Serial(str(port),9600,bytesize=8, parity='N', stopbits=1,xonxoff=0,write_timeout=1,timeout=2)
                                    ser.write('Q')
                                    thread_connection = threading.Thread(target=data_handler_blu, args = ("K"+pass_code_,))
                                    thread_connection.daemon = True
                                    thread_connection.start()
                                    port_available = True
                                except Exception,e:
                                    widget = QtGui.QWidget()
                                    widget.setWindowTitle(window_title)
                                    widget.setWindowIcon(QtGui.QIcon(icon_name))
                                    QtGui.QMessageBox.question(widget,'Alert',"Please check Device is ON and Blutooth is paired with PC?",QtGui.QMessageBox.Ok)
                            else:
                                widget = QtGui.QWidget()
                                widget.setWindowTitle(window_title)
                                widget.setWindowIcon(QtGui.QIcon(icon_name))
                                QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device,Com port not available!",QtGui.QMessageBox.Ok)
                    except Exception,e:
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
                                    vpt_ser = serial.Serial(port,9600,parity='N',write_timeout=1)
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
                            device = devices[0]
                            device.open()
                            hex_string = "Q"
                            buffer = ToByteArray(hex_string)
                            device.send_output_report(buffer)
                            time.sleep(1)
                            buffer = ToByteArray('K'+str(pass_code))
                            device.send_output_report(buffer)
                            lead_off = False
                            air_leak = False
                            error_1 = False
                            error_2 = False
                            error_3 = False
                            device.set_raw_data_handler(data_handler_can)
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
                    browser_func = self.browser
                    try:
                        if can_blu_device_status != "CONNECTED":
                            pass_code_ = pass_code.split(":")[0]
                            bt_mac_addr = pass_code.split(":")[1]
                            bt_spp = BluetoothSpp()
                            port = bt_spp.get_spp_com_port(bt_mac_addr)
                            if port:
                                try:
                                    ser = serial.Serial(str(port),9600 ,bytesize=8, parity='N', stopbits=1,xonxoff=0,write_timeout=1,timeout=2)
                                    ser.write('Q')
                                    lead_off = False
                                    air_leak = False
                                    thread_connection = threading.Thread(target=can_blu_connection, args = ("K"+pass_code_,))
                                    thread_connection.daemon = True
                                    thread_connection.start()
                                    thread_connection2 = threading.Thread(target=data_handler_can_blu)
                                    thread_connection2.daemon = True
                                    thread_connection2.start()
                                    thread_connection1 = threading.Thread(target=arrhytmia_check)
                                    thread_connection1.daemon = True
                                    thread_connection1.start()
                                    thread_connection3 = threading.Thread(target=can_blu_device_check_status)
                                    thread_connection3.daemon = True
                                    thread_connection3.start()
                                except Exception,e:
	                                ser = None
	                                browser_func = None
	                                widget = QtGui.QWidget()
	                                widget.setWindowTitle(window_title)
	                                widget.setWindowIcon(QtGui.QIcon(icon_name))
	                                QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device,Com port not available!",QtGui.QMessageBox.Ok)
                            else:
                                widget = QtGui.QWidget()
                                widget.setWindowTitle(window_title)
                                widget.setWindowIcon(QtGui.QIcon(icon_name))
                                QtGui.QMessageBox.question(widget,'Alert',"Unable to connect with device,Com port not available!",QtGui.QMessageBox.Ok)
                    except Exception,e:
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
            print(connect_type,command,"commad")
            global can_data_type
            global prev_time
            global air_leak
            global can_password_ok
            if command == "A" or command == "C" or command == "E" or command == "G" or command == "I" or command == "W":
                prev_time = datetime.datetime.now()
                can_data_type = "PARA"
            elif command == "L" or command == "N" or command == "P" or command == "S" or command == "U":
                can_data_type = "SYM"
            elif command == "B" or command == "D" or command == "F" or command == "H" or command == "J" or command == "X":
                can_data_type = ""
            elif command == "7":
                air_leak = False
            if connect_type == "BLU":
                send_command_to_device_via_blu(command)
            else:
                send_command_to_device(command)
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
            global can_blu_device_status
            global device_status
            global vpt_ser
            global browser_func
            global device
            global dev
            global ser
            global can_password_ok
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
                    if connect_type == "USB" and hcp_usb_device_status == "CONNECTED":
                        hcp_usb_device_status = "DISCONNECTED"
                        send_command_to_device('Z')
                    elif connect_type == "BLU" and hcp_device_status == "CONNECTED":
                        hcp_device_status = "DISCONNECTED"
                        ser.write('Z')
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
                        can_password_ok = False
                        send_command_to_device('Z')
                        browser_func = None
                    elif connect_type == "BLU":
                        can_blu_device_status = "DISCONNECTED"
                        send_command_to_device_via_blu('Z')
                        browser_func = None
            except:
                pass
        js_callback.Call("str",close_device)

    def export_as_pdf(self,js_callback):
        def save_file(ele):
            try:
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
                name = QtGui.QFileDialog.getSaveFileName(caption='Save File', filter="PDF Files (*.pdf *.PDF)")
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
        self.timer.start(10)

    def onTimer(self):
        cefpython.MessageLoopWork()

    def stopTimer(self):
        self.timer.stop()

if __name__ == '__main__':
    config_file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config','config.json'))
    try:
        with open(config_file_path) as data_file:    
            data = json.load(data_file)
            django_app_data = data["application"]
            project_dir_name = django_app_data["project_dir_name"]
            assets_dir_name = django_app_data["assets_dir_name"]
            assets_media_dir_name = django_app_data["assets_media_dir_name"]
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
            print fullscreen_allowed,max_width,max_height
    except:
        print "Failed Reading Config"
    compileall.compile_dir(project_dir_path, force=True)
    proc = subprocess.Popen(['python','..\\' + project_dir_name + '\manage.pyc','runserver','127.0.0.1:5423'])
    print("[pyqt.py] PyQt version: %s" % QtCore.PYQT_VERSION_STR)
    print("[pyqt.py] QtCore version: %s" % QtCore.qVersion())

    sys.excepthook = ExceptHook

    # Application settings
    settings = {
        "debug": True,
        "log_severity": cefpython.LOGSEVERITY_INFO,
        "log_file": GetApplicationPath("debug.log"),
        "release_dcheck_enabled": True,
        "locales_dir_path": cefpython.GetModuleDirectory()+"/locales",
        "resources_dir_path": cefpython.GetModuleDirectory(),
        "browser_subprocess_path": "%s/%s" % (
            cefpython.GetModuleDirectory(), "subprocess"),
        "context_menu":{
            "enabled" : dev_tools_menu_enabled
        },
    }

    # Command line switches set programmatically
    switches = {
    "remote_debugging_port":"http://127.0.0.1:5423"
    }

    cefpython.Initialize(settings, switches)

    app = CefApplication(sys.argv)
    

    # Create and display the splash screen
    app_dir_path = os.path.abspath(os.path.join(os.path.dirname( __file__ )))
    splash_pix = QtGui.QPixmap(app_dir_path+'\\splash_screen.png')
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
    splash.setEnabled(False)
    progressBar = QtGui.QProgressBar(splash)
    progressBar.setMaximum(10)
    progressBar.setGeometry(0, splash_pix.height()-50, splash_pix.width(), 20)
    progressBar.setStyleSheet(" QProgressBar { border: 1px solid black; border-radius: 0px; text-align: center;font-size:16px;color:black; } QProgressBar::chunk {background-color: #3add36; width: 1px;}")
    splash.show()

    mainWindow = MainWindow()
    mainWindow.show()
    for i in range(1, 11):
        progressBar.setValue(i)
        t = time.time()
        while time.time() < t + 0.1:
           app.processEvents()
    splash.finish(mainWindow)
    sys.exit(app.exec_())
    app.stopTimer()
    del mainWindow
    del app

    cefpython.Shutdown()
