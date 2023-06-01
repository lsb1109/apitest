import requests
from bs4 import BeautifulSoup
import re
# import os
# import multiprocessing
# from multiprocessing import Queue

import urllib.request

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import sys

import time

import webbrowser

py_drive_url = "https://github.com/kh1012/python-examples/tree/main/python_app"
xl_drive_url = "https://github.com/kh1012/python-examples/tree/main/excel_app"
js_drive_url = "https://github.com/kh1012/sproj-examples/tree/main/examples"
xl_raw_file_url = "https://raw.githubusercontent.com/kh1012/python-examples/main/excel_app/"
img_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/0_app_selection/source/icon/"
xl_file_local_path = r"C:\Temp\CIM_API_APP\\"


def extract_soup(link, search):
    req = requests.get(link)
    req.encoding = None
    html = req.content
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    temp_list = soup.select(search)
    temp_contents = [re.search('>(.+?)<', str(i)).group(1) for i in temp_list]
    return temp_contents


tab_selector_list = ["a.js-navigation-open.Link--primary",
                     "a.Link--primary", "a.Link--primary"]
tab_link_list = [py_drive_url, xl_drive_url, js_drive_url]

ok_img = "ok.png"
app_img = "app_selection_v3.png"
href_img = "href.png"
update_img = "update.png"
type_icon_img = ["py_v2.png", "xl_v2.png", "js_v2.png"]

tab_widget_list = []
tab_listwidget_list = []
all_contents_list = []

selection_tool_wh = [300, 650]

tab_num = 0
app_num = 0

custom_style = '''
    QWidget{font-size: 9pt; background: rgb(20, 31, 45); color: rgb(255, 255, 255);}
    QPushButton{background: rgb(47, 59, 76); height: 30px; border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
    QPushButton:hover{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242);}
    QPushButton:pressed{background: rgb(11, 125, 182);}
    QListWidget{outline: 0; border: 1px solid; border-radius: 3px; border-color: transparent;}
    QListWidget::item{height: 30px; border: 1px solid; border-radius: 3px; border-color: rgb(25, 35, 45);}
    QListWidget::item:hover{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242);}
    QListWidget::item:selected{background: rgb(11, 125, 182); color: rgb(255, 255, 255);}
    QScrollBar:vertical{background-color: rgb(41, 41, 41); width: 15px; margin: 2px 1px 2px 5px; border: 1px transparent #2A2929; border-radius: 4px;}
    QScrollBar::handle:vertical{background-color: rgb(63, 68, 75); min-height: 5px; border-radius: 4px;}
    QScrollBar::sub-line:vertical{background: transparent;}
    QScrollBar::add-line:vertical{background: transparent;}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{background: none;}
    QTabWidget {background: rgb(20, 31, 45);}
    QTabWidget::pane {border: none; margin: 0px 0px 0px 0px;}
    QTabBar::tab {background: rgb(44, 52, 63); font-weight: bold; width: 44px; height:38px; color: rgb(150, 160, 160); padding-bottom: 15px; padding-right: -2px;}
    QTabBar::tab:selected {background: rgb(6, 13, 20); color: white; border-left: 3px solid rgb(11, 125, 182); padding-left: -3px;}
    '''


class app_selection(QDialog):
    select_sig = pyqtSignal(int)
    move_sig = pyqtSignal(QPoint)
    close_sig = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.win_cen()
        self.setFixedSize(selection_tool_wh[0], selection_tool_wh[1])

        # 전체 위젯 / 전체 레이아웃
        void_layout = QVBoxLayout(self)
        void_layout.setContentsMargins(0, 0, 0, 0)
        void_widget = QWidget()
        void_widget.setStyleSheet("background: rgb(12, 20, 31);")
        main_layout = QVBoxLayout(void_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)

        # header layout
        app_pixmap = QPixmap()
        temp_img_path = img_drive_url + app_img
        temp_img = urllib.request.urlopen(temp_img_path).read()
        app_pixmap.loadFromData(temp_img)

        self.header_widget = QWidget()
        self.header_widget.setStyleSheet(
            "background: rgb(35, 40, 50); color: rgb(255, 255, 255);")
        self.header_layout = QHBoxLayout(self.header_widget)

        self.header_icon = QLabel()
        self.header_icon.setPixmap(app_pixmap)
        self.header_lable = QLabel()
        self.header_lable.setFixedHeight(24)
        self.header_lable.setStyleSheet("font-size: 18px;")
        self.header_lable.setFont(QFont("Noto Sans CJK KR Bold", 1))
        self.header_lable.setText("API Extension Tool")

        self.header_layout.addWidget(self.header_icon)
        self.header_layout.addWidget(self.header_lable)
        self.header_layout.setStretchFactor(self.header_lable, 1)

        main_layout.addWidget(self.header_widget)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(custom_style)
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.currentChanged.connect(self.tab_changed)

        for i in type_icon_img:
            self.tab_inner = QWidget()
            tab_index = self.tabs.addTab(self.tab_inner, "")

            temp_icon = self.icon_create(i)

            self.tabs.setTabIcon(tab_index, temp_icon)
            self.tabs.setIconSize(QSize(25, 25))

            self.tab_sub_layout = QVBoxLayout(self.tab_inner)
            self.tab_sub_layout.setContentsMargins(2, 2, 2, 2)

            self.tab_app_list = QListWidget()
            self.tab_app_list.itemSelectionChanged.connect(self.selected_app)
            self.tab_app_list.doubleClicked.connect(self.ok_fun)

            self.tab_sub_layout.addWidget(self.tab_app_list)

            tab_widget_list.append(self.tab_inner)
            tab_listwidget_list.append(self.tab_app_list)

        self.app_list_build()

        main_layout.addWidget(self.tabs)

        # 2 layout (UI default)
        ok_icon = self.icon_create(ok_img)
        update_icon = self.icon_create(update_img)

        self.sub_widget1 = QWidget()
        self.sub_widget1.setStyleSheet(custom_style)
        self.sub_layout1 = QHBoxLayout(self.sub_widget1)
        self.sub_layout1.setContentsMargins(10, 6, 10, 6)

        self.ok_btn = QPushButton(self)
        self.ok_btn.setFixedSize(28, 28)
        self.ok_btn.setIcon(ok_icon)
        self.ok_btn.clicked.connect(self.ok_fun)

        self.update_btn = QPushButton(self)
        self.update_btn.setFixedSize(28, 28)
        self.update_btn.setIcon(update_icon)
        self.update_btn.clicked.connect(self.update_fun)

        self.sub_layout1.addStretch(1)
        self.sub_layout1.addWidget(self.update_btn)
        self.sub_layout1.addWidget(self.ok_btn)

        main_layout.addWidget(self.sub_widget1)

        void_layout.addWidget(void_widget)
        self.setLayout(void_layout)

        self.show()

    def win_cen(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def tab_changed(self):
        global tab_num
        try:
            tab_num = tab_widget_list.index(self.tabs.currentWidget())
            self.selected_app()
        except:
            pass

    def selected_app(self):
        global app_num
        try:
            selected_app = tab_listwidget_list[tab_num].selectedItems()
            app_num = all_contents_list[tab_num].index(selected_app[0].text())
            self.select_sig.emit(app_num)
        except:
            pass

    def app_list_build(self):
        all_contents_list.clear
        for i in range(len(type_icon_img)):
            tab_listwidget_list[i].clear()
            temp_contents = extract_soup(
                tab_link_list[i], tab_selector_list[i])
            if i == 0:
                temp_contents_list = [j for j in temp_contents if ord(
                    j[0]) >= 48 and ord(j[0]) <= 57]
            elif i == 1:
                temp_contents_list = [temp_contents[j+1]
                                      for j in range(len(temp_contents)-1)]
            else:
                temp_contents_list = [temp_contents[j+1]
                                      for j in range(len(temp_contents)-1)]
            for j in temp_contents_list:
                tab_listwidget_list[i].addItem(j)
            all_contents_list.append(temp_contents_list)
            tab_listwidget_list[i].setCurrentRow(0)

    def icon_create(self, img_file_name):
        temp_pixmap = QPixmap()
        temp_img_path = img_drive_url + img_file_name
        temp_img = urllib.request.urlopen(temp_img_path).read()
        temp_pixmap.loadFromData(temp_img)
        temp_icon = QIcon()
        temp_icon.addPixmap(temp_pixmap)
        return temp_icon

    def update_fun(self):
        self.app_list_build()

    def ok_fun(self):
        self.close()

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
                self.move_sig.emit(app_pos_dist)
            else:
                super().mouseMoveEvent(event)
        except:
            pass

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

    def closeEvent(self, QCloseEvent):
        self.close_sig.emit(1)


class manual_dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.win_cen()
        self.setFixedSize(750, selection_tool_wh[1])

        # 전체 위젯 / 전체 레이아웃
        void_layout = QVBoxLayout(self)
        void_layout.setContentsMargins(0, 0, 0, 0)
        void_widget = QWidget()
        void_widget.setStyleSheet("background: rgb(12, 20, 31);")
        main_layout = QVBoxLayout(void_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)

        # 1 layout
        self.sub_widget0 = QWidget()
        self.sub_widget0.setStyleSheet(custom_style)
        self.sub_widget0.setFixedSize(746, 646)
        self.sub_layout0 = QVBoxLayout(self.sub_widget0)
        self.sub_layout0.setContentsMargins(0, 6, 0, 6)
        self.web_widget = QWebEngineView()
        self.web_widget.loadFinished.connect(self.loading_end)
        self.web_widget.setUrl(
            QUrl("http://127.0.0.1:5500/html_temp_" + str(tab_num) + "/test_html" + str(app_num + 1) + "/index.html"))
        self.web_widget.setHidden(True)

        # 2 layout (UI default)
        href_icon = self.icon_create(href_img)

        self.sub_widget1 = QWidget()
        self.sub_widget1.setStyleSheet("background: transparent;")
        self.sub_layout1 = QVBoxLayout(self.sub_widget1)
        self.sub_layout1.setContentsMargins(0, 6, 12, 6)

        self.manual_link = QPushButton(self)
        self.manual_link.setStyleSheet(custom_style)
        self.manual_link.setFixedSize(160, 28)
        self.manual_link.setText(" Detail With Browser")
        self.manual_link.setIcon(href_icon)
        self.manual_link.clicked.connect(self.web_manual)
        self.sub_layout1.addWidget(self.manual_link, alignment=Qt.AlignRight)

        self.sub_layout0.addWidget(self.web_widget)
        main_layout.addWidget(self.sub_widget0)
        main_layout.addWidget(self.sub_widget1)
        main_layout.setStretchFactor(self.sub_widget0, 1)

        void_layout.addWidget(void_widget)
        self.setLayout(void_layout)

        self.app_connect()
        self.show()

    def win_cen(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft() + QPoint(selection_tool_wh[0], 0))

    def icon_create(self, img_file_name):
        temp_pixmap = QPixmap()
        temp_img_path = img_drive_url + img_file_name
        temp_img = urllib.request.urlopen(temp_img_path).read()
        temp_pixmap.loadFromData(temp_img)
        temp_icon = QIcon()
        temp_icon.addPixmap(temp_pixmap)
        return temp_icon

    def loading_end(self):
        time.sleep(0.1)
        self.web_widget.setHidden(False)

    def web_manual(self):
        target_link = "https://blog.midasuser.com/ko/bridge/page/" + \
            str(app_num)
        webbrowser.open(target_link)

    def app_connect(self):
        self.main_app = app_selection()
        self.main_app.select_sig.connect(self.selection_changed)
        self.main_app.move_sig.connect(self.app_moved)
        self.main_app.close_sig.connect(self.app_closed)

    def selection_changed(self):
        if tab_num == 2:
            js_app_name = all_contents_list[tab_num][app_num]
            self.web_widget.setUrl(
                QUrl("https://kh1012.github.io/sproj-examples/" + js_app_name + "/"))
        else:
            self.web_widget.setUrl(
                QUrl("http://127.0.0.1:5500/html_temp_" + str(tab_num) + "/test_html" + str(app_num + 1) + "/index.html"))

    def app_moved(self, pos_dist):
        self.move(pos_dist + QPoint(selection_tool_wh[0], 0))

    def app_closed(self):
        self.close()


first_app = QApplication([sys.argv,  '--no-sandbox'])
dialog = manual_dialog()
first_app.exec_()

selected_tab = tab_num
selected_app = app_num
