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

global result_list
result_list = [0, 0] # [total, delta]


# Province, City, Area, Street 分别对应省级、地级、县级、乡级的行政区划

province_list_page = pywikibot.Page(site, "Template:PRC_admin/list/00/00/00/000/000")
pattern = re.compile(r'\d{2}')
province_list = pattern.findall(province_list_page.text)
wd_id_pattern = re.compile(r'wikidata=([Q|q]\d{1,9})\|')
repo = site.data_repository()

if (len(province_list) != 34):
    print("[ERR]Isn't it 34?")
    exit

def province_check(incoming_list):
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
        out_text += old_id.ljust(10) + '\t'
        province_page = pywikibot.Page(site, name)
        if (province_page.isRedirectPage()):
            province_page = province_page.getRedirectTarget()
        new_id = pywikibot.ItemPage.fromPage(province_page).getID().casefold()
        out_text += new_id.ljust(10) + '\t'
        if (new_id != old_id):
            province_delta += 1
            text = re.sub(old_id, new_id, text)
            pywikibot.showDiff(data_page.text, text)
            data_page.text = text
            data_page.save(summary = "Updating wikidata item id from [[:d:{0}|{0}]] to [[:d:{1}|{1}]]".format(old_id, new_id), minor = False)
            out_text += '\n'
        print(out_text) # print detail only when updated
        city_check(province)
    result_list[0] += province_total
    result_list[1] += province_delta


def city_check(province):
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
        out_text += old_id.ljust(10) + '\t'
        city_page = pywikibot.Page(site, name)
        if (city_page.isRedirectPage()):
            city_page = city_page.getRedirectTarget()
        new_id = pywikibot.ItemPage.fromPage(city_page).getID().casefold()
        out_text += new_id.ljust(10) + '\t'
        if (new_id != old_id):
            city_delta += 1
            text = re.sub(old_id, new_id, text)
            pywikibot.showDiff(data_page.text, text)
            data_page.text = text
            data_page.save(summary = "Updating wikidata item id from [[:d:{0}|{0}]] to [[:d:{1}|{1}]]".format(old_id, new_id), minor = False)
            out_text += '\n'
        print(out_text) # print detail only when updated
        area_check(province, city)
    result_list[0] += city_total
    result_list[1] += city_delta


def area_check(province, city):
    area_list_page = pywikibot.Page(site, "Template:PRC_admin/list/{0}/{1}/00/000/000".format(province, city))
    area_list = pattern.findall(area_list_page.text)
    area_total = len(area_list)
    area_delta = 0

    for area in area_list:
        out_text = ''
        data_page = pywikibot.Page(site, "Template:PRC_admin/data/{0}/{1}/{2}/000/000".format(province, city, area))
        if data_page.isRedirectPage():
            data_page = data_page.getRedirectTarget()
        text = data_page.text
        if "fake=" in text:
            print('[INFO]Skip {0} {1} {2} with fake tag'.format(province, city, area))
            continue
        out_text += province + ' '  + city + ' ' + area + '\t'
        if ("title" in text):
            name_pattern = re.compile(r'title=(.*)\|')
        else:
            name_pattern = re.compile(r'name=(.*)\|')
        name = name_pattern.findall(text)[0]
        width = 20 - len(name.encode("GBK")) + len(name)
        out_text += name.ljust(width) + '\t'
        if "wikidata" not in text:
            print('[ERR]Wikidata ID not found for {0} {1} {2}!'.format(province, city, area))
            continue
        old_id = wd_id_pattern.findall(text)[0]
        out_text += old_id.ljust(10) + '\t'
        area_page = pywikibot.Page(site, name)
        if (area_page.isRedirectPage()):
            area_page = area_page.getRedirectTarget()
        new_id = pywikibot.ItemPage.fromPage(area_page).getID().casefold()
        out_text += new_id.ljust(10) + '\t'
        if (new_id != old_id):
            area_delta += 1
            text = re.sub(old_id, new_id, text)
            pywikibot.showDiff(data_page.text, text)
            data_page.text = text
            data_page.save(summary = "Updating wikidata item id from [[:d:{0}|{0}]] to [[:d:{1}|{1}]]".format(old_id, new_id), minor = False)
            out_text += '\n'
        print(out_text) # print detail only when updated
    result_list[0] += area_total
    result_list[1] += area_delta
# TODO: 简繁转换

if __name__ == '__main__':
    print("Start check operations")
    province_check(province_list)
    print('Check completed.\n{0} total, {1} delta.'.format(result_list[0], result_list[1]), end='\n')

end_time = time.time()
print("Elasped time: " + str(format(end_time - start_time, '.2f') + ' seconds'))

