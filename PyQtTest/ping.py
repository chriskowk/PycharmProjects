from threading import Thread
import subprocess
import queue
import sys, os, time
import platform
import traceback
import socket

def ping(
        hostname=None,
        count=1,
        timeout=3
):
    data = {
        'errorcode': 0xff,
        'errorinfo': None,
        'data': {
            'hostname': hostname,
            'isUp': None
        }
    }
    try:
        outfile = ''
        if "Linux" == platform.system():
            cmd = "ping -c %d -w %d %s" % (count, timeout, hostname)
            outfile = "/dev/null"
        elif "Windows" == platform.system():
            cmd = "ping -n %d -w %d %s" % (count, timeout, hostname)
            outfile = "ping.temp"
        ret = subprocess.call(cmd, shell=True, stdout=open(outfile, 'w'), stderr=subprocess.STDOUT)
        data['data']['isUp'] = True if 0 == ret else False
        data['errorcode'] = 0x00
    except Exception as e:
        print(traceback.format_exc())
    finally:
        return data


def ping_with_queue(in_queue, out_queue):
    while True:
        ip = in_queue.get()
        data = ping(hostname=ip)
        out_queue.put(data)
        in_queue.task_done()  # 向任务已完成的队列,发送一个通知信号


def append_result(out_queue, result):
    while True:
        data = out_queue.get()
        result.append(data)
        out_queue.task_done()  # 向任务已完成的队列,发送一个通知信号


def get_all_device_status(ips):
    data = {
        'errorcode': 0xff,
        'errorinfo': None,
        'data': []
    }
    threads_nums = len(ips)
    in_queue = queue.Queue()
    out_queue = queue.Queue()
    for i in range(threads_nums):
        t = Thread(target=ping_with_queue, args=(in_queue, out_queue))
        t.setDaemon(True)
        t.start()

    for ip in ips:
        in_queue.put(ip)

    for i in range(threads_nums):
        t = Thread(target=append_result, args=(out_queue, data['data']))
        t.setDaemon(True)
        t.start()

    data['errorcode'] = 0x00
    in_queue.join()
    out_queue.join()
    return data

def get_host_ip():
    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip


if __name__ == '__main__':
    print(get_host_ip())
    ips = ['172.18.99.' + str(i) for i in range(0xff)]
    print(get_all_device_status(ips))
    print('main process begin sleep 20 seconds....')
    time.sleep(20)
    print('main process exit')