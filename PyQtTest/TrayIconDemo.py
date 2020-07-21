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
import win32com.client
import configparser
import copy

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
        for item in self.parent().mu2.actions():
            self.menu1.addAction(item)

        self.menu2 = QMenu("编译版本")
        self.menu2.setIcon(QtGui.QIcon(":/images/start.png"))
        for item in self.parent().mu1.actions():
            self.menu2.addAction(item)

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
    # cx = GetSystemMetrics(SM_CXSCREEN)  # 获得屏幕分辨率X轴
    # cy = GetSystemMetrics(SM_CYSCREEN)  # 获得屏幕分辨率Y轴
    rect = RECT()
    ctypes.windll.user32.SystemParametersInfoA(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect

class window(QMainWindow):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle("作业调度控制器")
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
        for item in _dict.items():
            print(item)
            act = QAction(text=item[1].name, checkable=True, parent=self.mu1)
            act.setStatusTip("%s/BatchFiles/全编译Upload.bat" % item[1].base_path)
            self.mu1.addAction(act)
        self.mu1.actions()[0].setIcon(QtGui.QIcon(":/images/location.png"))
        self.mu1.setTearOffEnabled(False)
        self.mu1.triggered[QAction].connect(self.processtrigger)

        self.mu2 = QMenu()
        act0 = QAction(icon=QtGui.QIcon(":/images/setup1.png"), text="服务", parent=self.mu2, triggered=self.restart_service)
        act1 = QAction(text="配置", parent=self.mu2)
        act2 = QAction(text="调度计划", parent=self.mu2)
        self.mu2.addAction(act0)
        self.mu2.addAction(act1)
        self.mu2.addAction(act2)
        self.mu2.setTearOffEnabled(False)

        tbrMain = self.addToolBar("Scheduler")
        self.startAct = QAction(QtGui.QIcon(":/images/start.png"), "启动", self)
        self.startAct.setMenu(self.mu1)
        tbrMain.addAction(self.startAct)
        pause = QAction(QtGui.QIcon(":/images/pause.png"), "暂停", self)
        tbrMain.addAction(pause)
        setup = QAction(QtGui.QIcon(":/images/setup.png"), "设置", self)
        setup.setMenu(self.mu2)
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
        self.txtMsg.setStyleSheet("color:rgb(10,10,10,255);font-size:14px;font-weight:normal;font-family:Roman times;")
        self.setCentralWidget(self.txtMsg)
        self.status.installEventFilter(self)
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

    def eventFilter(self, watched, event):
        if watched == self.status and event.type() == QEvent.MouseButtonDblClick:
            print("pos: ", event.pos())
            self.txtMsg.clear()
        return QWidget.eventFilter(self, watched, event)

    def toggleVisibility(self):
        if self.isVisible():
            self.hide_window()
        else:
            self.show_window()

    def show_window(self):
        hwnd = self.winId()
        win32gui.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        self.showNormal()
        # self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        # self.activateWindow()

    def hide_window(self):
        hwnd = self.winId()
        win32gui.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        self.hide()

    def toolbarpressed(self, sender):
        opt = sender.text()
        if opt == "启动":
            self.start_default(sender)
        elif opt == "暂停":
            print("按下的ToolBar按钮是 %s" % opt)
        elif opt == "设置":
            print("按下的ToolBar按钮是 %s" % opt)
        self.status.showMessage("正在执行 %s ..." % opt, 5000)

    def start_default(self, sender):
        found = False
        for act in sender.menu().actions():
            if act.isChecked():
                self.push_queue(Task(act))
                found = True
        if not found:
            self.processtrigger(sender.menu().actions()[0])

    def restart_service(self):
        found = False
        computer = "."
        service = "jssvcl"
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(computer, "root\cimv2")
        colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_Service WHERE name='%s'" % service)
        for item in colItems:
            oldpath = item.PathName != None and item.PathName or ""
            self.txtMsg.append("服务已安装在 %s" % oldpath)
            found = True
        if not found:
            oldpath = ""
            self.txtMsg.append("服务 %s 已卸载，请重新安装服务！" % service)
        newpath = oldpath
        key = self.get_current_version()
        if key != '':
            newpath = '"%s\Lib\jssvc.exe"' % _dict[key].base_path
        cmd = '_$RestartLocalService.bat ' + oldpath + ' ' + newpath
        print(cmd)
        self.push_queue(Task(QAction(text="本地服务", statusTip=cmd), os.path.dirname(sys.argv[0])))


    def processtriggerX(self, qaction):
        path = os.path.dirname(qaction.statusTip())
        t = Thread(target=self.runCmd, args=(qaction.statusTip(), path))
        t.start()

    def get_current_version(self):
        ret = ""
        for act in self.mu1.actions():
            if act.isChecked():
                ret = act.text()
        return ret

    def processtrigger(self, qaction):
        for act in qaction.parent().actions():
            act.setChecked(True if qaction == act else False)
        self.push_queue(Task(qaction))

    def push_queue(self, task):
        self.work_queue.put(task)
        self.txtMsg.append("%s 任务已进入调度队列，等待执行中..." % task.id)
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
    def __init__(self, qaction=QAction(), path=''):
        self.id = qaction.text()
        self.cmd = qaction.statusTip()
        self.path = path == '' and os.path.dirname(qaction.statusTip()) or path
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

class VERSION:
    def __init__(self):
        self.key = ''
        self.name = ''
        self.base_path = ''


if __name__ == "__main__":
    _dict = {}
    conf = configparser.ConfigParser()
    conf.read('cfg.ini', encoding='utf-16')
    for sec in conf.sections():
        ver = VERSION()
        ver.key = conf.get(sec, 'key')
        ver.name = conf.get(sec, 'name')
        ver.base_path = conf.get(sec, 'base_path')
        _dict[sec] = ver
    print(_dict)

    timer_interval = 1
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(":/images/scheduler.ico"))
    win = window()
    win.hide()
    win.fun_timer()
    sys.exit(app.exec_())
