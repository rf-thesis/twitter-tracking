#!/usr/bin/env python
import pika

# establish conn
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# check if queque exsists (redundant)
channel.queue_declare(queue='hello')

# receive message
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

# print messages
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
