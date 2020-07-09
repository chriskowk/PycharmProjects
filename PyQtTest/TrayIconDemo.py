import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.initMenu()
        self.initOthers()

    def initMenu(self):
        # 设计托盘的菜单，这里我实现了一个二级菜单
        self.menu = QMenu()
        self.menu1 = QMenu("二级菜单")
        self.menu1.setIcon(QIcon('images/start.png'))

        self.showAction1 = QAction("显示消息1", self, triggered=self.showMsg)
        self.showAction2 = QAction("显示消息2", self, triggered=self.showMsg)
        self.quitAction = QAction(QIcon('images/exit.png'), "退出", self, triggered=self.quit)

        self.menu1.addAction(self.showAction1)
        self.menu1.addAction(self.showAction2)
        self.menu.addMenu(self.menu1)

        self.menu.addAction(self.showAction1)
        self.menu.addAction(self.showAction2)
        self.menu.addSeparator()
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

    def initOthers(self):
        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.iconClicked)
        # 把鼠标点击弹出消息的信号和槽连接
        self.messageClicked.connect(self.msgClicked)
        self.setIcon(QIcon("images/tray.ico"))
        # 设置图标
        self.icon = self.MessageIcon()

    def iconClicked(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            pw = self.parent()
            if pw.isVisible():
                pw.hide()
            else:
                pw.show()
                pw.setWindowState(Qt.WindowActive)
        # print(reason)

    def msgClicked(self):
        self.showMessage("提示", "你点了消息", self.icon)

    def showMsg(self):
        self.showMessage("测试", "我是消息", self.icon)

    def quit(self):
        # 保险起见，为了完整的退出
        self.setVisible(False)
        self.parent().exit()
        qApp.quit()
        sys.exit()


class window(QMainWindow):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle("文件处理器")
        self.resize(400, 300)
        self.status = self.statusBar()
        ti = TrayIcon(self)
        ti.show()

    def closeEvent(self, event):  # 覆写窗口关闭事件（函数名固定不可变）
        event.ignore()  # 忽视点击X事件
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images/tray.ico"))
    win = window()
    win.show()
    sys.exit(app.exec_())
