# ！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 10 Aug 2024 22:53
# Name: edit.py
# Author: CHAU SHING SHING HAMISH

import pywikibot
from pywikibot.data.api import Request
import pandas as pd
from pywikibot.exceptions import NoSiteLinkError

site = pywikibot.Site('zh', 'wikipedia')
site.login()

def get_data(title, code):
    wd_search = Request(site=pywikibot.Site('wikidata', 'wikidata'),
                      parameters={
                          'action': 'wbsearchentities',
                          'search': title,
                          'language': 'zh',
                          'format': 'json'
                      }).submit()
    try:
        wikidata_id = wd_search['search'][0]['id']
        data_dict = {
            'id': wikidata_id,
            'name': '',
            'lat': '',
            'lon': '',
            'link': '',
        }
        item = pywikibot.ItemPage(pywikibot.Site('wikidata', 'wikidata'), wikidata_id)
        if (item.claims['P442'][0].getTarget().replace(' ', '') !=
                code[:len(item.claims['P442'][0].getTarget().replace(' ', ''))]):
            return {
                'id': '',
                'name': '',
                'lat': '',
                'lon': '',
                'link': '',
            }
        try:
            if item.claims['P1448']:
                data_dict['name'] = item.claims['P1448'][0].getTarget().text
        except KeyError:
            pass
        try:
            if item.claims['P625']:
                data_dict['lat'] = item.claims['P625'][0].getTarget().lat
                data_dict['lon'] = item.claims['P625'][0].getTarget().lon
        except KeyError:
            pass
        try:
            data_dict['link'] = item.getSitelink(site)
        except NoSiteLinkError:
            pass
        return data_dict
    except IndexError:
        return {
            'id': '',
            'name': '',
            'lat': '',
            'lon': '',
            'link': '',
        }
    except KeyError:
        return {
            'id': '',
            'name': '',
            'lat': '',
            'lon': '',
            'link': '',
        }

def determine_type(code):
    if code[2:] == '0000000000':
        return 'province'
    elif code[4:] == '00000000':
        return 'city'
    elif code[6:] == '000000':
        return 'county'
    elif code[9:] == '000':
        return 'town'

def build_data_page(incoming_dict):
    text = '{{ {{{1|PRC admin/showdata}}}|\n'
    text += 'name=' + incoming_dict['name'] + '|\n'
    if incoming_dict['title'] and incoming_dict['title'] != incoming_dict['name']:
        text += 'title=' + incoming_dict['title'] + '|\n'
    if incoming_dict['lat']:
        text += 'lat=' + str(incoming_dict['lat']) + '|\n'
    if incoming_dict['lon']:
        text += 'lng=' + str(incoming_dict['lon']) + '|\n'
    if incoming_dict['wd_name']:
        text += 'wikidata-original-name=' + incoming_dict['wd_name'] + '|\n'
    if incoming_dict['id']:
        text += 'wikidata=' + incoming_dict['id'].lower() + '|\n'
    text += 'arg={{{arg|}}}}}'
    return text

def build_list_page(*args):
    text = '{{ {{{1|PRC admin/showlist}}}\n'
    if len(args) == 2:
        filtered = df.query('province_code == @args[1] and city_code != "00" and district_code == "00" and county_code == "000" and town_code == "000"')
        for index, row in filtered.iterrows():
            data = row.to_list()
            text += '|' + data[3]
    elif len(args) == 3:
        filtered = df.query('province_code == @args[1] and city_code == @args[2] and district_code != "00" and county_code == "000" and town_code == "000"')
        for index, row in filtered.iterrows():
            data = row.to_list()
            text += '|' + data[4]
    elif len(args) == 4:
        filtered = df.query('province_code == @args[1] and city_code == @args[2] and district_code == @args[3] and county_code != "000" and town_code == "000"')
        for index, row in filtered.iterrows():
            data = row.to_list()
            text += '|' + data[5]
    elif len(args) == 5:
        filtered = df.query('province_code == @args[1] and city_code == @args[2] and district_code == @args[3] and county_code == @args[4] and town_code != "000"')
        for index, row in filtered.iterrows():
            data = row.to_list()
            text += '|' + data[6]
    text += '|\narg={{{arg|}}}}}'
    return text

df = pd.read_excel('admin.xlsx', dtype=str)

for index, row in df.iterrows():
    data = row.to_list()
    # ['110119203214', '桃条沟村委会', '11', '01', '19', '203', '214', '北京市', '市辖区', '延庆区', '珍珠泉乡']
    print(data)
    full_code = data[0]
    name = data[1]
    province_code = data[2]
    city_code = data[3]
    county_code = data[4]
    town_code = data[5]
    village_code = data[6]
    if village_code != '000':
        if name.find('社区') != -1:
            name = name[:name.find('社区')+2]
        elif name.find('村') != -1:
            name = name[:name.find('村')+1]
    province = data[7]
    city = data[8]
    county = data[9]
    town = data[10]
    admin_type = determine_type(full_code)
    wd_dict = get_data(name, full_code)
    dict_to_data = {
        'name': name,
        'title': wd_dict['link'],
        'id': '',
        'lat': '',
        'lon': '',
        'wd_name': ''
    }
    if wd_dict['id']:
        dict_to_data['id'] = wd_dict['id']
    if wd_dict['lat']:
        dict_to_data['lat'] = wd_dict['lat']
    if wd_dict['lon']:
        dict_to_data['lon'] = wd_dict['lon']
    if wd_dict['name']:
        dict_to_data['wd_name'] = wd_dict['name']
    data_page_text = build_data_page(dict_to_data)
    data_page = pywikibot.Page(site, 'Template:PRC admin/data/' +
                               f"{data[0][:2]}/{data[0][2:4]}/{data[0][4:6]}/{data[0][6:9]}/{data[0][9:]}")
    if not data_page.exists():
        print(data_page_text)
        data_page.text = data_page_text
        data_page.save(summary='建立區劃數據')

    list_page_text = ''
    if admin_type == 'province':
        list_page_text = build_list_page(df, province_code)
    elif admin_type == 'city':
        list_page_text = build_list_page(df, province_code, city_code)
    elif admin_type == 'county':
        list_page_text = build_list_page(df, province_code, city_code, county_code)
    elif admin_type == 'town':
        list_page_text = build_list_page(df, province_code, city_code, county_code, town_code)

    list_page = pywikibot.Page(site, 'Template:PRC admin/list/' +
                                 f"{data[0][:2]}/{data[0][2:4]}/{data[0][4:6]}/{data[0][6:9]}/{data[0][9:]}")
    if not list_page.exists():
        print(list_page_text)
        list_page.text = list_page_text
        list_page.save(summary='建立區劃下級列表')