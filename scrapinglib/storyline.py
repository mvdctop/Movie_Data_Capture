# -*- coding: utf-8 -*-
"""
此部分暂未修改

"""


import os
import re
import time
import secrets
import builtins
from urllib.parse import urljoin
from lxml.html import fromstring
from multiprocessing.dummy import Pool as ThreadPool
from .httprequest  import get_html_by_browser, get_html_by_form, get_html_by_scraper, get_html_session

# 舍弃 Amazon 源
G_registered_storyline_site = {"airavwiki", "airav", "avno1", "xcity", "58avgo"}

G_mode_txt = ('顺序执行','线程池')
def is_japanese(raw: str) -> bool:
    """
    日语简单检测
    """
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\uFF66-\uFF9F]', raw, re.UNICODE))

class noThread(object):
    def map(self, fn, param):
        return list(builtins.map(fn, param))
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# 获取剧情介绍 从列表中的站点同时查，取值优先级从前到后
def getStoryline(number, title = None, sites: list=None, uncensored=None):
    start_time = time.time()
    debug = False
    storyine_sites = "1:avno1,4:airavwiki".split(',')
    if uncensored:
        storyine_sites += "3:58avgo".split(',')
    else:
        storyine_sites += "2:airav,5:xcity".split(',')
    r_dup = set()
    sort_sites = []
    for s in storyine_sites:
        ns = re.sub(r'.*?:', '', s, re.A)
        if ns in G_registered_storyline_site and ns not in r_dup:
            sort_sites.append(s)
            r_dup.add(ns)
    sort_sites.sort()
    apply_sites = [re.sub(r'.*?:', '', s, re.A) for s in sort_sites]
    mp_args = ((site, number, title, debug) for site in apply_sites)
    cores = min(len(apply_sites), os.cpu_count())
    if cores == 0:
        return ''
    run_mode = 1
    with ThreadPool(cores) if run_mode > 0 else noThread() as pool:
        results = pool.map(getStoryline_mp, mp_args)
    sel = ''

    # 以下debug结果输出会写入日志
    s = f'[!]Storyline{G_mode_txt[run_mode]}模式运行{len(apply_sites)}个任务共耗时(含启动开销){time.time() - start_time:.3f}秒，结束于{time.strftime("%H:%M:%S")}'
    sel_site = ''
    for site, desc in zip(apply_sites, results):
        if isinstance(desc, str) and len(desc):
            if not is_japanese(desc):
                sel_site, sel = site, desc
                break
            if not len(sel_site):
                sel_site, sel = site, desc
    for site, desc in zip(apply_sites, results):
        sl = len(desc) if isinstance(desc, str) else 0
        s += f'，[选中{site}字数:{sl}]' if site == sel_site else f'，{site}字数:{sl}' if sl else f'，{site}:空'
    print(s)
    return sel


def getStoryline_mp(args):
    (site, number, title, debug) = args
    start_time = time.time()
    storyline = None
    if not isinstance(site, str):
        return storyline
    elif site == "airavwiki":
        storyline = getStoryline_airavwiki(number, debug)
        #storyline = getStoryline_airavwiki_super(number, debug)
    elif site == "airav":
        storyline = getStoryline_airav(number, debug)
    elif site == "avno1":
        storyline = getStoryline_avno1(number, debug)
    elif site == "xcity":
        storyline = getStoryline_xcity(number, debug)
    # elif site == "amazon":
    #     storyline = getStoryline_amazon(title, number, debug)
    elif site == "58avgo":
        storyline = getStoryline_58avgo(number, debug)
    if not debug:
        return storyline
    print("[!]MP 线程[{}]运行{:.3f}秒，结束于{}返回结果: {}".format(
            site,
            time.time() - start_time,
            time.strftime("%H:%M:%S"),
            storyline if isinstance(storyline, str) and len(storyline) else '[空]')
    )
    return storyline


def getStoryline_airav(number, debug):
    try:
        site = secrets.choice(('airav.cc','airav4.club'))
        url = f'https://{site}/searchresults.aspx?Search={number}&Type=0'
        res, session = get_html_session(url, return_type='session')
        if not res:
            raise ValueError(f"get_html_by_session('{url}') failed")
        lx = fromstring(res.text)
        urls = lx.xpath('//div[@class="resultcontent"]/ul/li/div/a[@class="ga_click"]/@href')
        txts = lx.xpath('//div[@class="resultcontent"]/ul/li/div/a[@class="ga_click"]/h3[@class="one_name ga_name"]/text()')
        detail_url = None
        for txt, url in zip(txts, urls):
            if re.search(number, txt, re.I):
                detail_url = urljoin(res.url, url)
                break
        if detail_url is None:
            raise ValueError("number not found")
        res = session.get(detail_url)
        if not res.ok:
            raise ValueError(f"session.get('{detail_url}') failed")
        lx = fromstring(res.text)
        t = str(lx.xpath('/html/head/title/text()')[0]).strip()
        airav_number = str(re.findall(r'^\s*\[(.*?)]', t)[0])
        if not re.search(number, airav_number, re.I):
            raise ValueError(f"page number ->[{airav_number}] not match")
        desc = str(lx.xpath('//span[@id="ContentPlaceHolder1_Label2"]/text()')[0]).strip()
        return desc
    except Exception as e:
        if debug:
            print(f"[-]MP getStoryline_airav Error: {e},number [{number}].")
        pass
    return None


def getStoryline_airavwiki(number, debug):
    try:
        kwd = number[:6] if re.match(r'\d{6}[\-_]\d{2,3}', number) else number
        url = f'https://cn.airav.wiki/?search={kwd}'
        result, browser = get_html_by_browser(url, return_type='browser', use_scraper=True)
        if not result.ok:
            raise ValueError(f"get_html_by_browser('{url}','{number}') failed")
        s = browser.page.select('div.row > div > div.videoList.row > div > a.d-block')
        link = None
        for a in s:
            title = a.img['title']
            list_number = re.findall('^(.*?)\s+', title, re.A)[0].strip()
            if kwd == number:  # 番号PRED-164 和 RED-164需要能够区分
                if re.match(f'^{number}$', list_number, re.I):
                    link = a
                    break
            elif re.search(number, list_number, re.I):
                link = a
                break
        if link is None:
            raise ValueError("number not found")
        result = browser.follow_link(link)
        if not result.ok or not re.search(number, browser.url, re.I):
            raise ValueError("detail page not found")
        title = browser.page.select('head > title')[0].text.strip()
        detail_number = str(re.findall('\[(.*?)]', title)[0])
        if not re.search(number, detail_number, re.I):
            raise ValueError(f"detail page number not match, got ->[{detail_number}]")
        desc = browser.page.select_one('div.d-flex.videoDataBlock > div.synopsis > p').text.strip()
        return desc
    except Exception as e:
        if debug:
            print(f"[-]MP def getStoryline_airavwiki Error: {e}, number [{number}].")
        pass
    return ''


def getStoryline_58avgo(number, debug):
    try:
        url = 'http://58avgo.com/cn/index.aspx' + secrets.choice([
                '', '?status=3', '?status=4', '?status=7', '?status=9', '?status=10', '?status=11', '?status=12',
                '?status=1&Sort=Playon', '?status=1&Sort=dateupload', 'status=1&Sort=dateproduce'
        ]) # 随机选一个，避免网站httpd日志中单个ip的请求太过单一
        kwd = number[:6] if re.match(r'\d{6}[\-_]\d{2,3}', number) else number
        result, browser = get_html_by_form(url,
            fields = {'ctl00$TextBox_SearchKeyWord' : kwd},
            return_type = 'browser')
        if not result:
            raise ValueError(f"get_html_by_form('{url}','{number}') failed")
        if f'searchresults.aspx?Search={kwd}' not in browser.url:
            raise ValueError("number not found")
        s = browser.page.select('div.resultcontent > ul > li.listItem > div.one-info-panel.one > a.ga_click')
        link = None
        for a in s:
            title = a.h3.text.strip()
            list_number = title[title.rfind(' ')+1:].strip()
            if re.search(number, list_number, re.I):
                link = a
                break
        if link is None:
            raise ValueError("number not found")
        result = browser.follow_link(link)
        if not result.ok or 'playon.aspx' not in browser.url:
            raise ValueError("detail page not found")
        title = browser.page.select_one('head > title').text.strip()
        detail_number = str(re.findall('\[(.*?)]', title)[0])
        if not re.search(number, detail_number, re.I):
            raise ValueError(f"detail page number not match, got ->[{detail_number}]")
        return browser.page.select_one('#ContentPlaceHolder1_Label2').text.strip()
    except Exception as e:
        if debug:
            print(f"[-]MP getOutline_58avgo Error: {e}, number [{number}].")
        pass
    return ''


def getStoryline_avno1(number, debug):  #获取剧情介绍 从avno1.cc取得
    try:
        site = secrets.choice(['1768av.club','2nine.net','av999.tv','avno1.cc',
            'hotav.biz','iqq2.xyz','javhq.tv',
            'www.hdsex.cc','www.porn18.cc','www.xxx18.cc',])
        url = f'http://{site}/cn/search.php?kw_type=key&kw={number}'
        lx = fromstring(get_html_by_scraper(url))
        descs = lx.xpath('//div[@class="type_movie"]/div/ul/li/div/@data-description')
        titles = lx.xpath('//div[@class="type_movie"]/div/ul/li/div/a/h3/text()')
        if not descs or not len(descs):
            raise ValueError(f"number not found")
        partial_num = bool(re.match(r'\d{6}[\-_]\d{2,3}', number))
        for title, desc in zip(titles, descs):
            page_number = title[title.rfind(' ')+1:].strip()
            if not partial_num:
                if re.match(f'^{number}$', page_number, re.I):
                    return desc.strip()
            elif re.search(number, page_number, re.I):
                return desc.strip()
        raise ValueError(f"page number ->[{page_number}] not match")
    except Exception as e:
        if debug:
            print(f"[-]MP getOutline_avno1 Error: {e}, number [{number}].")
        pass
    return ''


def getStoryline_avno1OLD(number, debug):  #获取剧情介绍 从avno1.cc取得
    try:
        url = 'http://www.avno1.cc/cn/' + secrets.choice(['usercenter.php?item=' +
                secrets.choice(['pay_support', 'qa', 'contact', 'guide-vpn']),
                '?top=1&cat=hd', '?top=1', '?cat=hd', 'porn', '?cat=jp', '?cat=us', 'recommend_category.php'
        ]) # 随机选一个，避免网站httpd日志中单个ip的请求太过单一
        result, browser = get_html_by_form(url,
            form_select='div.wrapper > div.header > div.search > form',
            fields = {'kw' : number},
            return_type = 'browser')
        if not result:
            raise ValueError(f"get_html_by_form('{url}','{number}') failed")
        s = browser.page.select('div.type_movie > div > ul > li > div')
        for div in s:
            title = div.a.h3.text.strip()
            page_number = title[title.rfind(' ')+1:].strip()
            if re.search(number, page_number, re.I):
                return div['data-description'].strip()
        raise ValueError(f"page number ->[{page_number}] not match")
    except Exception as e:
        if debug:
            print(f"[-]MP getOutline_avno1 Error: {e}, number [{number}].")
        pass
    return ''


def getStoryline_xcity(number, debug):  #获取剧情介绍 从xcity取得
    try:
        xcity_number = number.replace('-','')
        query_result, browser = get_html_by_form(
            'https://xcity.jp/' + secrets.choice(['about/','sitemap/','policy/','law/','help/','main/']),
            fields = {'q' : xcity_number.lower()},
            return_type = 'browser')
        if not query_result or not query_result.ok:
            raise ValueError("page not found")
        result = browser.follow_link(browser.links('avod\/detail')[0])
        if not result.ok:
            raise ValueError("detail page not found")
        return browser.page.select_one('h2.title-detail + p.lead').text.strip()
    except Exception as e:
        if debug:
            print(f"[-]MP getOutline_xcity Error: {e}, number [{number}].")
        pass
    return ''
