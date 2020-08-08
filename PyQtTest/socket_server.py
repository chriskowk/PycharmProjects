# -*- coding: cp936 -*-
import socket
"""
����һ��python server������ָ���˿ڣ�
����ö˿ڱ�Զ�����ӷ��ʣ����ȡԶ�����ӣ�Ȼ��������ݣ�
����������Ӧ������
"""
if __name__ == "__main__":
    print("Server is starting")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 8001))  # ����soket����IP��ַ�Ͷ˿ں�
    sock.listen(5)  # ������������������������Ӻ�server��ͨ����ѭFIFOԭ��
    print("Server is listening port 8001, with max connection 5")
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
                buf = connection.recv(1024).decode(encoding='utf8')
                print("Get value %s" % buf)
                if buf == '1':
                    print("send welcome to client...")
                    connection.send(bytes('hello �ͻ���, welcome to ������!', encoding='utf8'))
                elif buf != '0':
                    print("send refuse to client...")
                    connection.send(bytes('please go out!', encoding='utf8'))
                else:
                    print("send closing faster")
                    connection.send(bytes('closing faster!', encoding='utf8'))

        except Exception as e:  # ����������Ӻ󣬸��������趨��ʱ���������ݷ�������time out
            print('exceopt on %s' % str(e))
            continue

    print("closing one connection")  # ��һ�����Ӽ���ѭ���˳������ӿ��Թص�
    connection.close()
