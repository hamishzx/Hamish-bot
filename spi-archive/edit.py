# -*- coding: utf-8 -*-
import hashlib

import mwparserfromhell
import pywikibot
import re
import time
import json
import datetime
import os
from config import config_page_name

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
os.environ['TZ'] = 'UTC'
print('Starting at: ' + time.asctime(time.localtime(time.time())))

site = pywikibot.Site("zh", "wikipedia")
site.login()

config_page = pywikibot.Page(site, config_page_name)
cfg = config_page.text
cfg = json.loads(cfg)
print(json.dumps(cfg, indent=4, ensure_ascii=False))
op = False

if not cfg["enable"]:
    exit("disabled\n")

summary_prefix = "[[Wikipedia:机器人/申请/Hamish-bot/6|T6]]："
spi_page = pywikibot.Page(site, "Wikipedia:傀儡調查/案件")
text = spi_page.text

spi_cases = re.findall(r'^(\{\{SPIstatusentry[^}]+}})$', text, flags=re.M)

archive_list = {}
count = 0

for case in spi_cases:
    case_info = re.findall(r'=([^|]*[^|}])', case)
    print(case_info[0], end='\t')
    print(case_info[1], end='\t')
    print(case_info[2], end='\t')

    if case_info[1] == 'close' or case_info[1] == 'closed':
        case_page = pywikibot.Page(site, "Wikipedia:傀儡調查/案件/" + case_info[0])
        case_text = case_page.text
        case_time_formatted = datetime.datetime.strptime(case_info[2], '%Y-%m-%d %H:%M') - datetime.timedelta(hours=8)
        case_time_formatted = case_time_formatted.strftime('%Y年%#m月%#d日')
        print(case_time_formatted, end='\t')
        if case_info[0] not in archive_list:
            archive_list[case_info[0]] = []
        archive_list[case_info[0]].append(
            re.findall(r'=== ' + case_time_formatted + ' ===.*----<!--- 所有留言請放在此行以上 -->[^=]?', case_text,
                       flags=re.S))
        case_text = re.sub(
            r'=== ' + case_time_formatted + ' ===.*----<!--- 所有留言請放在此行以上 -->[^=]?', '', case_text,
            flags=re.S)
        pywikibot.showDiff(case_page.text, case_text)
        case_page.text = case_text
        case_page.save(summary="存檔", minor=False)

    for archive_case in archive_list:
        archive_page = pywikibot.Page(site, "Wikipedia:傀儡調查/案件/" + archive_case + "/存檔")
        archive_text = archive_page.text
        for archive_case_text in archive_list[archive_case]:
            for archive_case_text_line in archive_case_text:
                archive_text += "\n" + archive_case_text_line
        pywikibot.showDiff(archive_page.text, archive_text)
        archive_page.text = archive_text
        archive_page.save(summary="存檔", minor=False)
        # [[Wikipedia:机器人/申请/Hamish-bot/6|T6]]：
        op = True

    print()
