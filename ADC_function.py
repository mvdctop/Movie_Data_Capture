import requests
from configparser import RawConfigParser
import os
import re
from retrying import retry
import sys

# content = open('proxy.ini').read()
# content = re.sub(r"\xfe\xff","", content)
# content = re.sub(r"\xff\xfe","", content)
# content = re.sub(r"\xef\xbb\xbf","", content)
# open('BaseConfig.cfg', 'w').write(content)

config = RawConfigParser()
if os.path.exists('proxy.ini'):
    config.read('proxy.ini', encoding='UTF-8')
else:
    with open("proxy.ini", "wt", encoding='UTF-8') as code:
        print("[proxy]",file=code)
        print("proxy=127.0.0.1:1080",file=code)
        print("timeout=10", file=code)
        print("[Name_Rule]", file=code)
        print("location_rule='JAV_output/'+actor+'/['+number+']-'+title",file=code)
        print("naming_rule=number+'-'+title",file=code)
        print("[update]",file=code)
        print("update_check=1")
def UpdateCheckSwitch():
    check=str(config['update']['update_check'])
    if check == '1':
        return '1'
    elif check == '0':
        return '0'
def get_html(url,cookies = None):#网页请求核心
    i = 0
    retry_count = int(config['proxy']['retry'])
    while i < retry_count:
        try:
            if not str(config['proxy']['proxy']) == '':
                proxies = {"http": "http://" + str(config['proxy']['proxy']),"https": "https://" + str(config['proxy']['proxy'])}
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36'}
                getweb = requests.get(str(url), headers=headers, timeout=int(config['proxy']['timeout']),proxies=proxies, cookies=cookies)
                getweb.encoding = 'utf-8'
                return getweb.text
            else:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                getweb = requests.get(str(url), headers=headers, timeout=int(config['proxy']['timeout']), cookies=cookies)
                getweb.encoding = 'utf-8'
                return getweb.text
        except requests.exceptions.RequestException:
            i += 1
            print('[-]Connect retry '+str(i)+'/'+str(retry_count))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Connect retry '+str(i)+'/'+str(retry_count))
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Connect retry '+str(i)+'/'+str(retry_count))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Connect retry '+str(i)+'/'+str(retry_count))



