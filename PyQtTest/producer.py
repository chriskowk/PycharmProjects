# put: 阻塞操作
# task_done: 队列中一个消息被处理后，发送的消息
# join(): 只有当所有队列中所有消息被处理及，及触发了task_done之后才会返回
from threading import Thread
from queue import Queue


class Task(object):
    def __init__(self, num=-1):
        self.id = num
    def __repr__(self):
        return "Task Id: %d" % self.id
    def __str__(self):
        return "Task Id: %d" % self.id

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
                yield  item
            finally:
                self.task_done()

class Consumer(Thread):
    def __init__(self, func, work_queue, out_queue):
        super().__init__()
        self.worker = func
        self.task = work_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.task:
            result = self.worker(item)
            self.out_queue.put(result)

def worker(arg):
    print("Worker Solve: %s" % arg)
    return arg


def producer():
    work_queue = ClosableQueue()
    out_queue = ClosableQueue()
    threads = [Consumer(worker, work_queue, out_queue)]
    # threads = [Consumer(worker,work_queue,out_queue),Consumer(worker,work_queue,out_queue)]
    for thread in threads:
        thread.start()
    for num in range(30):
        work_queue.put(Task(num))
    work_queue.close()
    # Num Consumers,then Call Num close.
    # work_queue.close()
    work_queue.join()


if __name__ == '__main__':
    producer()