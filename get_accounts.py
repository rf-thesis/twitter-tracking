#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tweepy import Stream
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API
import config
from telegram import Bot
import json
import twitter_to_es
import threading

consumer_key = config.consumer_key
consumer_secret = config.consumer_secret
access_token = config.access_token
access_secret = config.access_secret
telegram_token = config.telegram_token
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = API(auth)

twitter_to_es.check_index()

def send_to_es(line):
    doc = json.loads(line)
    if "limit" not in doc:
        twitter_to_es.load(doc)


class MyListener(StreamListener):

    def on_data(self, data):
        try:
            # if json.loads(data)["lang"] == "en":
            # send_to_es(data)
            print(data)
            threading.Thread(target=send_to_es, name="ES-LOADER",
                             args=(data,)).start()
            return True
        except BaseException as e:
            print("Error on: %s" % str(e))
        return True

    def on_error(self, status):
        print(status)
        return True

twitter_stream = Stream(auth, MyListener())
twitter_stream.filter(follow=[str(a) for a in config.accounts])
