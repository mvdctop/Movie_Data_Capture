#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from lxml import etree
import json
from ADC_function import *
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

def getTitle(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath('//*[@id="title"]/text()')[0]
    return result
def getActor(a): #//*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())
    result = str(html.xpath("//td[contains(text(),'出演者')]/following-sibling::td/span/a/text()")).strip(" ['']").replace("', '",',')
    return result
def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result1 = html.xpath("//td[contains(text(),'メーカー')]/following-sibling::td/a/text()")[0]
    except:
        result1 = html.xpath("//td[contains(text(),'メーカー')]/following-sibling::td/text()")[0]
    return result1
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath("//td[contains(text(),'収録時間')]/following-sibling::td/text()")[0]
    return re.search('\d+', str(result1)).group()
def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result1 = html.xpath("//td[contains(text(),'シリーズ：')]/following-sibling::td/a/text()")[0]
    except:
        result1 = html.xpath("//td[contains(text(),'シリーズ：')]/following-sibling::td/text()")[0]
    return result1
def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result1 = html.xpath("//td[contains(text(),'品番：')]/following-sibling::td/a/text()")[0]
    except:
        result1 = html.xpath("//td[contains(text(),'品番：')]/following-sibling::td/text()")[0]
    return result1
def getYear(getRelease):
    try:
        result = str(re.search('\d{4}',getRelease).group())
        return result
    except:
        return getRelease
def getRelease(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result1 = html.xpath("//td[contains(text(),'発売日：')]/following-sibling::td/a/text()")[0].lstrip('\n')
    except:
        result1 = html.xpath("//td[contains(text(),'発売日：')]/following-sibling::td/text()")[0].lstrip('\n')
    return result1
def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result1 = html.xpath("//td[contains(text(),'ジャンル：')]/following-sibling::td/a/text()")
    except:
        result1 = html.xpath("//td[contains(text(),'ジャンル：')]/following-sibling::td/text()")
    return result1
def getCover(htmlcode,number):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = html.xpath('//*[@id="'+number+'"]/@href')[0]
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result1 = html.xpath("//td[contains(text(),'監督：')]/following-sibling::td/a/text()")[0]
    except:
        result1 = html.xpath("//td[contains(text(),'監督：')]/following-sibling::td/text()")[0]
    return result1
def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath("//div[@class='mg-b20 lh4']/text()")[0]).replace('\n','')
    return result
def main(number):
    htmlcode=get_html('https://www.dmm.co.jp/digital/videoa/-/detail/=/cid='+number)
    url = 'https://www.dmm.co.jp/digital/videoa/-/detail/=/cid='+number
    if '404 Not Found' in htmlcode:
        htmlcode=get_html('https://www.dmm.co.jp/mono/dvd/-/detail/=/cid='+number)
        url = 'https://www.dmm.co.jp/mono/dvd/-/detail/=/cid='+number
    try:
        dic = {
            'title': getTitle(htmlcode).strip(getActor(htmlcode)),
            'studio': getStudio(htmlcode),
            'outline': getOutline(htmlcode),
            'runtime': getRuntime(htmlcode),
            'director': getDirector(htmlcode),
            'actor': getActor(htmlcode),
            'release': getRelease(htmlcode),
            'number': getNum(htmlcode),
            'cover': getCover(htmlcode,number),
            'imagecut': 1,
            'tag': getTag(htmlcode),
            'label':getLabel(htmlcode),
            'year': getYear(getRelease(htmlcode)),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': '',
            'website': url,
            'source': 'siro.py',
        }
    except :
        dic = {
            'title': '',
        }
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))  # .encode('UTF-8')
    return js

# main('DV-1562')
# input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
#print(main('ipx292'))
