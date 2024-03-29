# -*- coding:UTF-8 -*-
import sys
import os
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import subprocess
import threading
from queue import *
from PyQt5.QtWidgets import QMessageBox
import datetime
import time
import win32gui
from win32api import *
from win32con import *
import win32event
import win32process
import ctypes
import win32com.client
from win32com import *

import configparser
from PyQt5.QtCore import pyqtSlot
import pika
from apscheduler.schedulers.background import BackgroundScheduler

import resources_rc

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.initMenu()
        self.initOthers()

    def initMenu(self):
        # 设计托盘的菜单，这里我实现了一个二级菜单
        mainmenu = QMenu()
        self.menu1 = QMenu("重启服务")
        self.menu1.setIcon(QtGui.QIcon(":/images/setup.png"))
        for item in self.parent().mu2.actions():
            self.menu1.addAction(item)

        self.menu2 = QMenu("编译版本")
        self.menu2.setIcon(QtGui.QIcon(":/images/start.png"))
        for item in self.parent().mu1.actions():
            self.menu2.addAction(item)

        self.menu3 = QMenu("下载最新")
        self.menu3.setIcon(QtGui.QIcon(":/images/download.png"))
        for item in self.parent().mu3.actions():
            self.menu3.addAction(item)

        self.menu4 = QMenu("查看历史")
        self.menu4.setIcon(QtGui.QIcon(":/images/history.png"))
        for item in self.parent().mu4.actions():
            self.menu4.addAction(item)

        self.showme = QAction(icon=QtGui.QIcon(":/images/screen.png"), text="显示", parent=self, triggered=self.parent().toggleVisibility)
        mainmenu.addAction(self.showme)
        autorun = QAction("下次自动启动", self, checkable=True)
        ret = False
        keyNames = [r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
                    r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run']
        for item in keyNames:
            if _get_valuenames(item).__contains__(_abspath.upper()):
                ret = True; break
        autorun.setChecked(ret)
        autorun.triggered.connect(self.toggleStartup)
        mainmenu.addAction(autorun)
        mainmenu.addSeparator()
        mainmenu.addMenu(self.menu1)
        mainmenu.addMenu(self.menu2)
        mainmenu.addMenu(self.menu3)
        mainmenu.addMenu(self.menu4)
        mainmenu.addSeparator()
        exit = QAction(QtGui.QIcon(":/images/exit.png"), "退出", self, triggered=self.quit)
        mainmenu.addAction(exit)
        self.setContextMenu(mainmenu)

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
        self.showMessage("提示", "你点击了消息", self.icon)

    def quit(self):
        # 保险起见，为了完整的退出
        self.setVisible(False)
        # self.parent().exit()
        qApp.quit()
        sys.exit()

    def toggleStartup(self, checked):
        remove = not checked
        try:
            key = RegOpenKey(HKEY_LOCAL_MACHINE, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, KEY_ALL_ACCESS)
            if remove:
                RegDeleteValue(key, _basename)
            else:
                RegSetValueEx(key, _basename, 0, REG_SZ, _abspath)
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

def _get_work_area():
    # cx = GetSystemMetrics(SM_CXSCREEN)  # 获得屏幕分辨率X轴
    # cy = GetSystemMetrics(SM_CYSCREEN)  # 获得屏幕分辨率Y轴
    rect = RECT()
    ctypes.windll.user32.SystemParametersInfoA(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect

def _get_valuenames(fullname):
    ret = []
    key = _reg_open_key(fullname)
    if key is not None:
        info = RegQueryInfoKey(key)
        for i in range(0, info[1]):
            valuename = RegEnumValue(key, i)
            ret.append(valuename[1].upper())
            # print(str.ljust(valuename[0], 20), valuename[1])
        RegCloseKey(key)
    return ret

def _reg_open_key(fullname):
    name = str.split(fullname, '\\', 1)
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
    return key

class VERSION:
    def __init__(self, key='', name='', path='', url='', fireon='N/A', task=None):
        self.task = task
        self.key = key
        self.name = name
        self.base_path = path
        self.tfs_url = url
        fireon = fireon.replace(" ", "")
        self.fire_enabled = not fireon.upper().__contains__("N/A")
        self.fire_on = []
        if self.fire_enabled:
            for item in fireon.split(";"):
                self.fire_on.append(datetime.datetime.strptime(item, "%H:%M" if len(item) == 5 else "%H:%M:%S").time() or None)

def _get_version():
    ret = VERSION()
    path = _get_key_value(r'HKEY_LOCAL_MACHINE\SOFTWARE\JetSun\3.0', 'ExecutablePath')
    for item in _dict.items():
        if path.__contains__(item[1].base_path.upper()):
            ret = item[1]; break
    return ret

def _get_reg_basepath():
    ret = _get_version().base_path
    return ret

def _get_regfilepath(key = ''):
    v = _get_version() if key == '' else _dict[key]
    ret = r"%s\BatchFiles\注册表\%s注册表.reg" % (v.base_path, v.name) if v.base_path != '' else ''
    return ret

def _get_key_value(fullname, valuename):
    ret = ''
    key = _reg_open_key(fullname)
    if key is not None:
        info = RegQueryValueEx(key, valuename)
        ret = info[0].upper()
        RegCloseKey(key)
    return ret

class window(QMainWindow):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        dt = datetime.datetime.fromtimestamp(os.stat(_abspath).st_mtime)
        self.setWindowTitle("作业调度控制器 - BuiltOn: %s" % dt.strftime('%Y/%m/%d %H:%M:%S'))
        rect = _get_work_area()
        self.resize(480, 360)
        self.setGeometry(rect.right-self.width()-10, rect.bottom-self.height()-10, self.width(), self.height())
        self.status = self.statusBar()
        self.setWindowIcon(QtGui.QIcon(':/images/clock.ico'))
        self._consumer = ConsumeThread(self.run, _work_queue, _out_queue)
        self._consumer.setDaemon(True)
        self._consumer.start()
        self._responser = ResponseThread(self.pull_work_queue)
        self._responser.setDaemon(True)
        self._responser.start()

        self.mu1 = QMenu()
        for item in _dict.items():
            act = QAction(text=item[1].name, checkable=True, parent=self.mu1)
            act.setStatusTip(r"%s\BatchFiles\全编译Upload.bat" % item[1].base_path)
            self.mu1.addAction(act)
            item[1].task = Task(act, True)
        self.mu1.actions()[0].setIcon(QtGui.QIcon(":/images/location.png"))
        self.mu1.setTearOffEnabled(False)
        self.mu1.triggered[QAction].connect(self.processtrigger)

        self.mu2 = QMenu()
        act0 = QAction(icon=QtGui.QIcon(":/images/setup1.png"), text="服务", parent=self.mu2, triggered=self.restart_service)
        act1 = QAction(text="所有配置", parent=self.mu2, triggered=self.restart_all)
        act2 = QAction(text="配置文件...", parent=self.mu2, triggered=self.edit_configuration)
        act3 = QAction(text="文件夹(递归)可写...", parent=self.mu2, triggered=self.make_folder_writable)
        self.mu2.addAction(act0)
        self.mu2.addAction(act1)
        self.mu2.addAction(act2)
        self.mu2.addAction(act3)
        self.mu2.setTearOffEnabled(False)

        self.mu3 = QMenu()
        for item in _dict.items():
            act = QAction(text=item[1].name, checkable=True, parent=self.mu3)
            act.setStatusTip(r"%s\BatchFiles\TF_GET_MedicalHealth.bat" % item[1].base_path)
            self.mu3.addAction(act)
        self.mu3.actions()[0].setIcon(QtGui.QIcon(":/images/location.png"))
        self.mu3.setTearOffEnabled(False)
        self.mu3.triggered[QAction].connect(self.get_latest_version)

        self.mu4 = QMenu()
        for item in _dict.items():
            act = QAction(text=item[1].name, checkable=True, parent=self.mu4)
            act.setStatusTip("%s %s" % (os.path.join(_dirname, "TFSH.exe"), item[1].tfs_url))
            self.mu4.addAction(act)
        self.mu4.actions()[0].setIcon(QtGui.QIcon(":/images/location.png"))
        self.mu4.setTearOffEnabled(False)
        self.mu4.triggered[QAction].connect(self.show_latest_history)

        self.ti = TrayIcon(self)
        tbrMain = self.addToolBar("Scheduler")
        start = QAction(QtGui.QIcon(":/images/start.png"), "启动", self)
        start.setToolTip("启动编译任务")
        start.setMenu(self.mu1)
        tbrMain.addAction(start)
        getlatest = QAction(QtGui.QIcon(":/images/download.png"), "下载", self)
        getlatest.setToolTip("获取最新版本")
        getlatest.setMenu(self.mu3)
        tbrMain.addAction(getlatest)
        showhistory = QAction(QtGui.QIcon(":/images/history.png"), "历史", self)
        showhistory.setToolTip("查看历史记录")
        showhistory.setMenu(self.mu4)
        tbrMain.addAction(showhistory)
        setup = QAction(QtGui.QIcon(":/images/setup.png"), "设置", self)
        setup.setMenu(self.mu2)
        tbrMain.addAction(setup)
        clear = QAction(icon=QtGui.QIcon(":/images/clear.png"), text="清空队列", parent=self, triggered=self.clear_work_queue)
        clear.setToolTip("清空待调度队列")
        tbrMain.addAction(clear)
        tbrMain.addSeparator()
        shutdown = QAction(QtGui.QIcon(":/images/close.png"), "退出", self, triggered=self.ti.quit)
        tbrMain.addAction(shutdown)
        # 设置名称显示在图标下面（默认本来是只显示图标）
        tbrMain.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        tbrMain.actionTriggered.connect(self.toolbarpressed)

        self._date = datetime.date
        self._minute = datetime.datetime.now().minute
        self.txtMsg = QTextEdit()
        self.txtMsg.setReadOnly(True)
        self.txtMsg.setStyleSheet("color:rgb(10,10,10);font-size:14px;font-weight:normal;font-family:Roman times;")
        self.setCentralWidget(self.txtMsg)
        self.status.installEventFilter(self)
        self.ti.show()
        scheduler = BackgroundScheduler()
        # 每隔 1秒钟 运行一次 job 方法
        scheduler.add_job(self.func_timer, 'interval', seconds=1, args=[])
        scheduler.start()

    @pyqtSlot()
    def on_edit_textChanged(self):
        self.txtMsg.ensureCursorVisible()

    @pyqtSlot(int, int)
    def change_scroll(self, min, max):
        self.txtMsg.verticalScrollBar().setSliderPosition(max)

    # 覆写窗口隐藏事件
    def hideEvent(self, event) :
        self.ti.showme.setIcon(QtGui.QIcon(":/images/screen.png"))
        self.ti.showme.setText("显示")
        # self.update()

    # 覆写窗口显示事件
    def showEvent(self, event) :
        self.ti.showme.setIcon(QtGui.QIcon(":/images/noscreen.png"))
        self.ti.showme.setText("隐藏")
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
        elif opt == "下载":
            self.get_latest_default(sender)
        elif opt == "设置":
            pass
        self.status.showMessage("%s: 正在执行 %s ..." % (time.strftime('%H:%M:%S'), opt), 5000)

    def start_default(self, sender):
        found = False
        for act in sender.menu().actions():
            if act.isChecked():
                self.push_queue(Task(act, True))
                found = True
        if not found:
            self.processtrigger(sender.menu().actions()[0])

    def showStatus(self, text, movecursor=True):
        self.txtMsg.append(text)
        if movecursor:
            self.txtMsg.moveCursor(QTextCursor.End)

    def restart_service(self):
        task = self.get_service_task()
        if task is not None:
            self.push_queue(task)

    def get_service_task(self):
        found = False
        computer = "."
        service = "jssvcl"
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(computer, "root\cimv2")
        colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_Service WHERE name = '%s'" % service)
        for item in colItems:
            oldpath = item.PathName is not None and item.PathName or ""
            self.showStatus("%s: 服务已安装在 %s" % (time.strftime('%H:%M:%S'), oldpath))
            found = True
        if not found:
            bp = _get_reg_basepath()
            if bp != '':
                oldpath = r'"%s\Lib\jssvc.exe"' % bp
            self.showStatus("%s: 服务 %s 已卸载，请重新安装！" % (time.strftime('%H:%M:%S'), service))

        if oldpath is not None:
            newpath = oldpath
            key = self.get_cur_ver_key()
            if key != '':
                newpath = r'"%s\Lib\jssvc.exe"' % _dict[key].base_path
            cmd = '_$RestartLocalService.bat %s %s' % (oldpath, newpath)
            task = Task(QAction(text="本地服务", statusTip=cmd), False, _dirname)
        return task

    def restart_all(self):
        key = self.get_cur_ver_key()
        if key == '': return

        workdir = os.path.join(_dict[key].base_path, "BatchFiles")
        r = _get_regfilepath(key)
        if r != '' and os.path.exists(r) and os.path.isfile(r):
            # subprocess.call([r"C:\Windows\regedit.exe", "/s", r], shell=False, cwd=r"C:\Windows", stdin=None, stdout=None, stderr=None, timeout=None)
            task1 = Task(QAction(text="导入注册表文件", statusTip=r"C:\Windows\regedit.exe /s %s" % r), False, r"C:\Windows")

        # subprocess.call(os.path.join(workdir, "__copy2svcbin.bat"), shell=False, cwd=workdir, stdin=None, stdout=None, stderr=None, timeout=None)
        # subprocess.call(["cmd.exe", "/C", "__copy2svcbin.bat"], shell=False, cwd=workdir, stdin=None, stdout=None, stderr=None, timeout=None)
        # ShellExecute(0, 'open', os.path.join(workdir, "__copy2svcbin.bat"), '', workdir, 1)  # 最后一个参数bShow: 1(0)表示前台(后台)运行程序; 传递参数path打开指定文件
        # handle = win32process.CreateProcess(os.path.join(workdir, "__copy2svcbin.bat"), '', None, None, 0, win32process.CREATE_NEW_CONSOLE, None, None, win32process.STARTUPINFO()) # 创建进程获得句柄
        # win32event.WaitForSingleObject(handle[0], win32event.INFINITE)  # 等待进程结束
        task2 = Task(QAction(text="执行__copy2svcbin.bat", statusTip=os.path.join(workdir, "__copy2svcbin.bat")), False)
        task3 = self.get_service_task()
        if task1 is not None: self.push_queue(task1)
        if task2 is not None: self.push_queue(task2)
        if task3 is not None: self.push_queue(task3)

    def edit_configuration(self):
        try_times = 1
        run_cnt = 0
        while run_cnt < try_times:
            try:
                self.showStatus("%s: 编辑配置文件%s ..." % (time.strftime('%H:%M:%S'), _configuration_file))
                # subprocess.call(["notepad", os.path.join(_dirname, _configuration_file)], cwd=_dirname, shell=False, stdin=None, stdout=None, stderr=None, timeout=300)
                ShellExecute(0, 'open', "notepad", os.path.join(_dirname, _configuration_file), _dirname, 1)  # 最后一个参数showCmd: 1(0)表示前台(后台)运行程序
            except subprocess.TimeoutExpired:
                self.showStatus("%s: 记事本程序运行超时！" % time.strftime('%H:%M:%S'))
                continue
            else:
                break
            finally:
                run_cnt += 1

    # QFileDialog.getExistingDirectory()  返回选中的文件夹路径
    # QFileDialog.getOpenFileName()  返回选中的文件路径
    # QFileDialog.getOpenFileNames()  返回选中的多个文件路径
    # QFileDialog.getSaveFileName()  存储文件
    def make_folder_writable(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "选取文件夹", _dirname)
        if folder_selected != "":
            ShellExecute(0, 'open', os.path.join(_dirname, "sfw.exe"), folder_selected, _dirname, 1) # win32api.ShellExecute(0, lpVerb, cmd, params, cmdDir, showCmd)

    def get_cur_ver_key(self):
        ret = ''
        for act in self.mu1.actions():
            if act.isChecked():
                ret = act.text(); break
        return ret

    def processtriggerX(self, sender):
        path = os.path.dirname(sender.statusTip())
        t = threading.Thread(target=self.runCmd, args=(sender.statusTip(), path))
        t.start()

    def processtrigger(self, qaction):
        self.push_queue(Task(qaction, True))

    def push_queue(self, task, remote=False, host_ip=''):
        header = remote and "[来自%s]" % host_ip or '[本地请求]'
        self.showStatus("%s: %s %s 任务已入队..." % (time.strftime('%H:%M:%S'), header, task.id))
        for item in _tasks_todo:
            if task.id == item.id: return
        _tasks_todo.append(task)
        _work_queue.put(task)

    # def runCmd(self, cmd, path):
        # 语法：subprocess.Popen(args, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False, startupinfo=None, creationflags=0)
        # subprocess.Popen 不会阻止正在执行的线程，这是与subprocess.call的区别。
        # res = subprocess.Popen(cmd, shell=False, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # sout, serr = res.communicate() # 该方法和子进程交互，返回一个包含 输出和错误的元组，如果对应参数没有设置的，则无法返回
        # return res.returncode, sout, serr, res.pid # 可获得返回码、输出、错误、进程号；
        # subprocess.check_call(cmd, shell=False, cwd=path, stdin=None, stdout=None, stderr=None, timeout=None)
        # subprocess.call 会阻止正在执行的线程，直到该命令子进程执行完， timeout参数为等待秒数，时间到则结束子进程并抛出异常（timeout=None则一直等待）
        # subprocess.call(cmd, shell=False, cwd=path, stdin=None, stdout=None, stderr=None, timeout=None)

    def run(self, task):
        if task.add_arg:
            for act in task.qaction.parent().actions():
                act.setChecked(True if task.qaction == act else False)

        cmd = '%s "%s"' % (task.cmd, _get_regfilepath()) if task.add_arg else task.cmd
        subprocess.call(cmd, shell=False, cwd=task.path, stdin=None, stdout=None, stderr=None, timeout=None)
        print("Worker Solve: %s" % task)
        self.showStatus("%s: %s 任务已执行结束。" % (time.strftime('%H:%M:%S'), task.id))
        return task

    # 使用pyinstaller打包python程序，使用 - w参数，去掉console，发现执行命令行的subprocess相关语句报“[ERROR][WinError 6] 句柄无效”的错误。去掉 - w参数，将console显示的话，就正常
    # 可行的解决方案是用subpross.Popen来替代subprocess.check_output，Popen函数加入如下参数：shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    # Popen方法执行命令，父进程不会等待子进程。这个时候需要用wait()方法来等待运行的结果（所以定义如下方法提供本地调用）。
    def subprocess_check_output(self, *args):
        p = subprocess.Popen(*args, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        status = p.wait()
        return out
        # msg = ''
        # for line in p.stdout.readlines():
        #     msg += line.decode("gbk", "ignore")
        # _statusBar = p.wait()
        # return msg

    def get_latest_version(self, qaction):
        try:
            for act in qaction.parent().actions():
                act.setChecked(True if qaction == act else False)
            workdir = os.path.join(_dict[qaction.text()].base_path, "BatchFiles")
            fn = os.path.join(workdir, "TF_GET_MedicalHealth.bat")
            # self.showStatus("%s: 执行命令 %s ..." % (time.strftime('%H:%M:%S'), fn))
            if os.path.exists(fn) and os.path.isfile(fn):
                output = self.subprocess_check_output(fn)
                response = output.decode("gbk", "ignore")
                self.txtMsg.setText("%s: 下载最新[%s]...\r\n%s" % (time.strftime('%H:%M:%S'), qaction.text(), response))
        except Exception as e:
            self.showStatus(str(e))
        finally:
            return

    def show_latest_history(self, qaction):
        try:
            for act in qaction.parent().actions():
                act.setChecked(True if qaction == act else False)
            fn = os.path.join(_dirname, "TFSH.exe")
            if os.path.exists(fn) and os.path.isfile(fn):
                output = self.subprocess_check_output([fn, _dict[qaction.text()].tfs_url])
                response = output.decode("gbk", "ignore")
                self.txtMsg.setText("%s: 查看历史[%s]...\r\n%s" % (time.strftime('%H:%M:%S'), qaction.text(), response))
        except Exception as e:
            self.showStatus(str(e))
        finally:
            return

    def get_latest_default(self, sender):
        found = False
        for act in sender.menu().actions():
            if act.isChecked():
                self.get_latest_version(act)
                found = True
        if not found:
            self.get_latest_version(sender.menu().actions()[0])

    def clear_work_queue(self):
        try:
            self.txtMsg.clear()
            while not _work_queue.empty():
                task = _work_queue.get(False)
                self.showStatus("%s: %s 任务已移除..." % (time.strftime('%H:%M:%S'), task.id))
        except Queue.Empty:
            pass  # Handle empty queue here
        finally:
            _tasks_todo.clear()
            return  # Handle task here and call q.task_done()

    #（1）threading.Timer()主要有2个参数：第一个参数为时间，第二个参数为函数名；
    #（2）必须在定时器执行函数内部重复构造定时器，因为定时器构造后只执行1次，必须循环调用；
    #（3）定时器间隔单位是秒，可以是浮点数，如5.5，0.02等；
    #（4）使用cancel停止定时器的工作；
    def func_timer(self):
        self.check_fired()
        self.check_finished()
        self.check_isalive()

    def check_fired(self):
        if  self._minute != datetime.datetime.now().minute:
            self._minute = datetime.datetime.now().minute
            if not os.path.exists('logs'):
                os.makedirs('logs')
            with open(r'logs\check_fired_%s.log' % time.strftime('%Y-%m-%d'), 'a', encoding='utf-8') as f:
                f.write('\ncheck_fired: %s' % time.strftime('%H:%M:%S'))

        if datetime.date != self._date:
            self._date = datetime.date
            self.showStatus(time.strftime("%Y-%m-%d %H:%M:%S"))

        for item in _dict.items():
            if item[1].fire_enabled:
                dt = datetime.datetime.now().time()
                dt = datetime.time(dt.hour, dt.minute, dt.second)
                if dt in item[1].fire_on:
                    self.push_queue(item[1].task)

    def check_finished(self):
        if not _out_queue.empty():
            for i in range(_out_queue.qsize()):
                item = _out_queue.get()  # q.get会阻塞，q.get_nowait()不阻塞，但会抛异常
                self.push_out_queue(item.id)
                _tasks_todo.remove(item)
                msg = u"任务%s已完成" % item.id
                dt = datetime.datetime.now().time()
                if 9 <= dt.hour <= 18: # 上班期间弹出消息框
                    # MessageBox(0, msg, u"任务调度结果", MB_OK | MB_ICONINFORMATION | MB_TOPMOST | MB_SYSTEMMODAL)
                    # ctypes.windll.user32.MessageBoxA(0, msg.encode('gb2312'), u"任务调度结果".encode('gb2312'), MB_OK | MB_ICONINFORMATION | MB_TOPMOST)
                    # ShellExecute(0, 'open', os.path.join(_dirname, "MessageBox.exe"), msg, _dirname, 1)  # 最后一个参数bShow: 1(0)表示前台(后台)运行程序; 传递参数path打开指定文件
                    # subprocess.call会阻止正在执行的线程，直到该程序完成 timeout超时秒数结束进程并抛出异常
                    subprocess.call([os.path.join(_dirname, "MessageBox.exe"), msg], cwd=_dirname, shell=False, stdin=None, stdout=None, stderr=None, timeout=120)

    def check_isalive(self):
        if not self._consumer.isAlive():
            self._consumer = ConsumeThread(self.run, _work_queue, _out_queue)
            self._consumer.setDaemon(True)
            self._consumer.start()
        if not self._responser.isAlive():
            self._responser = ResponseThread(self.pull_work_queue)
            self._responser.setDaemon(True)
            self._responser.start()

    def push_out_queue(self, message):
        for key in _remote_messages:
            names = str.split(_remote_messages[key], ',')
            if names.__contains__(message):
                self.push_specified_queue(key, message)
                remains = []
                for item in names:
                    if item != message:
                        remains.append(item)
                _remote_messages[key] = ','.join(remains)
                self.showStatus("%s: %s:%s" % (time.strftime('%H:%M:%S'), key, _remote_messages[key]))

    def push_specified_queue(self, queue_name, message):
        username = 'guest'
        pwd = 'guest'
        ip_addr = 'localhost'
        # rabbitmq 报错 pika.exceptions.IncompatibleProtocolError: StreamLostError: (‘Transport indicated EOF’,) 产生此报错的原因是我将port写成了15672
        # rabbitmq需要通过端口5672连接 - 而不是15672. 更改端口，转发，一切正常
        port_num = 5672
        credentials = pika.PlainCredentials(username, pwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, port_num, '/', credentials))
        channel = connection.channel()
        channel.queue_declare(queue_name, durable=True)
        channel.basic_publish(
            exchange = '',
            routing_key = queue_name,  # 写明将消息发送给队列balance
            body = message,  # 要发送的消息
            properties = pika.BasicProperties(delivery_mode=2, )  # 设置消息持久化(持久化第二步)，将要发送的消息的属性标记为2，表示该消息要持久化
        )  # 向消息队列发送一条消息
        connection.close()

    def pull_work_queue(self):
        username = 'guest'
        pwd = 'guest'
        ip_addr = 'localhost'
        # rabbitmq 报错 pika.exceptions.IncompatibleProtocolError: StreamLostError: (‘Transport indicated EOF’,) 产生此报错的原因是我将port写成了15672
        # rabbitmq 需要通过端口5672连接 - 而不是15672. 更改端口，转发，一切正常
        port_num = 5672
        credentials = pika.PlainCredentials(username, pwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, port_num, '/', credentials))
        channel = connection.channel()
        channel.queue_declare('work_queue', durable=True)
        for message in channel.consume('work_queue', auto_ack=True, inactivity_timeout=1):
            if not message: continue
            method, properties, body = message  # message 是一个三元组<class 'tuple'>:(None, None, None)，分别赋值给(method, properties, body)三个变量
            if body is not None:
                msg = body.decode('utf-8')
                self.status.showMessage("%s: %s" % (time.strftime('%H:%M:%S'), msg))
                names = str.split(msg, ';')
                key = names[0]
                if not _remote_messages.keys().__contains__(key) or _remote_messages[key] == '':
                    _remote_messages[key] = names[1]
                else:
                    _remote_messages[key] += ',' + names[1]
                for item in _dict.items():
                    if item[1].name == names[1]:
                        self.showStatus("%s: %s|%s" % (time.strftime('%H:%M:%S'), key, item[1].task.id))
                        self.push_queue(item[1].task, True, key)
        connection.close()

class Task(object):
    def __init__(self, qaction=QAction(), add_arg=False, path=''):
        self.qaction = qaction
        self.id = qaction.text()
        self.cmd = qaction.statusTip()
        self.add_arg = add_arg
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

class ConsumeThread(threading.Thread):
    # def __init__(self, func, args, work_queue, out_queue):
    # self.args = args
    def __init__(self, func, work_queue, out_queue):
        super(ConsumeThread, self).__init__()
        self.func = func
        self.work_queue = work_queue
        self.out_queue = out_queue
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True

    def run(self):
        if self.__running.isSet():
            for item in self.work_queue:
                result = self.func(item)
                self.out_queue.put(result)
        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            time.sleep(1)

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False

class ResponseThread(threading.Thread):
    def __init__(self, func):
        super(ResponseThread, self).__init__()
        self.func = func
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True

    def run(self):
        if self.__running.isSet():
            self.func()
        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            time.sleep(1)

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False

# WINDOWS系统判断进程是否存在
def proc_exist(process_name):
    is_exist = False
    wmi = win32com.client.GetObject('winmgmts:')
    processCodeCov = wmi.ExecQuery('select * from Win32_Process where name=\"%s\"' %(process_name))
    if len(processCodeCov) > 2: # 因为自身启动会启动进程（且进程数为2）
        is_exist = True
    if is_exist:
        log('\"%s\" is running, proc_cnt:%s' %(process_name, len(processCodeCov)))
    else:
        log('\"%s\" no such process...' %(process_name))
    return is_exist

# LINUX系统判断进程是否存在
def progress_exist(progress_name):
    try:
        progress_num = int(os.popen('ps -ef | grep ' + progress_name + ' | grep -v grep | wc -l').read())
        if progress_num > 2:
            return {'name': progress_name, 'status': 1}
        else:
            return {'name': progress_name, 'status': 0}
    except Exception as e:
        log("Unexpected error:" + str(e))
    return {'name': progress_name, 'status': 0}

def log(msg):
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    logstr = '%s : %s \n' % (now, msg)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    with open(r'logs\check_running_%s.log' % time.strftime('%Y-%m-%d'), 'a', encoding='utf-8') as f:
        f.write(logstr)

if __name__ == "__main__":
    _configuration_file = "cfg.ini";
    _tasks_todo = []
    _remote_messages = {}
    _abspath = sys.argv[0]
    _basename = os.path.basename(_abspath) # 获取文件名
    _dirname = os.path.dirname(_abspath) # 获取路径名
    os.chdir(_dirname)  # 改变当前运行路径，注意双引号和反斜杠（避免设置随操作系统启动时运行报错“Failed to execute script xxx.exe”问题）
    print(os.getcwd())  # 查看当前工作目录
    if proc_exist(_basename):
        sys.exit(1)

    _dict = {}
    _interval = 1
    _conf = configparser.ConfigParser()
    _conf.read(os.path.join(_dirname, _configuration_file), encoding='utf-16')
    for sec in _conf.sections():
        _dict[sec] = VERSION(_conf.get(sec, 'key'), _conf.get(sec, 'name'), _conf.get(sec, 'base-path'), _conf.get(sec, 'tfs-url'), _conf.get(sec, 'fire-on'))
    print(_dict)
    _work_queue = ClosableQueue()
    _out_queue = ClosableQueue()

    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(":/images/clock.ico"))
    win = window()
    win.hide()
    sys.exit(app.exec_())
