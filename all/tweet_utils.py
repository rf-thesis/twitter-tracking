#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
forked from mentzera --> from AWS/Twitter/ES tutorial
'''
import re
import time
from textblob import TextBlob
import config
import arrow
import json
from models import Tweet

class Sentiments:
    POSITIVE = 'Positive'
    NEGATIVE = 'Negative'
    NEUTRAL = 'Neutral'
    CONFUSED = 'Confused'
    
id_field = 'id'
emoticons = {Sentiments.POSITIVE:'😀|😁|😂|😃|😄|😅|😆|😇|😈|😉|😊|😋|😌|😍|😎|😏|😗|😘|😙|😚|😛|😜|😝|😸|😹|😺|😻|😼|😽',
             Sentiments.NEGATIVE : '😒|😓|😔|😖|😞|😟|😠|😡|😢|😣|😤|😥|😦|😧|😨|😩|😪|😫|😬|😭|😾|😿|😰|😱|🙀',
             Sentiments.NEUTRAL : '😐|😑|😳|😮|😯|😶|😴|😵|😲',
             Sentiments.CONFUSED: '😕'
             }

tweet_mapping = {
  "properties": {
    "UserName": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "UserScreenName": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "TweetDate": {
      "type": "date"
    },
    "OriginalTweetId": {
      "type": "long"
    },
    "OriginalTweetDate": {
      "type": "date"
    },
    "hashtags": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
     "mentions": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "Retweeted": {
      "type": "boolean"
    },
    "coordinates": {
      "properties": {
        "coordinates": {
          "type": "geo_point"
        },
        "type": {
          "type": "text",
          "index": "not_analyzed"
        }
      }
    },
    "UserLocation": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "Source": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "TweetLang": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "Favorited": {
      "type": "boolean"
    },
    "RetweetCount": {
      "type": "long"
    },
    "UserCreatedDate": {
      "type": "date"
    },
    "OriginalTweetUserScreenName": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "OriginalTweetUserName": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "OriginalTweetUserId": {
      "type": "long"
    },
    "sentiments": {
      "type": "text",
      "fielddata": True
    },
    "UserFollowerCount": {
      "type": "long"
    },
    "UserFavoritesCount": {
      "type": "long"
    },
    "UserStatusesCount": {
      "type": "long"
    },
    "UserUTCOffset": {
      "type": "text",
      "fielddata": True
    },
    "UserLang": {
      "type": "text",
      "fielddata": True
    },
    "Urls": {
      "type": "text",
      "fields": {
        "keyword": {
          "type": "keyword"
        }
      }
    },
    "UserId": {
      "type": "long"
    },
    "FavoriteCount": {
      "type": "long"
    },
    "Text": {
      "type": "text",
      "fields": {
        "all": {
          "type": "keyword"
        },
        "raw": {
          "type": "text",
          "fielddata": True
        }
      }
    },
    "UserTimeZone": {
      "type": "text",
      "fielddata": True
    },
    "UserFriendsCount": {
      "type": "long"
    },
    "wordcloud": {
      "type": "text",
      "fields": {
        "all": {
          "type": "keyword"
        },
        "raw": {
          "type": "text",
          "fielddata": True
        }
      }
    }

  }
}



def _sentiment_analysis(tweet):
    tweet['emoticons'] = []
    tweet['sentiments'] = []
    _sentiment_analysis_by_emoticons(tweet)
    if len(tweet['sentiments']) == 0:
        _sentiment_analysis_by_text(tweet)


def _sentiment_analysis_by_emoticons(tweet):
    for sentiment, emoticons_icons in emoticons.items():
        matched_emoticons = re.findall(emoticons_icons, tweet['text'])
        if len(matched_emoticons) > 0:
            tweet['emoticons'].extend(matched_emoticons)
            tweet['sentiments'].append(sentiment)
    
    if Sentiments.POSITIVE in tweet['sentiments'] and Sentiments.NEGATIVE in tweet['sentiments']:
        tweet['sentiments'] = Sentiments.CONFUSED
    elif Sentiments.POSITIVE in tweet['sentiments']:
        tweet['sentiments'] = Sentiments.POSITIVE
    elif Sentiments.NEGATIVE in tweet['sentiments']:
        tweet['sentiments'] = Sentiments.NEGATIVE

def _sentiment_analysis_by_text(tweet):
    blob = TextBlob(tweet['text'])
    sentiment_polarity = blob.sentiment.polarity
    if sentiment_polarity < 0:
        sentiment = Sentiments.NEGATIVE
    elif sentiment_polarity <= 0.2:
                sentiment = Sentiments.NEUTRAL
    else:
        sentiment = Sentiments.POSITIVE
    tweet['sentiments'] = sentiment


def parse_tweet(doc):
    TweetId = doc.get('id')
    TweetDate = arrow.get(doc.get('created_at'), "ddd MMM DD HH:mm:ss Z YYYY").format('YYYY-MM-DD HH:mm:ss ZZ')
    Text = doc.get("text")
    RetweetCount = doc.get("retweet_count")
    FavoriteCount = doc.get("favorite_count")

    Retweeted = None
    OriginalTweetId = None
    OriginalTweetUserId = None
    OriginalTweetUserName = None
    OriginalTweetUserScreenName = None
    OriginalTweetDate = None

    if doc.get("retweeted_status") is not None:
        Retweeted = True
        OriginalTweetId = doc.get("retweeted_status").get('id')
        OriginalTweetUserId = doc.get("retweeted_status").get('user').get('id')
        OriginalTweetUserName = doc.get("retweeted_status").get('user').get('name')
        OriginalTweetUserScreenName = doc.get("retweeted_status").get('user').get('screen_name')
        # OriginalTweetDate = arrow.get(doc.get("retweeted_status").get('created_at'), "ddd MMM DD HH:mm:ss Z YYYY").format('YYYY-MM-DD HH:mm:ss ZZ')
        OriginalTweetDate = time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.strptime(doc.get("retweeted_status").get('created_at'),'%a %b %d %H:%M:%S +0000 %Y'))


    Favorited = doc.get("favorited")
    TweetLang = doc.get('lang')
    Source = doc.get('source', "").partition('>')[-1].rpartition('<')[0]

    Mentions = []
    if doc.get('entities').get('user_mentions'):
        for m in doc.get('entities').get('user_mentions'):
            Mentions.append(m.get('screen_name'))

    Hashtags = []
    if doc.get('entities').get('hashtags'):
        for m in doc.get('entities').get('hashtags'):
            Hashtags.append(m.get('text'))

    Urls = []
    if doc.get('entities').get('urls'):
        for m in doc.get('entities').get('urls'):
            Urls.append(m.get('expanded_url'))

    UserId = doc.get('user').get('id')
    UserName = doc.get('user').get('name')
    UserScreenName = doc.get('user').get('screen_name')
    # UserCreatedDate = arrow.get(doc.get('user').get('created_at'), "ddd MMM DD HH:mm:ss Z YYYY").format('YYYY-MM-DD HH:mm:ss ZZ')
    UserCreatedDate = time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.strptime(doc.get('user').get('created_at'),'%a %b %d %H:%M:%S +0000 %Y'))
    UserLang = doc.get('user').get('lang')
    UserLocation = doc.get('user').get('location')

    UserTimeZone = doc.get('user').get('time_zone')
    UserUTCOffset = doc.get('user').get('utc_offset')

    UserFollowerCount = doc.get('user').get('followers_count')
    UserFriendsCount = doc.get('user').get('friends_count')
    UserFavoritesCount = doc.get('user').get('statuses_count')
    UserStatusesCount = doc.get('user').get('favourites_count')


    es_json = {"id":str(TweetId),
                "TweetDate":time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.strptime(doc['created_at'],'%a %b %d %H:%M:%S +0000 %Y')),
                "Text":Text,
                "RetweetCount":RetweetCount,
                "FavoriteCount":FavoriteCount,
                "Retweeted":Retweeted,
                "Favorited":Favorited,
                "TweetLang":TweetLang,
                "Source":Source,
                "Urls":Urls,
                "OriginalTweetId":OriginalTweetId,
                "OriginalTweetUserId":OriginalTweetUserId,
                "OriginalTweetUserName":OriginalTweetUserName,
                "OriginalTweetUserScreenName":OriginalTweetUserScreenName,
                "OriginalTweetDate":OriginalTweetDate,
                "UserId":UserId,
                "UserName":UserName,
                "UserScreenName":UserScreenName,
                "UserCreatedDate":UserCreatedDate,
                "UserLang":UserLang,
                "UserLocation":UserLocation,
                "UserTimeZone":UserTimeZone,
                "UserUTCOffset":UserUTCOffset,
                "UserFollowerCount":UserFollowerCount,
                "UserFriendsCount":UserFriendsCount,
                "UserFavoritesCount":UserFavoritesCount,
                "UserStatusesCount":UserStatusesCount,
                "coordinates": doc['coordinates']}

    es_json["mentions"] = list(map(lambda x: x['screen_name'],doc['entities']['user_mentions']))
    es_json["hashtags"] = list(map(lambda x: x['text'],doc['entities']['hashtags']))

    wcl = doc.get('text').lower()
    wcl = re.sub(r'^https?:\/\/.*[\r\n]*', '', wcl, flags=re.MULTILINE)
    querywords = wcl.split()
    resultwords  = [word for word in querywords if word.lower() not in config.stops]
    wcl = ' '.join(resultwords)
    for c in config.cleaner:
        wcl = wcl.replace(c, "")
    es_json["wordcloud"] = wcl
    if TweetLang == "en":
        _sentiment_analysis(doc)
        es_json["sentiments"] = doc.get("sentiments")

    tw = Tweet(TweetId=TweetId,
                  TweetDate=TweetDate,
                  Text=Text,
                  RetweetCount=RetweetCount,
                  FavoriteCount=FavoriteCount,
                  Retweeted=Retweeted,
                  Favorited=Favorited,
                  TweetLang=TweetLang,
                  Source=Source,
                  Mentions=Mentions,
                  Hashtags=Hashtags,
                  Urls=Urls,
                  OriginalTweetId=OriginalTweetId,
                  OriginalTweetUserId=OriginalTweetUserId,
                  OriginalTweetUserName=OriginalTweetUserName,
                  OriginalTweetUserScreenName=OriginalTweetUserScreenName,
                  OriginalTweetDate=OriginalTweetDate,
                  UserId=UserId,
                  UserName=UserName,
                  UserScreenName=UserScreenName,
                  UserCreatedDate=UserCreatedDate,
                  UserLang=UserLang,
                  UserLocation=UserLocation,
                  UserTimeZone=UserTimeZone,
                  UserUTCOffset=UserUTCOffset,
                  UserFollowerCount=UserFollowerCount,
                  UserFriendsCount=UserFriendsCount,
                  UserFavoritesCount=UserFavoritesCount,
                  UserStatusesCount=UserStatusesCount,
                  Json=json.dumps(doc))
    return tw, es_json


# def get_tweet(doc):
#     tweet = {}
#     tweet[id_field] = doc[id_field]
#     tweet['hashtags'] =
#     tweet['coordinates'] = doc['coordinates']
#     tweet['date'] = 
#     tweet['text'] = doc['text']



#     Retweeted = None
#     OriginalTweetId = None
#     OriginalTweetUserId = None
#     OriginalTweetUserName = None
#     OriginalTweetUserScreenName = None
#     OriginalTweetDate = None

#     if doc.get("retweeted_status") is not None:
#         Retweeted = True
#         OriginalTweetId = doc.get("retweeted_status").get('id')
#         OriginalTweetUserId = doc.get("retweeted_status").get('user').get('id')
#         OriginalTweetUserName = doc.get("retweeted_status").get('user').get('name')
#         OriginalTweetUserScreenName = doc.get("retweeted_status").get('user').get('screen_name')
#         OriginalTweetDate = arrow.get(doc.get("retweeted_status").get('created_at'), "ddd MMM DD HH:mm:ss Z YYYY").format('YYYY-MM-DD HH:mm:ss ZZ')

#     tweet["retweeted"] = Retweeted
#     tweet["OriginalTweetId"] = OriginalTweetId
#     tweet["OriginalTweetUserId"] = OriginalTweetUserId
#     tweet["OriginalTweetUserName"] = OriginalTweetUserName
#     tweet["OriginalTweetUserScreenName"] = OriginalTweetUserScreenName
#     tweet["OriginalTweetDate"] = OriginalTweetDate


#     # tweet['language'] = doc['lang']
#     tweet['source'] = doc.get('source', "").partition('>')[-1].rpartition('<')[0]
#     tweet['user'] = {'id': doc['user']['id'], 'name': doc['user']['name'], "screenName": doc.get('user').get('screen_name'),
#                      'followers': doc['user']['followers_count'], 'friends': doc['user']['friends_count'],
#                      'favourites': doc['user']['favourites_count'], 'statuses': doc['user']['statuses_count'],
#                      'created_at': time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.strptime(doc['user']['created_at'],'%a %b %d %H:%M:%S +0000 %Y')), 
#                      'time_zone': doc['user']['time_zone'], 'verified': doc['user']['verified']}
#     tweet['mentions'] = 
    
#     return tweet
