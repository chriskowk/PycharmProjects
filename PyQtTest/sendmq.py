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

# 消息队列服务的连接和队列的创建
credentials = pika.PlainCredentials(username, pwd)
connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, port_num, '/', credentials))
channel = connection.channel()
# 创建一个名为balance的队列，对queue进行durable持久化设为True(持久化第一步)
channel.queue_declare(queue='balance', durable=True)

message_str = 'Hello World!'
for i in range(100000000):
    # n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
    channel.basic_publish(
        exchange='',
        routing_key='balance',  # 写明将消息发送给队列balance
        body=message_str,  # 要发送的消息
        properties=pika.BasicProperties(delivery_mode=2, )  # 设置消息持久化(持久化第二步)，将要发送的消息的属性标记为2，表示该消息要持久化
    )  # 向消息队列发送一条消息
    print(" [%s] Sent 'Hello World!'" % time.strftime('%H:%M:%S'))
    # time.sleep(0.2)
connection.close()  # 关闭消息队列服务的连接