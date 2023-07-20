import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("230812 test", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.resize(300, 100)
        self.show()
    
    def closeEvent(self, event):
        self.close()


if __name__ == "__main__":
    app = QApplication([sys.argv,  '--no-sandbox'])
    form = Window()
    sys.exit(app.exec_())