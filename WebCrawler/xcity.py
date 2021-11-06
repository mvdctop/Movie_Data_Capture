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
    result = html.xpath('//*[@id="program_detail_title"]/text()')[0]
    return result


def getActor(browser):
    htmla = browser.page.select('#avodDetails > div > div.frame > div.content > div > ul.profileCL > li.credit-links > a')
    t = []
    for i in htmla:
        t.append(i.text.strip())
    return t


def getActorPhoto(browser):
    htmla = browser.page.select('#avodDetails > div > div.frame > div.content > div > ul.profileCL > li.credit-links > a')
    t = {}
    for i in htmla:
        p = {i.text.strip(): i['href']}
        t.update(p)
    o = {}
    for k, v in t.items():
        r = browser.open_relative(v)
        if r.ok:
            pic = browser.page.select_one('#avidolDetails > div > div.frame > div > p > img')
            p = {k: urljoin(browser.url, pic['src'])}
        else:
            p = {k, ''}
        o.update(p)
    return o


def getStudio(html):
    try:
        result = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[4]/a/span/text()')).strip(" ['']")
    except:
        result = str(html.xpath('//strong[contains(text(),"片商")]/../following-sibling::span/a/text()')).strip(" ['']")
    return result.strip('+').replace("', '", '').replace('"', '')


def getRuntime(html):
    try:
        x = html.xpath('//span[@class="koumoku" and text()="収録時間"]/../text()')[1].strip()
        return x
    except:
        return ''

def getLabel(html):
    try:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[5]/a/span/text()')[0]
        return result
    except:
        return ''


def getNum(html):
    try:
        result = html.xpath('//*[@id="hinban"]/text()')[0]
        return result
    except:
        return ''


def getYear(getRelease):
    try:
        result = str(re.search('\d{4}', getRelease).group())
        return result
    except:
        return getRelease


def getRelease(html):
    try:
        result = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[2]/text()')[1])
    except:
        return ''
    try:
        return re.findall('\d{4}/\d{2}/\d{2}', result)[0].replace('/','-')
    except:
        return ''


def getTag(html):
    result = html.xpath('//span[@class="koumoku" and text()="ジャンル"]/../a[starts-with(@href,"/avod/genre/")]/text()')
    total = []
    for i in result:
        total.append(i.replace("\n","").replace("\t",""))
    return total


def getCover_small(html, index=0):
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
    if not 'https' in result:
        result = 'https:' + result
    return result


def getCover(html):
    try:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[1]/p/a/@href')[0]
        return 'https:' + result
    except:
        return ''


def getDirector(html):
    try:
        result = html.xpath('//*[@id="program_detail_director"]/text()')[0].replace(u'\n','').replace(u'\t', '')
        return result
    except:
        return ''


def getOutline(html, number, title):
    storyline_site = config.getInstance().storyline_site().split(',')
    a = set(storyline_site) & {'airav', 'avno1'}  # 只要中文的简介文字
    if len(a):
        site = [n for n in storyline_site if n in a]
        g = getStoryline(number, title, site)
        if len(g):
            return g
    try:
        x = html.xpath('//h2[@class="title-detail"]/../p[@class="lead"]/text()')[0]
        return x.replace(getNum(html), '')
    except:
        return ''

def getSeries(html):
    try:
        try:
            result = html.xpath("//span[contains(text(),'シリーズ')]/../a/span/text()")[0]
            return result
        except:
            result = html.xpath("//span[contains(text(),'シリーズ')]/../span/text()")[0]
            return result
    except:
        return ''

def getExtrafanart(htmlcode):  # 获取剧照
    html_pather = re.compile(r'<div id="sample_images".*?>[\s\S]*?</div>')
    html = html_pather.search(htmlcode)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<a.*?href=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            s = []
            for urli in extrafanart_imgs:
                urli = 'https:' + urli.replace('/scene/small', '')
                s.append(urli)
            return s
    return ''

def open_by_browser(number):
        xcity_number = number.replace('-','')
        query_result, browser = get_html_by_form(
            'https://xcity.jp/' + secrets.choice(['about/','sitemap/','policy/','law/','help/','main/']),
            fields = {'q' : xcity_number.lower()},
            return_type = 'browser')
        if not query_result or not query_result.ok:
            raise ValueError("xcity.py: page not found")
        result = browser.follow_link(browser.links('avod\/detail')[0])
        if not result.ok:
            raise ValueError("xcity.py: detail page not found")
        return str(browser.page), browser

def main(number):
    try:
        detail_page, browser = open_by_browser(number)
        url = browser.url
        lx = etree.fromstring(detail_page, etree.HTMLParser())
        newnum = getNum(lx).upper()
        number_up = number.upper()
        if newnum != number_up:
            if newnum == number.replace('-','').upper():
                newnum = number_up
            else:
                raise ValueError("xcity.py: number not found")
        title = getTitle(lx)
        dic = {
            'actor': getActor(browser),
            'title': title,
            'studio': getStudio(lx),
            'outline': getOutline(lx, number, title),
            'runtime': getRuntime(lx),
            'director': getDirector(lx),
            'release': getRelease(lx),
            'number': newnum,
            'cover': getCover(lx),
            'cover_small': '',
            'extrafanart': getExtrafanart(detail_page),
            'imagecut': 1,
            'tag': getTag(lx),
            'label': getLabel(lx),
            'year': getYear(getRelease(lx)),  # str(re.search('\d{4}',getRelease(a)).group()),
#            'actor_photo': getActorPhoto(browser),
            'website': url,
            'source': 'xcity.py',
            'series': getSeries(lx),
        }
    except Exception as e:
        if config.getInstance().debug():
            print(e)
        dic = {"title": ""}

    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

if __name__ == '__main__':
    print(main('RCTD-288'))
    #print(main('VNDS-2624'))
    #print(main('ABP-345'))
