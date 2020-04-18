import requests
from lxml import etree

import config


def get_data_state(data: dict) -> bool:  # 元数据获取失败检测
    if data["title"] is None or data["title"] == "" or data["title"] == "null":
        return False

    if data["number"] is None or data["number"] == "" or data["number"] == "null":
        return False

    return True


def getXpathSingle(htmlcode,xpath):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath(xpath)).strip(" ['']")
    return result1


# 网页请求核心
def get_html(url, cookies=None):
    proxy, timeout, retry_count = config.Config().proxy()

    for i in range(retry_count):
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
        except requests.exceptions.ProxyError:
            print("[-]Connect retry {}/{}".format(i + 1, retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')
    input("Press ENTER to exit!")
    exit()


def post_html(url: str, query: dict) -> requests.Response:
    proxy, timeout, retry_count = config.Config().proxy()

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
    input("Press ENTER to exit!")
    exit()
