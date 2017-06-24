'''
forked from mentzera --> from AWS/Twitter/ES tutorial
'''
from elasticsearch import Elasticsearch
import config
from elasticsearch.exceptions import ElasticsearchException
from tweet_utils import id_field, tweet_mapping
from models import *
import json

index_name = 'rf17'
doc_type = 'tweet'
mapping = {doc_type: tweet_mapping}
bulk_chunk_size = config.es_bulk_chunk_size

user = config.xpackUser
secret = config.xpackPwd


def create_index(es, index_name, mapping):
    print('creating index {}...'.format(index_name))
    es.indices.create(index_name + "accounts", body={'mappings': mapping})
    es.indices.create(index_name + "hashtags", body={'mappings': mapping})


def check_index():
    es = Elasticsearch(host=config.es_host,
                       port=config.es_port,
                       http_auth=(user, secret), request_timeout=45)
    if es.indices.exists(index_name):
        print('index {} already exists'.format(index_name))
        try:
            es.indices.put_mapping(doc_type, tweet_mapping, index_name)
        except ElasticsearchException as e:
            print('error putting mapping:\n' + str(e))
            print('deleting index {}...'.format(index_name))
            es.indices.delete(index_name)
            create_index(es, index_name, mapping)
    else:
        print('index {} does not exist'.format(index_name))
        create_index(es, index_name, mapping)


def load_accounts(tweet):
    es = Elasticsearch(host=config.es_host,
                       port=config.es_port,
                       http_auth=(user, secret), request_timeout=45)
    tweetid = tweet[id_field]
    tweet.pop(id_field)
    result = es.index(index=index_name + "accounts", doc_type=doc_type,
                      id=tweetid, body=json.dumps(tweet), request_timeout=30)
    return result


def load_hashtags(tweet):
    es = Elasticsearch(host=config.es_host,
                       port=config.es_port,
                       http_auth=(user, secret), request_timeout=45)
    tweetid = tweet[id_field]
    tweet.pop(id_field)
    result = es.index(index=index_name + "hashtags", doc_type=doc_type,
                      id=tweetid, body=json.dumps(tweet), request_timeout=30)
    return result


def load_pg(doc):
    db_eng = db_connect()
    db_session = create_db_session(db_eng)
    create_tables(db_eng)
    db_session.add(doc)
    db_session.commit()
