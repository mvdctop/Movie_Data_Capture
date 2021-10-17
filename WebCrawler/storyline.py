import sys
sys.path.append('../')
import re
import json
from ADC_function import *
from WebCrawler.xcity import open_by_browser, getOutline as xcity_getOutline
from multiprocessing import Pool
from difflib import SequenceMatcher
from unicodedata import category

G_registered_storyline_site = {"airav", "avno1", "xcity", "amazon"}


# 获取剧情介绍 从列表中的站点同时查，取值优先级从前到后
def getStoryline(number, title):
    start_time = time.time()
    conf = config.getInstance()
    debug = conf.debug() or conf.storyline_show() == 2
    storyine_sites = conf.storyline_site().split(',')
    apply_sites = [ s for s in storyine_sites if s in G_registered_storyline_site]
    mp_args = ((site, number, title, debug) for site in apply_sites)
    # choose process pool not thread pool because https://www.python.org/dev/peps/pep-0371/
    with Pool() as proc_pool:
        result = proc_pool.map(getStoryline_mp, mp_args)
    if not debug and conf.storyline_show() == 0:
        for value in result:
            if isinstance(value, str) and len(value):
                return value
        return ''
    # 以下debug结果输出会写入日志，进程池中的则不会，只在标准输出中显示
    cnt = len(apply_sites)
    s = f'[!]MP Storyline 运行{cnt}个进程总用时(含启动开销){time.time() - start_time:.3f}秒，结束于{time.strftime("%H:%M:%S")}'
    first = True
    sel = ''
    for i in range(cnt):
        sl = len(result[i])if isinstance(result[i], str) else 0
        if sl and first:
            s += f'，[选中结果{apply_sites[i]}字数:{sl}]'
            first = False
            sel = result[i]
        elif sl:
            s += f'，{apply_sites[i]}字数:{sl}'
        else:
            s += f'，{apply_sites[i]}:空'
    print(s)
    return sel


def getStoryline_mp(args):
    return _getStoryline_mp(*args)


# 注：新进程的print()不会写入日志中，将来调试修复失效数据源需直接查看标准输出，issue信息需截图屏幕
def _getStoryline_mp(site, number, title, debug):
    start_time = time.time()
    storyline = None
    if not isinstance(site, str):
        return storyline
    elif site == "airav":
        storyline = getStoryline_airav(number, debug)
    elif site == "avno1":
        storyline = getStoryline_avno1(number, debug)
    elif site == "xcity":
        storyline = getStoryline_xcity(number, debug)
    elif site == "amazon":
        storyline = getStoryline_amazon(title, number, debug)
    if not debug:
        return storyline
    print("[!]MP 进程[{}]运行{:.3f}秒，结束于{}返回结果: {}".format(
            site,
            time.time() - start_time,
            time.strftime("%H:%M:%S"),
            storyline if isinstance(storyline, str) and len(storyline) else '[空]')
    )
    return storyline


def getStoryline_airav(number, debug):
    try:
        number_up = number
        site = secrets.choice(('airav.cc','airav4.club'))
        url = f'https://{site}/searchresults.aspx?Search={number}&Type=0'
        res, browser = get_html_by_browser(url, return_type='browser')
        if not res.ok:
            raise ValueError(f"get_html_by_browser('{url}') failed")
        avs = browser.page.select_one('div.resultcontent > ul > li:nth-child(1) > div')
        if number_up not in avs.select_one('a > h3').text.upper():
            raise ValueError("number not found")
        detail_url = avs.select_one('a')['href']
        res = browser.open_relative(detail_url)
        if not res.ok:
            raise ValueError(f"browser.open_relative('{detail_url}') failed")
        t = browser.page.select_one('head > title').text
        airav_number = str(re.findall(r'^\s*\[(.*?)]', t)[0]).upper()
        if number.upper() != airav_number:
            raise ValueError(f"page number ->[{airav_number}] not match")
        desc = browser.page.select_one('li.introduction > span').text.strip()
        return desc
    except Exception as e:
        if debug:
            print(f"[-]MP getOutline_amazon Error: {e},number [{number}].")
        pass
    return None


def getStoryline_avno1(number, debug):  #获取剧情介绍 从avno1.cc取得
    try:
        url = 'http://www.avno1.cc/cn/' + secrets.choice(['usercenter.php?item=' +
                secrets.choice(['pay_support', 'qa', 'contact', 'guide-vpn']),
                '?top=1&cat=hd', '?top=1', '?cat=hd', 'porn', '?cat=jp', '?cat=us', 'recommend_category.php'
        ]) # 随机选一个，避免网站httpd日志中单个ip的请求太过单一
        number_up = number.upper()
        result, browser = get_html_by_form(url,
            form_select='div.wrapper > div.header > div.search > form',
            fields = {'kw' : number_up},
            return_type = 'browser')
        if not result.ok:
            raise ValueError(f"get_html_by_form('{url}','{number_up}') failed")
        title = browser.page.select('div.type_movie > div > ul > li > div > a > h3')[0].text.strip()
        page_number = title[title.rfind(' '):].upper()
        if not number_up in page_number:
            raise ValueError(f"page number ->[{page_number}] not match")
        return browser.page.select('div.type_movie > div > ul > li:nth-child(1) > div')[0]['data-description'].strip()
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


def getStoryline_amazon(q_title, number, debug):
    if not isinstance(q_title, str) or not len(q_title):
        return None
    try:
        amazon_cookie, _ = load_cookies('amazon.json')
        cookie = amazon_cookie if isinstance(amazon_cookie, dict) else None
        url = "https://www.amazon.co.jp/s?k=" + q_title
        res, browser = get_html_by_browser(url, cookies=cookie, return_type='browser')
        if not res.ok:
            raise ValueError("get_html_by_browser() failed")
        lks = browser.links(r'/black-curtain/save-eligibility/black-curtain')
        if isinstance(lks, list) and len(lks):
            browser.follow_link(lks[0])
            cookie = None
        html = etree.fromstring(str(browser.page), etree.HTMLParser())
        titles = html.xpath("//span[contains(@class,'a-color-base a-text-normal')]/text()")
        urls = html.xpath("//span[contains(@class,'a-color-base a-text-normal')]/../@href")
        if not len(urls) or len(urls) != len(titles):
            raise ValueError("titles not found")
        idx = amazon_select_one(titles, q_title, number, debug)
        if not isinstance(idx, int) or idx < 0:
            raise ValueError("title and number not found")
        furl = urls[idx]
        r = browser.open_relative(furl)
        if not r.ok:
            raise ValueError("browser.open_relative()) failed.")
        lks = browser.links(r'/black-curtain/save-eligibility/black-curtain')
        if isinstance(lks, list) and len(lks):
            browser.follow_link(lks[0])
            cookie = None

        ama_t = browser.page.select_one('#productDescription > p').text.replace('\n',' ').strip()
        ama_t = re.sub(r'審査番号:\d+', '', ama_t)

        if cookie is None:
        # 自动创建的cookies文件放在搜索路径表的末端，最低优先级。有amazon.co.jp帐号的用户可以从浏览器导出cookie放在靠前搜索路径
            ama_save = Path.home() / ".local/share/avdc/amazon.json"
            ama_save.parent.mkdir(parents=True, exist_ok=True)
            ama_save.write_text(json.dumps(browser.session.cookies.get_dict(), sort_keys=True, indent=4), encoding='utf-8')

        return ama_t

    except Exception as e:
        if debug:
            print(f'[-]MP getOutline_amazon Error: {e}, number [{number}], title: {q_title}')
        pass
    return None

# 查货架中DVD和蓝光商品中标题相似度高的
def amazon_select_one(a_titles, q_title, number, debug):
    sel = -1
    ratio = 0
    que_t = ''.join(c for c in q_title if not re.match(r'(P|S|Z).*', category(c), re.A))
    for loc in range(len(a_titles)):
        t = a_titles[loc]
        if re.search(number, t, re.I): # 基本不带番号，但也有极个别有的，找到番号相同的直接通过
            ratio = 1.0
            sel = loc
            save_t_ = t
            break
        if not re.search('DVD|Blu-ray', t, re.I):
            continue
        ama_t = str(re.sub('DVD|Blu-ray', "", t, re.I))
        ama_t = ''.join(c for c in ama_t if not re.match(r'(P|S|Z).*', category(c), re.A))
        findlen = 0
        lastpos = -1
        cnt = len(ama_t)
        for c in reversed(ama_t):
            cnt -= 1
            pos = que_t.rfind(c)
            if lastpos >= 0:
                pos_near = que_t[:lastpos].rfind(c)
                if pos_near < 0:
                    findlen = 0
                    lastpos = -1
                    ama_t = ama_t[:cnt+1]
                else:
                    pos = pos_near
            if pos < 0:
                if category(c) == 'Nd':
                    return -1
                ama_t = ama_t[:cnt]
                findlen = 0
                lastpos = -1
                continue
            if findlen > 0 and len(que_t) > 1 and lastpos == pos+1:
                findlen += 1
                lastpos = pos
                if findlen >= 4:
                    break
                continue
            findlen = 1
            lastpos = pos
        if findlen==0:
            return -1
        r = SequenceMatcher(None, ama_t, que_t).ratio()
        if r > ratio:
            sel = loc
            ratio = r
            save_t_ = ama_t
            if ratio > 0.999:
                break

    if ratio < 0.5:
        return -1

    if not debug:
         # 目前采信相似度高于0.9的结果
        return sel if ratio >= 0.9 else -1

    # debug 模式下记录识别准确率日志
    if ratio < 0.9:
        # 相似度[0.5, 0.9)的淘汰结果单独记录日志
        (Path.home() / '.avlogs/ratio0.5.txt').open('a', encoding='utf-8').write(
            f' [{number}]  Ratio:{ratio}\n{a_titles[sel]}\n{q_title}\n{save_t_}\n{que_t}')
        return -1
    # 被采信的结果日志
    (Path.home() / '.avlogs/ratio.txt').open('a', encoding='utf-8').write(
        f' [{number}]  Ratio:{ratio}\n{a_titles[sel]}\n{q_title}\n{save_t_}\n{que_t}')
    return sel
