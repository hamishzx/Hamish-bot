# ！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 5 Aug 2024 18:11
# Name: edit
# Author: CHAU SHING SHING HAMISH

import requests
from bs4 import BeautifulSoup

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

    for village_link in village_soup.find_all('tr', class_='villagetr'):
        td_tags = village_link.find_all('td')
        if len(td_tags) == 3:
            key = td_tags[0].get_text()
            value = td_tags[2].get_text()
            villages_data[key] = value
    admins_data.update(villages_data)
    return villages_data


if __name__ == '__main__':
    get_province_list()
    for province_code in provinces_data.keys():
        print("Getting city list for province: " + provinces_data[province_code])
        get_city_list(province_code)
    for city_code in cities_data.keys():
        print("Getting county list for city: " + cities_data[city_code])
        get_county_list(city_code)
    for county_code in counties_data.keys():
        print("Getting town list for county: " + counties_data[county_code])
        get_town_list(county_code)
    for town_code in towns_data.keys():
        print("Getting village list for town: " + towns_data[town_code])
        get_village_list(town_code)

    print(admins_data)
