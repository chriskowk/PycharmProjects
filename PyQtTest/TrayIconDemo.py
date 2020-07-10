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
        self.menu1 = QMenu("重启")
        self.menu1.setIcon(QIcon('images/start.png'))
        seviceAct = QAction("服务", self, triggered=self.showMsg)
        configAct = QAction("配置", self, triggered=self.showMsg)
        scheduleAct = QAction("调度", self, triggered=self.showMsg)
        self.menu1.addAction(seviceAct)
        self.menu1.addAction(configAct)
        self.menu1.addAction(scheduleAct)

        self.menu2 = QMenu("版本")
        self.menu2.setIcon(QIcon('images/location.png'))
        version1 = QAction("中山眼科", self, checkable=True)
        version2 = QAction("省医", self, checkable=True)
        version3 = QAction("市一", self, checkable=True)
        self.menu2.addAction(version1)
        self.menu2.addAction(version2)
        self.menu2.addAction(version3)

        showAct = QAction("显示/隐藏", self, triggered=self.toggleVisibility)
        self.menu.addAction(showAct)
        autoStartupAct = QAction("下次自动启动", self, checkable=True)
        autoStartupAct.setChecked(True)
        autoStartupAct.triggered.connect(self.toggleStartup)
        self.menu.addAction(autoStartupAct)

        self.menu.addSeparator()
        self.menu.addMenu(self.menu1)
        self.menu.addMenu(self.menu2)

        self.menu.addSeparator()
        self.quitAction = QAction(QIcon('images/exit.png'), "退出", self, triggered=self.quit)
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
            self.toggleVisibility()

    def toggleVisibility(self):
        win = self.parent()
        if win.isVisible():
            win.hide()
        else:
            win.show()
            win.setWindowState(Qt.WindowActive)

    def msgClicked(self):
        self.showMessage("提示", "你点了消息", self.icon)

    def showMsg(self):
        self.showMessage("测试", "我是消息", self.icon)

    def toggleStartup(self):
        self.showMessage("测试", "自动启动程序", self.icon)

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
        self.setWindowTitle("作业调度控制器")
        self.resize(400, 300)
        self.status = self.statusBar()

        tbrMain = self.addToolBar("Scheduler")
        start = QAction(QIcon('images/start.png'), "启动", self)
        tbrMain.addAction(start)
        pause = QAction(QIcon('images/pause.png'), "暂停", self)
        tbrMain.addAction(pause)
        setup = QAction(QIcon('images/setup.png'), "设置", self)
        tbrMain.addAction(setup)
        tbrExit = self.addToolBar("Exit")
        close = QAction(QIcon('images/close.png'), "退出", self)
        tbrExit.addAction(close)
        # 设置名称显示在图标下面（默认本来是只显示图标）
        tbrMain.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        tbrExit.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        tbrMain.actionTriggered.connect(self.toolbarpressed)
        ti = TrayIcon(self)
        tbrExit.actionTriggered.connect(ti.quit)
        textEdit = QTextEdit()
        # textEdit.setReadOnly(True)
        textEdit.setStyleSheet("color:rgb(10,10,10,255);font-size:16px;font-weight:normal;font-family:Roman times;")
        self.setCentralWidget(textEdit)
        ti.show()

    def toolbarpressed(self, sender):
        print("按下的ToolBar按钮是", sender.text())
        self.status.showMessage(sender.text(), 5000)

    def closeEvent(self, event):  # 覆写窗口关闭事件（函数名固定不可变）
        event.ignore()  # 忽视点击X事件
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images/tray.ico"))
    win = window()
    win.show()
    sys.exit(app.exec_())
