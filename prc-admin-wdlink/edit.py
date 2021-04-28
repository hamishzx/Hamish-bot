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

def province_check(incoming_list):
    print("Start province check\n")
    province_list = incoming_list
    province_total = len(province_list)
    province_delta = 0

    for province in province_list:
        out_text = ''
        data_page = pywikibot.Page(site, "Template:PRC_admin/data/{0}/00/00/000/000".format(province))
        if data_page.isRedirectPage():
            data_page = data_page.getRedirectTarget()
        text = data_page.text
        out_text += province + '\t'
        if ("title" in text):
            name_pattern = re.compile(r'title=(.*)\|')
        else:
            name_pattern = re.compile(r'name=(.*)\|')
        name = name_pattern.findall(text)[0]
        width = 20 - len(name.encode("GBK")) + len(name)
        out_text += name.ljust(width) + '\t'
        old_id = wd_id_pattern.findall(text)[0]
        out_text += old_id + '\t'
        province_page = pywikibot.Page(site, name)
        new_id = pywikibot.ItemPage.fromPage(province_page).getID().casefold()
        out_text += new_id + '\t'
        if (new_id != old_id):
            province_delta += 1
            text = re.sub(old_id, new_id, text)
            pywikibot.showDiff(data_page.text, text)
            data_page.text = text
            data_page.save(summary = "Updating wikidata item id from [[:d:{0}|{0}]] to [[:d:{1}|{1}]]".format(old_id, new_id), minor = False)
            out_text += '\n'
            print(out_text) # print detail only when updated
        city_check(province)
    print('Province check completed.\n{0} total, {1} delta.'.format(province_total, province_delta), end='\n')

def city_check(province):
    print("Start city check\n")
    city_list_page = pywikibot.Page(site, "Template:PRC_admin/list/{0}/00/00/000/000".format(province))
    city_list = pattern.findall(city_list_page.text)
    city_total = len(city_list)
    city_delta = 0

    for city in city_list:
        out_text = ''
        data_page = pywikibot.Page(site, "Template:PRC_admin/data/{0}/{1}/00/000/000".format(province, city))
        if data_page.isRedirectPage():
            data_page = data_page.getRedirectTarget()
        text = data_page.text
        if "fake=" in text:
            print('[INFO]Skip {0} {1} with fake tag'.format(province, city))
            continue
        out_text += province + ' '  + city + '\t'
        if ("title" in text):
            name_pattern = re.compile(r'title=(.*)\|')
        else:
            name_pattern = re.compile(r'name=(.*)\|')
        name = name_pattern.findall(text)[0]
        width = 20 - len(name.encode("GBK")) + len(name)
        out_text += name.ljust(width) + '\t'
        if "wikidata" not in text:
            print('[ERR]Wikidata ID not found for {0} {1}!'.format(province, city))
            continue
        old_id = wd_id_pattern.findall(text)[0]
        out_text += old_id + '\t'
        city_page = pywikibot.Page(site, name)
        new_id = pywikibot.ItemPage.fromPage(city_page).getID().casefold()
        out_text += new_id + '\t'
        if (new_id != old_id):
            city_delta += 1
            text = re.sub(old_id, new_id, text)
            pywikibot.showDiff(data_page.text, text)
            data_page.text = text
            data_page.save(summary = "Updating wikidata item id from [[:d:{0}|{0}]] to [[:d:{1}|{1}]]".format(old_id, new_id), minor = False)
            out_text += '\n'
            print(out_text) # print detail only when updated
    print('City check for {0} completed.\n{1} total, {2} delta.\n'.format(province, city_total, city_delta), end='----------\n')

if __name__ == '__main__':
    # Province, City, Area, Street 分别对应省级、地级、县级、乡级的行政区划

    province_list_page = pywikibot.Page(site, "Template:PRC_admin/list/00/00/00/000/000")
    pattern = re.compile(r'\d{2}')
    province_list = pattern.findall(province_list_page.text)
    wd_id_pattern = re.compile(r'wikidata=([Q|q]\d{1,9})\|')
    repo = site.data_repository()

    if (len(province_list) != 34):
        print("[ERR]Isn't it 34?")
        exit
    province_check(province_list)

end_time = time.time()
print("Elasped time: " + str(format(end_time - start_time, '.2f') + ' seconds'))