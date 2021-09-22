import sys
sys.path.append('../')
import re
from lxml import etree
import json
from bs4 import BeautifulSoup
from ADC_function import *


# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

def getTitle(a):
    html = etree.fromstring(a, etree.HTMLParser())
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
            p = {k: abs_url(browser.url, pic['src'])}
        else:
            p = {k, ''}
        o.update(p)
    return o


def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[4]/a/span/text()')).strip(" ['']")
    except:
        result = str(html.xpath('//strong[contains(text(),"片商")]/../following-sibling::span/a/text()')).strip(" ['']")
    return result.strip('+').replace("', '", '').replace('"', '')


def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result1 = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[2]/li[3]/text()')[0]
    except:
        return ''
    try:
        return re.findall('\d+',result1)[0]
    except:
        return ''


def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[5]/a/span/text()')[0]
        return result
    except:
        return ''


def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())
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


def getRelease(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[2]/text()')[1])
    except:
        return ''
    try:
        return re.findall('\d{4}/\d{2}/\d{2}', result)[0].replace('/','-')
    except:
        return ''


def getTag(a):
    result2=[]
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[6]/a/text()')
    for i in result1:
        i=i.replace(u'\n','')
        i=i.replace(u'\t','')
        result2.append(i)
    return result2


def getCover_small(a, index=0):
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
    if not 'https' in result:
        result = 'https:' + result
    return result


def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[1]/p/a/@href')[0]
        return 'https:' + result
    except:
        return ''


def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//*[@id="program_detail_director"]/text()')[0].replace(u'\n','').replace(u'\t', '')
        return result
    except:
        return ''


def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[2]/li[5]/p/text()')[0]
    except:
        return ''
    try:
        return re.sub('\\\\\w*\d+','',result)
    except:
        return result

def getSeries(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
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

def main(number):
    try:
        query_result, browser = get_html_by_form(
            'https://xcity.jp/about/',
            fields = {'q' : number.replace('-','').lower()},
            return_type = 'browser')
        if not query_result or not query_result.ok:
            raise ValueError("xcity.py: page not found")
        result = browser.follow_link(browser.links('avod\/detail')[0])
        if not result.ok:
            raise ValueError("xcity.py: detail page not found")
        detail_page = str(browser.page)
        url = browser.url
        dic = {
            'actor': getActor(browser),
            'title': getTitle(detail_page),
            'studio': getStudio(detail_page),
            'outline': getOutline(detail_page),
            'runtime': getRuntime(detail_page),
            'director': getDirector(detail_page),
            'release': getRelease(detail_page),
            'number': getNum(detail_page),
            'cover': getCover(detail_page),
            'cover_small': '',
            'extrafanart': getExtrafanart(detail_page),
            'imagecut': 1,
            'tag': getTag(detail_page),
            'label': getLabel(detail_page),
            'year': getYear(getRelease(detail_page)),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': getActorPhoto(browser),
            'website': url,
            'source': 'xcity.py',
            'series': getSeries(detail_page),
        }
    except Exception as e:
        if config.Config().debug():
            print(e)
        dic = {"title": ""}

    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

if __name__ == '__main__':
    print(main('RCTD-288'))
    #print(main('VNDS-2624'))
    #print(main('ABP-345'))
