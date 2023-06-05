try:
    import sys
    import re
    import webbrowser

    import urllib.request

    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWebEngineWidgets import QWebEngineView

    import time
    
except:
    pass
start = time.time()


app_language = ['py_app_ver', 'xl_app_ver', 'js_app_ver']

py_selector = "python_app/"
xl_selector = "excel_app/"
js_selector = "javascript_app/"

git_org_link = "https://github.com/lsb1109/apitest/tree/main/"
git_raw_link = "https://raw.githubusercontent.com/lsb1109/apitest/main/"

js_drive_url = "https://github.com/kh1012/sproj-examples/tree/main/examples/"

local_contents_path = r"C:\Temp\CIM_API_APP\\"

tab_selector = "a.js-navigation-open.Link--primary"
tab_link_list = [git_org_link + py_selector,
                 git_org_link + xl_selector, js_drive_url]

img_drive_url = "https://patch.midasit.com/00_MODS/kr/80_WebResource/CIM/lsb1109apptest/0_app_selection/source/icon/"
ok_img = "ok.png"
app_img = "app_selection_v3.png"
href_img = "href_v3.png"
update_img = "update.png"
run_img = "run.png"
download_img = "download_v2.png"
type_icon_img = ["py_v2.png", "xl_v2.png", "js_v2.png"]

version_json = "app_version.json"
package_txt = "requirements.txt"

selection_tool_wh = [300, 650]

all_contents_list = [0]

tab_num = 0
app_num = 0

style_type1 = '''
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
    '''

style_type2 = '''
    QPushButton{background: rgb(47, 59, 76); border: 1px solid; border-radius: 3px; border-color: rgb(56, 69, 90);}
    QPushButton:hover{border: 1px solid; border-radius: 3px; border-color: rgb(70, 150, 200);}
    QPushButton:pressed{background: rgb(31, 39, 52);}
    '''


try:
    class AppSelection(QDialog):
        select_sig = pyqtSignal(int)
        move_sig = pyqtSignal(QPoint)
        btn_sig = pyqtSignal(int)
        close_sig = pyqtSignal(int)

        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            self.tab_widget_list = []
            self.tab_listwidget_list = []
            self.all_items_layout_list = []
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.win_cen()
            self.setFixedSize(selection_tool_wh[0], selection_tool_wh[1])

            # 전체 위젯 / 전체 레이아웃
            void_widget = self.qwidget_create("background: rgb(12, 20, 31);")

            # header layout
            header_widget = self.qwidget_create(style_type1)

            app_pixmap = self.qpixmap_create(app_img)
            header_icon = self.qlable_create(app_pixmap)
            header_lable = self.qlable_create("API Extension Tool")
            header_lable.setFixedHeight(24)
            header_lable.setStyleSheet("font-size: 18px;")
            header_lable.setFont(QFont("Noto Sans CJK KR Bold", 1))

            header_layout = self.qlayout_create(
                0, header_widget, [header_icon, header_lable], None)
            header_layout.setStretchFactor(header_lable, 1)

            # 1 layout (tab_widget)
            self.tabs = self.qtab_create(style_type1, self.tab_changed, 0)

            for i in type_icon_img:
                tab_inner = QWidget()
                this_tab = self.tabs.addTab(tab_inner, "")
                temp_icon = self.qicon_create(i)
                self.tabs.setTabIcon(this_tab, temp_icon)
                self.tabs.setIconSize(QSize(25, 25))
                tab_app_list = QListWidget()
                tab_app_list.currentItemChanged.connect(self.selected_app)
                tab_app_list.doubleClicked.connect(self.ok_fun)
                self.qlayout_create(1, tab_inner, [tab_app_list], (2, 2, 2, 2))
                self.tab_widget_list.append(tab_inner)
                self.tab_listwidget_list.append(tab_app_list)

            self.app_list_build()

            # 2 layout (btn_group)
            sub_widget1 = self.qwidget_create(style_type1)

            update_icon = self.qicon_create(update_img)
            update_btn = self.qbtn_create(update_icon, 28, self.app_list_build)

            self.qlayout_create(0, sub_widget1, [1, update_btn], (10, 6, 10, 6))

            # main_layout
            self.qlayout_create(
                1, void_widget, [header_widget, self.tabs, sub_widget1], (2, 2, 2, 2))
            void_layout = self.qlayout_create(1, self, [void_widget], (0, 0, 0, 0))
            self.setLayout(void_layout)

            # independent_btn
            run_icon = self.qicon_create(run_img)
            self.run_btn = self.qbtn_create(run_icon, 24, self.ok_fun)
            self.run_btn.setStyleSheet(style_type2)
            self.all_items_layout_list[tab_num][app_num].addWidget(self.run_btn)

            self.download_icon = self.qicon_create(download_img)
            self.href_icon = self.qicon_create(href_img)
            self.download_btn = self.qbtn_create(
                self.download_icon, 24, self.download_fun)
            self.download_btn.setStyleSheet(style_type2)

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
                    self.all_items_layout_list[tab_num][app_num].removeWidget(
                        self.run_btn)
                except:
                    pass
                app_num = self.tab_listwidget_list[tab_num].currentRow()
                if tab_num == 1:
                    self.all_items_layout_list[tab_num][app_num].addWidget(
                        self.download_btn)
                    xl_file_name = all_contents_list[tab_num][app_num]
                    temp_xl_file_path = local_contents_path + xl_file_name
                    if not os.path.isfile(temp_xl_file_path):
                        self.download_btn.setIcon(self.download_icon)
                    else:
                        self.download_btn.setIcon(self.href_icon)
                self.all_items_layout_list[tab_num][app_num].addWidget(
                    self.run_btn)
                self.select_sig.emit(app_num)
            except:
                pass

        def convert_soup_data(self, link, search):
            soup = extract_soup(link)
            temp_list = soup.select(search)
            temp_contents = [re.search('>(.+?)<', str(i)).group(1)
                            for i in temp_list]
            return temp_contents

        def app_list_build(self):
            all_contents_list.clear()
            self.all_items_layout_list.clear()
            for i in range(len(type_icon_img)):
                self.tab_listwidget_list[i].clear()
                temp_contents = self.convert_soup_data(tab_link_list[i], tab_selector)
                temp_contents_list = [temp_contents[j]
                                    for j in range(len(temp_contents))]
                temp_item_layout_list = []
                for j in temp_contents_list:
                    item = QListWidgetItem(self.tab_listwidget_list[i])
                    temp_item_widget = self.qwidget_create(
                        "background: transparent;")
                    temp_item_label = self.qlable_create(j)
                    temp_item_layout = self.qlayout_create(
                        0, temp_item_widget, [temp_item_label], (6, 0, 4, 0))
                    temp_item_layout.setStretchFactor(temp_item_label, 1)
                    self.tab_listwidget_list[i].setItemWidget(
                        item, temp_item_widget)
                    temp_item_layout_list.append(temp_item_layout)
                all_contents_list.append(temp_contents_list)
                self.all_items_layout_list.append(temp_item_layout_list)
                self.tab_listwidget_list[i].setCurrentRow(0)

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

        def qlable_create(self, inner):
            temp_lable = QLabel()
            if type(inner) == str:
                temp_lable.setText(inner)
            else:
                temp_lable.setPixmap(inner)
            return temp_lable

        def qtab_create(self, style, function, position):
            temp_tabs = QTabWidget()
            temp_tabs.setStyleSheet(style)
            temp_tabs.currentChanged.connect(function)
            if position == 0:
                temp_tabs.setTabPosition(QTabWidget.West)
            return temp_tabs

        def ok_fun(self):
            version_compare(app_language[tab_num], all_contents_list[tab_num][app_num])
            self.close()

        def download_fun(self):
            xl_file_name = all_contents_list[tab_num][app_num]
            temp_xl_file_path = local_contents_path + xl_file_name
            if not os.path.isfile(temp_xl_file_path):
                if not os.path.exists(local_contents_path):
                    os.makedirs(local_contents_path)
                url = git_raw_link + xl_selector + xl_file_name
                with open(temp_xl_file_path, "wb") as file:
                    response = requests.get(url)
                    file.write(response.content)
                self.selected_app()
            else:
                os.startfile(local_contents_path)

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


    class ManualDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            self.setWindowFlags(
                Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.win_cen()
            self.setFixedSize(750, selection_tool_wh[1])

            # 전체 위젯 / 전체 레이아웃
            void_widget = self.qwidget_create("background: rgb(12, 20, 31);")

            # 1 layout
            self.sub_widget0 = self.qwidget_create(style_type1)
            self.sub_widget0.setFixedSize(746, 646)
            self.web_widget = QWebEngineView()
            self.web_widget.loadFinished.connect(self.loading_end)
            self.web_widget.setUrl(
                QUrl("http://127.0.0.1:5500/html_temp_" + str(tab_num) + "/test_html" + str(app_num + 1) + "/index.html"))
            self.web_widget.setHidden(True)

            # 2 layout (UI default)
            href_icon = self.qicon_create(href_img)

            self.sub_widget1 = self.qwidget_create("background: transparent;")

            self.manual_link = self.qbtn_create(href_icon, 28, self.web_manual)
            self.manual_link.setStyleSheet(style_type1)
            self.manual_link.setFixedSize(160, 28)
            self.manual_link.setText(" Detail With Browser")

            self.sub_layout0 = self.qlayout_create(
                1, self.sub_widget0, [self.web_widget], (0, 6, 0, 6))
            self.sub_layout1 = self.qlayout_create(
                1, self.sub_widget1, [], (0, 6, 12, 6))
            self.sub_layout1.addWidget(self.manual_link, alignment=Qt.AlignRight)
            self.main_layout = self.qlayout_create(
                1, void_widget, [self.sub_widget0, self.sub_widget1], (2, 2, 2, 2))
            self.main_layout.setStretchFactor(self.sub_widget0, 1)

            void_layout = self.qlayout_create(1, self, [void_widget], (0, 0, 0, 0))
            self.setLayout(void_layout)

            self.app_connect()
            self.show()

        def win_cen(self):
            qr = self.frameGeometry()
            cp = QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft() + QPoint(selection_tool_wh[0], 0))

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

        def qlable_create(self, inner):
            temp_lable = QLabel()
            if type(inner) == str:
                temp_lable.setText(inner)
            else:
                temp_lable.setPixmap(inner)
            return temp_lable

        def loading_end(self):
            self.web_widget.setHidden(False)

        def web_manual(self):
            target_link = "https://blog.midasuser.com/ko/bridge/page/" + \
                str(app_num)
            webbrowser.open(target_link)

        def app_connect(self):
            self.main_app = AppSelection()
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
    dialog = ManualDialog()

    print(time.time() - start)

    first_app.exec_()

except:
    pass

selected_tab = tab_num
selected_app = app_num
