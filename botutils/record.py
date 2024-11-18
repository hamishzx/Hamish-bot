# ！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 15 Nov 2024 Fri 16:25
# Name: record
# Author: CHAU SHING SHING HAMISH

import pywikibot
import re

site = pywikibot.Site('zh', 'wikipedia')
site.login()

def time_record(task_nbr, t, op):
    user_page = pywikibot.Page(site, "User:Hamish-bot")
    user_page_text = user_page.text
    task_row = re.search(fr'\|\s{task_nbr}\s\|\|\s.*\s\|\|\s(.*)\s\|\|\s(.*)\s\|\|\s.*\s\|\|.*', user_page_text)
    run_time = task_row.group(1)
    op_time = task_row.group(2)
    user_page_text = user_page_text.replace(run_time, t)
    if op:
        user_page_text = user_page_text.replace(op_time, t)
    pywikibot.showDiff(user_page.text, user_page_text)
    user_page.text = user_page_text
    user_page.save(summary = "更新任務報告", minor = False)