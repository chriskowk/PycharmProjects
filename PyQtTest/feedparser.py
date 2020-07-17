import time
from queue import Queue
from threading import Thread
#: 自己写的解析模块
import feedparser

num_fetch_threads = 2
enclosure_queue = Queue()
feed_urls = ['http:xxx/xxx',]

def downloadEnclosures(i, q):
    """ 线程worker函数
    用于处理队列中的元素项，这些守护线程在一个无限循环中，只有当主线程结束时才会结束循环
    """
    while True:
        print('%s: Looking for the next enclosure' % i)
        url = q.get()
        print('%s: Downloading: %s' % (i, url))
        #: 用sleep代替真实的下载
        time.sleep(i + 2)
        q.task_done()

for i in range(num_fetch_threads):
    worker = Thread(target=downloadEnclosures, args=(i, enclosure_queue))
    worker.setDaemon(True)
    worker.start()

for url in feed_urls:
    response = feedparser.parse(url, agent='fetch_podcasts.py')
    for entry in response['entries']:
        for enclosure in entry.get('enclosures', []):
            print('Queuing:', enclosure['url'])
            enclosure_queue.put(enclosure['url'])

# Now wait for the queue to be empty, indicating that we have
# processed all of the downloads.
print('*** Main thread waiting')
enclosure_queue.join()
print('*** Done')
