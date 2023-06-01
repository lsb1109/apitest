from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qtwidgets import AnimatedToggle

import pandas as pd

import time
# import pyautogui

import os
import sys
import win32com.client as win32
from win32 import win32gui
import win32con
import requests
import urllib.request

import winreg as reg

temp_path = r"C:\Temp\CIM_API_APP"

if os.path.exists(temp_path + "\\ing.txt"):
    os.remove(temp_path + "\\ing.txt")

# 파일 경로 정의

csv_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/2_api_connect_xl/source/"
img_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/2_api_connect_xl/source/icon/"

xl_img = "xl.png"
lock_img = "lock.png"
unlock_img = "unlock.png"
show_img = "show.png"
hide_img = "hide.png"
api_list_img = "api_list_icon.png"
request_img = "request_icon.png"
cancel_img = "cancel.png"

key = reg.HKEY_CURRENT_USER 
key_value = "SOFTWARE\MIDAS\midas CIM\APISetting"
open = reg.OpenKey(key,key_value,0,reg.KEY_ALL_ACCESS)
api_key_value, api_key_type = reg.QueryValueEx(open,"APIKey")

header = {'MAPI-Key' : api_key_value}
uri_first = "https://api-beta.midasit.com/cim"

mode_short_list = ["b", "p", "c", "a"]
mode_list = ["base-mode", "point-library-mode", "curve-library-mode", "assembly-unit-mode"]

def query_text_const(request_key, apply_bool):
    if apply_bool == 0 :
        apply_query = ""
    else :
        apply_query = "apply=true"
    
    if request_key != "" or apply_query != "" :
        query_text1 = "?"
        if request_key != "" and apply_query != "" :
            query_text2 = "&"
        else : 
            query_text2 = ""
    else :
        query_text1 = ""
        query_text2 = ""

    query_result = query_text1 + request_key + query_text2 + apply_query
    
    return query_result

def request_fun(request_mode, matching_method, request_last, request_key, request_body, apply_bool) :
    query = query_text_const(request_key, apply_bool)
    new_code_str = "requests." + matching_method + "(\"" + uri_first + "/" + request_mode + request_last + query + "\", headers=header, json = [" + request_body + "])"
    # print(new_code_str)
    run_request = eval(new_code_str)
    status_result = run_request.status_code
    if status_result < 300 :
        massege = run_request.json()
    else :
        massege = "400"
    # print(massege)
    return new_code_str, massege

def cell_autofit(load_wb):
    if toggle2_state[0] == 1 :
        for sh in load_wb.Sheets:
            ws = load_wb.Worksheets(sh.Name)
            # 셀의 너비를 조절한다.
            ws.Columns.AutoFit()
            ws.Rows.AutoFit()

def df_column_selection(df) :
    temp_list = df.columns.to_list()
    if "uri" in temp_list : 
        df = df[["name", "key", "select key"]]
    elif "enable" in temp_list :
        df = df[["id", "value"]]
    return df

def csv2json_id(df_list, csv_name) :
    temp_csv = csv_drive_url + csv_name + ".csv"
    temp_df1 = pd.read_csv(temp_csv , \
                        header= None, \
                        encoding='CP949')
    temp_df1 = temp_df1.drop(2, axis= 1)
    temp_df1.columns = ["id", "new_id"]
    temp_df1 = temp_df1.set_index("id")
    sum_df_list = [temp_df1] + df_list
    new_df = pd.concat(sum_df_list, axis = 1)
    validation = (new_df["new_id"] != "-")
    new_df = new_df[validation]
    new_df = new_df.set_index("new_id")
    return new_df

def id_convert(csv_name, id_list) :
    temp_csv = csv_drive_url + csv_name + ".csv"
    temp_df = pd.read_csv(temp_csv , \
                        header= None, \
                        encoding='CP949')
    validation = (temp_df[1] != "-")
    temp_df = temp_df[validation]
    old_id = temp_df[0].values.tolist()
    new_id = temp_df[1].values.tolist()
    data_type = temp_df[2].values.tolist()
    matching_id_list = []
    matching_type_list = []
    for i in id_list :
        matching_id = old_id[new_id.index(i)]
        matching_id_list.append(matching_id)
        matching_type = data_type[new_id.index(i)]
        matching_type_list.append(matching_type)
    return matching_id_list, matching_type_list


def api_method() :
    if radio1_state[0] == 0 :
        method = "get"
    elif radio1_state[0] == 1 :
        method = "post"
    elif radio1_state[0] == 2 :
        method = "patch"
    return method

def get_window_hwnd_list():
    def callback(_hwnd, _result: list):
        title = win32gui.GetWindowText(_hwnd)
        if win32gui.IsWindowEnabled(_hwnd) and win32gui.IsWindowVisible(_hwnd) and title is not None and len(title) > 0:
            _result.append(_hwnd)
        return True

    result = []
    win32gui.EnumWindows(callback, result)
    return result

connected_xl = []
con_xl_hidden = [0]
con_xl_lock = [0]
toggle1_state = [0]
toggle2_state = [0]
radio1_state = [0]

custom_style = '''
    QWidget{font-size: 9pt; background: rgb(20, 31, 45); color: rgb(255, 255, 255);}
    QPushButton{background: rgb(47, 59, 76); height: 30px; border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
    QPushButton:hover{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242);}
    QPushButton:pressed{background: rgb(11, 125, 182);}
    QLabel{}
    QLineEdit{background: rgb(34, 44, 60); border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
    QLineEdit:hover{background: rgb(45, 53, 68);}
    QLineEdit:focus{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242); background: rgb(41, 48, 61)}
    QGroupBox{}
    QRadioButton{}
    QRadioButton::indicator {width:12px; height:12px; background: rgb(34, 44, 60); border: 1px solid; border-radius:7px; border-color: rgb(56, 69, 90);}
    QRadioButton::indicator:hover {width:10px; height:10px; background: rgb(34, 44, 60); border: 2px solid; border-radius:7px; border-color: rgb(26, 132, 213);}
    QRadioButton::indicator:checked {width:6px; height:6px; background: rgb(255, 255, 255); border: 4px solid; border-radius:7px; border-color: rgb(26, 132, 213);}
    '''
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(344, 105)
        self.setWindowFlags(Qt.WindowStaysOnTopHint  |  Qt.FramelessWindowHint)
        self.setWindowTitle("API Tool")
        
        # 전체 위젯 / 전체 레이아웃
        void_widget = QWidget()
        void_widget.setStyleSheet("background: rgb(12, 20, 31);")
        main_layout = QVBoxLayout(void_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)

        # 1 layout
        xl_pixmap = QPixmap()
        temp_img_path = img_drive_url + xl_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        xl_pixmap.loadFromData(temp_img)
        
        lock_pixmap = QPixmap()
        temp_img_path = img_drive_url + lock_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        lock_pixmap.loadFromData(temp_img)
        
        unlock_pixmap = QPixmap()
        temp_img_path = img_drive_url + unlock_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        unlock_pixmap.loadFromData(temp_img)
        
        show_pixmap = QPixmap()
        temp_img_path = img_drive_url + show_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        show_pixmap.loadFromData(temp_img)
        
        hide_pixmap = QPixmap()
        temp_img_path = img_drive_url + hide_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        hide_pixmap.loadFromData(temp_img)
        
        api_list_pixmap = QPixmap()
        temp_img_path = img_drive_url + api_list_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        api_list_pixmap.loadFromData(temp_img)
        
        request_pixmap = QPixmap()
        temp_img_path = img_drive_url + request_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        request_pixmap.loadFromData(temp_img)
        
        cancel_pixmap = QPixmap()
        temp_img_path = img_drive_url + cancel_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        cancel_pixmap.loadFromData(temp_img)

        xl_icon = QIcon()
        xl_icon.addPixmap(xl_pixmap)
        self.lock_icon = QIcon()
        self.lock_icon.addPixmap(lock_pixmap)
        self.unlock_icon = QIcon()
        self.unlock_icon.addPixmap(unlock_pixmap)
        self.show_icon = QIcon()
        self.show_icon.addPixmap(show_pixmap)
        self.hide_icon = QIcon()
        self.hide_icon.addPixmap(hide_pixmap)

        sub_widget1 = QWidget()
        sub_widget1.setStyleSheet(custom_style)
        sub_layout1 = QHBoxLayout(sub_widget1)
        sub_layout1.setContentsMargins(10, 10, 10, 10)
        self.btn1 = QPushButton("  Run", self)
        self.btn1.setIcon(xl_icon)
        self.btn1.setFixedSize(84, 30)
        self.btn1.clicked.connect(self.excel_run)
        self.btn2 = QPushButton("  Close", self)
        self.btn2.setIcon(xl_icon)
        self.btn2.setFixedSize(84, 30)
        self.btn2.clicked.connect(self.excel_close)
        # self.btn11 = QPushButton("", self)
        # self.btn11.setStyleSheet("background: rgb(20, 31, 45); border-color: rgb(35, 45, 60);")
        # self.btn11.setIcon(self.lock_icon)
        # self.btn11.setFixedSize(30, 30)
        # self.btn11.clicked.connect(self.excel_lock)
        self.btn12 = QPushButton("", self)
        self.btn12.setStyleSheet("background: rgb(20, 31, 45); border-color: rgb(35, 45, 60);")
        self.btn12.setIcon(self.show_icon)
        self.btn12.setFixedSize(30, 30)
        self.btn12.clicked.connect(self.excel_call)
        sub_layout1.addWidget(self.btn1)
        sub_layout1.addWidget(self.btn2)
        sub_layout1.addStretch(100)
        # sub_layout1.addWidget(self.btn11, alignment=QtCore.Qt.AlignRight)
        sub_layout1.addWidget(self.btn12, alignment=QtCore.Qt.AlignRight)
        main_layout.addWidget(sub_widget1)
        
        # 2 layout
        api_list_icon = QIcon()
        api_list_icon.addPixmap(api_list_pixmap)
        
        sub_widget2 = QWidget()
        sub_widget2.setStyleSheet(custom_style)
        sub_layout2 = QVBoxLayout(sub_widget2)
        sub_layout2.setContentsMargins(10, 10, 10, 10)
        layout_key = QHBoxLayout()
        self.lable1 = QLabel()
        self.lable1.setText("API_Key")
        self.lable1.setFixedSize(66, 30)
        self.input1 = QLineEdit(api_key_value, self)
        self.input1.setFixedHeight(30)
        layout_key.addWidget(self.lable1)
        layout_key.setStretchFactor(self.lable1, 1)
        layout_key.addWidget(self.input1)
        layout_key.setStretchFactor(self.input1, 4)
        sub_layout2.addLayout(layout_key)

        layout_mode = QHBoxLayout()
        self.lable2 = QLabel()
        self.lable2.setText("Mode")
        self.lable2.setFixedSize(66, 30)
        self.input2 = QLineEdit(self)
        self.input2.setText("c")
        self.input2.setFixedHeight(30)
        layout_mode.addWidget(self.lable2)
        layout_mode.setStretchFactor(self.lable2, 1)
        layout_mode.addWidget(self.input2)
        layout_mode.setStretchFactor(self.input2, 4)
        sub_layout2.addLayout(layout_mode)        
        self.btn4 = QPushButton("  API Function List", self)
        self.btn4.setIcon(api_list_icon)
        self.btn4.clicked.connect(self.fun_btn)        
        sub_layout2.addWidget(self.btn4)
        
        main_layout.addWidget(sub_widget2)
        
        # 3 layout
        request_icon = QIcon()
        request_icon.addPixmap(request_pixmap)
        
        sub_widget3 = QWidget()
        sub_widget3.setStyleSheet(custom_style)
        sub_layout3 = QVBoxLayout(sub_widget3)
        sub_layout3.setContentsMargins(10, 10, 10, 10)

        layout_btn_set = QHBoxLayout()
        layout_btn_set.addWidget(self.request_group_rad())
        
        layout_btn_tog_set = QVBoxLayout()
        layout_btn_tog1 = QHBoxLayout()
        toggle_1 = AnimatedToggle(checked_color="#1A84D5", pulse_checked_color="#44FFB000")
        toggle_1.setFixedSize(48, 32)
        toggle_1.toggled.connect(self.toggle1)
        self.lable0 = QLabel()
        self.lable0.setText("TRANSPOSE")
        self.lable0.setFixedSize(140, 30)
        layout_btn_tog1.addWidget(toggle_1)
        layout_btn_tog1.addWidget(self.lable0)
        layout_btn_tog_set.addStretch(30)
        layout_btn_tog_set.addLayout(layout_btn_tog1)
        
        layout_btn_tog2 = QHBoxLayout()
        toggle_2 = AnimatedToggle(checked_color="#1A84D5", pulse_checked_color="#44FFB000")
        toggle_2.setFixedSize(48, 32)
        toggle_2.toggled.connect(self.toggle2)
        self.lable3 = QLabel()
        self.lable3.setText("AUTO FIT")
        self.lable3.setFixedSize(140, 30)
        layout_btn_tog2.addWidget(toggle_2)
        layout_btn_tog2.addWidget(self.lable3)
        layout_btn_tog_set.addLayout(layout_btn_tog2)
        layout_btn_tog_set.addStretch(30)
        
        layout_btn_set.addLayout(layout_btn_tog_set)
        
        sub_layout3.addLayout(layout_btn_set)
        
        self.btn5 = QPushButton("  Request", self)
        self.btn5.setIcon(request_icon)
        self.btn5.clicked.connect(self.request_btn)
        
        self.output_area = QtWidgets.QTextBrowser(self)
        self.output_area.setStyleSheet("color: rgb(150, 150, 150); background-color: rgb(20, 22, 20);")
        self.output_area.setText("request")
        sub_layout3.addWidget(self.btn5)        
        sub_layout3.addWidget(self.output_area)
        
        main_layout.addWidget(sub_widget3)
        
        # 4 layout (UI default)
        cancel_icon = QIcon()
        cancel_icon.addPixmap(cancel_pixmap)
        
        sub_widget4 = QWidget()
        sub_widget4.setStyleSheet(custom_style)
        sub_layout4 = QVBoxLayout(sub_widget4)
        sub_layout4.setContentsMargins(10, 6, 10, 6)
        
        self.xbtn = QPushButton(self)
        self.xbtn.setFixedSize(28, 28)
        self.xbtn.setIcon(cancel_icon)
        self.xbtn.setShortcut("ALT+X")
        self.xbtn.clicked.connect(self.closeEvent)
        sub_layout4.addWidget(self.xbtn, alignment=QtCore.Qt.AlignRight)
        
        main_layout.addWidget(sub_widget4)

        self.setCentralWidget(void_widget)

    def excel_run(self):
        global xl, wb, ws
        ex_hwnd_list = get_window_hwnd_list()
        xl = win32.Dispatch("Excel.Application")
        xl.Visible = True
        wb = xl.Workbooks.Add()
        ws = wb.Worksheets(1)
        new_hwnd_list = get_window_hwnd_list()
        new_xl_hwnd = list(set(new_hwnd_list) - set(ex_hwnd_list))[0]
        connected_xl.append(new_xl_hwnd)
        self.output_area.setText("[" + time.strftime("%X") + "] " + "Done")
        
    def excel_close(self):
        connected_xl.clear()
        try :
            wb.Close()
            xl.Quit()
            os.remove("temp.xlsx")
            self.output_area.setText("[" + time.strftime("%X") + "] " + "Done")
        except :
            self.output_area.setText("[" + time.strftime("%X") + "] " + "연결된 Excel이 없습니다.")
        
    # def excel_lock(self):
    #     if con_xl_lock[0] == 0 :
    #         con_xl_lock[0] = 1
    #         self.btn11.setIcon(self.unlock_icon)
    #         for i in connected_xl :
    #             try : 
    #                 win32gui.SetWindowPos(i, win32con.HWND_TOPMOST, 500, 500, 500, 500, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    #                 self.output_area.setText("[" + time.strftime("%X") + "] " + "Done")
    #             except :
    #                 pass
    #     else : 
    #         con_xl_lock[0] = 0
    #         self.btn11.setIcon(self.lock_icon)
    #         for i in connected_xl :
    #             try : 
    #                 win32gui.SetWindowPos(i, win32con.HWND_NOTOPMOST, 500, 500, 500, 500, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    #                 self.output_area.setText("[" + time.strftime("%X") + "] " + "Done")
    #             except :
    #                 pass
                
    def excel_call(self):
        if con_xl_hidden[0] == 0 :
            con_xl_hidden[0] = 1
            self.btn12.setIcon(self.hide_icon)
            for i in connected_xl :
                try : 
                    win32gui.ShowWindow(i, win32con.SW_HIDE)
                    self.output_area.setText("[" + time.strftime("%X") + "] " + "Done")
                except :
                    pass
        else : 
            con_xl_hidden[0] = 0
            self.btn12.setIcon(self.show_icon)
            for i in connected_xl :
                try : 
                    win32gui.ShowWindow(i, win32con.SW_SHOW)
                    self.output_area.setText("[" + time.strftime("%X") + "] " + "Done")
                except :
                    pass

    def data_read(self, df, color, bool_num) :
        active_cell = xl.ActiveCell

        dir1, dir2 = self.dir_tester()
        
        df_index_list = df.index.to_list()
        df_column_list = df.columns.to_list()

        offset_cell_d1 = active_cell
        if bool_num == 0 :
            for i in range(df.shape[0]) :
                offset_cell_d1 = offset_cell_d1.Offset (dir1[0], dir1[1])
                offset_cell_d1.Value = i + 1
                offset_cell_d1.font.ColorIndex = 15
        else : 
            for i in range(df.shape[0]) :
                offset_cell_d1 = offset_cell_d1.Offset (dir1[0], dir1[1])
                offset_cell_d1.Value = df_index_list[i]

        offset_cell_d2 = active_cell
        if bool_num == 0 :
            for i in range(df.shape[1]) :
                offset_cell_d2 = offset_cell_d2.Offset (dir2[0], dir2[1])
                offset_cell_d2.Value = df_column_list[i]

        for i in range(df.shape[0]) :
            active_cell = active_cell.Offset (dir1[0], dir1[1])
            offset_cell = active_cell
            for j in range(df.shape[1]) :
                offset_cell = offset_cell.Offset (dir2[0], dir2[1])
                offset_cell.Value = str(df.iat[i,j])
                if type(color) == int :
                    offset_cell.Interior.ColorIndex = color

        if toggle2_state[0] == 1 :
            cell_autofit(wb)

    def cell_move1(self, vector, data, color) :
        active_cell = xl.ActiveCell
        offset_cell = active_cell.Offset (vector[0], vector[1])
        offset_cell.Value = data
        offset_cell.Interior.ColorIndex = color
        offset_cell.Activate()
    
    def cell_move2(self, vector, df) :
        active_cell = xl.ActiveCell
        offset_cell = active_cell.Offset(((vector[0]-1) * (df.shape[0] + 1)) + 1, ((vector[1]-1) * (df.shape[0] + 1)) + 1)
        offset_cell.Activate()
        
    def fun_btn(self):
        global mode_df
        try : 
            str(xl)
            # current_mode = mode_get()
            current_mode = mode_list[mode_short_list.index(self.input2.text())]
            
            mode_csv = pd.read_csv(csv_drive_url + current_mode + ".csv", \
                                header= None, \
                                encoding='CP949')
            normalize = mode_csv
            normalize = normalize.set_index(0)
            mode_df = normalize

            mode_df.columns = ["Function List"]
            self.data_read(mode_df, 34, 0)
            self.output_area.setText("[" + time.strftime("%X") + "] " + "Done")
        except :
            self.output_area.setText("[" + time.strftime("%X") + "] " + "연결된 Excel이 없습니다.")
            

    def request_btn(self):
        try :
            dir1, dir2 = self.dir_tester()
            # current_mode = mode_get()
            current_mode = mode_list[mode_short_list.index(self.input2.text())]

            method = api_method()

            active_cell = xl.ActiveCell
            selected_fun = mode_df.index[mode_df["Function List"] == str(active_cell)].tolist()[0]

            offset_cell = active_cell.Offset(dir2[0], dir2[1])
            key_tester = offset_cell.Value

            if method == "get" :
                if key_tester is None :
                    self.read_fun1(current_mode, method, selected_fun, dir1)
                else :
                    self.read_fun2(current_mode, method, selected_fun, offset_cell, dir2)
            elif method == "patch" :
                self.modify_fun(current_mode, method, selected_fun, active_cell, offset_cell, dir1, dir2)
            elif method == "post" :
                self.create_fun(current_mode, method, selected_fun, active_cell, offset_cell, dir1, dir2)
        
        except NameError :
            self.output_area.setText("[" + time.strftime("%X") + "] " + "The function list is not called.")
        
        except IndexError :
            self.output_area.setText("[" + time.strftime("%X") + "] " + "That funtion is not defined")
            


    def read_fun1(self, current_mode, method, selected_fun, dir1):
        run_code, temp_json = request_fun(current_mode, method, selected_fun, "", "", 0)
        self.output_area.setText("[" + time.strftime("%X") + "] " + run_code)

        json_keys1 = list(temp_json.keys())
        json_val1 = list(temp_json.values())
        for i in json_keys1 :
            self.cell_move1(dir1, i, 36)
            temp_df = pd.json_normalize(temp_json[i])
            # print(temp_df)
            # temp_df.to_csv(new_folder_path + i + ".csv")
            temp_df = df_column_selection(temp_df)
            if i == "json-body-format" :
                temp_df = temp_df.set_index("id")
                fun_csv_name = selected_fun.replace("/", "_")
                temp_df = csv2json_id([temp_df], fun_csv_name)
                self.data_read(temp_df, "", 1)            
            else :
                self.data_read(temp_df, "", 0)
            self.cell_move2(dir1, temp_df)
            
            temp_child_json = json_val1[json_keys1.index(i)]
            for j in temp_child_json :
                tester_key = list(j.keys())
                tester = list(j.values())
                if type(tester[0]) == list :
                    self.cell_move1(dir1, tester_key, 35)
                    temp_df = pd.json_normalize(j[tester_key[0]])
                    temp_df = df_column_selection(temp_df)
                    self.data_read(temp_df, "", 0)
                    self.cell_move2(dir1, temp_df)

    def read_fun2(self, current_mode, method, selected_fun, offset_cell, dir2):
        temp_key_list = []
        temp_df_list = []        
        if "library" in selected_fun :
            key_type = "librarykey="
        else :
            key_type = "entitykey="
        while offset_cell.Value is not None :
            uri_key = key_type + str(int(offset_cell.Value))
            offset_cell = offset_cell.Offset(dir2[0], dir2[1])
            temp_key_list.append(uri_key)
        for uri_key in temp_key_list :
            run_code, temp_json = request_fun(current_mode, method, selected_fun, uri_key, "", 0)
            temp_df = pd.json_normalize(temp_json["json-body-format"])
            temp_df = df_column_selection(temp_df)
            temp_df = temp_df.set_index("id")
            temp_df_list.append(temp_df)
            self.output_area.setText("[" + time.strftime("%X") + "] " + run_code)
        
        fun_csv_name = selected_fun.replace("/", "_")
        new_df = csv2json_id(temp_df_list, fun_csv_name)
        
        self.data_read(new_df, "", 1)

    def modify_fun(self, current_mode, method, selected_fun, active_cell, offset_cell, dir1, dir2):
        temp_key_list = []
        offset_cell = active_cell.Offset(dir2[0], dir2[1])
        while offset_cell.Value is not None :
            temp_key = offset_cell.Value
            offset_cell = offset_cell.Offset(dir2[0], dir2[1])
            temp_key_list.append(temp_key)

        temp_id_list = []
        offset_cell = active_cell.Offset(dir1[0], dir1[1])
        while offset_cell.Value is not None :
            temp_id = offset_cell.Value
            offset_cell = offset_cell.Offset(dir1[0], dir1[1])
            temp_id_list.append(temp_id)
            
        fun_csv_name = selected_fun.replace("/", "_")
        org_id_list, org_type_list = id_convert(fun_csv_name, temp_id_list)
        
        for i in temp_key_list :            
            if "library" in selected_fun :
                key_type = "librarykey="
            else :
                key_type = "entitykey="
            uri_key = key_type + str(int(i))
            
            active_cell = active_cell.Offset (dir2[0], dir2[1])
            offset_cell = active_cell
            
            temp_value_list = []
            for j in range(len(temp_id_list)) :
                offset_cell = offset_cell.Offset (dir1[0], dir1[1])
                temp_value = offset_cell.Value
                temp_value_list.append(temp_value)
            
            data_set_list = []
            for j in range(len(temp_id_list)) :
                str_value = str(temp_value_list[j])
                if org_type_list[j] == "string" :
                    result_value = "\"" + str_value + "\""

                elif org_type_list[j] == "select" :
                    result_value = "\"" + str_value + "\""

                elif org_type_list[j] == "scalar" :
                    result_value = str_value

                elif org_type_list[j] == "scalar array" :
                    result_value = str_value

                elif org_type_list[j] == "option" :
                    result_value = int(temp_value_list[j])

                elif org_type_list[j] == "boolean" :
                    if str_value == "True" :
                        result_value = True
                    else :
                        result_value = False
                data_set = "{" + "\"id\": \"" + str(org_id_list[j]) + "\"," + "\"value\": "+ str(result_value) + "}"
                data_set_list.append(data_set)
            body_json = ",".join(data_set_list)
            run_code, temp_json = request_fun(current_mode, method, selected_fun, uri_key, body_json, 1)
            self.output_area.setText("[" + time.strftime("%X") + "] " + run_code)

    def create_fun(self, current_mode, method, selected_fun, active_cell, offset_cell, dir1, dir2):
        temp_key_list = []
        offset_cell = active_cell.Offset(dir2[0], dir2[1])
        while offset_cell.Value is not None :
            temp_key = offset_cell.Value
            offset_cell = offset_cell.Offset(dir2[0], dir2[1])
            temp_key_list.append(temp_key)

        temp_id_list = []
        offset_cell = active_cell.Offset(dir1[0], dir1[1])
        while offset_cell.Value is not None :
            temp_id = offset_cell.Value
            offset_cell = offset_cell.Offset(dir1[0], dir1[1])
            temp_id_list.append(temp_id)
            
        fun_csv_name = selected_fun.replace("/", "_")
        org_id_list, org_type_list = id_convert(fun_csv_name, temp_id_list)
        
        uri_key = ""

        for i in temp_key_list :
            active_cell = active_cell.Offset (dir2[0], dir2[1])
            offset_cell = active_cell
            
            temp_value_list = []
            for j in range(len(temp_id_list)) :
                offset_cell = offset_cell.Offset (dir1[0], dir1[1])
                temp_value = offset_cell.Value
                temp_value_list.append(temp_value)
            
            data_set_list = []
            for j in range(len(temp_id_list)) :
                str_value = str(temp_value_list[j])
                if org_type_list[j] == "string" :
                    result_value = "\"" + str_value + "\""

                elif org_type_list[j] == "select" :
                    result_value = "\"" + str_value + "\""

                elif org_type_list[j] == "scalar" :
                    result_value = str_value

                elif org_type_list[j] == "scalar array" :
                    result_value = str_value

                elif org_type_list[j] == "option" :
                    result_value = int(temp_value_list[j])

                elif org_type_list[j] == "boolean" :
                    if str_value == "True" :
                        result_value = True
                    else :
                        result_value = False
                data_set = "{" + "\"id\": \"" + str(org_id_list[j]) + "\"," + "\"value\": "+ str(result_value) + "}"
                data_set_list.append(data_set)
            body_json = ",".join(data_set_list)
            run_code, temp_json = request_fun(current_mode, method, selected_fun, uri_key, body_json, 1)
            self.output_area.setText("[" + time.strftime("%X") + "] " + run_code)

    '''
    ----------------------------------------------------------------------------------------------------toggle / radio button의 정보 생성 및 활용 관련 함수
    '''
    def dir_tester(self) :
        if toggle1_state[0] == 1 :
            data_dir1 = (1, 2)
            data_dir2 = (2, 1)
        else :
            data_dir1 = (2, 1)
            data_dir2 = (1, 2)
        return data_dir1, data_dir2
    
    # depth_toggle_btn의 on sign : 1 / off : 0로 전달
    def toggle1(self) :
        if toggle1_state[0] == 0 :
            toggle1_state[0] = 1
        else :
            toggle1_state[0] = 0

    def toggle2(self) :
        if toggle2_state[0] == 0 :
            toggle2_state[0] = 1
        else :
            toggle2_state[0] = 0

    def request_type(self) :
        temp_sender = self.sender()
        selected_radio = temp_sender.text()
        if selected_radio == "Read" :
            radio1_state[0] = 0
        elif selected_radio == "Create" :
            radio1_state[0] = 1
        else :
            radio1_state[0] = 2
        
    def request_group_rad(self) :
        groupbox = QGroupBox('Request Type')

        radio1 = QRadioButton('Read')
        radio1.clicked.connect(self.request_type)
        radio2 = QRadioButton('Create')
        radio2.clicked.connect(self.request_type)
        radio3 = QRadioButton('Modify')
        radio3.clicked.connect(self.request_type)
        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        groupbox.setLayout(vbox)

        return groupbox


    '''
    ----------------------------------------------------------------------------------------------------ui 종료 이벤트 (엑셀 종료)
    '''
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        try :
            if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.pos() - self.offset)
            else:
                super().mouseMoveEvent(event)
        except :
            pass

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)
    
    def closeEvent(self, QCloseEvent):
        try :
            wb.Close()
            xl.Quit()
            os.remove("temp.xlsx")
        except :
            pass
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_ui = MyApp()
    main_ui.show()
    sys.exit(app.exec_())