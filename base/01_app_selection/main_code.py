import os
import json
from pip._internal import main

import requests
from bs4 import BeautifulSoup

local_contents_path = r"C:\Temp\CIM_API_APP\\"

git_org_root_link = "https://github.com/"
git_raw_root_link = "https://raw.githubusercontent.com/"
midas_link = "lsb1109/apitest/"
personal_link = "lsb1109/personal/"
apps_source = [personal_link, midas_link]

link_bri0 = "tree/"
link_bri1 = "main/"
selector_list = ["python_app/", "excel_app/", "javascript_app/", "base/"]

version_key_type = ["py_app_ver", "xl_app_ver", "js_app_ver", "tool_ver"]
version_json = "app_version.json"
package_txt = "requirements.txt"


# fmt: off
def extract_soup(link):
    req = requests.get(link)
    req.encoding = None
    html = req.content
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    return soup

def version_compare(target_type, content_name, link):
    temp_json_path = local_contents_path + version_json
    selector = selector_list[version_key_type.index(target_type)]
    if not os.path.isfile(temp_json_path):
        if not os.path.exists(local_contents_path):
            os.makedirs(local_contents_path)
        default_dic = {version_key_type[0]: {}, version_key_type[1]: {},
                        version_key_type[2]: {}, version_key_type[3]: {}}
        with open(temp_json_path, "w") as f:
            json.dump(default_dic, f)

    json_soup = extract_soup(git_raw_root_link + link + link_bri1 + selector + content_name + "/" + version_json)
    app_ver_dict = json.loads(str(json_soup))        
    current_app_key = list(app_ver_dict.keys())[0]
    current_app_ver = list(app_ver_dict.values())[0]

    with open(temp_json_path, "r") as f:
        all_dict = json.load(f)
    target_old_dict = all_dict[target_type]
    last_app_ver = target_old_dict.get(current_app_key)

    if last_app_ver and last_app_ver == current_app_ver:
        pass
    else:
        if target_type == version_key_type[0] or target_type == version_key_type[3]:
            txt_soup = extract_soup(git_raw_root_link + link + link_bri1 + selector +  content_name + "/" + package_txt)
            lines = str(txt_soup).splitlines()
            for temp_pkg in lines:
                main(["install", temp_pkg])
        target_old_dict.update({current_app_key: current_app_ver})
        all_dict.update({target_type: target_old_dict})
        with open(temp_json_path, "w") as f:
            json.dump(all_dict, f)

version_compare("tool_ver", "01_app_selection", midas_link)
# fmt: on

import sys
import webbrowser

import urllib.request

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

import time

start = time.time()

img_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/0_app_selection/source/icon/"
ok_img = "ok.png"
cancel_img = "cancel.png"
app_img = "app_selection_v8.png"
href_img = "href_v3.png"
update_img = "update.png"
run_img = "run.png"
download_img = "download_v2.png"
type_icon_img = ["py_v2.png", "xl_v2.png", "js_v2.png"]

version_json = "app_version.json"
package_txt = "requirements.txt"


selection_tool_wh = (300, 650)

all_contents_list = []

tab_num = 0
app_num = 0


class AppUICreator:
    style_type1 = """
        QWidget{font-size: 9pt; background: rgb(20, 31, 45); color: rgb(255, 255, 255);}
        QPushButton{background: rgb(47, 59, 76); border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
        QPushButton:hover{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242);}
        QPushButton:pressed{background: rgb(11, 125, 182);}
        QListWidget{outline: 0; border: 1px solid; border-radius: 3px; border-color: transparent;}
        QListWidget::item{height: 32px; border: 1px solid; border-radius: 3px; border-color: rgb(30, 40, 50);}
        QListWidget::item:hover{border: 1px solid; border-radius: 3px; border-color: rgb(36, 153, 242);}
        QListWidget::item:selected{background: rgb(11, 125, 182); color: rgb(255, 255, 255);}
        QScrollBar:vertical{background-color: rgb(41, 41, 41); width: 15px; margin: 2px 1px 2px 5px; border: 1px transparent #2A2929; border-radius: 4px;}
        QScrollBar::handle:vertical{background-color: rgb(63, 68, 75); min-height: 5px; border-radius: 4px;}
        QTabWidget::pane {border: none; margin: 0px 0px 0px 0px;}
        QTabBar::tab {background: rgb(44, 52, 63); font-weight: bold; width: 44px; height:38px; padding-bottom: 15px; padding-right: -2px;}
        QTabBar::tab:selected {background: rgb(6, 13, 20); border-left: 3px solid rgb(11, 125, 182); padding-left: -3px;}
        QRadioButton{}
        QRadioButton::indicator {width:12px; height:12px; background: rgb(34, 44, 60); border: 1px solid; border-radius:7px; border-color: rgb(56, 69, 90);}
        QRadioButton::indicator:hover {width:10px; height:10px; background: rgb(34, 44, 60); border: 2px solid; border-radius:7px; border-color: rgb(26, 132, 213);}
        QRadioButton::indicator:checked {width:6px; height:6px; background: rgb(255, 255, 255); border: 4px solid; border-radius:7px; border-color: rgb(26, 132, 213);}
        """

    style_type2 = """
        QPushButton{background: rgb(47, 59, 76); border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
        QPushButton:hover{border: 1px solid; border-radius: 3px; border-color: rgb(70, 150, 200);}
        QPushButton:pressed{background: rgb(31, 39, 52);}
        QPushButton:disabled{border: 1px solid; border-radius: 3px; border-color: rgb(85, 130, 160); background: rgb(100, 100, 100);}
        """

    def qwidget_create(app, style):
        temp_widget = QWidget()
        temp_widget.setStyleSheet(style)
        return temp_widget

    def qlayout_create(app, dir, target_widget, sub_widget_list, margin_type):
        if dir == 0:
            temp_layout = QHBoxLayout(target_widget)
        else:
            temp_layout = QVBoxLayout(target_widget)
        for i in sub_widget_list:
            if type(i) == int:
                temp_layout.addStretch(i)
            elif type(i) == QHBoxLayout or type(i) == QVBoxLayout:
                temp_layout.addLayout(i)
            else:
                temp_layout.addWidget(i)
        if margin_type is not None:
            margins = [(10, 6, 10, 6), (2, 2, 2, 2), (0, 0, 0, 0)]
            m1, m2, m3, m4 = margins[margin_type]
            temp_layout.setContentsMargins(m1, m2, m3, m4)
        return temp_layout

    def qpixmap_create(app, img_file_name):
        temp_pixmap = QPixmap()
        temp_img_path = img_drive_url + img_file_name
        temp_img = urllib.request.urlopen(temp_img_path).read()
        temp_pixmap.loadFromData(temp_img)
        return temp_pixmap

    def qicon_create(app, img_file_name):
        temp_pixmap = AppUICreator.qpixmap_create(app, img_file_name)
        temp_icon = QIcon()
        temp_icon.addPixmap(temp_pixmap)
        return temp_icon

    def qbtn_create(app, btn_inner, size, function):
        temp_btn = QPushButton()
        temp_btn.setFixedSize(size, size)
        if type(btn_inner) == str:
            temp_btn.setText(btn_inner)
        else:
            temp_btn.setIcon(btn_inner)
        temp_btn.clicked.connect(function)
        return temp_btn

    def qlabel_create(app, inner, w, h):
        temp_lable = QLabel()
        if type(inner) == str:
            temp_lable.setText(inner)
        else:
            temp_lable.setPixmap(inner)
        if w is not None:
            temp_lable.setFixedHeight(w)
        if h is not None:
            temp_lable.setFixedHeight(h)
        return temp_lable

    def qlineedit_create(app, default_text, value_type, phtext, align_type):
        temp_lineedit = QLineEdit(default_text, app)
        if value_type is not None:
            if value_type == 0:
                temp_lineedit.setValidator(QIntValidator(app))
            elif value_type == 1:
                temp_lineedit.setValidator(QDoubleValidator(app))
        if phtext is not None:
            temp_lineedit.setPlaceholderText(phtext)
        if align_type is not None:
            if align_type == 0:
                temp_lineedit.setAlignment(Qt.AlignCenter)
            elif align_type == 1:
                temp_lineedit.setAlignment(Qt.AlignRight)
        return temp_lineedit

    def qslider_create(app, min, max, default, funtion):
        temp_slider = QSlider(Qt.Horizontal)
        temp_slider.setStyleSheet(AppUICreator.AppUICreator.style_type1)
        temp_slider.setFixedWidth(240)
        temp_slider.setRange(min, max)
        temp_slider.setValue(default)
        temp_slider.valueChanged[int].connect(funtion)
        return temp_slider

    def qtab_create(app, style, function, position):
        temp_tabs = QTabWidget()
        temp_tabs.setStyleSheet(style)
        temp_tabs.currentChanged.connect(function)
        if position == 0:
            temp_tabs.setTabPosition(QTabWidget.West)
        return temp_tabs

    def qradio_create(app, btn_inner, w, h):
        temp_radio = QRadioButton(btn_inner)
        if w is not None:
            temp_radio.setFixedHeight(w)
        if h is not None:
            temp_radio.setFixedHeight(h)
        return temp_radio


class AppSelection(QDialog):
    select_sig = pyqtSignal(int)
    move_sig = pyqtSignal(QPoint)
    close_sig = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.initUI()

    # fmt: off
    def initUI(self):
        self.tab_widget_list = []
        self.tab_listwidget_list = []
        self.all_items_layout_list = []
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.win_cen()
        self.setFixedSize(selection_tool_wh[0], selection_tool_wh[1])

        # 전체 위젯 / 전체 레이아웃
        void_widget = AppUICreator.qwidget_create(self, "background: rgb(12, 20, 31);")

        # header layout
        header_widget = AppUICreator.qwidget_create(self, AppUICreator.style_type1)

        app_pixmap = AppUICreator.qpixmap_create(self, app_img)
        header_icon = AppUICreator.qlabel_create(self, app_pixmap, None, None)
        header_lable = AppUICreator.qlabel_create(self, " API Extension Tool", None, 24)
        header_lable.setStyleSheet("font-size: 18px;")
        header_lable.setFont(QFont("Noto Sans CJK KR Bold", 1))

        header_layout = AppUICreator.qlayout_create(self,0, header_widget, [header_icon, header_lable], None)
        header_layout.setStretchFactor(header_lable, 1)

        # 1 layout (app_type_widget)
        app_type_widget = AppUICreator.qwidget_create(self, AppUICreator.style_type1)
        self.app_type_radio0 = AppUICreator.qradio_create(self, "midas Apps", None, 24)
        app_type_radio1 = AppUICreator.qradio_create(self, "MY Apps", None, 24)
        self.app_type_radio0.setChecked(True)
        update_icon = AppUICreator.qicon_create(self, update_img)
        update_btn = AppUICreator.qbtn_create(self, update_icon, 28, self.app_list_build)
        AppUICreator.qlayout_create(self, 0, app_type_widget, [self.app_type_radio0, app_type_radio1, update_btn], 0)
        
        # 2 layout (tab_widget)
        self.tabs = AppUICreator.qtab_create(self, AppUICreator.style_type1, self.tab_changed, 0)

        for i in type_icon_img:
            tab_inner = QWidget()
            this_tab = self.tabs.addTab(tab_inner, "")
            temp_icon = AppUICreator.qicon_create(self, i)
            self.tabs.setTabIcon(this_tab, temp_icon)
            self.tabs.setIconSize(QSize(25, 25))
            tab_app_list = QListWidget()
            tab_app_list.currentItemChanged.connect(self.selected_app)
            tab_app_list.doubleClicked.connect(self.ok_fun)
            AppUICreator.qlayout_create(self, 1, tab_inner, [tab_app_list], 1)
            self.tab_widget_list.append(tab_inner)
            self.tab_listwidget_list.append(tab_app_list)

        self.app_list_build()

        # 3 layout (btn_group)
        btns_widget = AppUICreator.qwidget_create(self, AppUICreator.style_type1)

        cancel_icon = AppUICreator.qicon_create(self, cancel_img)
        cancel_btn = AppUICreator.qbtn_create(self, cancel_icon, 28, self.closeEvent)

        AppUICreator.qlayout_create(self, 0, btns_widget, [1, cancel_btn], 0)

        # main_layout
        AppUICreator.qlayout_create(self, 1, void_widget, [header_widget, app_type_widget, self.tabs, btns_widget], 1)
        void_layout = AppUICreator.qlayout_create(self, 1, self, [void_widget], 2)
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
            tab_num = self.tab_widget_list.index(self.tabs.currentWidget())
            self.selected_app()
        except:
            pass

    def selected_app(self):
        global app_num
        try:
            try:
                self.all_items_layout_list[tab_num][app_num].removeWidget(self.run_btn)
            except:
                pass
            app_num = self.tab_listwidget_list[tab_num].currentRow()
            if tab_num == 1:
                self.all_items_layout_list[tab_num][app_num].addWidget(self.download_btn)
                xl_file_name = all_contents_list[tab_num][app_num]
                temp_xl_file_path = local_contents_path + xl_file_name
                if not os.path.exists(temp_xl_file_path):
                    self.download_btn.setIcon(self.download_icon)
                    self.run_btn.setDisabled(True)
                else:
                    self.download_btn.setIcon(self.href_icon)
                    self.run_btn.setDisabled(False)
            else:
                self.run_btn.setDisabled(False)
            if tab_num != 2:
                self.all_items_layout_list[tab_num][app_num].addWidget(self.run_btn)
            self.select_sig.emit(app_num)
        except:
            pass

    def extract_apps(self, link):
        soup = extract_soup(link)
        # print(soup)
        # temp_pages = (str(soup).replace("&quot;", "\"").replace("&#039;", "'").replace("&#035;", "#").replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))
        # print(temp_pages)
        app_data_jsons = json.loads(str(soup))["payload"]["tree"]["items"]
        temp_contents_list = [i["name"] for i in app_data_jsons]
        return temp_contents_list

    def app_list_build(self):
        global app_type_num
        # independent_btn
        run_icon = AppUICreator.qicon_create(self, run_img)
        self.run_btn = AppUICreator.qbtn_create(self, run_icon, 24, self.ok_fun)
        self.run_btn.setStyleSheet(AppUICreator.style_type2)

        self.download_icon = AppUICreator.qicon_create(self, download_img)
        self.href_icon = AppUICreator.qicon_create(self, href_img)
        self.download_btn = AppUICreator.qbtn_create(self, self.download_icon, 24, self.download_fun)
        self.download_btn.setStyleSheet(AppUICreator.style_type2)

        all_contents_list.clear()
        self.all_items_layout_list.clear()
        
        app_type_num = int(self.app_type_radio0.isChecked())
        
        for i in range(len(type_icon_img)):
            self.tab_listwidget_list[i].clear()
            temp_contents_list = self.extract_apps(git_org_root_link + apps_source[app_type_num] + link_bri0 + link_bri1 + selector_list[i])
            temp_item_layout_list = []
            for j in temp_contents_list:
                item = QListWidgetItem(self.tab_listwidget_list[i])
                temp_item_widget = AppUICreator.qwidget_create(self,"background: transparent;")
                temp_item_label = AppUICreator.qlabel_create(self, j, None, None)
                temp_item_layout = AppUICreator.qlayout_create(self, 0, temp_item_widget, [temp_item_label], 1)
                temp_item_layout.setStretchFactor(temp_item_label, 1)
                self.tab_listwidget_list[i].setItemWidget(
                    item, temp_item_widget)
                temp_item_layout_list.append(temp_item_layout)
            all_contents_list.append(temp_contents_list)
            self.all_items_layout_list.append(temp_item_layout_list)
            self.tab_listwidget_list[i].setCurrentRow(0)

    def ok_fun(self):
        version_compare(version_key_type[tab_num], all_contents_list[tab_num][app_num], apps_source[app_type_num])
        self.close()

    def download_fun(self):
        xl_file_name = all_contents_list[tab_num][app_num] + "/"
        temp_xl_file_path = local_contents_path + xl_file_name
        if not os.path.exists(temp_xl_file_path):
            if not os.path.exists(local_contents_path):
                os.makedirs(local_contents_path)
            os.makedirs(temp_xl_file_path)

            temp_file_list = self.extract_apps(git_org_root_link + apps_source[app_type_num] + link_bri0 + link_bri1 + selector_list[1] + xl_file_name)

            for i in temp_file_list:
                if i != version_json:
                    url = (git_raw_root_link + apps_source[app_type_num] + link_bri1 + selector_list[1] + xl_file_name + i)
                    with open(temp_xl_file_path + i, "wb") as file:
                        response = requests.get(url)
                        file.write(response.content)
            self.selected_app()
        else:
            os.startfile(temp_xl_file_path)
    # fmt: on

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            self.move_sig.emit(self.pos())
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
        self.close()


class ManualDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    # fmt: off
    def initUI(self):
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setFixedSize(750, selection_tool_wh[1])

        # 전체 위젯 / 전체 레이아웃
        void_widget = AppUICreator.qwidget_create(self, "background: rgb(12, 20, 31);")

        # 1 layout
        self.sub_widget0 = AppUICreator.qwidget_create(self, AppUICreator.style_type1)
        self.sub_widget0.setFixedSize(746, 646)
        self.web_widget = QWebEngineView()
        self.web_widget.loadFinished.connect(self.loading_end)
        self.web_widget.setUrl(QUrl("http://127.0.0.1:5500/html_temp_0/test_html0/index.html"))
        self.web_widget.setHidden(True)

        # 2 layout (UI default)
        href_icon = AppUICreator.qicon_create(self, href_img)

        self.btns_widget = AppUICreator.qwidget_create(self, "background: transparent;")

        self.manual_link = AppUICreator.qbtn_create(self, href_icon, 28, self.web_manual)
        self.manual_link.setStyleSheet(AppUICreator.style_type1)
        self.manual_link.setFixedSize(160, 28)
        self.manual_link.setText(" Detail With Browser")

        self.sub_layout0 = AppUICreator.qlayout_create(self, 1, self.sub_widget0, [self.web_widget], 1)
        self.sub_layout1 = AppUICreator.qlayout_create(self, 1, self.btns_widget, [], 0)
        self.sub_layout1.addWidget(self.manual_link, alignment=Qt.AlignRight)
        self.main_layout = AppUICreator.qlayout_create(self, 1, void_widget, [self.sub_widget0, self.btns_widget], 1)
        self.main_layout.setStretchFactor(self.sub_widget0, 1)

        void_layout = AppUICreator.qlayout_create(self, 1, self, [void_widget], 2)
        self.setLayout(void_layout)

        self.app_connect()
        self.show()

    def loading_end(self):
        self.web_widget.setHidden(False)

    def web_manual(self):
        target_link = "https://blog.midasuser.com/ko/bridge/page/" + str(app_num)
        webbrowser.open(target_link)

    def app_connect(self):
        self.main_app = AppSelection()
        self.main_app.select_sig.connect(self.selection_changed)
        self.main_app.move_sig.connect(self.app_moved)
        self.main_app.close_sig.connect(self.app_closed)
        self.app_moved(self.main_app.pos())

    def selection_changed(self):
        try:
            if tab_num == 2:
                js_app_name = all_contents_list[tab_num][app_num]
                self.web_widget.setUrl(QUrl("https://midasd.github.io/sproj-examples/examples/" + js_app_name + "/")
                )
            else:
                if app_type_num == 1:
                    self.web_widget.setUrl(QUrl("http://127.0.0.1:5500/html_temp_" + str(tab_num) + "/test_html" + str(app_num + 1) + "/index.html"))
                else:
                    self.web_widget.setUrl(QUrl("http://127.0.0.1:5500/html_per_temp_" + str(tab_num) + "/test_html" + str(app_num + 1) + "/index.html"))
                
        except:
            pass

    def app_moved(self, pos_dist):
        self.activateWindow()
        self.move(pos_dist + QPoint(selection_tool_wh[0], 0))

    def app_closed(self):
        self.close()
    # fmt: on

first_app = QApplication([sys.argv, "--no-sandbox"])
dialog = ManualDialog()

print(time.time() - start)

first_app.exec_()