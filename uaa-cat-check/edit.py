# -*- coding: utf-8 -*-
import json
import os
import re
import time
import requests
from datetime import datetime

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot
from config import config_page_name  # pylint: disable=E0611,W0614

os.environ['TZ'] = 'UTC'
print('Starting at: ' + time.asctime(time.localtime(time.time())))

site = pywikibot.Site()
site.login()

config_page = pywikibot.Page(site, config_page_name)
cfg = config_page.text
cfg = json.loads(cfg)
print(json.dumps(cfg, indent=4, ensure_ascii=False))

if not cfg["enable"]:
    exit("disabled\n")

catpage = pywikibot.Category(site, "Category:可能违反方针的用户名")
for page in catpage.articles():
    if not re.search("User talk:", page.title()):
        continue
    session = requests.Session()
    params = {
        "action": "query",
        "list": "blocks",
        "bkusers": page.title()[10:],
        "format": "json"
    }
    blockinfo = session.get(url="https://zh.wikipedia.org/w/api.php", params=params).json()
    print(blockinfo['query']['blocks'])
    if not blockinfo['query']['blocks'] or blockinfo['query']['blocks'][0]['expiry'] != "infinity" or "partial" in a['query']['blocks'][0]:
        continue
    utpage = pywikibot.Page(site, page.title())
    template_text = "{{subst:uw-username|category=}}"
    text = utpage.text
    text = re.sub(r'\[\[Category:可能(违|違)反方(针|針)的用(户|戶)名(\|{{PAGENAME}}|)\]\]', '', text, flags=re.M)
    text = re.sub(r'\{\{Uw-username\}\}', template_text, text, flags=re.M)
    pywikibot.showDiff(utpage.text, text)
    utpage.text = text
    utpage.save(summary="uaa-cat-check", minor=False)
