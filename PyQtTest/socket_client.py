import socket
import time

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8001))

    flag = '1'
    count = 0
    while True:
        time.sleep(1)
        print("send to server with value: %s" % flag)
        sock.send(bytes(flag, encoding='utf8'))
        bs = sock.recv(1024)
        print(bs.decode(encoding='utf8'))
        flag = (flag == '1') and '2' or '1'  # change to another type of value each time
        count += 1
        if count % 3 == 0:
            flag = '0'
        elif count == 10:
            break

    print("closing me: %s" % flag)
    sock.close()
