# -*- coding: utf-8 -*-
import os, re, time, datetime

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot
from config import config_page_name  # pylint: disable=E0611,W0614

os.environ['TZ'] = 'UTC'
print('Starting at: ' + time.asctime(time.localtime(time.time())))
rec_time = (datetime.datetime.now() + datetime.timedelta(hours = 8)).__format__('%d/%m/%y %H:%M')

site = pywikibot.Site()
site.login()

# Province, City, Area, Street 分别对应省级、地级、县级、乡级的行政区划

province_list_page = pywikibot.Page(site, "Template:PRC_admin/list/00/00/00/000/000")
pattern = re.compile(r'\d{2}')
province_list = pattern.findall(province_list_page.text)

if (len(province_list) != 34):
    print("[ERR]Isn't it 34?")
    exit
