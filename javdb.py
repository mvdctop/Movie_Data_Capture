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
    result = html.xpath("/html/body/section/div/h2/strong/text()")[0]
    return result
def getActor(a):  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"演員")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"演員")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace(",\\xa0", "").replace("'", "").replace(' ', '').replace(',,', '').lstrip(',').replace(',', ', ')
def getActorPhoto(actor): #//*[@id="star_qdt"]/li/a/img
    a = actor.split(',')
    d={}
    for i in a:
        p={i:''}
        d.update(p)
    return d
def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"片商")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"片商")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')
def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result1 = str(html.xpath('//strong[contains(text(),"番號")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"番號")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result2 + result1).strip('+')
def getYear(getRelease):
    try:
        result = str(re.search('\d{4}', getRelease).group())
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
    return str(result1 + result2).strip('+').replace(",\\xa0", "").replace("'", "").replace(' ', '').replace(',,', '').lstrip(',')
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
    result = str(html.xpath("//div[@class='column column-video-cover']/a/img/@src")).strip(" ['']")
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"導演")]/../following-sibling::span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"導演")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="introduction"]/dd/p[1]/text()')).strip(" ['']")
    return result
def main(number):
    try:
        number = number.upper()
        query_result = get_html('https://javdb.com/search?q=' + number + '&f=all')
        html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        # javdb sometime returns multiple results,
        # and the first elememt maybe not the one we are looking for
        # iterate all candidates and find the match one
        urls = html.xpath('//*[@id="videos"]/div/div/a/@href')
        ids =html.xpath('//*[@id="videos"]/div/div/a/div[contains(@class, "uid")]/text()')
        correct_url = urls[ids.index(number)]
        detail_page = get_html('https://javdb.com' + correct_url)
        dic = {
            'actor': getActor(detail_page),
            'title': getTitle(detail_page),
            'studio': getStudio(detail_page),
            'outline': getOutline(detail_page),
            'runtime': getRuntime(detail_page),
            'director': getDirector(detail_page),
            'release': getRelease(detail_page),
            'number': getNum(detail_page),
            'cover': getCover(detail_page),
            'cover_small': getCover_small(query_result, index=ids.index(number)),
            'imagecut': 3,
            'tag': getTag(detail_page),
            'label': getLabel(detail_page),
            'year': getYear(getRelease(detail_page)),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': getActorPhoto(getActor(detail_page)),
            'website': 'https://javdb.com' + correct_url,
            'source': 'javdb.py',
        }
    except Exception as e:
        # print(e)
        dic = {"title": ""}
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

# main('DV-1562')
# input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
#print(main('ipx-292'))
