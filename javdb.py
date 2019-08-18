import re
from lxml import etree
import json
from bs4 import BeautifulSoup
from ADC_function import *

def getTitle(a):
    try:
        html = etree.fromstring(a, etree.HTMLParser())
        result = str(html.xpath('/html/body/section/div/h2/strong/text()')).strip(" ['']")
        return re.sub('.*\] ','',result.replace('/', ',').replace('\\xa0','').replace(' : ',''))
    except:
        return re.sub('.*\] ','',result.replace('/', ',').replace('\\xa0',''))
def getActor(a): #//*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser()) #//table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"演員")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"演員")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace(",\\xa0","").replace("'","").replace(' ','').replace(',,','').lstrip(',').replace(',',', ')
def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser()) #//table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"製作")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"製作")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1+result2).strip('+').replace("', '",'').replace('"','')
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')
def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '",'').replace('"','')
def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result1 = str(html.xpath('//strong[contains(text(),"番號")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"番號")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+')
def getYear(getRelease):
    try:
        result = str(re.search('\d{4}',getRelease).group())
        return result
    except:
        return getRelease
def getRelease(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時間")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時間")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+')
def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"类别")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"类别")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace(",\\xa0","").replace("'","").replace(' ','').replace(',,','').lstrip(',')
def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/section/div/div[2]/div[1]/a/img/@src')).strip(" ['']")
    if result == '':
        result = str(html.xpath('/html/body/section/div/div[3]/div[1]/a/img/@src')).strip(" ['']")
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"導演")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"導演")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '",'').replace('"','')
def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="introduction"]/dd/p[1]/text()')).strip(" ['']")
    return result
def main(number):
    try:
        a = get_html('https://javdb.com/search?q=' + number + '&f=all')
        html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        result1 = str(html.xpath('//*[@id="videos"]/div/div/a/@href')).strip(" ['']")
        if result1 == '':
            a = get_html('https://javdb.com/search?q=' + number.replace('-', '_') + '&f=all')
            html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
            result1 = str(html.xpath('//*[@id="videos"]/div/div/a/@href')).strip(" ['']")
        b = get_html('https://javdb1.com' + result1)
        soup = BeautifulSoup(b, 'lxml')
        a = str(soup.find(attrs={'class': 'panel'}))
        dic = {
            'actor': getActor(a),
            'title': getTitle(b).replace("\\n", '').replace('        ', '').replace(getActor(a), '').replace(getNum(a),
                                                                                                             '').replace(
                '无码', '').replace('有码', '').lstrip(' '),
            'studio': getStudio(a),
            'outline': getOutline(a),
            'runtime': getRuntime(a),
            'director': getDirector(a),
            'release': getRelease(a),
            'number': getNum(a),
            'cover': getCover(b),
            'imagecut': 0,
            'tag': getTag(a),
            'label': getLabel(a),
            'year': getYear(getRelease(a)),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': '',
            'website': 'https://javdb1.com' + result1,
            'source': 'javdb.py',
        }
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
        return js
    except:
        a = get_html('https://javdb.com/search?q=' + number + '&f=all')
        html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        result1 = str(html.xpath('//*[@id="videos"]/div/div/a/@href')).strip(" ['']")
        if result1 == '' or result1 == 'null':
            a = get_html('https://javdb.com/search?q=' + number.replace('-', '_') + '&f=all')
            html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
            result1 = str(html.xpath('//*[@id="videos"]/div/div/a/@href')).strip(" ['']")
        b = get_html('https://javdb.com' + result1)
        soup = BeautifulSoup(b, 'lxml')
        a = str(soup.find(attrs={'class': 'panel'}))
        dic = {
            'actor': getActor(a),
            'title': getTitle(b).replace("\\n", '').replace('        ', '').replace(getActor(a), '').replace(
                getNum(a),
                '').replace(
                '无码', '').replace('有码', '').lstrip(' '),
            'studio': getStudio(a),
            'outline': getOutline(a),
            'runtime': getRuntime(a),
            'director': getDirector(a),
            'release': getRelease(a),
            'number': getNum(a),
            'cover': getCover(b),
            'imagecut': 0,
            'tag': getTag(a),
            'label': getLabel(a),
            'year': getYear(getRelease(a)),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': '',
            'website': 'https://javdb.com' + result1,
            'source': 'javdb.py',
        }
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4,separators=(',', ':'), )  # .encode('UTF-8')
        return js

#print(main('061519-861'))