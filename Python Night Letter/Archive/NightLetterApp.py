import sys
from PyQt5.QtWidgets import QDialog, QApplication
from TestMain import Ui_MainWindow

class AppWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.showMaximized()  

app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())
