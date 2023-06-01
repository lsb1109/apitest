import requests
import urllib.request

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import os

import webbrowser

temp_path = r"C:\Temp\CIM_API_APP"

if os.path.exists(temp_path + "\\ing.txt"):
    pass
else:
    temp_path = r"C:\Temp\CIM_API_APP"
    with open(temp_path + "\\ing.txt", "w") as File:
        File.write("")
        
    img_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/0_app_selection/source/icon/"

    json_link = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/0_app_selection/source/app_list_v11.json"

    ok_img = "ok.png"
    app_img = "app_selection_v2.png"

    temp_json = requests.get(json_link).json()
    catagory = list(temp_json.keys())
    manual_link_dic = temp_json[catagory[1]]
    app_list = list(manual_link_dic.keys())
    link_list = list(manual_link_dic.values())

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
        '''

    class app_selection(QDialog):
        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

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
            app_pixmap = app_pixmap.scaled(QSize(25, 25))

            self.header_widget = QWidget()
            self.header_widget.setStyleSheet(
                "background: rgb(35, 40, 50); color: rgb(255, 255, 255);")
            self.header_layout = QHBoxLayout(self.header_widget)

            self.header_icon = QLabel()
            self.header_icon.setPixmap(app_pixmap)
            self.header_lable = QLabel()
            self.header_lable.setStyleSheet("font-size: 15px; font-weight:bold")
            self.header_lable.setFont(QFont('Arial', 1))
            self.header_lable.setFixedHeight(20)
            self.header_lable.setText(" App Selection Tool")

            self.header_layout.addWidget(self.header_icon)
            self.header_layout.addWidget(self.header_lable)
            self.header_layout.setStretchFactor(self.header_lable, 1)

            main_layout.addWidget(self.header_widget)

            # 1 layout
            self.sub_widget0 = QWidget()
            self.sub_widget0.setStyleSheet(custom_style)
            self.sub_layout0 = QVBoxLayout(self.sub_widget0)
            self.sub_layout0.setContentsMargins(2, 2, 2, 2)

            self.key_list = QListWidget()
            for i in manual_link_dic:
                self.key_list.addItem(i)
            self.key_list.doubleClicked.connect(self.ok_btn)

            self.sub_layout0.addWidget(self.key_list)

            main_layout.addWidget(self.sub_widget0)

            # 2 layout (UI default)
            ok_pixmap = QPixmap()
            temp_img_path = img_drive_url + ok_img
            temp_img = urllib.request.urlopen(temp_img_path).read()
            ok_pixmap.loadFromData(temp_img)
            ok_icon = QIcon()
            ok_icon.addPixmap(ok_pixmap)

            self.sub_widget1 = QWidget()
            self.sub_widget1.setStyleSheet(custom_style)
            self.sub_layout1 = QVBoxLayout(self.sub_widget1)
            self.sub_layout1.setContentsMargins(10, 6, 10, 6)

            self.xbtn = QPushButton(self)
            self.xbtn.setFixedSize(28, 28)
            self.xbtn.setIcon(ok_icon)
            self.xbtn.clicked.connect(self.ok_btn)
            self.sub_layout1.addWidget(self.xbtn, alignment=Qt.AlignRight)

            main_layout.addWidget(self.sub_widget1)

            void_layout.addWidget(void_widget)
            self.setLayout(void_layout)
            
            self.show()

        def keyPressEvent(self, event):
            f1_key = 16777264
            if event.key() == f1_key :
                selected_app = self.key_list.selectedItems()
                app_num = app_list.index(selected_app[0].text())
                target_link = link_list[app_num]
                webbrowser.open(target_link)
            
        def ok_btn(self):
            selected_app = self.key_list.selectedItems()
            app_num = app_list.index(selected_app[0].text())

            try:
                path = r"C:\Temp\CIM_API_APP"
                os.mkdir(path)
            except:
                pass

            with open(path + "\\last_used.txt", "w") as File:
                File.write(str(app_num))
            self.close()

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

    first_app = QApplication(sys.argv)
    w = app_selection()
    first_app.exec_()