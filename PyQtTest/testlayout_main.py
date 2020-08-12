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
        self.ui.textEdit.append(u"[%s] 编译任务已入队..." % msg)

    def run(self, msg):
        self._message = msg
        self._status = 2
        msg = u"[%s] 编译任务已完成。" % msg
        self.ui.textEdit.append(msg)

    def fun_timer(self):
        global timer
        # print(time.strftime('%Y-%m-%d %H:%M:%S'))
        timer = threading.Timer(1, self.fun_timer)
        timer.start()
        self.check_finished()

    def check_finished(self):
        if self._status == 1:
            self.ui.textEdit.moveCursor(QTextCursor.End)
            self.ui.textEdit.insertPlainText('.')

        elif self._status == 2:
            msg = u"[%s] 编译任务已完成。" % self._message
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

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = main_window()
    win.show()
    win.fun_timer()
    sys.exit(app.exec_())
