#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 3 Apr 2020 08:08
# @Author  : Hamish Shing Shing Chau
# @File    : edit.py
# @Software: PyCharm

import json
import os
import re
import time
import requests
from datetime import datetime

import mwparserfromhell
os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot
# from config import config_page_name  # pylint: disable=E0611,W0614

t1 = datetime.now().microsecond
t3 = time.mktime(datetime.now().timetuple())
os.environ['TZ'] = 'UTC'
print('Starting at: ' + time.asctime(time.localtime(time.time())))

site = pywikibot.Site()
site.login()
config_page_name = 'User:Hamish-bot/config1.json'
config_page = pywikibot.Page(site, config_page_name)
config_text = config_page.text
old_config_text = config_page.text
cfg = json.loads(config_text)
original_time = cfg['recognized_time']
print(json.dumps(cfg, indent=4, ensure_ascii=False))

if not cfg["enable"]:
    exit("disabled\n")

summary_prefix = "[[Wikipedia:機械人方針#毋須事先批准而合規操作|合規操作]]："
session = requests.Session()
URL = "https://zh.wikipedia.org/w/api.php"
REGI_PARAMS = {
        'action': "query",
        'format': "json",
        'list': "logevents",
        'leprop': "title|timestamp|comment|type",
        'letype': "newusers",
        'leuser': "Hamish",
        'lelimit': "max"
        }
IPBE_PARAMS = {
        'action': "query",
        'format': "json",
        'list': "logevents",
        'leprop': "title|timestamp|comment|type|details",
        'letype': "rights",
        'leuser': "Hamish",
        'lelimit': "max"
        }
R = session.post(URL, data=REGI_PARAMS)
DATA = R.json()
events = DATA['query']['logevents']
R = session.post(URL, data=IPBE_PARAMS)
DATA = R.json()
events = events + DATA['query']['logevents']

record_page = pywikibot.Page(site, cfg["main_page_name"])
record_text = record_page.text
old_record_text = record_page.text
archivelist = {}
count = 0

MARK = '<!-- BOT_MARK -->'
TAG = True
append_text = ''

for record in events:
    if record['action'] == 'byemail':
        timestamp = record['timestamp']
        if TAG:
            new_time = timestamp
            TAG = False
        print(timestamp, end='\t')
        action = '註冊'
        print(action, end='\t')
        target = record['title'][5:]
        print(target, end='\t')
        link_pattern = re.compile(r'unblock-zh/20\d{2}-.+/\d{6}')
        id_pattern = re.compile(r'\d+')
        comment = record['comment']
        prefix = 'https://lists.wikimedia.org/mailman/private/'
        mid = link_pattern.findall(comment)[0]
        suffix = '.html'
        link = prefix + mid + suffix
        id = id_pattern.findall(link)[1]
        reason = '[' + link + ' {}]'.format(id)
        print(id, end='\t')
        new_log = '|-\n|{}\n|{}\n|{}\n|{}\n'.format(timestamp, action, target, reason)
        if new_log not in old_record_text:
            append_text = append_text + new_log
        print()
    elif record['type'] == 'rights':
        if 'unblock-zh' == record['comment'][:10]:
            timestamp = record['timestamp']
            if TAG:
                new_time = timestamp
                TAG = False
            print(timestamp, end='\t')
            action = '授權'
            print(action, end='\t')
            target = record['title'][5:]
            print(target, end='\t')
            if len(record['comment']) > 10:
                link_pattern = re.compile(r'unblock-zh/20\d{2}-.+/\d{6}')
                id_pattern = re.compile(r'\d+')
                comment = record['comment']
                prefix = 'https://lists.wikimedia.org/mailman/private/'
                mid = link_pattern.findall(comment)[0]
                suffix = '.html'
                link = prefix + mid + suffix
                id = id_pattern.findall(link)[1]
                reason = '[' + link + ' {}]'.format(id)
                print(id, end='\t')
                new_log = '|-\n|{}\n|{}\n|{}\n|{}\n'.format(timestamp, action, target, reason)
                if new_log not in old_record_text:
                    append_text = append_text + new_log
            else:
                reason = record['comment']
                print(reason, end='\t')
                new_log = '|-\n|{}\n|{}\n|{}\n|{}\n'.format(timestamp, action, target, reason)
                if new_log not in old_record_text:
                    append_text = append_text + new_log
            print()

if new_time == original_time:
    exit("No change")
config_text = re.sub(original_time, new_time, config_text)
append_text = append_text + MARK
record_text = re.sub(MARK, append_text, record_text)
config_page.text = config_text
record_page.text = record_text
t2 = datetime.now().microsecond
t4 = time.mktime(datetime.now().timetuple())
strTime = '(Elasped %dms)' % ((t4 - t3) * 1000 + (t2 - t1) / 1000)
summary = "Recording new action(s). " + strTime
print(summary)
pywikibot.showDiff(old_record_text, record_page.text)
record_page.save(summary=summary_prefix + summary, minor=False)
pywikibot.showDiff(old_config_text, config_page.text)
config_page.save(summary=summary_prefix + summary, minor=False)

