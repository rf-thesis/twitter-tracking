#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tweepy import Stream
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, API
import config
from telegram import Bot
import json
import twitter_loader
import threading
from tweet_utils import parse_tweet


consumer_key = config.consumer_key2
consumer_secret = config.consumer_secret2
access_token = config.access_token2
access_secret = config.access_secret2
telegram_token = config.telegram_token
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = API(auth)

twitter_loader.check_index()


def send_to_es(doc):
    twitter_loader.load_es_all(doc)


def send_to_pg(doc):
    twitter_loader.load_pg_all(doc)


class MyListener(StreamListener):

    def on_data(self, data):
        try:
            # if json.loads(data)["lang"] == "en":
            # send_to_es(data)
            doc = json.loads(data)
            if "limit" not in doc:
                tw, es_json = parse_tweet(doc)
                print(es_json)
                threading.Thread(target=send_to_es, name="ES-LOADER",
                                 args=(es_json,)).start()
                send_to_pg(tw)
                # send_to_es(es_json)

                # threading.Thread(target=send_to_pg, name="PG-LOADER",
                #                  args=(tw,)).start()
            return True
        except BaseException as e:
            print("Error on: %s" % str(e))
        return True

    def on_error(self, status):
        print(status)
        return True

twitter_stream = Stream(auth, MyListener())
twitter_stream.filter(follow=[str(a) for a in config.accounts])
