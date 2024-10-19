# ！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 10 Aug 2024 22:53
# Name: edit.py
# Author: CHAU SHING SHING HAMISH
import re
import sys

import pywikibot
from mwparserfromhell.wikicode import FLAGS

from pywikibot.data.api import Request
from pywikibot.exceptions import NoSiteLinkError
import toolforge


def get_data(title, code):
    code_parts = [code[:2], code[2:4], code[4:6], code[6:9], code[9:]]
    code_search = ' '.join([part for part in code_parts if int(part) != 0])
    code_query = f"SELECT * FROM query WHERE China_administrative_division_code = '{code_search}';"
    cursor.execute(code_query)
    wd_search_by_code = cursor.fetchall()
    wd_search_by_title = Request(site=pywikibot.Site('wikidata', 'wikidata'),
                        parameters={
                            'action': 'wbsearchentities',
                            'search': title,
                            'language': 'zh',
                            'format': 'json'
                        }).submit()
    try:
        by_code = wd_search_by_code[0][0][wd_search_by_code[0][0].find('Q'):] if wd_search_by_code else ''
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
            if item.claims['P442'][0].getTarget()[:5] == code_search[:5]:
                if item.claims['P442'][0].getTarget()[:12] == code_search[:12]:
                    pass
                elif get_whitelist(item.claims['P442'][0].getTarget(), code_search):
                    pass
                elif input('Continue?') == '2':
                    return {
                        'id': '',
                        'name': '',
                        'lat': '',
                        'lon': '',
                        'link': '',
                    }
            else:
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
    else:
        return 'village'

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
    if len(args) == 1:
        query = f"""
        SELECT * FROM admin
        WHERE province_code = '{args[0]}' AND city_code != '00' AND district_code = '00' AND county_code = '000' AND town_code = '000';
        """
        cursor.execute(query)
        filtered = cursor.fetchall()
        for row in filtered:
            text += '|' + row[3]
    elif len(args) == 2:
        query = f"""
        SELECT * FROM admin
        WHERE province_code = '{args[0]}' AND city_code = '{args[1]}' AND district_code != '00' AND county_code = '000' AND town_code = '000';
        """
        cursor.execute(query)
        filtered = cursor.fetchall()
        for row in filtered:
            text += '|' + row[4]
    elif len(args) == 3:
        query = f"""
        SELECT * FROM admin
        WHERE province_code = '{args[0]}' AND city_code = '{args[1]}' AND district_code = '{args[2]}' AND county_code != '000' AND town_code = '000';
        """
        cursor.execute(query)
        filtered = cursor.fetchall()
        for row in filtered:
            text += '|' + row[5]
    elif len(args) == 4:
        query = f"""
        SELECT * FROM admin
        WHERE province_code = '{args[0]}' AND city_code = '{args[1]}' AND district_code = '{args[2]}' AND county_code = '{args[3]}' AND town_code != '000';
        """
        cursor.execute(query)
        filtered = cursor.fetchall()
        for row in filtered:
            text += '|' + row[6]
    text += '|\narg={{{arg|}}}}}'
    return text

def check_onsite_page(srsearch):
    onsite_page_query = Request(site=site,
            parameters={
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'formatversion': '2',
                'srsearch': srsearch,
                'srnamespace': '10'
            }).submit()
    page = onsite_page_query['query']['search'][0]['title'] if onsite_page_query['query']['search'] else ''
    return page

def get_whitelist(before, after):
    before_parts = before.split()
    after_parts = after.split()

    for i in range(min(len(before_parts), len(after_parts))):
        if before_parts[i] != after_parts[i]:
            differing_index = i
            break

    from_segment = ' '.join(before_parts[:differing_index + 1])
    to_segment = ' '.join(after_parts[:differing_index + 1])

    whitelist_query = f"SELECT * FROM prc_admin_whitelist WHERE from_segment = '{from_segment}' AND to_segment = '{to_segment}';"
    cursor.execute(whitelist_query)
    whitelist = cursor.fetchall()
    if whitelist:
        print(f'Whitelist entry found: {from_segment} -> {to_segment}')
        return True

    from_code = from_segment.replace(' ', '').ljust(12, '0')
    to_code = to_segment.replace(' ', '').ljust(12, '0')
    from_parts = [from_code[:2], from_code[2:4], from_code[4:6], from_code[6:9], from_code[9:]]
    to_parts = [to_code[:2], to_code[2:4], to_code[4:6], to_code[6:9], to_code[9:]]
    from_page = pywikibot.Page(site, 'Template:PRC admin/data/' + '/'.join(from_parts))
    to_page = pywikibot.Page(site, 'Template:PRC admin/data/' + '/'.join(to_parts))
    if from_page.getRedirectTarget() == to_page:
        add_whitelist_query = f"INSERT INTO prc_admin_whitelist (from_segment, to_segment) VALUES ('{from_segment}', '{to_segment}');"
        cursor.execute(add_whitelist_query)
        conn.commit()
        print(f'Added whitelist entry: {from_segment} -> {to_segment}')
        return True
    return False


if len(sys.argv) != 2:
    print("Usage: python file.py <number>")
    sys.exit(1)

site = pywikibot.Site('zh', 'wikipedia')
site.login()
conn = toolforge.toolsdb('s53993__prc_admin_db')
cursor = conn.cursor()

try:
    query = f"SELECT * FROM admin WHERE full_code LIKE '{sys.argv[1]}%' LIMIT 1;"
    cursor.execute(query)
    data = cursor.fetchall()[0]
    while data:
        data_flag = False
        list_flag = False
        # ('110119203214', '桃条沟村委会', '11', '01', '19', '203', '214', '北京市', '市辖区', '延庆区', '珍珠泉乡')
        print(data)
        full_code = data[0]
        name = data[1]
        original_name = data[1]
        province_code = full_code[:2]
        city_code = full_code[2:4]
        county_code = full_code[4:6]
        town_code = full_code[6:9]
        village_code = full_code[9:]
        admin_type = determine_type(full_code)
        if admin_type == 'village':
            if custom_search := re.search(r'(?:.*省)?(.*?)(社区|街道办事处)(第(一|二|三|四|五|六|七|八|九|十))居(民)?委(员)?会', name):
                name = custom_search.group(1) + custom_search.group(3) + '社区'
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
                print('Custom search matched:', name, end='\n')
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
            if name.find('社区居委会') != -1 or name.find('社区居民委员会') != -1 or name.find('社区居民居委会') != -1:
                name = name[:name.find('社区')+2]
            elif name.find('村') != -1:
                name = name[:name.find('村')+1]
            name = re.sub(r'居委会|居民委员会', '社区', name) # custom replace
            if name.find('办事处') != -1 and name.find('办事处') != 0:
                name = name[:name.find('办事处')+3]
            if name.find('街道') != -1 and name.find('街道') != 0:
                name = name[:name.find('街道')+2]
        elif admin_type == 'town':
            if name.find('县') != -1:
                name = name[name.find('县')+1:]
            name = re.sub(r'办事处(街道)?', '街道', name)
        # data page
        if name != '市辖区':
            wd_dict = get_data(name, full_code)
            # 机场工作区 110105020400
            if wd_dict['id'] == '' and name.find('社区') != -1:
                wd_dict = get_data(name[:-2], full_code)
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
                    data_page.save(summary='更新行政區劃數據：'+ name)
                    data_flag = True
            else:
                if wd_dict['id']:
                    current_data_page_title = check_onsite_page(wd_dict['id']) if check_onsite_page(wd_dict['id']) else ''
                    if current_data_page_title:
                        current_data_page = pywikibot.Page(site, current_data_page_title)
                        current_data_page.move(data_page.title(), reason='行政區劃代碼變更：' + name, movetalk=True,
                                               noredirect=False)
                        print(f'Moved {current_data_page_title} to {data_page.title()}')
                        # move related list page for incoming handle
                        if village_code == '000':
                            current_list_page = pywikibot.Page(site, current_data_page_title.replace('data', 'list'))
                            current_list_page.move(data_page.title().replace('data', 'list'), reason='行政區劃代碼變更：' + name, movetalk=True, noredirect=False)
                            print(f'Moved {current_list_page.title()} to {data_page.title().replace("data", "list")}')
                        if data_page.text != data_page_text:
                            pywikibot.showDiff(data_page.text, data_page_text)
                            data_page.text = data_page_text
                            data_page.save(summary='更新行政區劃數據：' + name)
                            data_flag = True
                    else:
                        pywikibot.showDiff('', data_page_text)
                        data_page.text = data_page_text
                        data_page.save(summary='建立行政區劃數據：' + name)
                        data_flag = True
                else:
                    pywikibot.showDiff('', data_page_text)
                    data_page.text = data_page_text
                    data_page.save(summary='建立行政區劃數據：' + name)
                    data_flag = True

        # list page
        if admin_type != 'village':
            list_page_text = ''
            if admin_type == 'province':
                list_page_text = build_list_page(province_code)
            elif admin_type == 'city':
                list_page_text = build_list_page(province_code, city_code)
            elif admin_type == 'county':
                list_page_text = build_list_page(province_code, city_code, county_code)
            elif admin_type == 'town':
                list_page_text = build_list_page(province_code, city_code, county_code, town_code)

            list_page = pywikibot.Page(site, 'Template:PRC admin/list/' +
                                         f"{data[0][:2]}/{data[0][2:4]}/{data[0][4:6]}/{data[0][6:9]}/{data[0][9:]}")

            if list_page_text != list_page.text:
                pywikibot.showDiff(list_page.text, list_page_text)
                list_page.text = list_page_text
                list_page.save(summary='更新行政區劃下級列表：' + name)
                list_flag = True
        record_query = f"INSERT INTO admin_done (full_code, name, format_name, data, list) VALUES ('{full_code}', '{original_name}', '{name}', {data_flag}, {list_flag});"
        cursor.execute(record_query)
        conn.commit()
        delete_query = f"DELETE FROM admin WHERE full_code = '{full_code}';"
        cursor.execute(delete_query)
        conn.commit()

        cursor.execute(query)
        data = cursor.fetchall()[0]

except KeyboardInterrupt:
    print('Interrupted by user')
    cursor.close()
    conn.close()