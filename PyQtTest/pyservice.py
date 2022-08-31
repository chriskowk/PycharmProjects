# encoding=utf-8
import win32serviceutil
import win32service
import win32event
import os
import logging
import inspect
import servicemanager
import sys
import win32timezone
import winerror
import subprocess
import threading

class PythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PyService"  # 服务名
    _svc_display_name_ = "Check Compiler Manager Running"  # 服务在windows系统中显示的名称
    _svc_description_ = "Check compiler process running, otherwise run it immediately."  # 服务的描述

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._getLogger()
        self.run = True

    def _getLogger(self):
        # 创建一个logger，设置日志名称，为我们的模块名
        # 返回一个logger实例，如果没有指定name，返回root logger。
        # 只要name相同，返回的logger实例都是同一个而且只有一个，
        # 即name和logger实例是一一对应的。这意味着，
        # 无需把logger实例在各个模块中传递。只要知道name，
        # 就能得到同一个logger实例。
        logger = logging.getLogger('[PyService]')
        # 获取当前文件夹路径
        self.this_file = inspect.getfile(inspect.currentframe())
        self.dirpath = os.path.abspath(os.path.dirname(self.this_file))
        # 创建一个handler，用于写入日志文件
        # StreamHandler: 输出到控制台
        # FileHandler:   输出到文件
        # BaseRotatingHandler 可以按时间写入到不同的日志中。比如将日志按天写入不同   的日期结尾的文件文件。
        # SocketHandler 用TCP网络连接写LOG
        # DatagramHandler 用UDP网络连接写LOG
        # SMTPHandler 把LOG写成EMAIL邮寄出去
        handler = logging.FileHandler(os.path.join(self.dirpath, "pyservice.log"))
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        # 给logger添加handler
        logger.addHandler(handler)

        # 日志等级(从高到低)：CRITICAL->ERROR->WARNING->INFO->DEBUG
        # 一旦设置了日志等级，则调用比等级低的日志记录函数则不会输出
        logger.setLevel(logging.INFO)

        return logger

    def SvcDoRun(self):
        import time
        self.logger.info("service is run....")  # 记录一条日志
        while self.run:
            try:
                fn = os.path.join(os.path.join(self.dirpath, "startproc.bat"))
                self.logger.info(("%s: 执行命令 %s ..." % (time.strftime('%H:%M:%S'), fn)))
                if os.path.exists(fn) and os.path.isfile(fn):
                    output = self.subprocess_check_output(fn)
                    response = output.decode("gbk", "ignore")
                    self.logger.info(("%s: 执行结果...\r\n%s" % (time.strftime('%H:%M:%S'), response)))
            except Exception as e:
                self.logger.info(e)
            finally:
                time.sleep(60)

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

    def SvcStop(self):
        self.logger.info("service is stop....")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(PythonService)
            servicemanager.Initialize('PyService', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(PythonService)
