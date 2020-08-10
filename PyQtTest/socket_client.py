import socket
import time

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8001))

    flag = '1'
    count = 0
    while True:
        time.sleep(1)
        print("%s: send to server with value: %s" % (time.strftime('%H:%M:%S'), flag))
        sock.send(bytes(flag, encoding='utf-8'))
        bs = sock.recv(1024)
        print(bs.decode(encoding='utf-8'))
        flag = (flag == '1') and '2' or '1'  # change to another type of value each time
        count += 1
        if count % 3 == 0:
            flag = '0'
        elif count == 10:
            break

    print("%s: closing me: %s" % (time.strftime('%H:%M:%S'), flag))
    sock.close()
