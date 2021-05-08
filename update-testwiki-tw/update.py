#!/usr/bin/env python                                                                                                                                                                                                                            
# -*- coding: utf-8 -*-                                                                                                                                                                                                                          

import json
import os
import urllib.request
import re
import sys
import pywikibot

os.environ['TZ'] = 'UTC'

file_path_list = {    
    "modules/friendlyshared.js",
    "modules/friendlytag.js",
    "modules/friendlytalkback.js",
    "modules/twinklearv.js",
    "modules/twinklebatchdelete.js",
    "modules/twinklebatchundelete.js",
    "modules/twinkleblock.js",
    "modules/twinkleclose.js",
    "modules/twinkleconfig.js",
    "modules/twinklecopyvio.js",
    "modules/twinklediff.js",
    "modules/twinklefluff.js",
    "modules/twinkleimage.js",
    "modules/twinkleprotect.js",
    "modules/twinklespeedy.js",
    "modules/twinklestub.js",
    "modules/twinkleunlink.js",
    "modules/twinklewarn.js",
    "modules/twinklexfd.js",
    "morebits.css",
    "morebits.js",
    "select2/select2.min.css",
    "select2/select2.min.js",
    "twinkle.css",
    "twinkle.js",
    "twinkle-pagestyles.css"
}

site = pywikibot.Site("test", "wikipedia")
site.login()
prefix = "User:Hamish/Twinkle/"
repo_info_str = urllib.request.urlopen('https://api.github.com/repos/xi-plus/twinkle/commits?sha=master').read().decode("utf8")
try:
    repo_info = json.loads(repo_info_str)
except json.decoder.JSONDecodeError as e:
    print('JSONDecodeError: {} content: {}'.format(e, repo_info_str))
    exit
sha = repo_info[0]['sha']
i = 0
for path in file_path_list:
    i += 1
    print(str(i) + "/" + str(len(file_path_list)) + ": " + path)
    source_url = 'https://raw.githubusercontent.com/xi-plus/twinkle/master/{0}'.format(path)
    if "select2" in path:
        path = path[8:]
    base_page = pywikibot.Page(site, prefix + str(path))
    base_text = base_page.text
    source_text = urllib.request.urlopen(source_url).read().decode('utf8')
    if source_text != base_text:
        base_page.text = source_text
        pywikibot.showDiff(base_text, base_page.text)
        summary = 'Initialise to ' + sha + ' at xi-plus/master'
        base_page.save(summary=summary, minor=True)
    else:
        continue