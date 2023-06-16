# build-in lib
import os.path
import os
import re
import uuid
import json
import time
import typing
from unicodedata import category
from concurrent.futures import ThreadPoolExecutor

# third party lib
import requests
from requests.adapters import HTTPAdapter
import mechanicalsoup
from pathlib import Path
from urllib3.util.retry import Retry
from lxml import etree
from cloudscraper import create_scraper

# project wide
import config


def get_xpath_single(html_code: str, xpath):
    html = etree.fromstring(html_code, etree.HTMLParser())
    result1 = str(html.xpath(xpath)).strip(" ['']")
    return result1


G_USER_AGENT = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.133 Safari/537.36'


def get_html(url, cookies: dict = None, ua: str = None, return_type: str = None, encoding: str = None, json_headers=None):
    """
    网页请求核心函数
    """
    verify = config.getInstance().cacert_file()
    config_proxy = config.getInstance().proxy()
    errors = ""

    headers = {"User-Agent": ua or G_USER_AGENT}  # noqa
    if json_headers is not None:
        headers.update(json_headers)

    for i in range(config_proxy.retry):
        try:
            if config_proxy.enable:
                proxies = config_proxy.proxies()
                result = requests.get(str(url), headers=headers, timeout=config_proxy.timeout, proxies=proxies,
                                      verify=verify,
                                      cookies=cookies)
            else:
                result = requests.get(str(url), headers=headers, timeout=config_proxy.timeout, cookies=cookies)

            if return_type == "object":
                return result
            elif return_type == "content":
                return result.content
            else:
                result.encoding = encoding or result.apparent_encoding
                return result.text
        except Exception as e:
            print("[-]Connect retry {}/{}".format(i + 1, config_proxy.retry))
            errors = str(e)
    if "getaddrinfo failed" in errors:
        print("[-]Connect Failed! Please Check your proxy config")
        debug = config.getInstance().debug()
        if debug:
            print("[-]" + errors)
    else:
        print("[-]" + errors)
        print('[-]Connect Failed! Please check your Proxy or Network!')
    raise Exception('Connect Failed')


def post_html(url: str, query: dict, headers: dict = None) -> requests.Response:
    config_proxy = config.getInstance().proxy()
    errors = ""
    headers_ua = {"User-Agent": G_USER_AGENT}
    if headers is None:
        headers = headers_ua
    else:
        headers.update(headers_ua)

    for i in range(config_proxy.retry):
        try:
            if config_proxy.enable:
                proxies = config_proxy.proxies()
                result = requests.post(url, data=query, proxies=proxies, headers=headers, timeout=config_proxy.timeout)
            else:
                result = requests.post(url, data=query, headers=headers, timeout=config_proxy.timeout)
            return result
        except Exception as e:
            print("[-]Connect retry {}/{}".format(i + 1, config_proxy.retry))
            errors = str(e)
    print("[-]Connect Failed! Please check your Proxy or Network!")
    print("[-]" + errors)


G_DEFAULT_TIMEOUT = 10  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = G_DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


#  with keep-alive feature
def get_html_session(url: str = None, cookies: dict = None, ua: str = None, return_type: str = None,
                     encoding: str = None):
    config_proxy = config.getInstance().proxy()
    session = requests.Session()
    if isinstance(cookies, dict) and len(cookies):
        requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
    retries = Retry(total=config_proxy.retry, connect=config_proxy.retry, backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=config_proxy.timeout))
    session.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=config_proxy.timeout))
    if config_proxy.enable:
        session.verify = config.getInstance().cacert_file()
        session.proxies = config_proxy.proxies()
    headers = {"User-Agent": ua or G_USER_AGENT}
    session.headers = headers
    try:
        if isinstance(url, str) and len(url):
            result = session.get(str(url))
        else:  # 空url参数直接返回可重用session对象，无需设置return_type
            return session
        if not result.ok:
            return None
        if return_type == "object":
            return result
        elif return_type == "content":
            return result.content
        elif return_type == "session":
            return result, session
        else:
            result.encoding = encoding or "utf-8"
            return result.text
    except requests.exceptions.ProxyError:
        print("[-]get_html_session() Proxy error! Please check your Proxy")
    except requests.exceptions.RequestException:
        pass
    except Exception as e:
        print(f"[-]get_html_session() failed. {e}")
    return None


def get_html_by_browser(url: str = None, cookies: dict = None, ua: str = None, return_type: str = None,
                        encoding: str = None, use_scraper: bool = False):
    config_proxy = config.getInstance().proxy()
    s = create_scraper(browser={'custom': ua or G_USER_AGENT, }) if use_scraper else requests.Session()
    if isinstance(cookies, dict) and len(cookies):
        requests.utils.add_dict_to_cookiejar(s.cookies, cookies)
    retries = Retry(total=config_proxy.retry, connect=config_proxy.retry, backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=config_proxy.timeout))
    s.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=config_proxy.timeout))
    if config_proxy.enable:
        s.verify = config.getInstance().cacert_file()
        s.proxies = config_proxy.proxies()
    try:
        browser = mechanicalsoup.StatefulBrowser(user_agent=ua or G_USER_AGENT, session=s)
        if isinstance(url, str) and len(url):
            result = browser.open(url)
        else:
            return browser
        if not result.ok:
            return None

        if return_type == "object":
            return result
        elif return_type == "content":
            return result.content
        elif return_type == "browser":
            return result, browser
        else:
            result.encoding = encoding or "utf-8"
            return result.text
    except requests.exceptions.ProxyError:
        print("[-]get_html_by_browser() Proxy error! Please check your Proxy")
    except Exception as e:
        print(f'[-]get_html_by_browser() Failed! {e}')
    return None


def get_html_by_form(url, form_select: str = None, fields: dict = None, cookies: dict = None, ua: str = None,
                     return_type: str = None, encoding: str = None):
    config_proxy = config.getInstance().proxy()
    s = requests.Session()
    if isinstance(cookies, dict) and len(cookies):
        requests.utils.add_dict_to_cookiejar(s.cookies, cookies)
    retries = Retry(total=config_proxy.retry, connect=config_proxy.retry, backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=config_proxy.timeout))
    s.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=config_proxy.timeout))
    if config_proxy.enable:
        s.verify = config.getInstance().cacert_file()
        s.proxies = config_proxy.proxies()
    try:
        browser = mechanicalsoup.StatefulBrowser(user_agent=ua or G_USER_AGENT, session=s)
        result = browser.open(url)
        if not result.ok:
            return None
        form = browser.select_form() if form_select is None else browser.select_form(form_select)
        if isinstance(fields, dict):
            for k, v in fields.items():
                browser[k] = v
        response = browser.submit_selected()

        if return_type == "object":
            return response
        elif return_type == "content":
            return response.content
        elif return_type == "browser":
            return response, browser
        else:
            result.encoding = encoding or "utf-8"
            return response.text
    except requests.exceptions.ProxyError:
        print("[-]get_html_by_form() Proxy error! Please check your Proxy")
    except Exception as e:
        print(f'[-]get_html_by_form() Failed! {e}')
    return None


def get_html_by_scraper(url: str = None, cookies: dict = None, ua: str = None, return_type: str = None,
                        encoding: str = None):
    config_proxy = config.getInstance().proxy()
    session = create_scraper(browser={'custom': ua or G_USER_AGENT, })
    if isinstance(cookies, dict) and len(cookies):
        requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
    retries = Retry(total=config_proxy.retry, connect=config_proxy.retry, backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", TimeoutHTTPAdapter(max_retries=retries, timeout=config_proxy.timeout))
    session.mount("http://", TimeoutHTTPAdapter(max_retries=retries, timeout=config_proxy.timeout))
    if config_proxy.enable:
        session.verify = config.getInstance().cacert_file()
        session.proxies = config_proxy.proxies()
    try:
        if isinstance(url, str) and len(url):
            result = session.get(str(url))
        else:  # 空url参数直接返回可重用scraper对象，无需设置return_type
            return session
        if not result.ok:
            return None
        if return_type == "object":
            return result
        elif return_type == "content":
            return result.content
        elif return_type == "scraper":
            return result, session
        else:
            result.encoding = encoding or "utf-8"
            return result.text
    except requests.exceptions.ProxyError:
        print("[-]get_html_by_scraper() Proxy error! Please check your Proxy")
    except Exception as e:
        print(f"[-]get_html_by_scraper() failed. {e}")
    return None


# def get_javlib_cookie() -> [dict, str]:
#     import cloudscraper
#     switch, proxy, timeout, retry_count, proxytype = config.getInstance().proxy()
#     proxies = get_proxy(proxy, proxytype)
#
#     raw_cookie = {}
#     user_agent = ""
#
#     # Get __cfduid/cf_clearance and user-agent
#     for i in range(retry_count):
#         try:
#             if switch == 1 or switch == '1':
#                 raw_cookie, user_agent = cloudscraper.get_cookie_string(
#                     "http://www.javlibrary.com/",
#                     proxies=proxies
#                 )
#             else:
#                 raw_cookie, user_agent = cloudscraper.get_cookie_string(
#                     "http://www.javlibrary.com/"
#                 )
#         except requests.exceptions.ProxyError:
#             print("[-] ProxyError, retry {}/{}".format(i + 1, retry_count))
#         except cloudscraper.exceptions.CloudflareIUAMError:
#             print("[-] IUAMError, retry {}/{}".format(i + 1, retry_count))
#
#     return raw_cookie, user_agent


def translate(
        src: str,
        target_language: str = config.getInstance().get_target_language(),
        engine: str = config.getInstance().get_translate_engine(),
        app_id: str = "",
        key: str = "",
        delay: int = 0,
) -> str:
    """
    translate japanese kana to simplified chinese
    翻译日语假名到简体中文
    :raises ValueError: Non-existent translation engine
    """
    trans_result = ""
    # 中文句子如果包含&等符号会被谷歌翻译截断损失内容，而且中文翻译到中文也没有意义，故而忽略，只翻译带有日语假名的
    if (is_japanese(src) == False) and ("zh_" in target_language):
        return src
    if engine == "google-free":
        gsite = config.getInstance().get_translate_service_site()
        if not re.match('^translate\.google\.(com|com\.\w{2}|\w{2})$', gsite):
            gsite = 'translate.google.cn'
        url = (
            f"https://{gsite}/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=auto&tl={target_language}&q={src}"
        )
        result = get_html(url=url, return_type="object")
        if not result.ok:
            print('[-]Google-free translate web API calling failed.')
            return ''

        translate_list = [i["trans"] for i in result.json()["sentences"]]
        trans_result = trans_result.join(translate_list)
    elif engine == "azure":
        url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=" + target_language
        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Ocp-Apim-Subscription-Region': "global",
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        body = json.dumps([{'text': src}])
        result = post_html(url=url, query=body, headers=headers)
        translate_list = [i["text"] for i in result.json()[0]["translations"]]
        trans_result = trans_result.join(translate_list)
    elif engine == "deeplx":
        url = config.getInstance().get_translate_service_site()
        res = requests.post(f"{url}/translate", json={
            'text': src,
            'source_lang': 'auto',
            'target_lang': target_language,
        })
        if res.text.strip():
            trans_result = res.json().get('data')
    else:
        raise ValueError("Non-existent translation engine")

    time.sleep(delay)
    return trans_result


def load_cookies(cookie_json_filename: str) -> typing.Tuple[typing.Optional[dict], typing.Optional[str]]:
    """
    加载cookie,用于以会员方式访问非游客内容

    :filename: cookie文件名。获取cookie方式：从网站登录后，通过浏览器插件(CookieBro或EdittThisCookie)或者直接在地址栏网站链接信息处都可以复制或者导出cookie内容，以JSON方式保存

    # 示例: FC2-755670 url https://javdb9.com/v/vO8Mn
    # json 文件格式
    # 文件名: 站点名.json，示例 javdb9.json
    # 内容(文件编码:UTF-8)：
    {
        "over18":"1",
        "redirect_to":"%2Fv%2FvO8Mn",
        "remember_me_token":"***********",
        "_jdb_session":"************",
        "locale":"zh",
        "__cfduid":"*********",
        "theme":"auto"
    }
    """
    filename = os.path.basename(cookie_json_filename)
    if not len(filename):
        return None, None
    path_search_order = (
        Path.cwd() / filename,
        Path.home() / filename,
        Path.home() / f".mdc/{filename}",
        Path.home() / f".local/share/mdc/{filename}"
    )
    cookies_filename = None
    try:
        for p in path_search_order:
            if p.is_file():
                cookies_filename = str(p.resolve())
                break
        if not cookies_filename:
            return None, None
        return json.loads(Path(cookies_filename).read_text(encoding='utf-8')), cookies_filename
    except:
        return None, None


def file_modification_days(filename: str) -> int:
    """
    文件修改时间距此时的天数
    """
    mfile = Path(filename)
    if not mfile.is_file():
        return 9999
    mtime = int(mfile.stat().st_mtime)
    now = int(time.time())
    days = int((now - mtime) / (24 * 60 * 60))
    if days < 0:
        return 9999
    return days


def file_not_exist_or_empty(filepath) -> bool:
    return not os.path.isfile(filepath) or os.path.getsize(filepath) == 0


def is_japanese(raw: str) -> bool:
    """
    日语简单检测
    """
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\uFF66-\uFF9F]', raw, re.UNICODE))


def download_file_with_filename(url: str, filename: str, path: str) -> None:
    """
    download file save to give path with given name from given url
    """
    conf = config.getInstance()
    config_proxy = conf.proxy()

    for i in range(config_proxy.retry):
        try:
            if config_proxy.enable:
                if not os.path.exists(path):
                    try:
                        os.makedirs(path)
                    except:
                        print(f"[-]Fatal error! Can not make folder '{path}'")
                        os._exit(0)
                r = get_html(url=url, return_type='content')
                if r == '':
                    print('[-]Movie Download Data not found!')
                    return
                with open(os.path.join(path, filename), "wb") as code:
                    code.write(r)
                return
            else:
                if not os.path.exists(path):
                    try:
                        os.makedirs(path)
                    except:
                        print(f"[-]Fatal error! Can not make folder '{path}'")
                        os._exit(0)
                r = get_html(url=url, return_type='content')
                if r == '':
                    print('[-]Movie Download Data not found!')
                    return
                with open(os.path.join(path, filename), "wb") as code:
                    code.write(r)
                return
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Download :  Connect retry ' + str(i) + '/' + str(config_proxy.retry))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Download :  Connect retry ' + str(i) + '/' + str(config_proxy.retry))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Download :  Connect retry ' + str(i) + '/' + str(config_proxy.retry))
        except requests.exceptions.RequestException:
            i += 1
            print('[-]Download :  Connect retry ' + str(i) + '/' + str(config_proxy.retry))
        except IOError:
            raise ValueError(f"[-]Create Directory '{path}' failed!")
            return
    print('[-]Connect Failed! Please check your Proxy or Network!')
    raise ValueError('[-]Connect Failed! Please check your Proxy or Network!')
    return


def download_one_file(args) -> str:
    """
    download file save to given path from given url
    wrapped for map function
    """

    (url, save_path, json_headers) = args
    if json_headers is not None:
        filebytes = get_html(url, return_type='content', json_headers=json_headers['headers'])
    else:
        filebytes = get_html(url, return_type='content')
    if isinstance(filebytes, bytes) and len(filebytes):
        with save_path.open('wb') as fpbyte:
            if len(filebytes) == fpbyte.write(filebytes):
                return str(save_path)


def parallel_download_files(dn_list: typing.Iterable[typing.Sequence], parallel: int = 0, json_headers=None):
    """
    download files in parallel 多线程下载文件

    用法示例: 2线程同时下载两个不同文件，并保存到不同路径，路径目录可未创建，但需要具备对目标目录和文件的写权限
    parallel_download_files([
    ('https://site1/img/p1.jpg', 'C:/temp/img/p1.jpg'),
    ('https://site2/cover/n1.xml', 'C:/tmp/cover/n1.xml')
    ])

    :dn_list: 可以是 tuple或者list: ((url1, save_fullpath1),(url2, save_fullpath2),) fullpath可以是str或Path
    :parallel: 并行下载的线程池线程数，为0则由函数自己决定
    """
    mp_args = []
    for url, fullpath in dn_list:
        if url and isinstance(url, str) and url.startswith('http') \
                and fullpath and isinstance(fullpath, (str, Path)) and len(str(fullpath)):
            fullpath = Path(fullpath)
            fullpath.parent.mkdir(parents=True, exist_ok=True)
            mp_args.append((url, fullpath, json_headers))
    if not len(mp_args):
        return []
    if not isinstance(parallel, int) or parallel not in range(1, 200):
        parallel = min(5, len(mp_args))
    with ThreadPoolExecutor(parallel) as pool:
        results = list(pool.map(download_one_file, mp_args))
    return results


def delete_all_elements_in_list(string: str, lists: typing.Iterable[str]):
    """
    delete same string in given list
    """
    new_lists = []
    for i in lists:
        if i != string:
            new_lists.append(i)
    return new_lists


def delete_all_elements_in_str(string_delete: str, string: str):
    """
    delete same string in given list
    """
    for i in string:
        if i == string_delete:
            string = string.replace(i, "")
    return string


# print format空格填充对齐内容包含中文时的空格计算
def cn_space(v: str, n: int) -> int:
    return n - [category(c) for c in v].count('Lo')


"""
Usage: python ./ADC_function.py https://cn.bing.com/
Purpose: benchmark get_html_session
         benchmark get_html_by_scraper
         benchmark get_html_by_browser
         benchmark get_html
TODO: may be this should move to unittest directory
"""
if __name__ == "__main__":
    import sys, timeit
    from http.client import HTTPConnection


    def benchmark(times: int, url):
        print(f"HTTP GET Benchmark times:{times} url:{url}")
        tm = timeit.timeit(f"_ = session1.get('{url}')",
                           "from __main__ import get_html_session;session1=get_html_session()",
                           number=times)
        print(f' *{tm:>10.5f}s get_html_session() Keep-Alive enable')
        tm = timeit.timeit(f"_ = scraper1.get('{url}')",
                           "from __main__ import get_html_by_scraper;scraper1=get_html_by_scraper()",
                           number=times)
        print(f' *{tm:>10.5f}s get_html_by_scraper() Keep-Alive enable')
        tm = timeit.timeit(f"_ = browser1.open('{url}')",
                           "from __main__ import get_html_by_browser;browser1=get_html_by_browser()",
                           number=times)
        print(f' *{tm:>10.5f}s get_html_by_browser() Keep-Alive enable')
        tm = timeit.timeit(f"_ = get_html('{url}')",
                           "from __main__ import get_html",
                           number=times)
        print(f' *{tm:>10.5f}s get_html()')


    # target_url = "https://www.189.cn/"
    target_url = "http://www.chinaunicom.com"
    HTTPConnection.debuglevel = 1
    html_session = get_html_session()
    _ = html_session.get(target_url)
    HTTPConnection.debuglevel = 0

    # times
    t = 100
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    benchmark(t, target_url)
