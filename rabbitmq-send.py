#!/usr/bin/env python
import pika
import sys
from datetime import datetime
now = datetime.now().strftime('%b %d %H:%M:%S')

# establish conn
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# create "hello" queque
channel.queue_declare(queue='hello')
channel.exchange_declare(exchange='testexchange',
                         type='fanout')


# default exchange identified by an empty string
message = now + ', LOL1, lol2, lol3'
channel.basic_publish(exchange='testexchange',
                      routing_key='hello',
                      body=message)
print(" [x] Sent %r" % message)

# close conn to flush buffers
connection.close()
