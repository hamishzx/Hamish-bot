# ！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 5 Aug 2024 18:11
# Name: edit
# Author: CHAU SHING SHING HAMISH

import time
import openpyxl
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

base_url = "https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2023/"
admins_data = {}
provinces_data = {}
cities_data = {}
counties_data = {}
towns_data = {}
villages_data = {}


def get_province_list():
    province_data = requests.get(base_url + 'index.html')
    province_data.encoding = 'utf-8'

    province_soup = BeautifulSoup(province_data.text, 'html.parser')
    for province_link in province_soup.find_all('a')[:-1]:
        provinces_data.update({province_link.get('href')[:-5] + '0000000000': province_link.get_text()})
    admins_data.update(provinces_data)
    return provinces_data


def get_city_list(code):
    province = code[:2]
    city_data = requests.get(base_url + province + '.html')
    city_data.encoding = 'utf-8'

    city_soup = BeautifulSoup(city_data.text, 'html.parser')
    cities_data.clear()
    for city_link in city_soup.find_all('tr', class_='citytr'):
        a_tags = city_link.find_all('a')
        if len(a_tags) == 2:
            key = a_tags[0].get_text()
            value = a_tags[1].get_text()
            cities_data[key] = value
    admins_data.update(cities_data)
    return cities_data


def get_county_list(code):
    province = code[:2]
    city = code[2:4]
    county_data = requests.get(base_url + province + '/' + province + city + '.html')
    county_data.encoding = 'utf-8'

    county_soup = BeautifulSoup(county_data.text, 'html.parser')
    counties_data.clear()
    for county_link in county_soup.find_all('tr', class_='countytr'):
        a_tags = county_link.find_all('a')
        if len(a_tags) == 2:
            key = a_tags[0].get_text()
            value = a_tags[1].get_text()
            counties_data[key] = value
    admins_data.update(counties_data)
    return counties_data


def get_town_list(code):
    province = code[:2]
    city = code[2:4]
    county = code[4:6]
    town_data = requests.get(base_url + province + '/' + city + '/' + province + city + county + '.html')
    town_data.encoding = 'utf-8'

    town_soup = BeautifulSoup(town_data.text, 'html.parser')
    towns_data.clear()
    for town_link in town_soup.find_all('tr', class_='towntr'):
        a_tags = town_link.find_all('a')
        if len(a_tags) == 2:
            key = a_tags[0].get_text()
            value = a_tags[1].get_text()
            towns_data[key] = value
    admins_data.update(towns_data)
    return towns_data


def get_village_list(code):
    province = code[:2]
    city = code[2:4]
    county = code[4:6]
    town = code[6:9]

    village_data = requests.get(base_url +
                                province + '/' + city + '/' + county + '/' + province + city + county + town + '.html')
    village_data.encoding = 'utf-8'

    village_soup = BeautifulSoup(village_data.text, 'html.parser')
    villages_data.clear()
    for village_link in village_soup.find_all('tr', class_='villagetr'):
        td_tags = village_link.find_all('td')
        if len(td_tags) == 3:
            key = td_tags[0].get_text()
            value = td_tags[2].get_text()
            villages_data[key] = value
    admins_data.update(villages_data)
    return villages_data


def construct_sheet(data):
    wb = openpyxl.load_workbook('query.xlsx')
    sheet = wb.worksheets[0]
    for admin in data:
        if admin[2:] == '0000000000':
            row_to_insert = [admin, data[admin], admin[:2], '00', '00', '000', '000', '', '', '', '']
        elif admin[4:] == '00000000':
            row_to_insert = [admin, data[admin], admin[:2], admin[2:4], '00', '000', '000',
                             admins_data[admin[:2]+'0000000000'], '', '', '']
        elif admin[6:] == '000000':
            row_to_insert = [admin, data[admin], admin[:2], admin[2:4], admin[4:6], '000', '000',
                             admins_data[admin[:2]+'0000000000'], admins_data[admin[:4]+'00000000'], '', '']
        elif admin[9:] == '000':
            row_to_insert = [admin, data[admin], admin[:2], admin[2:4], admin[4:6], admin[6:9], '000',
                             admins_data[admin[:2]+'0000000000'], admins_data[admin[:4]+'00000000'],
                             admins_data[admin[:6]+'000000'], '']
        else:
            row_to_insert = [admin, data[admin], admin[:2], admin[2:4], admin[4:6], admin[6:9], admin[9:12],
                             admins_data[admin[:2]+'0000000000'], admins_data[admin[:4]+'00000000'],
                             admins_data[admin[:6]+'000000'], admins_data[admin[:9]+'000']]
        sheet.append(row_to_insert)
    wb.save('query.xlsx')


if __name__ == '__main__':
    try:
        get_province_list()
        for province_code in tqdm(provinces_data.keys(), desc='Provinces'):
            get_city_list(province_code)
            construct_sheet(cities_data)
            for city_code in tqdm(cities_data.keys(), desc='Cities'):
                get_county_list(city_code)
                construct_sheet(counties_data)
                for county_code in tqdm(counties_data.keys(), desc='Counties'):
                    get_town_list(county_code)
                    construct_sheet(towns_data)
                    for town_code in tqdm(towns_data.keys(), desc='Towns'):
                        get_village_list(town_code)
                        construct_sheet(villages_data)
            time.sleep(60)
    except Exception as e:
        print(e)

