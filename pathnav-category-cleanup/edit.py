# ！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 19 Nov 2024 Tue 18:45
# Name: edit
# Author: CHAU SHING SHING HAMISH

import pywikibot
import re
import os
import time

os.environ['TZ'] = 'UTC'
print('Starting at: ' + time.asctime(time.localtime(time.time())))
site = pywikibot.Site('zh', 'wikipedia')
site.login()

category = pywikibot.Category(site, 'Category:使用Pathnav的條目')
pages_to_clean = list(category.articles())
print(f'Pages to clean: {len(pages_to_clean)}')

for page in pages_to_clean:
    print(page.title())
    text = page.text
    text = re.sub(r'\{\{[Pp]athnav.*\}\}\n', '', text)
    pywikibot.showDiff(page.text, text)
    page.text = text
    page.save(summary='[[Wikipedia:机器人/申请/Hamish-bot/10|T10]]：從條目空間頁面中移除Pathnav模板', minor=False)



