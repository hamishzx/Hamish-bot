# -*- coding: utf-8 -*-
import os, re, time, datetime

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot

os.environ['TZ'] = 'UTC'
print('Starting at: ' + time.asctime(time.localtime(time.time())))
start_time = time.time()
rec_time = (datetime.datetime.now() + datetime.timedelta(hours = 8)).__format__('%d/%m/%y %H:%M')

site = pywikibot.Site()
site.login()

# Province, City, Area, Street 分别对应省级、地级、县级、乡级的行政区划

province_list_page = pywikibot.Page(site, "Template:PRC_admin/list/00/00/00/000/000")
pattern = re.compile(r'\d{2}')
province_list = pattern.findall(province_list_page.text)
wd_id_pattern = re.compile(r'wikidata=([Q|q]\d{1,9})\|')
repo = site.data_repository()

if (len(province_list) != 34):
    print("[ERR]Isn't it 34?")
    exit

print("Start province check\n")
province_total = len(province_list)
province_delta = 0
for code in province_list:
    data_page = pywikibot.Page(site, "Template:PRC_admin/data/{0}/00/00/000/000".format(code))
    text = data_page.text
    print(code, end='\t')
    name_pattern = re.compile(r'name=(.*)\|')
    name = name_pattern.findall(text)[0]
    width = 20 - len(name.encode("GBK")) + len(name)
    print(name.ljust(width), end='\t')
    old_id = wd_id_pattern.findall(text)[0]
    print(old_id, end='\t')
    item = pywikibot.ItemPage(repo, old_id)
    if (item.isRedirectPage()):
        new_id = item.getRedirectTarget().getID().casefold() # change into lowercase to avoid possible bug
    else:
        new_id = old_id
    print(new_id, end='\t')
    if (new_id != old_id):
        province_delta += 1
        text = re.sub(old_id, new_id, text)
        pywikibot.showDiff(data_page.text, text)
        data_page.text = text
        data_page.save(summary = "Updating wikidata item id from [[:d:{0}|{0}]] to [[:d:{1}|{1}]]".format(old_id, new_id), minor = False)
    print('\n')
print('Province check completed.\n{0} total, {1} delta.'.format(province_total, province_delta))

print("Start city check\n")

end_time = time.time()
print("Elasped time: " + str(format(end_time - start_time, '.2f') + 'seconds'))