import requests
from configparser import ConfigParser
import os

config = ConfigParser()
if os.path.exists('proxy.ini'):
    config.read('proxy.ini', encoding='UTF-8')
else:
    with open("proxy.ini", "wt", encoding='UTF-8') as code:
        print("[proxy]",file=code)
        print("proxy=127.0.0.1:1080",file=code)

def get_html(url):#网页请求核心
    if not str(config['proxy']['proxy']) == '':
        try:
            proxies = {"http": "http://" + str(config['proxy']['proxy']),
                       "https": "https://" + str(config['proxy']['proxy'])}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36'}
            getweb = requests.get(str(url), timeout=10, headers=headers, proxies=proxies)
            getweb.encoding = 'utf-8'
            # print(getweb.text)
            try:
                return getweb.text
            except:
                print('[-]Connected failed!:Proxy error')
        except:
            aaaa=''
            #print('[-]Connect Failed.')


    else:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            getweb = requests.get(str(url), timeout=10, headers=headers)
            getweb.encoding = 'utf-8'
            try:
                return getweb.text
            except:
                print("[-]Connect Failed.")
        except:
            aaaa = ''
            #print('[-]Connect Failed.')