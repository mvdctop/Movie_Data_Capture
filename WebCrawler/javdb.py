import sys
sys.path.append('../')
import re
from lxml import etree
import json
from ADC_function import *
from WebCrawler.storyline import getStoryline
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

def getTitle(html):
    browser_title = str(html.xpath("/html/head/title/text()")[0])
    return browser_title[:browser_title.find(' | JavDB')].strip()

def getActor(html):
    actors = html.xpath('//span[@class="value"]/a[contains(@href,"/actors/")]/text()')
    genders = html.xpath('//span[@class="value"]/a[contains(@href,"/actors/")]/../strong/@class')
    r = []
    idx = 0
    actor_gendor = config.getInstance().actor_gender()
    if not actor_gendor in ['female','male','both','all']:
        actor_gendor = 'female'
    for act in actors:
        if((actor_gendor == 'all')
        or (actor_gendor == 'both' and genders[idx] in ['symbol female', 'symbol male'])
        or (actor_gendor == 'female' and genders[idx] == 'symbol female')
        or (actor_gendor == 'male' and genders[idx] == 'symbol male')):
            r.append(act)
        idx = idx + 1
    return r

def getaphoto(url, session):
    html_page = session.get(url).text
    img_url = re.findall(r'<span class\=\"avatar\" style\=\"background\-image\: url\((.*?)\)', html_page)
    return img_url[0] if img_url else ''

def getActorPhoto(html, javdb_site, session):
    actorall = html.xpath('//strong[contains(text(),"演員:")]/../span/a[starts-with(@href,"/actors/")]')
    if not actorall:
        return {}
    a = getActor(html)
    actor_photo = {}
    if not session:
        session = get_html_session()
    for i in actorall:
        x = re.findall(r'/actors/(.*)', i.attrib['href'], re.A)
        if not len(x) or not len(x[0]) or i.text not in a:
            continue
        actor_id = x[0]
        pic_url = f"https://c1.jdbstatic.com/avatars/{actor_id[:2].lower()}/{actor_id}.jpg"
        if not session.head(pic_url).ok:
            pic_url = getaphoto(urljoin(f'https://{javdb_site}.com', i.attrib['href']), session)
        if len(pic_url):
            actor_photo[i.text] = pic_url
    return actor_photo

def getStudio(a, html):
    # html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # result1 = str(html.xpath('//strong[contains(text(),"片商")]/../span/text()')).strip(" ['']")
    # result2 = str(html.xpath('//strong[contains(text(),"片商")]/../span/a/text()')).strip(" ['']")
    # return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
    patherr = re.compile(r'<strong>片商\:</strong>[\s\S]*?<a href=\".*?>(.*?)</a></span>')
    pianshang = patherr.findall(a)
    if pianshang:
        result = pianshang[0].strip()
        if len(result):
            return result
    # 以卖家作为工作室
    try:
        result = str(html.xpath('//strong[contains(text(),"賣家:")]/../span/a/text()')).strip(" ['']")
    except:
        result = ''
    return result

def getRuntime(html):
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')
def getLabel(html):
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getNum(html):
    result1 = str(html.xpath('//strong[contains(text(),"番號")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"番號")]/../span/a/text()')).strip(" ['']")
    return str(result2 + result1).strip('+')
def getYear(getRelease):
    # try:
    #     result = str(re.search('\d{4}', getRelease).group())
    #     return result
    # except:
    #     return getRelease
    patherr = re.compile(r'<strong>日期\:</strong>\s*?.*?<span class="value">(.*?)\-.*?</span>')
    dates = patherr.findall(getRelease)
    if dates:
        result = dates[0]
    else:
        result = ''
    return result

def getRelease(a):
    # html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # result1 = str(html.xpath('//strong[contains(text(),"時間")]/../span/text()')).strip(" ['']")
    # result2 = str(html.xpath('//strong[contains(text(),"時間")]/../span/a/text()')).strip(" ['']")
    # return str(result1 + result2).strip('+')
    patherr = re.compile(r'<strong>日期\:</strong>\s*?.*?<span class="value">(.*?)</span>')
    dates = patherr.findall(a)
    if dates:
        result = dates[0]
    else:
        result = ''
    return result
def getTag(html):
    try:
        result = html.xpath('//strong[contains(text(),"類別")]/../span/a/text()')
        return result

    except:
        result = html.xpath('//strong[contains(text(),"類別")]/../span/text()')
        return result

def getCover_small(html, index=0):
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    try:
        result = html.xpath("//*[contains(@class,'movie-list')]/div/a/div[contains(@class, 'cover')]/img/@src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
    except: # 2020.7.17 Repair Cover Url crawl
        try:
            result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@data-src")[index]
            if not 'https' in result:
                result = 'https:' + result
            return result
        except:
            result = html.xpath("//div[@class='item-image']/img/@data-src")[index]
            if not 'https' in result:
                result = 'https:' + result
            return result


def getTrailer(htmlcode):  # 获取预告片
    video_pather = re.compile(r'<video id\=\".*?>\s*?<source src=\"(.*?)\"')
    video = video_pather.findall(htmlcode)
    # 加上数组判空
    if video and video[0] != "":
        if not 'https:' in video[0]:
            video_url = 'https:' + video[0]
        else:
            video_url = video[0]
    else:
        video_url = ''
    return video_url

def getExtrafanart(html):  # 获取剧照
    result = []
    try:
        result = html.xpath("//article[@class='message video-panel']/div[@class='message-body']/div[@class='tile-images preview-images']/a[contains(@href,'/samples/')]/@href")
    except:
        pass
    return result
def getCover(html):
    try:
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/a/img/@src")[0]
    except: # 2020.7.17 Repair Cover Url crawl
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/img/@src")[0]
    return result
def getDirector(html):
    result1 = str(html.xpath('//strong[contains(text(),"導演")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"導演")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getOutline(number, title, uncensored):  #获取剧情介绍 多进程并发查询
    return getStoryline(number, title, 无码=uncensored)
def getSeries(html):
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getUserRating(html):
    try:
        result = str(html.xpath('//span[@class="score-stars"]/../text()')[0])
        v = re.findall(r'(\d+|\d+\.\d+)分, 由(\d+)人評價', result)
        return float(v[0][0]), int(v[0][1])
    except:
        return
def getUncensored(html):
    x = html.xpath('//strong[contains(text(),"類別")]/../span/a[contains(@href,"/tags/uncensored?")'
                ' or contains(@href,"/tags/western?")]')
    return bool(x)

def main(number):
    # javdb更新后同一时间只能登录一个数字站，最新登录站会踢出旧的登录，因此按找到的第一个javdb*.json文件选择站点，
    # 如果无.json文件或者超过有效期，则随机选择一个站点。
    javdb_sites = config.getInstance().javdb_sites().split(',')
    debug = config.getInstance().debug()
    for i in javdb_sites:
        javdb_sites[javdb_sites.index(i)] = "javdb" + i
    javdb_sites.append("javdb")
    try:
        # if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', number).group():
        #     pass
        # else:
        #     number = number.upper()
        number = number.upper()
        javdb_cookies = {'over18':'1', 'theme':'auto', 'locale':'zh'}
        # 不加载过期的cookie，javdb登录界面显示为7天免登录，故假定cookie有效期为7天
        has_json = False
        for cj in javdb_sites:
            javdb_site = cj
            cookie_json = javdb_site + '.json'
            cookies_dict, cookies_filepath = load_cookies(cookie_json)
            if isinstance(cookies_dict, dict) and isinstance(cookies_filepath, str):
                cdays = file_modification_days(cookies_filepath)
                if cdays < 7:
                    javdb_cookies = cookies_dict
                    has_json = True
                    break
                elif cdays != 9999:
                    print(f'[!]Cookies file {cookies_filepath} was updated {cdays} days ago, it will not be used for HTTP requests.')
        if not has_json:
            javdb_site = secrets.choice(javdb_sites)
        if debug:
            print(f'[!]javdb:select site {javdb_site}')
        session = None
        javdb_url = 'https://' + javdb_site + '.com/search?q=' + number + '&f=all'
        try:
            if debug:
                raise # try get_html_by_scraper() branch
            res, session = get_html_session(javdb_url, cookies=javdb_cookies, return_type='session')
            if not res:
                raise
            query_result = res.text
        except:
            res, session = get_html_by_scraper(javdb_url, cookies=javdb_cookies, return_type='scraper')
            if not res:
                raise ValueError('page not found')
            query_result = res.text
        if session is None:
            raise ValueError('page not found')
        html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        # javdb sometime returns multiple results,
        # and the first elememt maybe not the one we are looking for
        # iterate all candidates and find the match one
        urls = html.xpath('//*[contains(@class,"movie-list")]/div/a/@href')
        # 记录一下欧美的ids  ['Blacked','Blacked']
        if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', number):
            correct_url = urls[0]
        else:
            ids = html.xpath('//*[contains(@class,"movie-list")]/div/a/div[contains(@class, "video-title")]/strong/text()')
            try:
                correct_url = urls[ids.index(number)]
            except:
                # 为避免获得错误番号，只要精确对应的结果
                if ids[0].upper() != number:
                    raise ValueError("number not found")
                correct_url = urls[0]
        try:
                # get faster benefit from http keep-alive
                javdb_detail_url = urljoin(res.url, correct_url)
                detail_page = session.get(javdb_detail_url).text
        except:
            detail_page = get_html('https://javdb.com' + correct_url, cookies=javdb_cookies)
            session = None

        # etree.fromstring开销很大，最好只用一次，而它的xpath很快，比bs4 find/select快，可以多用
        lx = etree.fromstring(detail_page, etree.HTMLParser())
        imagecut = 1
        dp_number = getNum(lx)
        if dp_number.upper() != number.upper():
            raise ValueError("number not eq"+dp_number)
        title = getTitle(lx)
        if title and dp_number:
            number = dp_number
            # remove duplicate title
            title = title.replace(number, '').strip()
        dic = {
            'actor': getActor(lx),
            'title': title,
            'studio': getStudio(detail_page, lx),
            'outline': getOutline(number, title, getUncensored(lx)),
            'runtime': getRuntime(lx),
            'director': getDirector(lx),
            'release': getRelease(detail_page),
            'number': number,
            'cover': getCover(lx),
            'trailer': getTrailer(detail_page),
            'extrafanart': getExtrafanart(lx),
            'imagecut': imagecut,
            'tag': getTag(lx),
            'label': getLabel(lx),
            'year': getYear(detail_page),  # str(re.search('\d{4}',getRelease(a)).group()),
            'website': urljoin('https://javdb.com', correct_url),
            'source': 'javdb.py',
            'series': getSeries(lx),
            '无码': getUncensored(lx)
        }
        userrating = getUserRating(lx)
        if isinstance(userrating, tuple) and len(userrating) == 2:
            dic['用户评分'] = userrating[0]
            dic['评分人数'] = userrating[1]
        if not dic['actor'] and re.match(r'FC2-[\d]+', number, re.A):
            dic['actor'].append('素人')
            if not dic['series']:
                dic['series'] = dic['studio']
            if not dic['label']:
                dic['label'] = dic['studio']
        if config.getInstance().download_actor_photo_for_kodi():
            dic['actor_photo'] = getActorPhoto(lx, javdb_site,  session)


    except Exception as e:
        if debug:
            print(e)
        dic = {"title": ""}
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

# main('DV-1562')
# input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
if __name__ == "__main__":
    config.getInstance().set_override("storyline:switch=0")
    config.getInstance().set_override("actor_photo:download_for_kodi=1")
    config.getInstance().set_override("debug_mode:switch=1")
    # print(main('blacked.20.05.30'))
    print(main('AGAV-042'))
    print(main('BANK-022'))
    print(main('070116-197'))
    print(main('093021_539'))  # 没有剧照 片商pacopacomama
    #print(main('FC2-2278260'))
    # print(main('FC2-735670'))
    # print(main('FC2-1174949')) # not found
    print(main('MVSD-439'))
    # print(main('EHM0001')) # not found
    #print(main('FC2-2314275'))
    print(main('EBOD-646'))
    print(main('LOVE-262'))
    print(main('ABP-890'))
    print(main('blacked.14.12.08'))
