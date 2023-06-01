import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qtwidgets import AnimatedToggle

import winreg as reg
import requests
import pandas as pd

import urllib.request


temp_path = r"C:\Temp\CIM_API_APP"

if os.path.exists(temp_path + "\\ing.txt"):
    os.remove(temp_path + "\\ing.txt")
    
# 파일 경로 정의

img_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/3_easy_abutment/source/icon/"

key = reg.HKEY_CURRENT_USER
key_value = "SOFTWARE\MIDAS\midas CIM\APISetting"
open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
api_key_value, api_key_type = reg.QueryValueEx(open, "APIKey")

header = {'MAPI-Key': api_key_value}
uri_first = "https://api-beta.midasit.com/cim"

window_x = 920
window_y = 620

default_scale = "20"

tab_list = ["Side View", "Front View"]

dis_unit_text = " (mm)"

dim_dist_1 = 8
dim_dist_2 = 25
dim_line_dist = 60
dim_line_dist_s = 45

tab1_org_point_x = int(window_x * 5/4 * 63/100)
tab1_org_point_y = int(window_y * 2/3)
tab2_org_point_x = int(window_x * 5/4 * 50/100)
tab2_org_point_y = int(window_y * 2/3)

toggle1_state = [0]

custom_style = '''
    QWidget{font-size: 9pt; background: rgb(20, 31, 45); color: rgb(255, 255, 255);}
    QPushButton{background: rgb(47, 59, 76); height: 30px; border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
    QPushButton:hover{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242);}
    QPushButton:pressed{background: rgb(11, 125, 182);}
    QLabel{}
    QLineEdit{background: rgb(34, 44, 60); border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
    QLineEdit:hover{background: rgb(45, 53, 68);}
    QLineEdit:focus{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242); background: rgb(41, 48, 61)}
    QTabWidget {background: rgb(44, 52, 63);}
    QTabWidget::pane {border: none; margin: 0px 0px 0px 0px;}
    QTabBar {background: rgb(44, 52, 63);}
    QTabBar::tab {background: rgb(44, 52, 63); width: 115px; font-weight: bold; height:30px; color: rgb(150, 160, 160);}
    QTabBar::tab:selected {background: rgb(6, 13, 20); color: white; border-top: 2px solid rgb(26, 132, 213);}
    '''

tab_widget_list = []

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(window_x, window_y)
        self.move(500, 500)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowTitle('parameter_canvas')
        self.tab1_var_list = ["H1", "H2", "H3", "H4",
                              "V1", "V2", "V3", "V4", "PW", "PH", "ST"]
        self.tab1_var_value_list = [4000, 1400, 1800, 1100,
                                    1100, 2200, 3000, 1000, 300, 300, 450]
        self.tab2_var_list = ["W1", "WW", self.tab1_var_list[4],
                              self.tab1_var_list[5], self.tab1_var_list[6]]
        self.tab2_var_value_list = [9000, 400, self.tab1_var_value_list[4],
                                    self.tab1_var_value_list[5], self.tab1_var_value_list[6]]

        # 전체 위젯 / 전체 레이아웃
        void_widget = QWidget()
        void_widget.setStyleSheet("background: transparent;")
        main_layout = QHBoxLayout(void_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(custom_style)
        self.tabs.currentChanged.connect(self.tab_changed)

        main_layout.addWidget(self.tabs)
        main_layout.addStretch(3)
        main_layout.setStretchFactor(self.tabs, 1)

        for i in tab_list:
            tab = QWidget()
            tab.setStyleSheet("background: rgb(12, 20, 31);")
            self.tabs.addTab(tab, i)
            tab_widget_list.append(tab)

        # 1 layout
        tab1_widget = QWidget()
        tab1_widget.setStyleSheet("background: rgb(12, 20, 31);")
        tab1_layout = QVBoxLayout(tab1_widget)
        tab1_layout.setContentsMargins(10, 6, 10, 6)

        tab1_widget_1 = QWidget()
        tab1_widget_1.setStyleSheet(custom_style)
        tab1_layout_1 = QHBoxLayout(tab1_widget_1)
        tab1_layout_1.setContentsMargins(10, 6, 10, 6)

        tab1_widget_2 = QWidget()
        tab1_widget_2.setStyleSheet(custom_style)
        tab1_layout_2 = QVBoxLayout(tab1_widget_2)
        tab1_layout_2.setContentsMargins(10, 6, 10, 6)
        tab1_layout_2.setSpacing(8)

        tab1_widget_3 = QWidget()
        tab1_widget_3.setStyleSheet(custom_style)
        tab1_layout_3 = QHBoxLayout(tab1_widget_3)
        tab1_layout_3.setContentsMargins(10, 6, 10, 6)

        tab1_layout.addWidget(tab1_widget_1)
        tab1_layout.addWidget(tab1_widget_2)
        tab1_layout.setStretchFactor(tab1_widget_2, 8)
        tab1_layout.addWidget(tab1_widget_3)

        self.scale_label = QLabel(self)
        self.scale_label.setText("Scale   1 :")
        self.tab1_scale_input = QLineEdit(self)
        self.tab1_scale_input.setValidator(QIntValidator(1, 50, self))
        self.tab1_scale_input.setText(default_scale)
        self.tab1_scale_input.setFixedHeight(30)
        self.tab1_scale_input.textChanged.connect(self.fun_input)
        self.phase_create(tab1_layout_1, self.scale_label,
                          self.tab1_scale_input)
        dummy_btn = self.btn_create("reset", "ALT+R", self.fun_input)
        dummy_btn.hide()
        self.scale_reset = self.btn_create(
            "reset", "ALT+R", self.scale_reset_fun)
        tab1_layout_1.addWidget(self.scale_reset)

        self.toggle_label = QLabel(self)
        self.toggle_label.setText("Show Dim. Label")
        self.toggle_1 = AnimatedToggle(
            checked_color="#1A84D5", pulse_checked_color="#44FFB000")
        self.toggle_1.setFixedSize(48, 32)
        self.toggle_1.toggled.connect(self.toggle)
        self.phase_create(tab1_layout_2, self.toggle_label, self.toggle_1)

        self.tab1_label_list = []
        for i in self.tab1_var_list:
            temp_label = QLabel(self)
            temp_label.setText(i + dis_unit_text)
            temp_label.setFixedHeight(30)
            self.tab1_label_list.append(temp_label)

        self.tab1_input_list = []
        for i in range(len(self.tab1_var_value_list)):
            temp_input = QLineEdit(self)
            temp_input.setValidator(QIntValidator(0, 100000, self))
            temp_input.setText(str(self.tab1_var_value_list[i]))
            temp_input.setFixedHeight(30)
            temp_input.editingFinished.connect(self.fun_input)
            self.tab1_input_list.append(temp_input)

        for i in range(len(self.tab1_label_list)):
            self.phase_create(
                tab1_layout_2, self.tab1_label_list[i], self.tab1_input_list[i])

        tab1_layout_2.addStretch(1)

        # UI default
        ok_btn = self.btn_create("ok", "ALT+A", self.onClicked)
        cancel_btn = self.btn_create("cancel", "ALT+X", self.closeEvent)

        tab1_layout_3.addStretch(1)
        tab1_layout_3.addWidget(ok_btn)
        tab1_layout_3.addWidget(cancel_btn)

        # 1 layout
        tab2_widget = QWidget()
        tab2_widget.setStyleSheet("background: rgb(12, 20, 31);")
        tab2_layout = QVBoxLayout(tab2_widget)
        tab2_layout.setContentsMargins(10, 6, 10, 6)

        tab2_widget_1 = QWidget()
        tab2_widget_1.setStyleSheet(custom_style)
        tab2_layout_1 = QHBoxLayout(tab2_widget_1)
        tab2_layout_1.setContentsMargins(10, 6, 10, 6)

        tab2_widget_2 = QWidget()
        tab2_widget_2.setStyleSheet(custom_style)
        tab2_layout_2 = QVBoxLayout(tab2_widget_2)
        tab2_layout_2.setContentsMargins(10, 6, 10, 6)
        tab2_layout_2.setSpacing(8)

        tab2_widget_3 = QWidget()
        tab2_widget_3.setStyleSheet(custom_style)
        tab2_layout_3 = QHBoxLayout(tab2_widget_3)
        tab2_layout_3.setContentsMargins(10, 6, 10, 6)

        tab2_layout.addWidget(tab2_widget_1)

        tab2_layout.addWidget(tab2_widget_2)
        tab2_layout.setStretchFactor(tab2_widget_2, 8)

        tab2_layout.addWidget(tab2_widget_3)

        self.scale_label = QLabel(self)
        self.scale_label.setText("Scale   1 :")
        self.tab2_scale_input = QLineEdit(self)
        self.tab2_scale_input.setValidator(QIntValidator(1, 50, self))
        self.tab2_scale_input.setText(default_scale)
        self.tab2_scale_input.setFixedHeight(30)
        self.tab2_scale_input.textChanged.connect(self.fun_input)
        self.phase_create(tab2_layout_1, self.scale_label,
                          self.tab2_scale_input)
        dummy_btn = self.btn_create("reset", "ALT+R", self.fun_input)
        dummy_btn.hide()
        self.scale_reset = self.btn_create(
            "reset", "ALT+R", self.scale_reset_fun)
        tab2_layout_1.addWidget(self.scale_reset)

        self.toggle_label = QLabel(self)
        self.toggle_label.setText("Show Dim. Label")
        self.toggle_2 = AnimatedToggle(
            checked_color="#1A84D5", pulse_checked_color="#44FFB000")
        self.toggle_2.setFixedSize(48, 32)
        self.toggle_2.toggled.connect(self.toggle)
        self.phase_create(tab2_layout_2, self.toggle_label, self.toggle_2)

        self.tab2_label_list = []
        for i in self.tab2_var_list:
            temp_label = QLabel(self)
            temp_label.setText(i + dis_unit_text)
            temp_label.setFixedHeight(30)
            self.tab2_label_list.append(temp_label)

        self.tab2_input_list = []
        for i in range(len(self.tab2_var_value_list)):
            temp_input = QLineEdit(self)
            temp_input.setValidator(QIntValidator(0, 100000, self))
            temp_input.setText(str(self.tab2_var_value_list[i]))
            temp_input.setFixedHeight(30)
            temp_input.editingFinished.connect(self.fun_input)
            self.tab2_input_list.append(temp_input)

        for i in range(len(self.tab2_label_list)):
            self.phase_create(
                tab2_layout_2, self.tab2_label_list[i], self.tab2_input_list[i])

        tab2_layout_2.addStretch(1)

        # UI default
        ok_btn = self.btn_create("ok", "ALT+A", self.onClicked)
        cancel_btn = self.btn_create("cancel", "ALT+X", self.closeEvent)

        tab2_layout_3.addStretch(1)
        tab2_layout_3.addWidget(ok_btn)
        tab2_layout_3.addWidget(cancel_btn)

        tab_widget_list[0].setLayout(tab1_layout)
        tab_widget_list[1].setLayout(tab2_layout)

        self.tab_num = 0
        self.var_list = self.tab1_var_list
        self.var_value_list = self.tab1_var_value_list
        self.input_list = self.tab1_input_list
        self.scale_input = self.tab1_scale_input
        self.org_point_x = tab1_org_point_x
        self.org_point_y = tab1_org_point_y

        self.setCentralWidget(void_widget)
        self.show()

    def tab_changed(self):
        try:
            if tab_widget_list.index(self.tabs.currentWidget()) == 0:
                self.tab_num = 0
                self.var_list = self.tab1_var_list
                self.var_value_list = self.tab1_var_value_list
                self.input_list = self.tab1_input_list
                self.scale_input = self.tab1_scale_input
                self.org_point_x = tab1_org_point_x
                self.org_point_y = tab1_org_point_y
            else:
                self.tab_num = 1
                self.var_list = self.tab2_var_list
                self.var_value_list = self.tab2_var_value_list
                self.input_list = self.tab2_input_list
                self.scale_input = self.tab2_scale_input
                self.org_point_x = tab2_org_point_x
                self.org_point_y = tab2_org_point_y
            self.fun_input()
        except:
            pass

    def phase_create(self, layout, label, widget):
        temp_sub_layout = QHBoxLayout()
        temp_sub_layout.addWidget(label)
        temp_sub_layout.setStretchFactor(label, 1)
        temp_sub_layout.addWidget(widget)
        temp_sub_layout.setStretchFactor(widget, 2)
        layout.addLayout(temp_sub_layout)

    def btn_create(self, png_name, short_key, event_name):
        temp_img_path = img_drive_url + png_name + ".png"
        temp_img = urllib.request.urlopen(temp_img_path).read()
        temp_pixmap = QPixmap()
        temp_pixmap.loadFromData(temp_img)
        temp_icon = QIcon()
        temp_icon.addPixmap(temp_pixmap)
        self.temp_btn = QPushButton(self)
        self.temp_btn.setFixedSize(28, 28)
        self.temp_btn.setIcon(temp_icon)
        self.temp_btn.setShortcut(short_key)
        self.temp_btn.clicked.connect(event_name)
        return self.temp_btn

    def fun_input(self):
        for i in range(len(self.var_value_list)):
            self.var_value_list[i] = int(self.input_list[i].text())
        for i in range(3):
            self.tab2_input_list[i+2].setDisabled(True)
            self.tab2_label_list[i+2].setStyleSheet("color: rgb(100, 100, 100);")
            self.tab2_input_list[i+2].setStyleSheet("color: rgb(100, 100, 100);")
            self.tab2_input_list[i+2].setText(self.tab1_input_list[i+4].text())
        self.update()

    def sum_var(self, num_list):
        temp_data = 0
        for i in range(len(num_list)):
            temp_data = temp_data + self.var_value_list[num_list[i]]

        return temp_data

    def make_var(self, dx_list, dy_list):
        coefficient = 1 / int(self.scale_input.text())
        calibrated_dx_list = [int(i * coefficient) for i in dx_list]
        calibrated_dy_list = [int(i * coefficient) for i in dy_list]

        temp_x_coo = [self.org_point_x]
        for i in range(len(calibrated_dx_list)):
            temp_value = temp_x_coo[i] + calibrated_dx_list[i]
            temp_x_coo.append(temp_value)
        del temp_x_coo[0]

        temp_y_coo = [self.org_point_y]
        for i in range(len(calibrated_dy_list)):
            temp_value = temp_y_coo[i] - calibrated_dy_list[i]
            temp_y_coo.append(temp_value)
        del temp_y_coo[0]

        points = []
        for i in range(len(temp_x_coo)):
            points.append(QPoint(temp_x_coo[i], temp_y_coo[i]))

        return (points)

    def dim_create(self, qp, p1, p2, dir, ref_coor, text):
        p1_x = p1.x()
        p1_y = p1.y()
        p2_x = p2.x()
        p2_y = p2.y()

        d1 = dir % 2
        d2 = (dir + 1) % 2
        if dir//3 == 1:
            d3 = 1
            d4 = 0
            d5 = -1
        elif (dir+1)//3 == 1:
            d3 = 0
            d4 = 1
            d5 = -1
        else:
            d3 = 0
            d4 = 0
            d5 = 1

        dx = dim_dist_1 * d1 * d5
        dy = dim_dist_1 * d2 * d5
        start_x1 = p1_x + dx
        start_y1 = p1_y + dy
        start_x2 = p2_x + dx
        start_y2 = p2_y + dy
        end_x1 = p1_x * d2 + ref_coor * d1
        end_y1 = p1_y * d1 + ref_coor * d2
        end_x2 = p2_x * d2 + ref_coor * d1
        end_y2 = p2_y * d1 + ref_coor * d2
        rect = QRect(end_x1 - dim_dist_2*d3 - 56, end_y1 - dim_dist_2*d4 + 56, (end_x2 - end_x1)
                     * d2 + dim_dist_2*d1 + 112, (end_y2 - end_y1)*d1 + dim_dist_2*d2 - 112)

        qp.drawLine(start_x1, start_y1, end_x1, end_y1)
        qp.drawLine(start_x2, start_y2, end_x2, end_y2)
        qp.drawLine(end_x1 - dx, end_y1 - dy, end_x2 - dx, end_y2 - dy)
        text = str(text)
        qp.drawText(rect, Qt.AlignCenter, text)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_polygon(qp)
        qp.end()

    def draw_polygon(self, qp):
        try:
            # ui Frame Draw
            qp.setPen(QPen(QColor('#0C141F'), 1))
            frame = QRect(0, 0, window_x-1, window_y-1)
            qp.drawRect(frame)

            if tab_widget_list.index(self.tabs.currentWidget()) == 0:
                foundation_dx = [self.sum_var(
                    [3]), 0, -self.sum_var([1, 2, 3]), 0]
                foundation_dy = [0, -self.sum_var([4]), 0, self.sum_var([4])]
                wall_dx = [0, -self.sum_var([2]), 0, self.sum_var([8]),
                           0, self.sum_var([2]) - self.sum_var([8])]
                wall_dy = [-self.sum_var([4]), 0, self.sum_var([4, 5]) +
                           self.sum_var([9]), 0, -self.sum_var([9]), 0]
                wing_dx = [0, -self.sum_var([1, 2]), 0, -self.sum_var([0]), 0, self.sum_var(
                    [0, 1]) + self.sum_var([8]), 0, self.sum_var([2]) - self.sum_var([8])]
                wing_dy = [-self.sum_var([4]), 0, self.sum_var([4]), self.sum_var(
                    [5, 6]) - self.sum_var([7]), self.sum_var([7]), 0, -self.sum_var([10]), 0]

                qp.setPen(QPen(QColor('#363635'), 1, Qt.SolidLine))
                qp.setBrush(QBrush(QColor('#5C5C5B'), Qt.SolidPattern))
                foundation_points = self.make_var(foundation_dx, foundation_dy)
                polygon0 = QPolygon(foundation_points)
                wall_points = self.make_var(wall_dx, wall_dy)
                polygon1 = QPolygon(wall_points)
                wing_points = self.make_var(wing_dx, wing_dy)
                polygon2 = QPolygon(wing_points)
                qp.drawPolygon(polygon2)
                qp.drawPolygon(polygon1)
                qp.drawPolygon(polygon0)

                # Org. Point Draw
                qp.setPen(QPen(QColor('#0000FF'), 5))
                self.org_point = QPoint(self.org_point_x, self.org_point_y)
                qp.drawPoint(self.org_point)

                qp.setPen(QPen(QColor('#FF0000'), 1))

                dim_bot_co = foundation_points[1].y() + dim_line_dist
                dim_right_co = foundation_points[1].x() + dim_line_dist
                dim_left_co = wing_points[3].x() - dim_line_dist

                if toggle1_state[0] == 0:
                    dim_text = self.tab1_var_value_list
                else:
                    dim_text = self.tab1_var_list
                self.update()

                self.dim_create(
                    qp, wing_points[3], foundation_points[2], 0, dim_bot_co, dim_text[0])
                self.dim_create(
                    qp, foundation_points[2], wall_points[1], 0, dim_bot_co, dim_text[1])
                self.dim_create(
                    qp, wall_points[1], wall_points[0], 0, dim_bot_co, dim_text[2])
                self.dim_create(
                    qp, wall_points[0], foundation_points[1], 0, dim_bot_co, dim_text[3])
                self.dim_create(
                    qp, foundation_points[1], foundation_points[0], 1, dim_right_co, dim_text[4])
                self.dim_create(
                    qp, foundation_points[0], wall_points[5], 1, dim_right_co, dim_text[5])
                self.dim_create(
                    qp, wall_points[5], wing_points[5], 1, dim_right_co, dim_text[6])
                self.dim_create(
                    qp, wing_points[3], wing_points[4], 3, dim_left_co, dim_text[7])
                self.dim_create(qp, wall_points[2], wall_points[3], 2, wall_points[2].y(
                ) - dim_line_dist_s, dim_text[8])
                self.dim_create(qp, wall_points[2], wall_points[4], 3, wall_points[2].x(
                ) - dim_line_dist_s, dim_text[9])
                self.dim_create(qp, wing_points[5], wing_points[6], 3, wing_points[5].x(
                ) - dim_line_dist_s, dim_text[10])

            else:
                foundation_dx = [self.sum_var(
                    [0])/2, -self.sum_var([0]), 0, self.sum_var([0])]
                foundation_dy = [-self.sum_var([2]), 0, self.sum_var([2]), 0]
                right_wing_dx = [self.sum_var(
                    [0])/2, -self.sum_var([1]), 0, self.sum_var([1])]
                left_wing_dx = [-1 * i for i in right_wing_dx]
                wing_dy = [-self.sum_var([2]), 0, self.sum_var([2, 3, 4]), 0]
                wall_dx = foundation_dx
                wall_dy = [-self.sum_var([2]), 0, self.sum_var([2, 3]), 0]

                qp.setPen(QPen(QColor('#363635'), 1, Qt.SolidLine))
                qp.setBrush(QBrush(QColor('#5C5C5B'), Qt.SolidPattern))
                foundation_points = self.make_var(foundation_dx, foundation_dy)
                polygon0 = QPolygon(foundation_points)
                wall_points = self.make_var(wall_dx, wall_dy)
                polygon1 = QPolygon(wall_points)
                right_wing_points = self.make_var(right_wing_dx, wing_dy)
                polygon2 = QPolygon(right_wing_points)
                left_wing_points = self.make_var(left_wing_dx, wing_dy)
                polygon3 = QPolygon(left_wing_points)
                qp.drawPolygon(polygon1)
                qp.drawPolygon(polygon2)
                qp.drawPolygon(polygon3)
                qp.drawPolygon(polygon0)

                # Org. Point Draw
                qp.setPen(QPen(QColor('#0000FF'), 5))
                self.org_point = QPoint(self.org_point_x, self.org_point_y)
                qp.drawPoint(self.org_point)

                # Dimension Draw
                qp.setPen(QPen(QColor('#FF0000'), 1))
                dim_bot_co = foundation_points[0].y() + dim_line_dist
                dim_right_co = foundation_points[0].x() + dim_line_dist
                dim_top_co = right_wing_points[3].y() - dim_line_dist
                dim_left_co = None

                if toggle1_state[0] == 0:
                    dim_text = self.tab2_var_value_list
                else:
                    dim_text = self.tab2_var_list
                self.update()

                self.dim_create(
                    qp, foundation_points[1], foundation_points[0], 0, dim_bot_co, dim_text[0])
                self.dim_create(
                    qp, right_wing_points[2], right_wing_points[3], 2, dim_top_co, dim_text[1])
                
                qp.setPen(QPen(QColor('#969696'), 1))
                self.dim_create(
                    qp, foundation_points[0], foundation_points[3], 1, dim_right_co, dim_text[2])
                self.dim_create(
                    qp, foundation_points[3], wall_points[3], 1, dim_right_co, dim_text[3])
                self.dim_create(
                    qp, wall_points[3], right_wing_points[3], 1, dim_right_co, dim_text[4])

        except:
            print("어딘가 에러가 있음.")

    # depth_toggle_btn의 on sign : 1 / off : 0로 전달
    def toggle(self):
        if toggle1_state[0] == 0:
            self.toggle_1.setChecked(True)
            self.toggle_2.setChecked(True)
            toggle1_state[0] = 1
        else:
            self.toggle_1.setChecked(False)
            self.toggle_2.setChecked(False)
            toggle1_state[0] = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        elif event.button() == Qt.MidButton:
            self.offset = event.pos()
            self.new_pos_x = self.org_point_x
            self.new_pos_y = self.org_point_y
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        try:
            global org_point_x, org_point_y
            if self.offset is not None and event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.pos() - self.offset)
            elif self.offset is not None and event.buttons() == Qt.MidButton:
                temp_qpoint = -self.offset + event.pos()
                self.org_point_x = self.new_pos_x + temp_qpoint.x()
                self.org_point_y = self.new_pos_y + temp_qpoint.y()
                self.update()
            else:
                super().mouseMoveEvent(event)
        except:
            pass

    def wheelEvent(self, e):
        try:
            wheel_vec = e.angleDelta().y() / abs(e.angleDelta().y())
            temp_scale = int(int(self.scale_input.text()) - wheel_vec)
            if temp_scale == 0:
                temp_scale = 1
            self.scale_input.setText(str(temp_scale))
        except:
            pass

    def mouseReleaseEvent(self, event):
        self.offset = None
        self.new_pos_x = None
        self.new_pos_y = None
        super().mouseReleaseEvent(event)

    def scale_reset_fun(self):
        self.scale_input.setText(default_scale)
        if self.tab_num == 0:
            self.org_point_x = tab1_org_point_x
            self.org_point_y = tab1_org_point_y
        else:
            self.org_point_x = tab2_org_point_x
            self.org_point_y = tab2_org_point_y
        self.update()

    def onClicked(self):
        try:
            # cvs data 정리
            csv = pd.read_csv(new_folder_path + "test.csv",
                              header=None,
                              encoding='CP949')
            new_csv = csv.drop(0)
            new_csv = new_csv.drop(0, axis='columns')

            result = [str(i * 1/1000) for i in self.tab1_var_value_list] + [str(i * 1/1000) for i in self.tab2_var_value_list[:2]]

            new_csv[2] = result

            com_in_val = new_csv.values
            com_in_list = com_in_val.tolist()

            # cvs를 문자열로
            uri_request_body = ''.join(''.join(l) for l in com_in_list)

            # Request 함수 생성 및 실행
            new_code_str = "requests.patch(\"https://api-beta.midasit.com/cim/" + "pointlibrary" + \
                "/UserParam?apply=true\", headers=header, json = [" + \
                uri_request_body + "])"
            requests.patch("https://api-beta.midasit.com/cim/pointlibrary/UserParam",
                           headers=header, json=[{"id": "content type", "value": 0}])
            exec(new_code_str)
        except:
            print("Error")

    def closeEvent(self, QCloseEvent):
        try:
            print("Close")
        except:
            pass
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
