# -*- coding: utf-8 -*-
import datetime
import os
import re
import time
import pywikibot
from pywikibot.data.api import Request

os.environ['TZ'] = 'UTC'
print('Starting at: ' + time.asctime(time.localtime(time.time())))
start_time = time.time()
rec_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).__format__('%d/%m/%y %H:%M')

site = pywikibot.Site()
site.login()

global result_list, table_element
result_list = [0, 0]  # [total, delta]
table_element = []


# Province, City, Area, Street 分别对应省级、地级、县级、乡级的行政区划
# old_id 是模板页面上已存在的 wikidata 值，new_id是模板页面上 name/title 值的条目的wikidata id
def convert_title(title):
    req = Request(site=site, parameters={
        'action': 'query',
        'titles': title,
        "redirects": 1,
        "converttitles": 1
    })
    data = req.submit()
    new_title = list(data['query']['pages'].values())[0]['title']
    return new_title


def build_request(incoming_list):
    # incoming_list is always province's list
    province_list = incoming_list
    request = {'type': '', 'code': ''}
    for province in province_list:
        request['type'] = 'province'
        request['code'] = province
        main_check(request)
        city_list_page = pywikibot.Page(site, "Template:PRC_admin/list/{0}/00/00/000/000".format(province))
        city_list = pattern.findall(city_list_page.text)
        for city in city_list:
            request['type'] = 'city'
            request['code'] = province + ' ' + city
            main_check(request)
            area_list_page = pywikibot.Page(site, "Template:PRC_admin/list/{0}/{1}/00/000/000".format(province, city))
            area_list = pattern.findall(area_list_page.text)
            for area in area_list:
                request['type'] = 'area'
                request['code'] = province + ' ' + city + ' ' + area
                main_check(request)
                street_list_page = pywikibot.Page(site,
                                                  "Template:PRC_admin/list/{0}/{1}/00/000/000".format(province, city))
                street_list = pattern.findall(street_list_page.text)
                for street in street_list:
                    request['type'] = 'area'
                    request['code'] = province + ' ' + city + ' ' + area + ' ' + street
                    main_check(request)


def main_check(incoming_request):
    province = "00"
    city = "00"
    area = "00"
    street = "000"
    doing_code = incoming_request['code']
    if incoming_request['type'] == 'province':
        province = incoming_request['code']
    elif incoming_request['type'] == 'city':
        province = incoming_request['code'][:2]
        city = incoming_request['code'][3:5]
    elif incoming_request['type'] == 'area':
        province = incoming_request['code'][:2]
        city = incoming_request['code'][3:5]
        area = incoming_request['code'][6:8]
    elif incoming_request['type'] == 'street':
        province = incoming_request['code'][:2]
        city = incoming_request['code'][3:5]
        area = incoming_request['code'][6:8]
        street = incoming_request['code'][9:12]
    else:
        print("[ERR]Unknown type for this request:\n" + incoming_request)
    wd_id_pattern = re.compile(r'wikidata=([Q|q]\d{1,9})\|')
    out_text = ''
    data_page = pywikibot.Page(site, "Template:PRC_admin/data/{0}/{1}/{2}/{3}/000".format(province, city, area, street))
    if data_page.isRedirectPage():
        data_page = data_page.getRedirectTarget()
    text = data_page.text
    if "fake=" in text:
        print('[INFO]Skip {0} with fake tag'.format(doing_code))
        return
    out_text += province + '\t'
    if "title" in text:
        name_pattern = re.compile(r'title=(.*)\|')
    else:
        name_pattern = re.compile(r'name=(.*)\|')
    name = name_pattern.findall(text)[0]
    width = 20 - len(name.encode("GBK")) + len(name)
    out_text += name.ljust(width) + '\t'
    try:
        old_id = wd_id_pattern.findall(text)[0]
    except IndexError:
        old_id = "Not Found"
    out_text += old_id.ljust(10) + '\t'
    try:
        new_id = pywikibot.ItemPage.fromPage(pywikibot.Page(site, name)).getID().casefold()
    except pywikibot.exceptions.NoPage:
        name = convert_title(name)
        new_id = pywikibot.ItemPage.fromPage(pywikibot.Page(site, name)).getID().casefold()
    out_text += new_id.ljust(10) + '\t'
    if new_id != old_id:
        result_list[1] += 1
        text = re.sub(old_id, new_id, text)
        pywikibot.showDiff(data_page.text, text)
        data_page.text = text
        # data_page.save(summary = "Updating wikidata item id from [[:d:{0}|{0}]] to [[:d:{1}|{1}]]".format(old_id, new_id), minor = False)
        out_text += '\n'
        print(out_text)  # print detail only when updated
        table_element.append([doing_code, name, old_id, new_id])
    result_list[0] += 1


def main():
    province_list_page = pywikibot.Page(site, "Template:PRC_admin/list/00/00/00/000/000")
    pattern = re.compile(r'\d{2}')
    province_list = pattern.findall(province_list_page.text)

    if len(province_list) != 34:
        print("[ERR]Isn't it 34?")
        exit()
    print("Start check operations")
    for province in province_list:
        request = {"type": "province", "code": province}
        main_check(request)

    print('Check completed.\n{0} total, {1} delta.'.format(result_list[0], result_list[1]), end='\n')


if __name__ == '__main__':
    main()

end_time = time.time()
print("Elapsed time: " + str(format(end_time - start_time, '.2f') + ' seconds'))
