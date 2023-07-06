import os
import sys

import urllib.request
import requests

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qtwidgets import AnimatedToggle

import cv2
import numpy as np
import csv

import math

import winreg

local_contents_path = r"C:\Temp\CIM_API_APP\\"

# reg에서 api key 받아오기
key = winreg.HKEY_CURRENT_USER
key_value = "SOFTWARE\MIDAS\midas CIM\APISetting"
api_connect_reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
api_key_value, api_key_type = winreg.QueryValueEx(api_connect_reg, "APIKey")

# reg의 key를 header 정보로 저장
header = {"MAPI-Key": api_key_value}


# 이미지 컨투어 생성기
def img_contours(image_gray, ex):
    # #외곽선
    edged = cv2.Canny(image_gray, 10, 250)

    # 폐합
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ex, ex))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    # 컨투어 찾기
    contours, _ = cv2.findContours(
        closed.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
    )
    return contours


def distance(point_set1, point_set2):
    line1 = [(point_set1[0][0], point_set1[0][1]), (point_set1[0][2], point_set1[0][3])]
    line2 = [(point_set2[0][0], point_set2[0][1]), (point_set2[0][2], point_set2[0][3])]
    dis2 = []
    for i in line1:
        dis1 = []
        for j in line2:
            dis1.append(math.sqrt(math.pow(i[0] - j[0], 2) + math.pow(i[1] - j[1], 2)))
        dis2.append(min(dis1))
    return dis2

def get_crosspt(point_set1, point_set2):
    xy = [
        point_set1[0][0],
        point_set1[0][1],
        point_set1[0][2],
        point_set1[0][3],
        point_set2[0][0],
        point_set2[0][1],
        point_set2[0][2],
        point_set2[0][3],
    ]
    if xy[2] == xy[0] or xy[6] == xy[4]:
        if xy[2] == xy[0]:
            cx = xy[2]
            m2 = (xy[7] - xy[5]) / (xy[6] - xy[4])
            cy = m2 * (cx - xy[4]) + xy[5]
            return cx, cy
        if xy[6] == xy[4]:
            cx = xy[6]
            m1 = (xy[3] - xy[1]) / (xy[2] - xy[0])
            cy = m1 * (cx - xy[0]) + xy[1]
            return cx, cy
    m1 = (xy[3] - xy[1]) / (xy[2] - xy[0])
    m2 = (xy[7] - xy[5]) / (xy[6] - xy[4])
    if m1 == m2:
        return None
    cx = (xy[0] * m1 - xy[1] - xy[4] * m2 + xy[5]) / (m1 - m2)
    cy = m1 * (cx - xy[0]) + xy[1]

    return int(cx), int(cy)


img_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/5_img2sec/source/icon/"
ok_img = "ok.png"
apply_img = "apply.png"
cancel_img = "cancel.png"
section_color_img = "section_color_v2.png"
origin_symbol_img = "origin_symbol.png"

selection_tool_wh = [340, 742]

red, pink, black, gray, white, purple, sky = (0,0,255), (200,11,214), (0,0,0), (100,100,100), (255,255,255), (169,46,169), (255,180,0)

section_vertex_list = []

style_type1 = '''
    QWidget{font-size: 9pt; background: rgb(20, 31, 45); color: rgb(255, 255, 255);}
    QPushButton{background: rgb(47, 59, 76); border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
    QPushButton:hover{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242);}
    QPushButton:pressed{background: rgb(11, 125, 182);}
    QPushButton:disabled{border-color: rgb(49, 61, 79); background: rgb(30, 40, 50); color: rgb(137, 144, 148);}
    QLineEdit{background: rgb(34, 44, 60); border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90); font-weight: bold;}
    QLineEdit:disabled{border-color: rgb(49, 61, 79); background: rgb(30, 40, 50); color: rgb(137, 144, 148);}
    QSlider::groove:horizontal {border: 0px solid; height: 4px; border-radius: 4px;}
    QSlider::handle:horizontal {background-color: rgb(148, 148, 254); border: 0px solid red; width: 16px; margin-top: -6px; margin-bottom: -6px; border-radius: 8px;}
    QSlider::handle:horizontal:pressed {background-color: rgb(36, 153, 242);}
    QSlider::add-page:horizontal {background: rgb(183, 183, 183);}
    QSlider::sub-page:horizontal {background: rgb(80, 80, 232);}
    QSlider::handle:disabled{background: rgb(60, 80, 100);}
    QSlider::add-page:disabled {background: rgb(130, 130, 130);}
    QSlider::sub-page:disabled {background: rgb(90, 90, 90);}
    '''

style_type2 = '''
    QWidget{font-size: 9pt; background: rgb(35, 40, 50); color: rgb(255, 255, 255);}
    QLabel{font-size: 13pt; height: 140px; background: rgb(35, 40, 50);}
    QLineEdit{background: rgb(34, 44, 60); border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90); color: rgb(255, 255, 255);}
    QLineEdit:disabled{border-color: rgb(49, 61, 79); background: rgb(30, 40, 50); color: rgb(137, 144, 148);}
    QLineEdit:focus{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242); background: rgb(41, 48, 61);}
    '''


class Image2Section(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.img_list = [0, 0]
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.win_cen()
        self.setFixedSize(selection_tool_wh[0], selection_tool_wh[1] - 208)

        # 전체 위젯 / 전체 레이아웃
        void_widget = self.qwidget_create("background: rgb(12, 20, 31);")

        # header layout
        header_widget = self.qwidget_create(style_type2)
        header_lable = self.qlabel_create("img2section")
        header_lable.setFixedHeight(24)
        header_lable.setFont(QFont("Noto Sans CJK KR Bold", 1))
        header_lable.setAlignment(Qt.AlignCenter)
        self.qlayout_create(0, header_widget, [header_lable], None)

        # 1 layout (input_ui)
        input_ui_widget = self.qwidget_create(style_type1)
        civil_img_label = self.qlabel_create("img File Path")
        self.img_path = self.qlineedit_create("Drop the image file below", None, None, None)
        self.img_path.setFixedSize(220, 30)
        self.img_path.setDisabled(True)
        input_sub_layout0 = self.qlayout_create(
            0, None, [civil_img_label, self.img_path], (0, 0, 0, 0)
        )

        self.img_get = QLabel()
        self.img_get.setAcceptDrops(True)
        self.img_get.installEventFilter(self)
        self.img_get.setStyleSheet(style_type2)

        section_color_icon = self.qicon_create(section_color_img)
        self.section_color_btn = self.qbtn_create(section_color_icon, 28, self.img_matching)
        self.section_color_btn.setFixedSize(314, 28)
        self.section_color_btn.setText(" Color Selection")

        toggle_widget = self.qwidget_create(style_type1)
        toggle_widget.setFixedHeight(64)
        reflection_label = self.qlabel_create("Real Time Reflection")
        reflection_label.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.reflection_toggle = AnimatedToggle(checked_color="#1A84D5", pulse_checked_color="#44FFB000")
        self.reflection_toggle.setFixedSize(52, 36)
        self.reflection_toggle.setChecked(True)
        reflection_layout = self.qlayout_create(
            0, None, [reflection_label, self.reflection_toggle], (0, 0, 0, 0)
        )
        detail_label = self.qlabel_create("Detail Option")
        detail_label.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.detail_toggle = AnimatedToggle(checked_color="#1A84D5", pulse_checked_color="#44FFB000")
        self.detail_toggle.setFixedSize(52, 36)
        self.detail_toggle.toggled.connect(self.detail_toggle_fun)
        detail_layout = self.qlayout_create(
            0, None, [detail_label, self.detail_toggle], (0, 0, 0, 0)
        )
        self.qlayout_create(1, toggle_widget, [reflection_layout, detail_layout], (0, 0, 0, 0))

        self.qlayout_create(
            1,
            input_ui_widget,
            [input_sub_layout0, self.img_get, self.section_color_btn, toggle_widget],
            (10, 6, 10, 6),
        )
        self.section_color_btn.setDisabled(True)

        # 2 layout (slider_widget)
        self.slider_widget = self.qwidget_create(style_type1)
        # color
        hsv_label = self.qlabel_create("color")
        self.hsv_slider = self.qslider_create(1, 90, 1, self.hsv_fun)
        hsv_layout = self.qlayout_create(
            0, None, [hsv_label, self.hsv_slider], (0, 0, 0, 0)
        )
        # fill
        fill_label = self.qlabel_create("fill")
        self.fill_slider = self.qslider_create(0, 10, 10, self.fill_fun)
        fill_layout = self.qlayout_create(
            0, None, [fill_label, self.fill_slider], (0, 0, 0, 0)
        )
        # outline
        outline_label = self.qlabel_create("outline")
        self.outline_slider = self.qslider_create(0, 10, 6, self.outline_fun)
        outline_layout = self.qlayout_create(
            0, None, [outline_label, self.outline_slider], (0, 0, 0, 0)
        )
        # approx
        approx_label = self.qlabel_create("approx")
        self.approx_slider = self.qslider_create(0, 5, 0, self.approx_fun)
        approx_layout = self.qlayout_create(
            0, None, [approx_label, self.approx_slider], (0, 0, 0, 0)
        )
        # rho
        rho_label = self.qlabel_create("rho")
        self.rho_slider = self.qslider_create(1, 100, 25, self.rho_fun)
        rho_layout = self.qlayout_create(
            0, None, [rho_label, self.rho_slider], (0, 0, 0, 0)
        )
        # threshold
        threshold_label = self.qlabel_create("threshold")
        self.threshold_slider = self.qslider_create(10, 50, 10, self.threshold_fun)
        threshold_layout = self.qlayout_create(
            0, None, [threshold_label, self.threshold_slider], (0, 0, 0, 0)
        )
        # grid
        grid_label = self.qlabel_create("grid")
        self.grid_slider = self.qslider_create(0, 8, 1, self.grid_fun)
        grid_layout = self.qlayout_create(
            0, None, [grid_label, self.grid_slider], (0, 0, 0, 0)
        )

        self.hsv_slider.setDisabled(True)
        self.fill_slider.setDisabled(True)
        self.outline_slider.setDisabled(True)
        self.approx_slider.setDisabled(True)
        self.rho_slider.setDisabled(True)
        self.threshold_slider.setDisabled(True)
        self.grid_slider.setDisabled(True)
        self.slider_widget.setHidden(True)
        self.qlayout_create(
            1,
            self.slider_widget,
            [
                hsv_layout,
                fill_layout,
                outline_layout,
                approx_layout,
                rho_layout,
                threshold_layout,
                grid_layout,
            ],
            (10, 6, 10, 6),
        )

        # 3 layout (section_convert)
        dimension_widget = self.qwidget_create(style_type1)
        dimension_label = self.qlabel_create("Dimension")
        self.dimension_input = self.qlineedit_create("", 0, "mm", 0)
        self.dimension_input.setFixedSize(220, 30)
        self.dimension_input.textChanged.connect(self.dimension_enter)
        section_sub_layout0 = self.qlayout_create(0, None, [dimension_label, self.dimension_input], (0, 0, 0, 0))
        round_label = self.qlabel_create("Rounding Value")
        self.round_input = self.qlineedit_create("", 0, "mm (only positive integer)", 0)
        self.round_input.setFixedSize(220, 30)
        section_sub_layout1 = self.qlayout_create(0, None, [round_label, self.round_input], (0, 0, 0, 0))
        self.dimension_input.setDisabled(True)
        self.round_input.setDisabled(True)
        self.qlayout_create(
            1,
            dimension_widget,
            [section_sub_layout0, section_sub_layout1],
            (10, 6, 10, 6),
        )

        # 4 layout (default)
        default_widget = self.qwidget_create(style_type1)
        ok_img_icon = self.qicon_create(ok_img)
        ok_btn = self.qbtn_create(ok_img_icon, 28, self.ok_fun)
        ok_btn.setShortcut(Qt.SHIFT + Qt.Key_Space)
        apply_img_icon = self.qicon_create(apply_img)
        apply_btn = self.qbtn_create(apply_img_icon, 28, self.apply_fun)
        apply_btn.setShortcut(Qt.CTRL + Qt.Key_Space)
        cancel_icon = self.qicon_create(cancel_img)
        cancel_btn = self.qbtn_create(cancel_icon, 28, self.close_act)
        cancel_btn.setShortcut(Qt.SHIFT + Qt.Key_Escape)
        self.qlayout_create(
            0,
            default_widget,
            [1, ok_btn, apply_btn, cancel_btn],
            (10, 6, 10, 6),
        )

        # main_layout
        main_layout = self.qlayout_create(
            1,
            void_widget,
            [header_widget, input_ui_widget, self.slider_widget, dimension_widget, default_widget],
            (2, 2, 2, 2),
        )
        main_layout.setStretchFactor(input_ui_widget, 1)
        self.setCentralWidget(void_widget)

        self.show()

    def win_cen(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def qwidget_create(self, style):
        temp_widget = QWidget()
        temp_widget.setStyleSheet(style)
        return temp_widget

    def qlayout_create(self, dir, target_widget, sub_widget_list, margin):
        if dir == 0:
            temp_layout = QHBoxLayout(target_widget)
        else:
            temp_layout = QVBoxLayout(target_widget)
        for i in sub_widget_list:
            if type(i) == int:
                temp_layout.addStretch(i)
            elif type(i) == QtWidgets.QHBoxLayout or type(i) == QtWidgets.QVBoxLayout:
                temp_layout.addLayout(i)
            else:
                temp_layout.addWidget(i)
        if margin is not None:
            m1, m2, m3, m4 = margin
            temp_layout.setContentsMargins(m1, m2, m3, m4)
        return temp_layout

    def qpixmap_create(self, img_file_name):
        temp_pixmap = QPixmap()
        temp_img_path = img_drive_url + img_file_name
        temp_img = urllib.request.urlopen(temp_img_path).read()
        temp_pixmap.loadFromData(temp_img)
        return temp_pixmap

    def qicon_create(self, img_file_name):
        temp_pixmap = self.qpixmap_create(img_file_name)
        temp_icon = QIcon()
        temp_icon.addPixmap(temp_pixmap)
        return temp_icon

    def qbtn_create(self, icon, size, function):
        temp_btn = QPushButton()
        temp_btn.setFixedSize(size, size)
        temp_btn.setIcon(icon)
        temp_btn.clicked.connect(function)
        return temp_btn

    def qlabel_create(self, inner):
        temp_lable = QLabel()
        if type(inner) == str:
            temp_lable.setText(inner)
        else:
            temp_lable.setPixmap(inner)
        return temp_lable

    def qlineedit_create(self, default_text, value_type, phtext, align_type):
        temp_lineedit = QLineEdit(default_text, self)
        if value_type is not None:
            if value_type == 0:
                temp_lineedit.setValidator(QIntValidator(self))
            elif value_type == 1:
                temp_lineedit.setValidator(QDoubleValidator(self))
        if phtext is not None:
            temp_lineedit.setPlaceholderText(phtext)
        if align_type is not None:
            if align_type == 0:
                temp_lineedit.setAlignment(Qt.AlignCenter)
            elif align_type == 1:
                temp_lineedit.setAlignment(Qt.AlignRight)
        return temp_lineedit

    def qslider_create(self, min, max, default, funtion):
        temp_slider = QSlider(Qt.Horizontal)
        temp_slider.setStyleSheet(style_type1)
        temp_slider.setFixedWidth(240)
        temp_slider.setRange(min, max)
        temp_slider.setValue(default)
        temp_slider.valueChanged[int].connect(funtion)
        return temp_slider

    def eventFilter(self, object, event):
        try:
            if object is self.img_get:
                if event.type() == QEvent.DragEnter:
                    if event.mimeData().hasUrls():
                        event.accept()
                    else:
                        event.ignore()
                if event.type() == QEvent.Drop:
                    drop_files = [u.toLocalFile() for u in event.mimeData().urls()]
                    if len(drop_files) != 1:
                        self.img_path.setStyleSheet("color: red;")
                        self.img_path.setText("Only 1 img files are required")
                        object.clear()
                    elif drop_files[0][-3:] != "png":
                        self.img_path.setStyleSheet("color: red;")
                        self.img_path.setText("Invalid file extension")
                        object.clear()
                    else:
                        self.img_path.setStyleSheet(style_type1)
                        self.img_path.setText(drop_files[0])
                        temp_img_array = np.fromfile(drop_files[0], np.uint8)
                        temp_img = cv2.imdecode(temp_img_array, cv2.IMREAD_COLOR)
                        h, w, c = temp_img.shape
                        qImg = QImage(temp_img.data, w, h, w * c, QImage.Format_RGB888)
                        pixmap = QPixmap.fromImage(qImg)
                        object.setPixmap(
                            pixmap.scaled(
                                object.width(), object.height(), Qt.KeepAspectRatio
                            )
                        )
                        object.setAlignment(Qt.AlignCenter)
                        self.section_color_btn.setDisabled(False)
            return False
        except:
            return False

    def pt2int(self, point):
        px = int(point[0])
        py = int(point[1])
        return px, py

    def org_symbol_draw(self, userpoint):
        org_x, org_y = self.pt2int(userpoint)
        background = user_img.copy()
        blending = user_img.copy()
        cv2.rectangle(background, (org_x-30, org_y-30), (org_x+30, org_y+30), gray, 1)
        cv2.line(background, (org_x-35, org_y), (org_x+35, org_y), gray, 1)
        cv2.line(background, (org_x, org_y-35), (org_x, org_y+35), gray, 1)
        cv2.rectangle(blending, (org_x-30, org_y-30), (org_x+30, org_y+30), gray, -1)
        cv2.addWeighted(blending, 0.4, background, 1 - .4, 0, background)
        return background

    def center_align_text(self, img, img2, point_set1, point_set2, usertext, color, roi_bool):
        font = cv2.FONT_ITALIC
        textsize = cv2.getTextSize(usertext, font, 0.6, 2)[0]
        textX = (point_set1[0] + point_set2[0] - textsize[0]) // 2
        textY = (point_set1[1] + point_set2[1] + textsize[1]) // 2
        if roi_bool == 1:
            x,y,w,h = textX-5, textY-textsize[1]-5, textsize[0]+10, textsize[1]+10
            roi = img2[y:y+h, x:x+w]
            img[y:y+h, x:x+w] = roi
        cv2.putText(img, usertext, (textX, textY), font, 0.6, color, 2)

    def all_point_draw(self, target_img, point_list, color):
        for i in point_list:
            p1, p2 = self.pt2int(i)
            cv2.circle(target_img, (p1, p2), 4, color, 2)

    def img_object_create(self):
        global user_img, img_size_over
        path_list = self.img_path.text()
        temp_img_array = np.fromfile(path_list, np.uint8)
        user_img = cv2.imdecode(temp_img_array, cv2.IMREAD_COLOR)
        imgperdt_ratio = 1.0
        temp_img_size = user_img.shape
        dt_size = (QDesktopWidget().availableGeometry().bottomRight().x()+1, QDesktopWidget().availableGeometry().bottomRight().y()+1)
        img_size_over = temp_img_size[1] < dt_size[0]*imgperdt_ratio and temp_img_size[0] < dt_size[1]*imgperdt_ratio

        if not img_size_over:
            resize_coefficient = max([temp_img_size[1] / dt_size[0], temp_img_size[0] / dt_size[1]])
            user_img = cv2.resize(user_img, (0, 0), fx=imgperdt_ratio / resize_coefficient, fy=imgperdt_ratio / resize_coefficient, interpolation=cv2.INTER_LANCZOS4)

    def img_matching(self):
        def get_hsv_in_image(event, x, y, flags, param):
            global hsv
            if event == cv2.EVENT_RBUTTONUP:
                run_sig[0] = 1
                value = param["image"][y, x, :]
                value2 = np.uint8([[value]])
                hsv = cv2.cvtColor(value2, cv2.COLOR_BGR2HSV)
                hsv = hsv[0][0]
                self.hsv_slider.setValue(13)
                self.hsv_fun(self.hsv_slider.value())
                self.hsv_slider.setDisabled(False)
                self.fill_slider.setDisabled(False)
                self.outline_slider.setDisabled(False)
                self.approx_slider.setDisabled(False)
                self.rho_slider.setDisabled(False)
                self.threshold_slider.setDisabled(False)
                self.grid_slider.setDisabled(False)
            return

        run_sig = [0]
        self.dimension_input.setDisabled(True)
        self.round_input.setDisabled(True)
        self.img_object_create()
        section_vertex_list.clear()
        step1_img = user_img.copy()
        param = {"image": step1_img}
        cv2.imshow("Find the vertex", step1_img)
        cv2.moveWindow("Find the vertex", (self.pos().x() + selection_tool_wh[0])*int(img_size_over), self.pos().y()*int(img_size_over))
        cv2.setMouseCallback("Find the vertex", get_hsv_in_image, param)
        while(True):
            if cv2.waitKey(0) == ord("n"):
                break
            elif cv2.waitKey(0) == 27:
                run_sig[0] = 0
                break
        cv2.destroyAllWindows()
        if run_sig[0] == 1:
            self.loop_define()

    def loop_define(self):
        def vertex_define(event, x, y, flags, param):
            global isDragging, x0, y0
            if event == cv2.EVENT_LBUTTONDOWN:
                x0 = x
                y0 = y
                if flags & cv2.EVENT_FLAG_SHIFTKEY:
                    self.all_point_draw(temp_background, [(x,y)], red)
                    param["point_list"].append((x,y))
                    used_vertex_list.append((x,y))
                    cv2.imshow("Select points for loop" + param["loop_num"], temp_background)
                elif flags & cv2.EVENT_FLAG_ALTKEY:
                    isDragging = True
                else:
                    isDragging = True

            elif event == cv2.EVENT_LBUTTONUP:
                isDragging = False
                if flags & cv2.EVENT_FLAG_SHIFTKEY:
                    pass
                elif flags & cv2.EVENT_FLAG_ALTKEY:
                    try:
                        for i in param["point_list"]:
                            if (x0 <= i[0] <= x or x <= i[0] <= x0) and (y0 <= i[1] <= y or y <= i[1] <= y0):
                                self.all_point_draw(temp_background, [i], sky)
                                if i in used_vertex_list:
                                    used_vertex_list.remove(i)
                    except:
                        pass
                else:
                    try:
                        for i in param["point_list"]:
                            if (x0 <= i[0] <= x or x <= i[0] <= x0) and (y0 <= i[1] <= y or y <= i[1] <= y0):
                                self.all_point_draw(temp_background, [i], red)
                                if i not in used_vertex_list:
                                    used_vertex_list.append(i)
                    except:
                        pass
                cv2.imshow("Select points for loop" + param["loop_num"], temp_background)
                    
            elif event == cv2.EVENT_MOUSEMOVE:
                if flags & cv2.EVENT_FLAG_SHIFTKEY:
                    try:
                        isDragging = False
                        temp_roi = user_img.copy()
                        img_draw = temp_background.copy()
                        w, h = 30, 30
                        nx, ny = int(x-w/2), int(y-h/2)
                        roi = temp_roi[ny:ny+h, nx:nx+w]
                        roi = cv2.pyrUp(roi, dstsize=(w*2, h*2), borderType=cv2.BORDER_DEFAULT)
                        cv2.rectangle(roi, (0, 0), (2*w-1, 2*h-1), red, 2)
                        location_y1 = y-h
                        location_y2 = y-h+2*h
                        location_x1 = x-w
                        location_x2 = x-w+2*w
                        img_draw[location_y1:location_y2, location_x1:location_x2] = roi
                        cv2.imshow("Select points for loop" + param["loop_num"], img_draw)
                    except:
                        pass
                else:
                    try:
                        if isDragging:
                            img_draw = temp_background.copy()
                            temp_blending = temp_background.copy()
                            cv2.rectangle(img_draw, (x0, y0), (x, y), purple, 1)
                            cv2.rectangle(temp_blending, (x0, y0), (x, y), purple, -1)
                            cv2.addWeighted(temp_blending, 0.4, img_draw, 1 - .4, 0, img_draw)
                            cv2.imshow("Select points for loop" + param["loop_num"], img_draw)
                        else:
                            cv2.imshow("Select points for loop" + param["loop_num"], temp_background) 
                    except:
                        pass
            
            return
        
        for i in cp_group_list:
            used_vertex_list = []
            temp_background = user_img.copy()
            self.all_point_draw(temp_background, i, sky)
            loop_num = str(cp_group_list.index(i) + 1)
            param = {"point_list": i, "loop_num": loop_num}
            cv2.imshow("Select points for loop" + loop_num, temp_background)
            cv2.moveWindow("Select points for loop" + loop_num, (self.pos().x() + selection_tool_wh[0])*int(img_size_over), self.pos().y()*int(img_size_over))
            cv2.setMouseCallback("Select points for loop" + loop_num, vertex_define, param)
            while(True):
                if cv2.waitKey(0) == ord("n"):
                    break
                elif cv2.waitKey(0) == 27:
                    break
            
            if used_vertex_list:
                jx = [j[0] for j in used_vertex_list]
                jy = [j[1] for j in used_vertex_list]
                for j in range(len(jx)):
                    for k in range(len(jx)):
                        if abs(jx[j] - jx[k]) < 5:
                            jx[k] = int(jx[j])
                        if abs(jy[j] - jy[k]) < 5:
                            jy[k] = int(jy[j])
                for j in range(len(jx)):
                    used_vertex_list[j] = (jx[j], jy[j])

                vertex_match = []
                for j in used_vertex_list:
                    temp_tester = 0
                    close_distance = []
                    for k in valid_contour_list[cp_group_list.index(i)]:
                        pt_dist = math.sqrt(math.pow(j[0] - k[0][0], 2) + math.pow(j[1] - k[0][1], 2))
                        close_distance.append(pt_dist)
                    for k in vertex_match:
                        if abs(k[1] - close_distance.index(min(close_distance))) < 5:
                            temp_tester = 1
                    if temp_tester == 0:
                            vertex_match.append((j, close_distance.index(min(close_distance))))
                    # print(min(close_distance))
                vertex_match.sort(key=lambda x: x[1])
                if math.sqrt(math.pow(vertex_match[0][0][0] - vertex_match[-1][0][0], 2) + math.pow(vertex_match[0][0][1] - vertex_match[-1][0][1], 2)) < 5:
                    vertex_match.pop(-1)
                sorted_vertex = [j[0] for j in vertex_match]
                for j in sorted_vertex:
                    self.center_align_text(temp_background, temp_background, self.pt2int((j[0], j[1]-20)), self.pt2int((j[0], j[1]-20)), str(sorted_vertex.index(j)), red, 0)
                cv2.imshow("Select points for loop" + loop_num, temp_background)
                while(True):
                    if cv2.waitKey(0) == ord("n"):
                        break
                    elif cv2.waitKey(0) == 27:
                        sorted_vertex.clear()
                        break
                cv2.destroyAllWindows()
                if sorted_vertex:
                    section_vertex_list.append(sorted_vertex)
            cv2.destroyAllWindows()
        if section_vertex_list:
            self.origin_define()

    def origin_define(self):
        def origin_selection(event, x, y, flags, param):
            global origin_point
            if event == cv2.EVENT_LBUTTONDOWN:
                run_sig[0] = 1
                close_distance = []
                for i in all_vertex:
                    pt_dist = math.sqrt(math.pow(i[0] - x, 2) + math.pow(i[1] - y, 2))
                    close_distance.append(pt_dist)
                temp_cp = all_vertex[close_distance.index(min(close_distance))]
                if flags & cv2.EVENT_FLAG_CTRLKEY:
                    if temp_cp not in temp_origins:
                        temp_origins.append(temp_cp)
                    nx = sum([i[0] for i in temp_origins]) / len(temp_origins)
                    ny = sum([i[1] for i in temp_origins]) / len(temp_origins)
                    origin_point = self.pt2int((nx, ny))
                elif flags & cv2.EVENT_FLAG_ALTKEY:
                    if temp_cp in temp_origins:
                        temp_origins.remove(temp_cp)
                    nx = sum([i[0] for i in temp_origins]) / len(temp_origins)
                    ny = sum([i[1] for i in temp_origins]) / len(temp_origins)
                    origin_point = self.pt2int((nx, ny))
                else:
                    temp_origins.clear()
                    origin_point = temp_cp
                                    
                temp_background = self.org_symbol_draw(origin_point)
                self.all_point_draw(temp_background, all_vertex, sky)
                self.all_point_draw(temp_background, temp_origins, red)
                self.all_point_draw(temp_background, [origin_point], red)
                self.center_align_text(temp_background, user_img, self.pt2int((origin_point[0], origin_point[1]-20)), self.pt2int((origin_point[0], origin_point[1]-20)), "Origin", red, 0)
                cv2.imshow("Define the origin", temp_background)
            return
        run_sig = [0]
        all_vertex = sum(section_vertex_list, [])
        temp_background = user_img.copy()
        self.all_point_draw(temp_background, all_vertex, sky)
        temp_origins = []
        cv2.imshow("Define the origin", temp_background)
        cv2.moveWindow("Define the origin", (self.pos().x() + selection_tool_wh[0])*int(img_size_over), self.pos().y()*int(img_size_over))
        cv2.setMouseCallback("Define the origin", origin_selection)
        while(True):
            if cv2.waitKey(0) == ord("n"):
                break
            elif cv2.waitKey(0) == 27:
                run_sig[0] = 0
                break
        cv2.destroyAllWindows()
        if run_sig[0] == 1:
            self.convert_length_define()
    
    def convert_length_define(self):
        def ref_point_selection(event, x, y, flags, param):
            global selected_point, overlay_img0, overlay_img1, dim_p1, dim_p2
            if event == cv2.EVENT_LBUTTONDOWN:
                temp_background = param["image"].copy()
                self.all_point_draw(temp_background, all_vertex, sky)
                if len(ref_point_list) == 2:
                    ref_point_list.clear()
                    self.dimension_input.setDisabled(True)
                    self.round_input.setDisabled(True)
                close_distance = []
                for i in all_vertex:
                    pt_dist = math.sqrt(math.pow(i[0] - x, 2) + math.pow(i[1] - y, 2))
                    close_distance.append(pt_dist)
                selected_point = all_vertex[close_distance.index(min(close_distance))]
                ref_point_list.append(selected_point)
                for i in ref_point_list:
                    self.all_point_draw(temp_background, [i], red)
                if len(ref_point_list) == 2:
                    p1x = ref_point_list[0][0]
                    p1y = ref_point_list[0][1]
                    p2x = ref_point_list[1][0]
                    p2y = ref_point_list[1][1]
                    rad = ((180 - (math.atan2(p2x - p1x, p2y - p1y)*180)/math.pi)*math.pi)/180
                    length = 30
                    x_dis = length * math.cos(rad)
                    y_dis = length * math.sin(rad)
                    p1 = self.pt2int((p1x, p1y))
                    p2 = self.pt2int((p2x, p2y))
                    dim_p1 = self.pt2int((p1x-x_dis, p1y-y_dis))
                    dim_p2 = self.pt2int((p2x-x_dis, p2y-y_dis))
                    
                    cv2.circle(temp_background, dim_p1, 3, red, -1)
                    cv2.circle(temp_background, dim_p2, 3, red, -1)
                    cv2.line(temp_background, p1, dim_p1, red, 1)
                    cv2.line(temp_background, dim_p2, p2, red, 1)
                    overlay_img0 = temp_background.copy()
                    cv2.line(temp_background, dim_p1, dim_p2, red, 1)
                    overlay_img1 = temp_background.copy()
                    if self.dimension_input.text() == "":
                        self.center_align_text(temp_background, overlay_img0, dim_p1, dim_p2, "Dimension", red, 1)
                    else:
                        self.center_align_text(temp_background, overlay_img0, dim_p1, dim_p2, self.dimension_input.text(), red, 1)
                    self.dimension_input.setDisabled(False)
                    self.round_input.setDisabled(False)
                    self.activateWindow()
                    self.dimension_input.setFocus(True)
                cv2.imshow("Define the reference points", temp_background)
            return
        global ref_point_list
        ref_point_list = []
        all_vertex = sum(section_vertex_list, [])
        temp_background = self.org_symbol_draw(origin_point)
        self.all_point_draw(temp_background, all_vertex, sky)
        param = {"image": temp_background}
        cv2.imshow("Define the reference points", temp_background)
        cv2.moveWindow("Define the reference points", (self.pos().x() + selection_tool_wh[0])*int(img_size_over), self.pos().y()*int(img_size_over))
        cv2.setMouseCallback("Define the reference points", ref_point_selection, param)
        while(True):
            if cv2.waitKey(0) == 27:
                break
        cv2.destroyAllWindows()
        self.dimension_input.setDisabled(True)
        self.round_input.setDisabled(True)

    def hsv_fun(self, value):
        global img_result
        temp_background = user_img.copy()
        th = 2 * value
        lower_col = np.array([hsv[0] - th, hsv[1] - th, hsv[2] - th])
        upper_col = np.array([hsv[0] + th, hsv[1] + th, hsv[2] + th])
        img_hsv = cv2.cvtColor(temp_background, cv2.COLOR_BGR2HSV)
        img_mask = cv2.inRange(img_hsv, lower_col, upper_col)
        img_result = cv2.bitwise_and(temp_background, temp_background, mask=img_mask)
        cv2.imshow("Find the vertex", img_result)
        if self.reflection_toggle.isChecked():
            self.fill_fun(self.fill_slider.value())

    def fill_fun(self, value):
        self.vertex_finder()
        
    def outline_fun(self, value):
        self.vertex_finder()

    def vertex_finder(self):
        global img_mask
        temp_gray = cv2.cvtColor(img_result, cv2.COLOR_BGR2GRAY)
        ret, temp_img = cv2.threshold(temp_gray, 15, 255, cv2.THRESH_BINARY)
        temp_kernel = np.ones((3, 3), np.uint8)
        temp_mask = cv2.morphologyEx(temp_img, cv2.MORPH_OPEN, temp_kernel)

        reverse_img = 255 - temp_mask
        ks = 1 + 2 * self.fill_slider.value()
        kernel = np.ones((ks, ks), np.uint8)
        img_mask = cv2.morphologyEx(reverse_img, cv2.MORPH_OPEN, kernel)
        temp_contour = img_contours(img_mask, 3)
        if self.outline_slider.value()-5 == 0:
            pass
        elif self.outline_slider.value()-5 < 0:
            cv2.drawContours(img_mask, temp_contour, -1, white, 5-(self.outline_slider.value()))
        else:
            cv2.drawContours(img_mask, temp_contour, -1, black, self.outline_slider.value()-5)
        cv2.imshow("Find the vertex", img_mask)
        if self.reflection_toggle.isChecked():
            self.approx_fun(self.approx_slider.value())

    def approx_fun(self, value):
        global valid_contour_img_list, valid_contour_list
        background_show = np.zeros(user_img.shape, np.uint8)
        valid_contour_list = []
        valid_contour_img_list = []
        contours = img_contours(img_mask, 3)
        for i in contours:
            temp_length = cv2.arcLength(i, closed=True)
            if temp_length > 200:
                if len(valid_contour_list) > 0:
                    same_contour = False
                    for j in valid_contour_list:
                        contr = j[0]
                        match = cv2.matchShapes(i, contr, cv2.CONTOURS_MATCH_I2, 0.0)
                        if match < 5e-02:
                            if abs(tuple(i[i[:,:,0].argmin()][0])[0] - tuple(contr[contr[:,:,0].argmin()][0])[0]) < 5 and abs(tuple(i[i[:,:,1].argmin()][0])[1] - tuple(contr[contr[:,:,1].argmin()][0])[1]) < 5:
                                same_contour = True
                                break
                    if same_contour == False:
                        valid_contour_list.append((i, temp_length))
                else:
                    valid_contour_list.append((i, temp_length))
        valid_contour_list.sort(key=lambda x: x[1], reverse=True)
        valid_contour_list = [j[0] for j in valid_contour_list]

        for i in valid_contour_list:
            temp_background = np.zeros(user_img.shape, np.uint8)
            epsilon = value / 5000 * cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, epsilon, True)
            cv2.drawContours(background_show, [approx], -1, (0, 255, 0), 1)
            cv2.drawContours(temp_background, [approx], -1, (0, 255, 0), 1)
            valid_contour_img_list.append(temp_background)
        cv2.imshow("Find the vertex", background_show)
        if self.reflection_toggle.isChecked():
            self.rho_fun(self.approx_slider.value())

    def rho_fun(self, value):
        self.cross_point_draw()

    def threshold_fun(self, value):
        self.cross_point_draw()

    def grid_fun(self, value):
        self.cross_point_draw()

    def cross_point_draw(self):
        global cp_group_list
        cp_group_list = []
        background2 = user_img.copy()
        for i in valid_contour_img_list:
            img_temp = cv2.cvtColor(i, cv2.COLOR_RGB2GRAY)
            lines = cv2.HoughLinesP(
                img_temp,
                (50 + self.rho_slider.value()) / 150,
                np.pi / 180,
                self.threshold_slider.value(),
                minLineLength=5,
                maxLineGap=50,
            )
            cp_list = []
            for i in lines:
                cv2.line(
                    background2,
                    self.pt2int((i[0][0], i[0][1])),
                    self.pt2int((i[0][2], i[0][3])),
                    red,
                    1,
                )
                vec1 = np.array([int(i[0][0]) - int(i[0][2]), int(i[0][1]) - int(i[0][3])])
                cross_lines = []
                p1_dis_list = []
                p2_dis_list = []
                for j in lines:
                    vec2 = np.array(
                        [int(j[0][0]) - int(j[0][2]), int(j[0][1]) - int(j[0][3])]
                    )
                    radian = np.arccos(
                        np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    )
                    theta = radian * 180 / np.pi
                    theta = np.fmin(theta, 180.0 - theta)
                    if theta > 1:
                        cross_lines.append(j)
                for j in cross_lines:
                    temp_dis = distance(i, j)
                    p1_min = temp_dis[0]
                    p2_min = temp_dis[1]
                    p1_dis_list.append(p1_min)
                    p2_dis_list.append(p2_min)
                result_line1 = cross_lines[p1_dis_list.index(min(p1_dis_list))]
                result_line2 = cross_lines[p2_dis_list.index(min(p2_dis_list))]

                cross_point1 = get_crosspt(i, result_line1)
                cross_point2 = get_crosspt(i, result_line2)
                cp_list.append(cross_point1)
                cp_list.append(cross_point2)

            round_value = 1 + 10 * self.grid_slider.value()
            round_cp_list = [
                (
                    round_value * round(i[0] / round_value),
                    round_value * round(i[1] / round_value),
                )
                for i in cp_list
            ]
            result_cp = []
            for i in list(set(round_cp_list)):
                result_cp.append(cp_list[round_cp_list.index(i)])

            self.all_point_draw(background2, result_cp, red)
            cp_group_list.append(result_cp)
        cv2.imshow("Find the vertex", background2)

    def detail_toggle_fun(self):
        if self.detail_toggle.isChecked():
            self.slider_widget.setVisible(True)
            self.setFixedSize(selection_tool_wh[0], selection_tool_wh[1])
        else:
            self.slider_widget.setHidden(True)
            self.setFixedSize(selection_tool_wh[0], selection_tool_wh[1] - 208)

    def dimension_enter(self):
        self.center_align_text(overlay_img1, overlay_img0, dim_p1, dim_p2, self.dimension_input.text(), red, 1)
        cv2.imshow("Define the reference points", overlay_img1)

    def apply_fun(self):
        try:
            def coo_convert(x, y):
                units_conversion = 1/1000
                round_value = int(self.round_input.text())
                return (round_value * round((x-origin_point[0])*convert_coefficient/round_value)*units_conversion, (round_value * round((y-origin_point[1])*convert_coefficient/round_value))*units_conversion*-1)
            img_dist = math.sqrt(math.pow(ref_point_list[0][0] - ref_point_list[1][0], 2) + math.pow(ref_point_list[0][1] - ref_point_list[1][1], 2))
            convert_coefficient = int(self.dimension_input.text()) / img_dist
            
            f = open(local_contents_path + "temp_output.csv", "w", newline="")
            data = [
                ["*SETTING_USER_SECTION", "", "", "", "", "", "", "", ""],
                [";NAME", "Material Type", "", "", "", "", "", "", ""],
                [self.img_path.text().split("/")[-1].split(".")[0], "concrete", "", "", "", "", "", "", ""],
                ["*SECTION_SHAPE", "Typical Sec", "", "", "", "", "", "", ""],
                [";LOOP (START VERTEX)", "X", "Y", "R", "CW", "BLEND TYPE", "R (FILLET)", "L1 (CHAMFER)", "L2 (CHAMFER)"]
            ]
            for i in section_vertex_list:
                for j in i:
                    if i.index(j) != 0:
                        loop_mark = 0
                    else:
                        loop_mark = 1
                    temp_row_data = [loop_mark, coo_convert(j[0], j[1])[0], coo_convert(j[0], j[1])[1], "0", "0", "none", "", "", ""]
                    data.append(temp_row_data)
            writer = csv.writer(f)
            writer.writerows(data)
            f.close()
            requests.post("https://api-beta.midasit.com/cim/base-mode/user-section/import-csv?apply=true", headers=header, json=[{"id":"filepath", "value":local_contents_path + "temp_output.csv"}])
            os.remove(local_contents_path + "temp_output.csv")
        except:
            print("apply error")

    def ok_fun(self):
        self.apply_fun()
        cv2.destroyAllWindows()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        try:
            if self.offset is not None and event.buttons() == Qt.LeftButton:
                app_pos_dist = self.pos() + event.pos() - self.offset
                self.move(app_pos_dist)
            else:
                super().mouseMoveEvent(event)
        except:
            pass

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

    def close_act(self):
        sys.exit(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Image2Section()
    sys.exit(app.exec_())