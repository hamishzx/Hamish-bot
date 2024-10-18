# ！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 10 Aug 2024 22:53
# Name: edit.py
# Author: CHAU SHING SHING HAMISH
import os
import re

import pywikibot

from pywikibot.data.api import Request
import pandas as pd
from pywikibot.exceptions import NoSiteLinkError
from SPARQLWrapper import SPARQLWrapper, JSON


site = pywikibot.Site('zh', 'wikipedia')
site.login()

def get_data(title, code):
    code_parts = [code[:2], code[2:4], code[4:6], code[6:9], code[9:]]
    code_search = ' '.join([part for part in code_parts if int(part) != 0])
    wd_search_by_code = SPARQLWrapper("https://query.wikidata.org/sparql")
    wd_search_by_code.setQuery(f"""
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        SELECT ?item ?itemLabel WHERE {{
          ?item wdt:P442 "{code_search}" .
        }}
        """)
    wd_search_by_code.setReturnFormat(JSON)
    wd_search_by_code = wd_search_by_code.query().convert()
    wd_search_by_title = Request(site=pywikibot.Site('wikidata', 'wikidata'),
                        parameters={
                            'action': 'wbsearchentities',
                            'search': title,
                            'language': 'zh',
                            'format': 'json'
                        }).submit()
    try:
        by_code = wd_search_by_code['results']['bindings'][0]['item']['value'][wd_search_by_code['results']['bindings'][0]['item']['value'].find('Q'):] if wd_search_by_code['results']['bindings'] else ''
        by_title = wd_search_by_title['search'][0]['id'] if wd_search_by_title['search'] else ''

        if by_code and by_title:
            wikidata_id = by_code if by_code != by_title else by_title
        elif by_code:
            wikidata_id = by_code
        elif by_title:
            wikidata_id = by_title
        else:
            return {
                'id': '',
                'name': '',
                'lat': '',
                'lon': '',
                'link': '',
            }
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
            print(f'Code mismatch: {item.claims["P442"][0].getTarget()} in {wikidata_id} vs {code_search} in table')
            if input('Continue?') == '2':
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
    except Exception as e:
        print(e)
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
    try:
        if incoming_dict['village']:
            text += 'title=|\n'
    except KeyError:
        pass
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

df = pd.read_excel(os.path.dirname(os.path.realpath(__file__)) + '/admin.xlsx', dtype=str)
processed_df = pd.read_excel(os.path.dirname(os.path.realpath(__file__)) + '/admin_done.xlsx', dtype=str)
try:
    for index, row in df.iterrows():
        if not processed_df[processed_df.eq(row).all(axis=1)].empty:
            print(row.to_list()[0] + ' Already processed')
            continue
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
        if village_code != '000':
            dict_to_data['village'] = True
        data_page_text = build_data_page(dict_to_data)
        data_page = pywikibot.Page(site, 'Template:PRC admin/data/' +
                                   f"{data[0][:2]}/{data[0][2:4]}/{data[0][4:6]}/{data[0][6:9]}/{data[0][9:]}")

        if data_page.exists():
            current_data_page_text = data_page.text
            name_pattern = re.compile(r'name=(.*?)\|')
            current_name = name_pattern.search(current_data_page_text).group(1)
            if current_name != name:
                print(f'Name mismatch: {current_name} on page vs {name} in table')
                pywikibot.showDiff(data_page.text, data_page_text)
                data_page.text = data_page_text
                data_page.save(summary='更新區劃數據')
        if not data_page.exists():
            pywikibot.showDiff('', data_page_text)
            data_page.text = data_page_text
            data_page.save(summary='更新區劃數據')

        if village_code == '000':
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

            if list_page_text != list_page.text:
                pywikibot.showDiff(list_page.text, list_page_text)
                list_page.text = list_page_text
                list_page.save(summary='更新區劃下級列表')
        processed_df = pd.concat([pd.DataFrame([row], columns=df.columns), processed_df], ignore_index=True)
except KeyboardInterrupt:
    print('Interrupted by user')
    processed_df.to_excel(os.path.dirname(os.path.realpath(__file__)) + '/admin_done.xlsx', index=False)
    print('Data saved')
except Exception as e:
    print(e)
    processed_df.to_excel(os.path.dirname(os.path.realpath(__file__)) + '/admin_done.xlsx', index=False)
    print('Data saved')