from testlayout import Ui_MainWindow
from PyQt5 import QtWidgets
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

import resources_rc

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
        # rabbitmq 报错 pika.exceptions.IncompatibleProtocolError: StreamLostError: (‘Transport indicated EOF’,) 产生此报错的原因是我将port写成了15672
        # rabbitmq需要通过端口5672连接 - 而不是15672. 更改端口，转发，一切正常
        port_num = 5672
        credentials = pika.PlainCredentials(username, pwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, port_num, '/', credentials))
        channel = connection.channel()
        channel.queue_declare('out_queue', durable=True)
        for message in channel.consume('out_queue', auto_ack=True, inactivity_timeout=1):
            if self._is_interrupted: break
            if not message: continue
            method, properties, body = message
            if body is not None:
                msg = body.decode('utf-8')
                self._func(msg)

class main_window(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.push_click)
        self.ui.closeButton.clicked.connect(self.quit)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowIcon(QtGui.QIcon(':/images/clock.ico'))
        consumer = Consumer(self.run)
        consumer.start()
        self._status = 0
        self._message = ''

    def push_click(self):
        msg = ''
        if self.ui.radioButton_1.isChecked():
            msg = self.ui.radioButton_1.text()
        elif self.ui.radioButton_2.isChecked():
            msg = self.ui.radioButton_2.text()
        elif self.ui.radioButton_3.isChecked():
            msg = self.ui.radioButton_3.text()
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
            body=msg,  # 要发送的消息
            properties=pika.BasicProperties(delivery_mode=2, )  # 设置消息持久化(持久化第二步)，将要发送的消息的属性标记为2，表示该消息要持久化
        )  # 向消息队列发送一条消息
        connection.close()
        self._status = 1
        self._message = msg
        self.ui.textEdit.append(u"[%s] 编译任务已入队... " % msg)

    def run(self, msg):
        if self._status == 1 and self._message == msg:
            self._status = 2
            text = u"[%s] 编译任务已完成。" % msg
            self.ui.textEdit.append(text)
            self.ui.textEdit.moveCursor(QTextCursor.End)

    def fun_timer(self):
        global timer
        # print(time.strftime('%Y-%m-%d %H:%M:%S'))
        timer = threading.Timer(_interval, self.fun_timer)
        timer.start()
        self.check_finished()

    def check_finished(self):
        if self._status == 1:
            self.ui.textEdit.moveCursor(QTextCursor.End)
            self.ui.textEdit.insertPlainText('.')
        elif self._status == 2:
            mark = u"下载路径：\r\n%s" % _dict[self._message].upload_path
            msg = u"[%s] 编译任务已完成，%s" % (self._message, mark)
            self._message = ''
            self._status = 0
            MessageBox(0, msg, u"任务调度结果", MB_OK | MB_ICONINFORMATION | MB_TOPMOST)

    def quit(self):
        self.exit()
        qApp.exit(0)
        sys.exit()

    # 覆写窗口关闭事件（函数名固定不可变）
    def closeEvent(self, event):
        self.quit()


class VERSION:
    def __init__(self, key='', name='', basepath='', url='', uploadpath='', fireon='N/A', task=None):
        self.task = task
        self.key = key
        self.name = name
        self.base_path = basepath
        self.tfs_url = url
        self.upload_path = uploadpath
        fireon = fireon.replace(" ", "")
        self.fire_enabled = not fireon.upper().__contains__("N/A")
        self.fire_on = []
        if self.fire_enabled:
            for item in fireon.split(";"):
                self.fire_on.append(datetime.datetime.strptime(item, "%H:%M" if len(item) == 5 else "%H:%M:%S").time() or None)


if __name__ == '__main__':
    _abspath = sys.argv[0]
    _basename = os.path.basename(_abspath)
    _dirname = os.path.dirname(_abspath)
    _dict = {}
    _interval = 1
    _conf = configparser.ConfigParser()
    _conf.read('cfg.ini', encoding='utf-16')
    for sec in _conf.sections():
        _dict[sec] = VERSION(_conf.get(sec, 'key'), _conf.get(sec, 'name'), _conf.get(sec, 'base-path'), _conf.get(sec, 'tfs-url'), _conf.get(sec, 'upload-path'), _conf.get(sec, 'fire-on'))
    print(_dict)
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(":/images/clock.ico"))
    win = main_window()
    win.show()
    win.fun_timer()
    sys.exit(app.exec_())
