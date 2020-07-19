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

        showAct = QAction("显示/隐藏", self, triggered=self.toggleVisibility)
        self.menu.addAction(showAct)
        autoStartupAct = QAction("下次自动启动", self, checkable=True)
        autoStartupAct.setChecked(True)
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
        ti = TrayIcon(self)
        tbrExit.actionTriggered.connect(ti.quit)
        self.txtMsg = QTextEdit()
        self.txtMsg.setReadOnly(True)
        self.txtMsg.setStyleSheet("color:rgb(10,10,10,255);font-size:16px;font-weight:normal;font-family:Roman times;")
        self.setCentralWidget(self.txtMsg)
        ti.show()

    def toolbarpressed(self, sender):
        print("按下的ToolBar按钮是", sender.text())
        self.status.showMessage(sender.text(), 5000)

    def closeEvent(self, event):  # 覆写窗口关闭事件（函数名固定不可变）
        event.ignore()  # 忽视点击X事件
        self.hide()

    def processtriggerX(self, qaction):
        path = os.path.dirname(qaction.statusTip())
        t = Thread(target=self.runCmd, args=(qaction.statusTip(), path))
        t.start()

    def processtrigger(self, qaction):
        for act in qaction.parent().actions():
            act.setChecked(True if qaction == act else False)
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
        self.txtMsg.append("%s 任务已执行结束。\r\n" % task.id)
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
    win.show()
    win.fun_timer()
    sys.exit(app.exec_())
