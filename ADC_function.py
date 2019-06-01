import requests

def get_html(url):#网页请求核心
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    getweb = requests.get(str(url),timeout=5,headers=headers)
    getweb.encoding='utf-8'
    try:
        return getweb.text
    except:
        print("[-]Connect Failed! Please check your Proxy.")