# -*- coding: cp936 -*-
import socket
import time
"""
����һ��python server������ָ���˿ڣ�
����ö˿ڱ�Զ�����ӷ��ʣ����ȡԶ�����ӣ�Ȼ��������ݣ�
����������Ӧ������
"""
if __name__ == "__main__":
    print("%s: Server is starting" % time.strftime('%H:%M:%S'))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 8001))  # ����soket����IP��ַ�Ͷ˿ں�
    sock.listen(5)  # ������������������������Ӻ�server��ͨ����ѭFIFOԭ��
    print("%s: Server is listening port 8001, with max connection 5" % time.strftime('%H:%M:%S'))
    while True:  # ѭ����ѯsocket״̬���ȴ�����
        connection, address = sock.accept()
        try:
            connection.settimeout(60)
            # ���һ�����ӣ�Ȼ��ʼѭ������������ӷ��͵���Ϣ
            """
            ���serverҪͬʱ���������ӣ������������Ӧ���ö��߳�������
            ����server��ʼ�����������while�����ﱻ��һ��������ռ�ã�
            �޷�ȥɨ�������������ˣ������̻߳�Ӱ�����ṹ�����Լǵ�������������1ʱ
            ��������Ҫ��Ϊ���̼߳��ɡ�
            """
            while True:
                buf = connection.recv(1024).decode(encoding='utf-8')
                print("%s: Get value %s"  % (time.strftime('%H:%M:%S'), buf))
                if buf == '1':
                    print("%s: send welcome to client..." % time.strftime('%H:%M:%S'))
                    connection.send(bytes('hello �ͻ���, welcome to ������!', encoding='utf-8'))
                elif buf != '0':
                    print("%s: send refuse to client..." % time.strftime('%H:%M:%S'))
                    connection.send(bytes('please go out!', encoding='utf-8'))
                else:
                    print("%s: send closing faster" % time.strftime('%H:%M:%S'))
                    connection.send(bytes('closing faster!', encoding='utf-8'))

        except Exception as e:  # ����������Ӻ󣬸��������趨��ʱ���������ݷ�������time out�����½���������
            print('%s: exceopt on %s'  % (time.strftime('%H:%M:%S'), str(e)))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', 8001))  # ����soket����IP��ַ�Ͷ˿ں�
            sock.listen(5)  # ������������������������Ӻ�server��ͨ����ѭFIFOԭ��
            print("%s: Server is listening port 8001, with max connection 5" % time.strftime('%H:%M:%S'))
            continue

    print("%s: closing one connection" % time.strftime('%H:%M:%S'))  # ��һ�����Ӽ���ѭ���˳������ӿ��Թص�
    connection.close()
