#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from configparser import ConfigParser
import os
import re
import time
import sys
from lxml import etree
import sys
import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)
# sys.setdefaultencoding('utf-8')

config_file='config.ini'
config = ConfigParser()

if os.path.exists(config_file):
    try:
        config.read(config_file, encoding='UTF-8')
    except:
        print('[-]Config.ini read failed! Please use the offical file!')
else:
    print('[+]config.ini: not found, creating...',end='')
    with open("config.ini", "wt", encoding='UTF-8') as code:
        file_text = """[common]
main_mode=1
failed_output_folder=failed
success_output_folder=JAV_output
soft_link=0

[proxy]
proxy=192.168.2.2:1080
timeout=10
retry=3

[Name_Rule]
location_rule=actor+'/'+number
naming_rule=number+'-'+title

[update]
update_check=1

[media]
media_warehouse=emby
#emby or plex or kodi ,emby=jellyfin

[escape]
literals=\()/
folders=failed,JAV_output

[debug_mode]
switch=0

"""
        print(file_text, file=code)
    time.sleep(2)
    print('.')
    print('[+]config.ini: created!')
    print('[+]Please restart the program!')
    time.sleep(4)
    os._exit(0)
    try:
        config.read(config_file, encoding='UTF-8')
    except:
        print('[-]Config.ini read failed! Please use the offical file!')

def get_network_settings():
    try:
        proxy = config["proxy"]["proxy"]
        timeout = int(config["proxy"]["timeout"])
        retry_count = int(config["proxy"]["retry"])
        assert timeout > 0
        assert retry_count > 0
    except:
        raise ValueError("[-]Proxy config error! Please check the config.")
    return proxy, timeout, retry_count


def get_data_state(data: dict) -> bool:  # 元数据获取失败检测
    if data["title"] is None or data["title"] == "" or data["title"] == "null":
        return False

    if data["number"] is None or data["number"] == "" or data["number"] == "null":
        return False

    return True

def ReadMediaWarehouse():
    return config['media']['media_warehouse']

def UpdateCheckSwitch():
    check=str(config['update']['update_check'])
    if check == '1':
        return '1'
    elif check == '0':
        return '0'
    elif check == '':
        return '0'

def getXpathSingle(htmlcode,xpath):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath(xpath)).strip(" ['']")
    return result1

def get_html(url,cookies = None):#网页请求核心
    proxy, timeout, retry_count = get_network_settings()
    i = 0
    while i < retry_count:
        try:
            if not proxy == '':
                proxies = {"http": "http://" + proxy,"https": "https://" + proxy}
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36'}
                getweb = requests.get(str(url), headers=headers, timeout=timeout,proxies=proxies, cookies=cookies)
                getweb.encoding = 'utf-8'
                return getweb.text
            else:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                getweb = requests.get(str(url), headers=headers, timeout=timeout, cookies=cookies)
                getweb.encoding = 'utf-8'
                return getweb.text
        except:
            i += 1
            print('[-]Connect retry '+str(i)+'/'+str(retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')


def post_html(url: str, query: dict) -> requests.Response:
    proxy, timeout, retry_count = get_network_settings()

    if proxy:
        proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
    else:
        proxies = {}

    for i in range(retry_count):
        try:
            result = requests.post(url, data=query, proxies=proxies)
            return result
        except requests.exceptions.ProxyError:
            print("[-]Connect retry {}/{}".format(i+1, retry_count))
    print("[-]Connect Failed! Please check your Proxy or Network!")
