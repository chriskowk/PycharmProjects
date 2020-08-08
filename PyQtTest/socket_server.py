# -*- coding: cp936 -*-
import socket
"""
建立一个python server，监听指定端口，
如果该端口被远程连接访问，则获取远程连接，然后接收数据，
并且做出相应反馈。
"""
if __name__ == "__main__":
    print("Server is starting")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 8001))  # 配置soket，绑定IP地址和端口号
    sock.listen(5)  # 设置最大允许连接数，各连接和server的通信遵循FIFO原则
    print("Server is listening port 8001, with max connection 5")
    while True:  # 循环轮询socket状态，等待访问
        connection, address = sock.accept()
        try:
            connection.settimeout(60)
            # 获得一个连接，然后开始循环处理这个连接发送的信息
            """
            如果server要同时处理多个连接，则下面的语句块应该用多线程来处理，
            否则server就始终在下面这个while语句块里被第一个连接所占用，
            无法去扫描其他新连接了，但多线程会影响代码结构，所以记得在连接数大于1时
            下面的语句要改为多线程即可。
            """
            while True:
                buf = connection.recv(1024).decode(encoding='utf8')
                print("Get value %s" % buf)
                if buf == '1':
                    print("send welcome to client...")
                    connection.send(bytes('hello 客户端, welcome to 服务器!', encoding='utf8'))
                elif buf != '0':
                    print("send refuse to client...")
                    connection.send(bytes('please go out!', encoding='utf8'))
                else:
                    print("send closing faster")
                    connection.send(bytes('closing faster!', encoding='utf8'))

        except Exception as e:  # 如果建立连接后，该连接在设定的时间内无数据发来，则time out
            print('exceopt on %s' % str(e))
            continue

    print("closing one connection")  # 当一个连接监听循环退出后，连接可以关掉
    connection.close()
