from testlayout import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class hello_window(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.push_click)
        # 给button 的 点击动作绑定一个事件处理函数

    def push_click(self):
        print('* push_click')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = hello_window()
    window.show()
    sys.exit(app.exec_())
