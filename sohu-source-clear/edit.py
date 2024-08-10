# -*- coding: utf-8 -*-       

"""
# author: Hamish Chengcheng Zou<hamish.zou@dell.com>
# file  : edit.py
# time  : 27/4/2024 2:01 am
# desc  : 
"""


import pywikibot

site = pywikibot.Site('zh', 'wikipedia')
site.login()

todo_list = site.search('insource:"www.sohu.com/a/www.sohu.com/"', namespace=0)

for page in todo_list:
    text = page.text
    text = text.replace('www.sohu.com/a/www.sohu.com/', 'www.sohu.com/')
    page.text = text
    page.save('去除冗余的sohu链接，[[Special:PermaLink/82374969#清理www.sohu.com/a/www.sohu.com/|BOTREQ]]', minor=True)
    print(page.title(), 'done')
