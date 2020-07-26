import requests
from lxml import etree

import config


def get_data_state(data: dict) -> bool:  # 元数据获取失败检测
    if "title" not in data or "number" not in data:
        return False

    if data["title"] is None or data["title"] == "" or data["title"] == "null":
        return False

    if data["number"] is None or data["number"] == "" or data["number"] == "null":
        return False

    return True


def getXpathSingle(htmlcode,xpath):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath(xpath)).strip(" ['']")
    return result1


def get_proxy(proxy: str, proxytype: str = None) -> dict:
    ''' 获得代理参数，默认http代理
    '''
    if proxy:
        if proxytype.startswith("socks"):
            proxies = {"http": "socks5://" + proxy, "https": "socks5://" + proxy}
        else:
            proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
    else:
        proxies = {}

    return proxies


# 网页请求核心
def get_html(url, cookies: dict = None, ua: str = None, return_type: str = None):
    proxy, timeout, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)

    if ua is None:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36"} # noqa
    else:
        headers = {"User-Agent": ua}

    for i in range(retry_count):
        try:
            if not proxy == '':
                result = requests.get(str(url), headers=headers, timeout=timeout, proxies=proxies, cookies=cookies)
            else:
                result = requests.get(str(url), headers=headers, timeout=timeout, cookies=cookies)

            result.encoding = "utf-8"

            if return_type == "object":
                return result
            else:
                return result.text

        except requests.exceptions.ProxyError:
            print("[-]Connect retry {}/{}".format(i + 1, retry_count))
        except requests.exceptions.ConnectionError:
            print("[-]Connect retry {}/{}".format(i + 1, retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')
    input("Press ENTER to exit!")
    exit()


def post_html(url: str, query: dict) -> requests.Response:
    proxy, timeout, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)

    for i in range(retry_count):
        try:
            result = requests.post(url, data=query, proxies=proxies)
            return result
        except requests.exceptions.ProxyError:
            print("[-]Connect retry {}/{}".format(i+1, retry_count))
    print("[-]Connect Failed! Please check your Proxy or Network!")
    input("Press ENTER to exit!")
    exit()


def get_javlib_cookie() -> [dict, str]:
    import cloudscraper
    proxy, timeout, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)

    raw_cookie = {}
    user_agent = ""

    # Get __cfduid/cf_clearance and user-agent
    for i in range(retry_count):
        try:
            raw_cookie, user_agent = cloudscraper.get_cookie_string(
                "http://www.m45e.com/",
                proxies=proxies
            )
        except requests.exceptions.ProxyError:
            print("[-] ProxyError, retry {}/{}".format(i+1, retry_count))
        except cloudscraper.exceptions.CloudflareIUAMError:
            print("[-] IUAMError, retry {}/{}".format(i+1, retry_count))

    return raw_cookie, user_agent
