import multiprocessing as mp
from multiprocessing import Queue

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pynput.keyboard import Listener, Key, KeyCode

import sys
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

import win32con
import pyautogui
import pywinauto
import win32gui
import pygetwindow as gw
import keyboard
import time
import pandas as pd
import os
import requests
import urllib.request

print("test")

'''
<---------- 글로벌 단축키 지정
'''

hot_key_btn = ["z", "c", "w", "e"]

HOT_KEYS = {
    "app_close": set([Key.alt_l, KeyCode(char=hot_key_btn[0])]),
    "app_activate": set([Key.alt_l, KeyCode(char=hot_key_btn[1])]),
    "cim_maxminsizing": set([Key.alt_l, KeyCode(char=hot_key_btn[2])]),
    "app_hide": set([Key.alt_l, KeyCode(char=hot_key_btn[3])])
}

def app_close():
    try:
        win = gw.getWindowsWithTitle("CIMCL")[0]
        win.close()
    except:
        pass
    
def app_activate():
    cursor_pos = pyautogui.position()
    win = gw.getWindowsWithTitle("CIMCL")[0]
    if win.isActive == False:
        pywinauto.application.Application().connect(
            handle=win._hWnd).top_window().set_focus()
    win.activate()
    pyautogui.moveTo(cursor_pos)

app_hide_value = 0

def cim_maxminsizing():
    global app_hide_value
    handle_list = gw.getAllWindows()
    target_hwnd = str(handle_list).split(str(cimz_hwnd))[0].count("hWnd")
    if handle_list[target_hwnd - 1].isMinimized == True:
        cursor_pos = pyautogui.position()
        handle_list[target_hwnd - 1].maximize()
        pywinauto.application.Application().connect(
            handle=handle_list[target_hwnd - 1]._hWnd).top_window().set_focus()
        handle_list[target_hwnd - 1].activate()
        pyautogui.moveTo(cursor_pos)
        app_hide_value = 1
        app_hide()
    else:
        handle_list[target_hwnd - 1].minimize()
        app_hide_value = 0
        app_hide()

def app_hide():
    global app_hide_value
    hwnd = win32gui.FindWindow(None, "CIMCL")
    if app_hide_value == 0:
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        app_hide_value = 1
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        cursor_pos = pyautogui.position()
        win = gw.getWindowsWithTitle("CIMCL")[0]
        pywinauto.application.Application().connect(
            handle=win._hWnd).top_window().set_focus()
        win.activate()
        pyautogui.moveTo(cursor_pos)
        app_hide_value = 0

def sub_process(q):
    global cimz_hwnd
    cimz_hwnd = q.get()
    temp_path = r"C:\Temp\CIM_API_APP"

    if os.path.exists(temp_path + "\\ing.txt"):
        os.remove(temp_path + "\\ing.txt")

    key_set = set()
    app_activate()

    def handleKeyPress(input_key):
        key_set.add(input_key)
        for action, trigger in HOT_KEYS.items():
            CHECK = all(
                [True if triggerKey in key_set else False for triggerKey in trigger])
            if CHECK:
                try:
                    func = eval(action)
                    if callable(func):
                        func()
                except NameError as err:
                    print(err)

    def handleKeyRelease(input_key):
        key_set.clear()

    with Listener(on_press=handleKeyPress, on_release=handleKeyRelease) as listener:
        listener.join()

'''
글로벌 단축키 지정 ---------->
'''

# 현재 폴더의 경로 정의

img_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/1_command_line/source/icon/"

# 단축키가 정의된 csv 파일
user_short_csv = "short.csv"

# 구동 정보를 담고있는 csv 파일 (응답 내용 / API 관련 정보)
# 추후 csv 정리 차원에서 분리한 csv 만들 예정.csv

# 아이콘 이미지 파일
cl_icon_img = "cl_icon.png"
cim_icon_img = "cim_icon2.png"
cancel_img = "cancel.png"

        
def window_find(text):
    find_window_text = text
    find_window = pyautogui.getWindowsWithTitle(find_window_text)[0]
    window_title_ext = find_window.title
    hwnd = win32gui.FindWindow(None, window_title_ext)
    return hwnd

def class_find(hwnd, text):
    view_port_class = text
    hwnd_A = win32gui.FindWindowEx(hwnd, 0, view_port_class, None)
    return hwnd_A

# API 구동 변수
header = {"MAPI-Key": "eyJ1ciI6ImxzYjE5OTExMTA5IiwicGciOiJjaW0iLCJjbiI6ImJyaloxUURqU2cifQ.d762ab1c8c828c383ca5ab50e6b4c110393d829d77577b369760a302328d7718"}
uri_first = "https://api-beta.midasit.com/cim"

# API 수행 완료 / 실패에 따른 Output massege 변수
done_massege = "Done"
unknown_short = "그 명령어는 지정한 적이 없으세요 ^^"

# Default Opacity option
opa_opt = 0
resize_opt = 1

custom_style = '''
    QWidget{font-size: 9pt; background: rgb(20, 31, 45); color: rgb(255, 255, 255); border: none;}
    QPushButton{background: rgb(47, 59, 76); height: 30px; border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
    QPushButton:hover{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242);}
    QPushButton:pressed{background: rgb(11, 125, 182);}
    QLabel{}
    QLineEdit{background: rgb(34, 44, 60); border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
    QLineEdit:disabled{background: rgb(55, 55, 55); color: rgb(137, 144, 148);}
    QLineEdit:hover{background: rgb(45, 53, 68);}
    QLineEdit:focus{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242); background: rgb(41, 48, 61)}
    QGroupBox{}
    QRadioButton{}
    QRadioButton::indicator {width:12px; height:12px; background: rgb(34, 44, 60); border: 1px solid; border-radius:7px; border-color: rgb(56, 69, 90);}
    QRadioButton::indicator:hover {width:10px; height:10px; background: rgb(34, 44, 60); border: 2px solid; border-radius:7px; border-color: rgb(26, 132, 213);}
    QRadioButton::indicator:checked {width:6px; height:6px; background: rgb(255, 255, 255); border: 4px solid; border-radius:7px; border-color: rgb(26, 132, 213);}
    QTextBrowser{background: rgb(20, 31, 45); border: 1px solid; border-color: rgb(20, 31, 45);}
    QScrollBar{height:0px;}
    '''

# UI 정의
class Ui_MainWindow(QMainWindow):
    def __init__(self, q):
        super().__init__()
        self.setWindowTitle("CIMCL")
        self.setFixedSize(400, 76)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.FramelessWindowHint)

        # 전체 위젯 / 전체 레이아웃
        void_widget = QWidget()
        void_widget.setStyleSheet(
            "background: rgb(12, 20, 31); border: 1px solid; border-color: rgb(56, 69, 90);")
        main_layout = QVBoxLayout(void_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        self.setStyleSheet("background-color: rgb(21, 22, 24);")

        # 1 layout
        temp_img_path = img_drive_url + cim_icon_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        cim_pixmap = QPixmap()
        cim_pixmap.loadFromData(temp_img)
        cim_icon = QIcon()
        cim_icon.addPixmap(cim_pixmap)
        self.sub_widget1 = QWidget()
        self.sub_widget1.setStyleSheet(custom_style)
        self.sub_layout1 = QHBoxLayout(self.sub_widget1)
        self.sub_layout1.setContentsMargins(2, 2, 2, 2)
        self.output_area = QTextBrowser(self)
        self.output_area.append("우측 버튼을 눌러 App을 부착할 CIM 창을 먼저 선택하세요.")
        self.output_area.append("(Select Window > Press Spacebar)")
        self.output_area.setFixedHeight(60)
        self.cimz_select_btn = QPushButton(self)
        self.cimz_select_btn.setFixedSize(32,32)
        self.cimz_select_btn.setIcon(cim_icon)
        self.cimz_select_btn.setIconSize(QSize(24,24))
        self.cimz_select_btn.pressed.connect(self.cimz_select)
        self.sub_layout1.addWidget(self.output_area)
        self.sub_layout1.addWidget(self.cimz_select_btn)

        main_layout.addWidget(self.sub_widget1)

        # 2 layout
        cl_icon = QPixmap()
        temp_img_path = img_drive_url + cl_icon_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        cl_icon.loadFromData(temp_img)
        cl_icon = cl_icon.scaled(QSize(30, 24))
        temp_img_path = img_drive_url + cancel_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        cancel_pixmap = QPixmap()
        cancel_pixmap.loadFromData(temp_img)
        cancel_icon = QIcon()
        cancel_icon.addPixmap(cancel_pixmap)

        self.sub_widget2 = QWidget()
        self.sub_widget2.setStyleSheet(custom_style)
        self.sub_layout2 = QHBoxLayout(self.sub_widget2)
        self.sub_layout2.setContentsMargins(2, 2, 2, 2)
        self.line_symbol = QLabel("", self)
        self.line_symbol.setPixmap(cl_icon)
        self.line_symbol.setFixedHeight(24)
        self.input_line = QLineEdit("", self)
        self.input_line.setFixedHeight(24)
        self.input_line.returnPressed.connect(self.enterkey)
        self.cancel_btn = QPushButton(self)
        self.cancel_btn.setFixedSize(24,24)
        self.cancel_btn.setIcon(cancel_icon)
        self.cancel_btn.pressed.connect(QCoreApplication.instance().quit)
        self.sub_layout2.addWidget(self.line_symbol)
        self.sub_layout2.addWidget(self.input_line)
        self.sub_layout2.addWidget(self.cancel_btn)
        self.sub_layout2.setStretchFactor(self.input_line, 10)

        main_layout.addWidget(self.sub_widget2)

        for i in hot_key_btn:
            self.i = QPushButton(self)
            self.i.setShortcut("Alt+" + i.upper())
            self.i.pressed.connect(self.focus_out)

        self.resize_btn = QPushButton(self)
        self.resize_btn.setShortcut("Alt+R")
        self.resize_btn.pressed.connect(self.resize_bar)

        self.opacity_btn = QPushButton(self)
        self.opacity_btn.setShortcut("Alt+O")
        self.opacity_btn.pressed.connect(self.opacity)

        self.parent_select_btn = QPushButton(self)
        self.parent_select_btn.pressed.connect(self.cimz_select)

        self.input_line.setText("inActive")
        self.input_line.setDisabled(True)

        self.setCentralWidget(void_widget)

    def enterkey(self):
        # 입력된 text를 변수 지정
        input_value = self.input_line.text()
        self.output_area.append(input_value)
        print(input_value)

        # 입력 값 변환 (Depth가 있는 명령 구동 시 "_" 기준 명령 분리)
        input_split_num = input_value.count("_")
        input_split = input_value.split("_")
        input_last = input_split.pop(input_split_num)
        if input_split_num == 0:
            input_fisrt = input_value
        else:
            input_fisrt = input_split.pop(0)

        self.input_line.setText("")

        # # 현재 사용자의 모드 확인하기 (rebar list 열람 활용)
        # current_mode = mode_get()

        # # csv - input value 매칭하여 api 명령 실행
        # else:
        #     # cvs data 정리 / 추후에는 csv 파일을 분리하여 사용자는 기능과 단축 명령만 정의 나머지 구동 정보를 담은 csv를 별도로 제공하는 것이 좋을 듯 함.
        #     csv = pd.read_csv(new_folder_path + user_short_csv,
        #                       header=None,
        #                       encoding="CP949")

        #     com_in = csv[2]
        #     com_in_val = com_in.values
        #     com_in_list = com_in_val.tolist()

        #     # 일치하는 단축 명령이 있는 경우 request 함수를 조립하여 실행
        #     if input_fisrt in com_in_list:
        #         # URI
        #         com_uri = csv[4]
        #         com_uri_val = com_uri.values
        #         com_uri_list = com_uri_val.tolist()
        #         matching_uri = com_uri_list.pop(com_in_list.index(input_fisrt))
        #         # Method
        #         com_method = csv[4 * input_split_num + 6]
        #         com_method_val = com_method.values
        #         com_method_list = com_method_val.tolist()
        #         matching_method = com_method_list.pop(
        #             com_in_list.index(input_fisrt))
        #         # mode
        #         com_mode = csv[3]
        #         com_mode_val = com_mode.values
        #         com_mode_list = com_mode_val.tolist()
        #         matching_mode = com_mode_list.pop(
        #             com_in_list.index(input_fisrt))
        #         # id
        #         com_id = csv[4 * input_split_num + 7]
        #         com_id_val = com_id.values
        #         com_id_list = com_id_val.tolist()
        #         matching_id = com_id_list.pop(com_in_list.index(input_fisrt))
        #         # key
        #         com_key = csv[4 * input_split_num + 8]
        #         com_key_val = com_key.values
        #         com_key_list = com_key_val.tolist()
        #         matching_key = com_key_list.pop(com_in_list.index(input_fisrt))

        #         # csv로부터 Request 구성을 파악하여, Request 함수 구성
        #         # Mode
        #         if pd.isna(matching_mode):
        #             request_mode = ""
        #         else:
        #             request_mode = current_mode
        #         # URI
        #         if pd.isna(matching_uri):
        #             request_last = ""
        #         else:
        #             request_last = matching_uri
        #         # id (Option 값에 의해 패널 구성이 바뀌는 경우 _optionnumber 식으로 Depth 진입)
        #         if pd.isna(matching_id):
        #             request_body = ""
        #         else:
        #             request_body = "{\"id\":\"" + matching_id + \
        #                 "\",\"value\":" + input_last + "}"
        #         # Key (Key 값을 포함해야 기능이 동작하는 경우, _keynum 식으로 Depth 진입)
        #         if pd.isna(matching_key):
        #             request_key = ""
        #         else:
        #             request_key = "?key=" + input_last

        #         # Request 함수 생성 및 실행
        #         new_code_str = "requests." + matching_method + \
        #             "(\"" + uri_first + "/" + request_mode + request_last + \
        #             request_key + \
        #             "\", headers=header, json = [" + request_body + "])"

        #         exec(new_code_str)

        #         # n차 명령이 있는가? (다음 Depth 확인)
        #         com_next = csv[4 * input_split_num + 9]
        #         com_next_val = com_next.values
        #         com_next_list = com_next_val.tolist()
        #         matching_next = com_next_list.pop(
        #             com_in_list.index(input_fisrt))

        #         # 다음 명령이 없다면(= 동작 수행 완료) if 메세지 / 다음 명령이 있다면 "_"를 붙여 계속 진행
        #         if pd.isna(matching_next):
        #             self.output_area.setText(done_massege)
        #             self.input_line.setText("")
        #         else:
        #             self.output_area.setText(matching_next)
        #             self.input_line.setText(input_value + "_")

        #     # 지정되지 않은 명령어 입력 시
        #     else:
        #         self.output_area.setText(unknown_short)
        #         self.input_line.setText("")

    # 단축키 입력 시 ui 사이즈 변경
    def resize_bar(self):
        global resize_opt
        hwnd_cim_view = class_find(target_cim_hwnd, "MDIClient")
        new_rect = win32gui.GetWindowRect(hwnd_cim_view)
        x = new_rect[0]
        y = new_rect[3] - 20
        w = new_rect[2] - new_rect[0]

        app_height = [32, 100]
        cube_width = 100

        if resize_opt == 0:
            self.sub_widget1.hide()
            self.setFixedSize(w - cube_width, app_height[0])
            self.setGeometry(
                x, y - app_height[0], w - cube_width, app_height[0])
            resize_opt = 1
        elif resize_opt == 1:
            self.sub_widget1.show()
            self.setFixedSize(w - cube_width, app_height[1])
            self.setGeometry(
                x, y - app_height[1], w - cube_width, app_height[1])
            resize_opt = 0

    # 단축키 입력 시 ui 투명도 변경
    def opacity(self):
        global opa_opt
        if opa_opt == 0:
            opa_opt = 1
            self.setWindowOpacity(0.5)

        else:
            opa_opt = 0
            self.setWindowOpacity(1)

        self.input_line.setFocus()

    def focus_out(self):
        self.output_area.setFocus()

    def keyPressEvent(self, event):
        self.input_line.setFocus()
        if event.key() in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Backspace]:
            pass
        else:
            self.input_line.setText(self.input_line.text() + event.text())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        try:
            if self.offset is not None and event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.pos() - self.offset)
            else:
                super().mouseMoveEvent(event)
        except:
            pass

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

    def cimz_select(self):
        global target_cim_hwnd
        while True:
            if keyboard.is_pressed(" "):
                time.sleep(0.2)
                break
        
        self.activateWindow()
        target_cim_hwnd = win32gui.GetForegroundWindow()
        q.put(target_cim_hwnd)
        self.resize_bar()

        self.cimz_select_btn.hide()
        self.input_line.setDisabled(False)
        self.output_area.setText("CIM Connected!")
        self.input_line.setText("")
        self.input_line.setFocus()
    
    def closeEvent(self, e) -> None:
        self.isClosed = True
        print("a")
        e.accept()

if __name__ == "__main__":
    q = Queue()

    sc_wait = mp.Process(name="short_cut", target=sub_process,
                            args=(q, ), daemon=True)
    sc_wait.start()
    app = QApplication(sys.argv)
    ui = Ui_MainWindow(q)
    ui.show()
    sys.exit(app.exec_())