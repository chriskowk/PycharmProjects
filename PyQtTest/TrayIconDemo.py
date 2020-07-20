import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui
import subprocess
import os
from threading import *
from queue import *
from PyQt5.QtWidgets import QMessageBox
import time
import win32gui
from win32api import *
from win32con import *
import ctypes
import resources_rc

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.initMenu()
        self.initOthers()

    def initMenu(self):
        # 设计托盘的菜单，这里我实现了一个二级菜单
        self.menu = QMenu()
        self.menu1 = QMenu("重启服务")
        self.menu1.setIcon(QtGui.QIcon(":/images/setup.png"))
        seviceAct = QAction(icon=QtGui.QIcon(":/images/setup1.png"), text="服务", parent=self.menu1)
        configAct = QAction(text="配置", parent=self.menu1)
        scheduleAct = QAction(text="调度", parent=self.menu1)
        self.menu1.addAction(seviceAct)
        self.menu1.addAction(configAct)
        self.menu1.addAction(scheduleAct)

        self.menu2 = QMenu("编译版本")
        self.menu2.setIcon(QtGui.QIcon(":/images/start.png"))
        act0 = QAction(icon=QtGui.QIcon(":/images/location.png"), text="中山眼科", checkable=True, parent=self.menu2)
        act0.setStatusTip("E:/VSTS/MedicalHealth/BatchFiles/全编译Upload.bat")
        act1 = QAction(text="省医", checkable=True, parent=self.menu2)
        act1.setStatusTip("E:/MedicalHealthSY/BatchFiles/全编译Upload.bat")
        act2 = QAction(text="市一", checkable=True, parent=self.menu2)
        act2.setStatusTip("E:/MedicalHealthS1/BatchFiles/全编译Upload.bat")
        self.menu2.addAction(act0)
        self.menu2.addAction(act1)
        self.menu2.addAction(act2)
        self.menu2.triggered[QAction].connect(self.parent().processtrigger)

        self.basename = os.path.basename(sys.argv[0])
        self.path = sys.argv[0]
        self.keyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'

        self.showAct = QAction(icon=QtGui.QIcon(":/images/screen.png"), text="显示", parent=self, triggered=self.parent().toggleVisibility)
        self.menu.addAction(self.showAct)
        autoStartupAct = QAction("下次自动启动", self, checkable=True)
        ret = False
        keyNames = ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run',
                    r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run']
        for keyName in keyNames:
            ret = ret or self.get_values(keyName).__contains__(self.path.upper())
        autoStartupAct.setChecked(ret)
        autoStartupAct.triggered.connect(self.toggleStartup)
        self.menu.addAction(autoStartupAct)

        self.menu.addSeparator()
        self.menu.addMenu(self.menu1)
        self.menu.addMenu(self.menu2)
        pauseAct = QAction(icon=QtGui.QIcon(":/images/pause.png"), text="暂停调度", parent=self)
        self.menu.addAction(pauseAct)

        self.menu.addSeparator()
        self.quitAction = QAction(QtGui.QIcon(":/images/exit.png"), "退出", self, triggered=self.quit)
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

    def initOthers(self):
        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.iconClicked)
        # 把鼠标点击弹出消息的信号和槽连接
        self.messageClicked.connect(self.msgClicked)
        self.setIcon(QtGui.QIcon(":/images/schedule.ico"))
        # 设置图标
        self.icon = self.MessageIcon()

    def iconClicked(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            self.parent().toggleVisibility()

    def msgClicked(self):
        self.showMessage("提示", "你点了消息", self.icon)

    def quit(self):
        # 保险起见，为了完整的退出
        self.setVisible(False)
        self.parent().exit()
        qApp.quit()
        sys.exit()

    def get_values(self, fullname):
        ret = []
        name = str.split(fullname, '\\', 1)
        try:
            if name[0] == 'HKEY_LOCAL_MACHINE':
                key = RegOpenKey(HKEY_LOCAL_MACHINE, name[1], 0, KEY_READ)
            elif name[0] == 'HKEY_CURRENT_USER':
                key = RegOpenKey(HKEY_CURRENT_USER, name[1], 0, KEY_READ)
            elif name[0] == 'HKEY_CLASSES_ROOT':
                key = RegOpenKey(HKEY_CLASSES_ROOT, name[1], 0, KEY_READ)
            elif name[0] == 'HKEY_CURRENT_CONFIG':
                key = RegOpenKey(HKEY_CURRENT_CONFIG, name[1], 0, KEY_READ)
            elif name[0] == 'HKEY_USERS':
                key = RegOpenKey(HKEY_USERS, name[1], 0, KEY_READ)
            else:
                raise ValueError('Error,no key named', name[0])
            info = RegQueryInfoKey(key)
            for i in range(0, info[1]):
                valuename = RegEnumValue(key, i)
                ret.append(valuename[1].upper())
                # print(str.ljust(valuename[0], 20), valuename[1])
            RegCloseKey(key)
        except Exception as e:
            print('发生异常:', str(e))
        return ret

    def toggleStartup(self, sender):
        remove = not sender
        try:
            key = RegOpenKey(HKEY_LOCAL_MACHINE, self.keyName, 0, KEY_ALL_ACCESS)
            if remove:
                RegDeleteValue(key, self.basename)
            else:
                RegSetValueEx(key, self.basename, 0, REG_SZ, self.path)
                RegCloseKey(key)
        except (OSError, TypeError) as reason:
            print('错误的原因是:', str(reason))

class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]

def get_work_area():
  rect = RECT()
  ctypes.windll.user32.SystemParametersInfoA(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
  return rect

class window(QMainWindow):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle("作业调度控制器")
        cx = GetSystemMetrics(SM_CXSCREEN)  # 获得屏幕分辨率X轴
        cy = GetSystemMetrics(SM_CYSCREEN)  # 获得屏幕分辨率Y轴
        rect = get_work_area()
        self.resize(400, 300)
        self.setGeometry(rect.right-self.width()-10, rect.bottom-self.height()-10, self.width(), self.height())
        self.status = self.statusBar()
        self.setWindowIcon(QtGui.QIcon(':/images/scheduler.ico'))
        self.work_queue = ClosableQueue()
        self.out_queue = ClosableQueue()
        consumer = Consumer(self.run, self.work_queue, self.out_queue)
        consumer.start()
        self.mu1 = QMenu()
        act0 = QAction(icon=QtGui.QIcon(":/images/location.png"), text="中山眼科", checkable=True, parent=self.mu1)
        act0.setStatusTip("E:/VSTS/MedicalHealth/BatchFiles/全编译Upload.bat")
        act1 = QAction(text="省医", checkable=True, parent=self.mu1)
        act1.setStatusTip("E:/MedicalHealthSY/BatchFiles/全编译Upload.bat")
        act2 = QAction(text="市一", checkable=True, parent=self.mu1)
        act2.setStatusTip("E:/MedicalHealthS1/BatchFiles/全编译Upload.bat")
        self.mu1.addAction(act0)
        self.mu1.addAction(act1)
        self.mu1.addAction(act2)
        self.mu1.setTearOffEnabled(False)
        self.mu1.triggered[QAction].connect(self.processtrigger)

        mu2 = QMenu()
        act20 = QAction(icon=QtGui.QIcon(":/images/setup1.png"), text="服务", parent=mu2)
        act21 = QAction(text="配置", parent=mu2)
        act22 = QAction(text="调度计划", parent=mu2)
        mu2.addAction(act20)
        mu2.addAction(act21)
        mu2.addAction(act22)
        mu2.setTearOffEnabled(False)

        tbrMain = self.addToolBar("Scheduler")
        start = QAction(QtGui.QIcon(":/images/start.png"), "启动", self)
        start.setMenu(self.mu1)
        tbrMain.addAction(start)
        pause = QAction(QtGui.QIcon(":/images/pause.png"), "暂停", self)
        tbrMain.addAction(pause)
        setup = QAction(QtGui.QIcon(":/images/setup.png"), "设置", self)
        setup.setMenu(mu2)
        tbrMain.addAction(setup)
        tbrExit = self.addToolBar("Exit")
        close = QAction(QtGui.QIcon(":/images/close.png"), "退出", self)
        tbrExit.addAction(close)
        # 设置名称显示在图标下面（默认本来是只显示图标）
        tbrMain.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        tbrExit.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        tbrMain.actionTriggered.connect(self.toolbarpressed)
        self.ti = TrayIcon(self)
        tbrExit.actionTriggered.connect(self.ti.quit)
        self.txtMsg = QTextEdit()
        self.txtMsg.setReadOnly(True)
        self.txtMsg.setStyleSheet("color:rgb(10,10,10,255);font-size:16px;font-weight:normal;font-family:Roman times;")
        self.setCentralWidget(self.txtMsg)
        # self.txtMsg.setText(sys.argv[0].upper())
        self.ti.show()

    # 覆写窗口隐藏事件
    def hideEvent(self, event) :
        self.ti.showAct.setIcon(QtGui.QIcon(":/images/screen.png"))
        self.ti.showAct.setText("显示")
        # self.update()

    # 覆写窗口显示事件
    def showEvent(self, event) :
        self.ti.showAct.setIcon(QtGui.QIcon(":/images/noscreen.png"))
        self.ti.showAct.setText("隐藏")
        # self.update()

    # 覆写窗口关闭事件（函数名固定不可变）
    def closeEvent(self, event):
        event.ignore()  # 忽视点击X事件
        self.hide()

    # 覆写窗口失焦事件
    def focusOutEvent(self, event):
        self.hide()

    def toggleVisibility(self):
        s = self.windowState()
        if self.isVisible():
            if s == Qt.WindowMinimized:
                self.showNormal()
                self.show()
            else:
                self.hide()
        else:
            self.showNormal()
            self.show()
            # self.setWindowState(Qt.WindowActive)

    def toolbarpressed(self, sender):
        print("按下的ToolBar按钮是", sender.text())
        self.status.showMessage(sender.text(), 5000)

    def processtriggerX(self, qaction):
        path = os.path.dirname(qaction.statusTip())
        t = Thread(target=self.runCmd, args=(qaction.statusTip(), path))
        t.start()

    def syncmenuchecked(self, qa):
        for act in self.mu1.actions():
            act.setChecked(True if qa.text() == act.text() else False)
        for act in self.ti.menu2.actions():
            act.setChecked(True if qa.text() == act.text() else False)

    def processtrigger(self, qaction):
        for act in qaction.parent().actions():
            act.setChecked(True if qaction == act else False)
        self.syncmenuchecked(qaction)
        self.work_queue.put(Task(qaction))
        self.txtMsg.append("%s 任务已进入调度队列，等待执行中..." % qaction.text())
        # self.work_queue.close()
        # self.work_queue.join()

    def runCmd(self, cmd, path):
        # 语法：subprocess.Popen(args, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False, startupinfo=None, creationflags=0)
        # res = subprocess.Popen(cmd, shell=False, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # sout, serr = res.communicate() # 该方法和子进程交互，返回一个包含 输出和错误的元组，如果对应参数没有设置的，则无法返回
        # return res.returncode, sout, serr, res.pid # 可获得返回码、输出、错误、进程号；
        # subprocess.check_call(cmd, shell=False, cwd=path, stdin=None, stdout=None, stderr=None, timeout=None)
        subprocess.call(cmd, shell=False, cwd=path, stdin=None, stdout=None, stderr=None, timeout=None)

    def run(self, task) :
        subprocess.call(task.cmd, shell=False, cwd=task.path, stdin=None, stdout=None, stderr=None, timeout=None)
        print("Worker Solve: %s" % task)
        self.txtMsg.append("%s 任务已执行结束。" % task.id)
        return task

    def fun_timer(self):
        # print(time.strftime('%Y-%m-%d %H:%M:%S'))
        global timer
        timer = Timer(timer_interval, self.fun_timer)
        timer.start()
        if not self.out_queue.empty():
            for i in range(self.out_queue.qsize()):
                item = self.out_queue.get()  # q.get会阻塞，q.get_nowait()不阻塞，但会抛异常
                argv = "任务%s已完成" % item.id
                subprocess.call("F:/GitHub/PycharmProjects/PyQtTest/dist/MessageBox.exe %s" % argv, shell=False, stdin=None, stdout=None, stderr=None, timeout=None)

class Task(object):
    def __init__(self, qaction=QAction()):
        self.id = qaction.text()
        self.cmd = qaction.statusTip()
        self.path = os.path.dirname(qaction.statusTip())
    def __repr__(self):
        return "任务(ID:%s)" % self.id
    def __str__(self):
        return "任务ID: %s" % self.id

class ClosableQueue(Queue):
    TERMINATOR = Task()
    def close(self):
        self.put(self.TERMINATOR)
    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.TERMINATOR:
                    return  # Exit Thread
                yield item
            finally:
                self.task_done()

class Consumer(Thread):
    # def __init__(self, func, args, work_queue, out_queue):
    # self.args = args
    def __init__(self, func, work_queue, out_queue):
        super().__init__()
        self.func = func
        self.task = work_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.task:
            result = self.func(item)
            self.out_queue.put(result)


if __name__ == "__main__":
    timer_interval = 1
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(":/images/scheduler.ico"))
    win = window()
    win.hide()
    win.fun_timer()
    sys.exit(app.exec_())
