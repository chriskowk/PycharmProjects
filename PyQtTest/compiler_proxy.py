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
import socket
import configparser
from PyQt5.QtCore import pyqtSlot
import pika

import resources_rc

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.initMenu()
        self.initOthers()

    def initMenu(self):
        # 设计托盘的菜单
        mainmenu = QMenu()
        self.showme = QAction(icon=QtGui.QIcon(":/images/screen.png"), text="显示", parent=self, triggered=self.parent().toggleVisibility)
        mainmenu.addAction(self.showme)
        mainmenu.addSeparator()
        exit = QAction(QtGui.QIcon(":/images/exit.png"), "退出", self, triggered=self.quit)
        mainmenu.addAction(exit)
        self.setContextMenu(mainmenu)

    def initOthers(self):
        # 把鼠标点击图标的信号和槽连接
        self.activated.connect(self.iconClicked)
        # 把鼠标点击弹出消息的信号和槽连接
        # self.messageClicked.connect(self.msgClicked)
        self.setIcon(QtGui.QIcon(":/images/proxy.ico"))
        # 设置图标
        self.icon = self.MessageIcon()

    def iconClicked(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            self.parent().toggleVisibility()

    def quit(self):
        # 保险起见，为了完整的退出
        self.setVisible(False)
        self.parent().exit()
        qApp.quit()
        sys.exit()

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

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def get_file_modify_time(path, filename):
    dt = datetime.datetime(1900, 1, 1)
    if os.path.exists(path):
        # 获取该目录下的所有文件或文件夹目录
        files = os.listdir(path)
        for file in files:
            # 得到该文件下所有目录的路径
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path) and file.lower() == filename.lower():
                dt = datetime.datetime.fromtimestamp(os.stat(full_path).st_mtime)
                # file_modify_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt))
                # print("%s 修改时间是: %s" % (full_path, file_modify_time))
                break

    return dt

def check_files_compiled(version):
    modify_time = get_file_modify_time(version.upload_path, "DataModel.Cis.Oracle.dll")
    # print("modify_time=%s version.requested_on=%s version.upload_path=%s" % (modify_time, version.requested_on, version.upload_path))
    return modify_time > version.requested_on

class VERSION:
    def __init__(self, key='', name='', basepath='', url='', uploadpath='', fireon='N/A', task=None):
        self.task = task
        self.key = key
        self.name = name
        self.base_path = basepath
        self.tfs_url = url
        self.upload_path = uploadpath
        self.requested_on = datetime.datetime.now()
        self.is_running = False
        fireon = fireon.replace(" ", "")
        self.fire_enabled = not fireon.upper().__contains__("N/A")
        self.fire_on = []
        if self.fire_enabled:
            for item in fireon.split(";"):
                self.fire_on.append(datetime.datetime.strptime(item, "%H:%M" if len(item) == 5 else "%H:%M:%S").time() or None)

class Consumer(threading.Thread):
    def __init__(self, func):
        super(Consumer, self).__init__()
        self._func = func
        self._is_interrupted = False

    def stop(self):
        self._is_interrupted = True

    def run(self):
        username = 'chris'
        pwd = '123456'
        ip_addr = '172.18.99.177'
        # rabbitmq 报错 pika.exceptions.IncompatibleProtocolError: StreamLostError: (‘Transport indicated EOF’,)
        # 产生此报错的原因是我将port写成了15672; rabbitmq需要通过端口5672连接 - 而不是15672. 更改端口，转发，一切正常
        port_num = 5672
        credentials = pika.PlainCredentials(username, pwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, port_num, '/', credentials))
        channel = connection.channel()
        channel.queue_declare(_host_ip, durable=True)
        for message in channel.consume(_host_ip, auto_ack=True, inactivity_timeout=1):
            if self._is_interrupted: break
            if not message: continue
            method, properties, body = message
            if body is not None:
                msg = body.decode('utf-8')
                self._func(msg)
        connection.close()

class window(QMainWindow):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        dt = datetime.datetime.fromtimestamp(os.stat(_abspath).st_mtime)
        self.setWindowTitle("编译请求客户端 - BuiltOn: %s" % dt.strftime('%Y/%m/%d %H:%M:%S'))
        rect = _get_work_area()
        self.resize(480, 360)
        self.setGeometry(rect.right-self.width()-10, rect.bottom-self.height()-10, self.width(), self.height())
        self._statusBar = self.statusBar()
        self._consumer = Consumer(self.show_message)
        self._consumer.start()
        self._status = 0
        self._message = ''
        self._duration = 0
        self._counter = 0

        self.mu1 = QMenu()
        for item in _dict.items():
            act = QAction(text=item[1].name, checkable=True, parent=self.mu1)
            self.mu1.addAction(act)
        self.mu1.actions()[0].setIcon(QtGui.QIcon(":/images/location.png"))
        self.mu1.setTearOffEnabled(False)
        self.mu1.triggered[QAction].connect(self.processtrigger)

        self._ti = TrayIcon(self)
        tbrMain = self.addToolBar("Scheduler")
        start = QAction(QtGui.QIcon(":/images/send.png"), "发送请求", self)
        start.setFont(QtGui.QFont("宋体", 11, QFont.Normal))
        start.setMenu(self.mu1)
        tbrMain.addAction(start)
        self._et = QAction(QtGui.QIcon(":/images/bell.png"), "00:00:00", self, triggered=self.bell_clicked)
        self._et.setFont(QtGui.QFont("Microsoft YaHei", 11, QFont.Normal))
        tbrMain.addAction(self._et)
        tbrMain.addSeparator()
        shutdown = QAction(QtGui.QIcon(":/images/close.png"), "退出", self, triggered=self._ti.quit)
        shutdown.setFont(QtGui.QFont("宋体", 11, QFont.Normal))
        tbrMain.addAction(shutdown)
        # 设置名称显示在图标下面（默认本来是只显示图标）
        tbrMain.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        tbrMain.actionTriggered.connect(self.toolbarpressed)

        self._txtMsg = QTextEdit()
        self._txtMsg.setReadOnly(True)
        self._txtMsg.setStyleSheet("color:rgb(10,10,10,255);font-size:15px;font-weight:normal;font-family:Roman times;")
        self.setCentralWidget(self._txtMsg)
        self._statusBar.installEventFilter(self)
        self._ti.show()

    @pyqtSlot()
    def on_edit_textChanged(self):
        self._txtMsg.ensureCursorVisible()

    @pyqtSlot(int, int)
    def change_scroll(self, min, max):
        self._txtMsg.verticalScrollBar().setSliderPosition(max)

    # 覆写窗口隐藏事件
    def hideEvent(self, event) :
        self._ti.showme.setIcon(QtGui.QIcon(":/images/screen.png"))
        self._ti.showme.setText("显示")
        # self.update()

    # 覆写窗口显示事件
    def showEvent(self, event) :
        self._ti.showme.setIcon(QtGui.QIcon(":/images/noscreen.png"))
        self._ti.showme.setText("隐藏")
        # self.update()

    # 覆写窗口关闭事件（函数名固定不可变）
    def closeEvent(self, event):
        event.ignore()  # 忽视点击X事件
        self.hide()

    def eventFilter(self, watched, event):
        if watched == self._statusBar and event.type() == QEvent.MouseButtonDblClick:
            print("pos: ", event.pos())
            self._txtMsg.clear()
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

    def hide_window(self):
        hwnd = self.winId()
        win32gui.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        self.hide()

    def bell_clicked(self, sender):
        self._et.setText("00:00:00")

    def toolbarpressed(self, sender):
        opt = sender.text()
        if opt == "发送请求":
            self.start_default(sender)
        self._statusBar.showMessage("%s: 正在执行 %s ..." % (time.strftime('%H:%M:%S'), opt), 5000)

    def start_default(self, sender):
        found = False
        for act in sender.menu().actions():
            if act.isChecked():
                self.processtrigger(act)
                found = True
        if not found:
            self.processtrigger(sender.menu().actions()[0])

    def showStatus(self, text, movecursor=True):
        self._txtMsg.append(text)
        if movecursor:
            self._txtMsg.moveCursor(QTextCursor.End)

    def processtrigger(self, qaction):
        for act in qaction.parent().actions():
            act.setChecked(True if qaction == act else False)
        msg = qaction.text()
        _dict[msg].requested_on = datetime.datetime.now()
        _dict[msg].is_running = True
        username = 'chris'
        pwd = '123456'
        ip_addr = '172.18.99.177'
        # rabbitmq 报错 pika.exceptions.IncompatibleProtocolError: StreamLostError: (‘Transport indicated EOF’,) 产生此报错的原因是我将port写成了15672
        # rabbitmq需要通过端口5672连接 - 而不是15672. 更改端口，转发，一切正常
        port_num = 5672
        credentials = pika.PlainCredentials(username, pwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, port_num, '/', credentials))
        channel = connection.channel()
        channel.queue_declare('work_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='work_queue',  # 写明将消息发送给队列balance
            body=_host_ip + ';' + msg,  # 要发送的消息
            properties=pika.BasicProperties(delivery_mode=2, )  # 设置消息持久化(持久化第二步)，将要发送的消息的属性标记为2，表示该消息要持久化
        )  # 向消息队列发送一条消息
        connection.close()
        self._status = 1
        self._message = msg
        self._duration = 0
        self.showStatus("%s: [%s] 编译任务已入队... " % (time.strftime('%H:%M:%S'), msg))

    def show_message(self, msg):
        if _dict[msg].is_running:
            _dict[msg].is_running = False
            self.reset_status()
            self.showStatus("%s: [%s] 编译任务已完成。" % (time.strftime('%H:%M:%S'), msg))
            mark = u"下载路径：\r\n%s" % _dict[msg].upload_path
            message = u"[%s] 编译任务已完成，%s" % (msg, mark)
            MessageBox(0, message, u"任务调度结果", MB_OK | MB_ICONINFORMATION | MB_TOPMOST | MB_SYSTEMMODAL)
            # subprocess.call([os.path.join(_dirname, "MessageBox.exe"), message], cwd=_dirname, shell=False, stdin=None, stdout=None, stderr=None, timeout=None)

    def reset_status(self):
        found = False
        if self._status == 1:
            for key in _dict:
                if _dict[key].is_running:
                    found = True
                    break
            if not found:
                self._status = 2

    def func_timer(self):
        global timer
        # print(time.strftime('%Y-%m-%d %H:%M:%S'))
        timer = threading.Timer(_interval, self.func_timer)
        timer.start()
        self.check_finished()

    def check_finished(self):
        if self._status == 1:
            self._duration += _interval
            self._et.setText(time.strftime('%H:%M:%S', time.gmtime(self._duration)))
            self._counter = (self._counter + 1) % 10
            if self._counter == 0:
                for key in _dict:
                    if _dict[key].is_running:
                        # self.showStatus("%s: [%s] is_running=%s check_files_compiled=%s" % (time.strftime('%H:%M:%S'), key, _dict[key].is_running, check_files_compiled(_dict[key])))
                        if check_files_compiled(_dict[key]):
                            self.show_message(key)
        elif self._status == 2:
            self._message = ''
            self._status = 0


if __name__ == "__main__":
    _latest_request_time = datetime.datetime.now()
    _interval = 1
    _host_ip = get_host_ip()
    _abspath = sys.argv[0]
    _basename = os.path.basename(_abspath)
    _dirname = os.path.dirname(_abspath)
    _dict = {}
    _conf = configparser.ConfigParser()
    _conf.read('cfg.ini', encoding='utf-16')
    for sec in _conf.sections():
        _dict[sec] = VERSION(_conf.get(sec, 'key'), _conf.get(sec, 'name'), _conf.get(sec, 'base-path'), _conf.get(sec, 'tfs-url'), _conf.get(sec, 'upload-path'), _conf.get(sec, 'fire-on'))
    print(_dict)

    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(":/images/client.ico"))
    win = window()
    win.hide()
    win.func_timer()
    sys.exit(app.exec_())

