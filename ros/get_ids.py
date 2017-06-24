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

acct = {}

accounts1 = ['orangefeeling', 'GlastoFest', 'cphdistortion', 'wayoutwestuk',
            'trailerparkfest', 'SonarFestival', 'rockenseine', 'Solidays',
            'bruningman', 'sxsw', 'RockWerchter', 'RockAlParque', 'Tinthepark',
            'ExitFestival', 'coachella', 'OfficialRandL', 'szigetofficial',
            'pinkpopfest', 'spotfestival', 'NorthsideFest', 'strictlyreading',
            'rockamring', 'summerjam', 'BottleRockNapa', 'ultra', 'boilerroomtv',
            'dkmntl', 'Dimensions_Fest', 'CleanOutLoud16', 'FOOFIGHTERS_US',
            'arcadefire', 'theweeknd', 'The_xx', 'IceCube_Us', 'ModeratOfficial',
            'solange_lebourg', 'trentemoeller', 'ThraxUS_', 'TheAvalanches',
            'brunoboo133', 'brysontiller', 'erasureinfo', 'fatherjohnmisty',
            'FreddieGibbs', 'futureislands', 'G_Eazy', 'gucci1017', 'halsey',
            'DregenOfficial', 'iconapop', 'TheMaryChain', 'Ushefer', 'lordemusic',
            'momeofficial', 'Nas', 'neurosisoakland', 'NicolasJaar', 'PopcaanMusic',
            'Residente', 'royalblooduk', 'RealSeunKuti', 'slowdiveband', 'thelumineers']

accounts2 = ['Tinashe', 'NikolajKoppel', '47soulofficial', 'adtr', 'againstme',
            'AngelOlsen', 'TheAVClub', 'CASHMERECAT', 'CircuitdesYeux', 'clammyclams',
            'Debashishguitar', 'digableplanets', 'DISCWOMANNYC', 'FIRSTHATE_HC',
            'HLeithauser', 'Machines4Lovers', 'Ibaaku1', 'idlesband', 'HuffPost_Maroc',
            'JagwarMa', 'jennyhval', 'JuliaJacklin', 'TheRealKano', 'KarenElson_',
            'kevinmorby', 'KreptandKonan', 'Mambanegralatin', 'LWoodrose',
            'MadameGandhi', 'MaxLucado', 'MissMargoPrice', 'moonduo', 'nogaerez',
            'Noisia_nl', 'noname', 'the_oathbreaker', 'OMandM', 'Oranssi_Pazuzu',
            'pertnearmusic', 'hunterplake', 'PigDestroyer', 'FarahBkr', 'RagNBoneManUK',
            'RedFang', 'ROMPERAYOMUSICA', 'rufussounds', 'rumoursaidfire',
            'SHOW_METHE_BODY', 'thisissigrid', 'SVINmusic', 'trapthem', 'vanishing_twin',
            'ViagraBoys', '_Warpaint', 'brassbandwiki', 'YoungMAMusic', 'AyOwAmusic',
            'baestCPH', 'Bogfinkevej', 'GaiusCharles', 'amandapalmer', 'KornelKovacs',
            'MBlicherDK', 'ModestMgmt', 'natjagerband', 'TheOddCoupleCBS', 'Purpurr',
            'schoolofxmusic', 'shitkidmusic', 'solid_blake']




a = api.lookup_users(screen_names=accounts1)

for u in a:
      acct[u.screen_name] = u.id

a = api.lookup_users(screen_names=accounts2)

for u in a:
      acct[u.screen_name] = u.id


print(acct)


# for a in accounts:
#       user = api.get_user(screen_name=a)
#       acct[a] = user.id


# print(acct)