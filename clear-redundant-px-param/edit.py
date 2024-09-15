#！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 15 Sept 2024 09:24
# Name: edit
# Author: CHAU SHING SHING HAMISH
import re

import pywikibot
from pywikibot.date import pattern

site = pywikibot.Site('zh', 'wikipedia')
site.login()

cat_list = pywikibot.Category(site, 'Category:圖片尺寸大小帶有額外_px_字元的頁面').articles()
todo_list = []
for page in cat_list:
    if page.title()[:14] == 'Wikipedia:每日图片' and page.title()[-1:] == '日':
        print(page.title())
        todo_list.append(page)

print('Total:', len(todo_list))

for page in todo_list:
    text = page.text
    pattern = re.compile(r'(\| Size = \d+)px')
    text = pattern.sub(r'\1', text)
    pywikibot.showDiff(page.text, text)
    page.text = text
    page.save('去除冗余的px参数，[[Special:PermaLink/84177489#清理每日圖片冗餘參數|BOTREQ]]', minor=True)