import pika
import sys
import time

# 远程rabbitmq服务的配置信息
username = 'chris'  # 指定远程rabbitmq的用户名密码
pwd = '123456'
ip_addr = '172.18.99.177'
# rabbitmq 报错 pika.exceptions.IncompatibleProtocolError: StreamLostError: (‘Transport indicated EOF’,) 产生此报错的原因是我将port写成了15672
# rabbitmq需要通过端口5672连接 - 而不是15672. 更改端口，转发，一切正常
port_num = 5672

credentials = pika.PlainCredentials(username, pwd)
connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, port_num, '/', credentials))
channel = connection.channel()


# 消费成功的回调函数
def callback(ch, method, properties, body):
    print(" [%s] Received %r" % (time.strftime('%H:%M:%S'), body))
    # time.sleep(0.2)


# 开始依次消费balance队列中的消息
channel.basic_consume(queue='balance', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()  # 启动消费

