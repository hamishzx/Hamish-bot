# -*- coding: utf-8 -*-
import json
import hashlib
import os
import re
import time
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

summary_prefix = "[[Wikipedia:机器人/申请/Hamish-bot/3|正式批准之任務]]："
rsnpage = pywikibot.Page(site, cfg["main_page_name"])
text = rsnpage.text

rndstr = hashlib.md5(str(time.time()).encode()).hexdigest()
text = re.sub(r'^(===[^=]+===)$', rndstr + r'\1', text, flags=re.M)
text = text.split(rndstr)

mainPageText = text[0].strip()
text = text[1:]

archivelist = {}
count = 0

for section in text:
    section = section.strip()
    if section == '':
        continue
    else:
        title = section.split('\n')[0]
        print(title, end="\t")

    processed = False
    publicizing = False

    for template in section.filter_templates():
        if template.name.lower() == "status2":
            if template.has(1):
                status = template.get(1)
            else:
                status = "(empty)"
            print("status", status, end="\t")
            if status in cfg["publicizing_status"]:
                publicizing = True
                print("publicizing", end="\t")
                break
            elif status in cfg["done_status"]:
                processed = True
                print("processed", end="\t")
                break
            else:
                print("not processed", end="\t")
                break

    lasttime = datetime(1, 1, 1)
    for m in re.findall(r"(\d{4})年(\d{1,2})月(\d{1,2})日 \(.\) (\d{2}):(\d{2}) \(UTC\)", str(section)):
        d = datetime(int(m[0]), int(m[1]), int(m[2]), int(m[3]), int(m[4]))
        lasttime = max(lasttime, d)
    print(lasttime, end="\t")

    if (
        (
            (processed and not publicizing and time.time() - lasttime.timestamp() > cfg["time_to_live_for_processed"])
            or (not processed and not publicizing and time.time() - lasttime.timestamp() > cfg["time_to_live_for_not_processed"])
        )
            and lasttime != datetime(1, 1, 1)):
        target = (lasttime.year, lasttime.month)
        if target not in archivelist:
            archivelist[target] = []
        archivestr = str(section).strip()
        archivestr = re.sub(
            r"{{bot-directive-archiver\|no-archive-begin}}[\s\S]+?{{bot-directive-archiver\|no-archive-end}}\n?", "", archivestr)
        archivelist[target].append(archivestr)
        count += 1
        section.remove(section)
        print("archive to " + str(target), end="\t")
    print()

text = str(wikicode)
if rsnpage.text == text:
    exit("nothing changed")

pywikibot.showDiff(rsnpage.text, text)
rsnpage.text = text
summary = cfg["main_page_summary"].format(count)
print(summary)
rsnpage.save(summary=summary_prefix + summary, minor=False)

for target in archivelist:
    archivepage = pywikibot.Page(site, cfg["archive_page_name"].format(target[0], target[1]))
    text = archivepage.text
    print(archivepage.title())
    if not archivepage.exists():
        text = cfg["archive_page_preload"]
    text += "\n\n" + "\n\n".join(archivelist[target])
    text = re.sub(r"{{status2\|(讨论|討論)中}}", "{{status2|-|已過時並存檔}}", text)
    pywikibot.showDiff(archivepage.text, text)
    archivepage.text = text
    summary = cfg["archive_page_summary"].format(len(archivelist[target]))
    print(summary)
    archivepage.save(summary=summary_prefix + summary, minor=False)
