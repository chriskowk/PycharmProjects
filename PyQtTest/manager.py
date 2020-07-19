from multiprocessing import Manager, Pool
import os, time, random


# 写数据
def writer(q):
    print('writer启动(%s),父进程为(%s)' % (os.getpid(), os.getppid()))
    for i in 'Love':
        q.put(i)


# 读数据
def reader(q):
    print('reader启动(%s),父进程为(%s)' % (os.getpid(), os.getppid()))
    for i in range(q.qsize()):
        print('reader 从Queue获取到消息:%s' % q.get())


if __name__ == '__main__':
    print('(%s) start' % os.getpid())
    q = Manager().Queue()  # 使用Manager中的Queue来初始化
    po = Pool()
    # 使用阻塞模式创建进程，这样就不需要再reader中使用死循环了，可以等write执行完成后，再用reader
    po.apply(writer, (q,))
    po.apply(reader, (q,))
    # 写进程
    po.close()
    po.join()
    print('(%s) End' % os.getpid())