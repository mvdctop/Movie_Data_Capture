import sys
sys.path.append('../')
import re
from pyquery import PyQuery as pq#need install
from lxml import etree#need install
from bs4 import BeautifulSoup#need install
import json
from ADC_function import *


host = 'https://www.91mv.org'

def getActorPhoto(htmlcode):
    return ''

def getTitle(htmlcode):  #获取标题
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        title = str(html.xpath('//div[@class="player-title"]/text()')[0])
        result = str(re.findall('(.*)(91.*-\d*)',title)[0][0])
        return result.strip()
    except:
        return ''

def getStudio(htmlcode): #获取厂商 已修改
    return '91制片厂'

def getYear(htmlcode):   #获取年份
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = str(html.xpath('//p[@class="date"]/text()')[0])
        date = result.replace('日期：','')
        if isinstance(date, str) and len(date):
            return date
    except:
        return ''
    return ''

def getCover(htmlcode):  #获取封面图片
    try:
        url = str(re.findall('var pic_url = "(.*?)"',htmlcode)[0])
        return url.strip()
    except:
        return ''

def getRelease(htmlcode): #获取出版日期
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = str(html.xpath('//p[@class="date"]/text()')[0])
        date = result.replace('日期：','')
        if isinstance(date, str) and len(date):
            return date
    except:
        return ''
    return ''

def getRuntime(htmlcode): #获取播放时长
    return ''

def getActor(htmlcode):   #获取女优
    b=[]
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    for player in html.xpath('//p[@class="player-name"]/text()'):
        player = player.replace('主演：','')
        b.append(player)
    return b

def getNum(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        title = str(html.xpath('//div[@class="player-title"]/text()')[0])
        result = str(re.findall('(.*)(91.*-\d*)',title)[0][1])
        return result.strip()
    except:
        return ''

def getDirector(htmlcode): #获取导演 已修改
    return ''

def getOutline(htmlcode):  #获取概述
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = str(html.xpath('//div[@class="play-text"]/text()')[0])
        return result.strip()
    except:
        return ''
  

def getSerise(htmlcode):   #获取系列 已修改
    return ''

def getTag(htmlcode):  # 获取标签
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    return html.xpath('//div[@class="player-tag"]/text()')

def getExtrafanart(htmlcode):  # 获取剧照
    return ''

def search(keyword): #搜索，返回结果
    search_html = get_html(host + '/index/search?keywords=' + keyword)
    html = etree.fromstring(search_html, etree.HTMLParser())
    return html.xpath('//a[@class="video-list"]/@href')[0]

def main(number):
    try:
        try:
            number = number.replace('91CM-','').replace('91MS-','')
            url = host + str(search(number))
            htmlcode = get_html(url)
        except:
            print(number)

        dic = {
            # 标题
            'title': getTitle(htmlcode),
            # 制作商
            'studio': getStudio(htmlcode),
            # 年份
            'year': getYear(htmlcode),
            # 简介
            'outline': getOutline(htmlcode),
            # 
            'runtime': getRuntime(htmlcode),
            # 导演 
            'director': getDirector(htmlcode),
            # 演员 
            'actor': getActor(htmlcode),
            # 发售日
            'release': getRelease(htmlcode),
            # 番号
            'number': getNum(htmlcode),
            # 封面链接
            'cover': getCover(htmlcode),
            # 剧照获取
            'extrafanart': getExtrafanart(htmlcode),
            'imagecut': 0,
            # 
            'tag': getTag(htmlcode),
            # 
            'label': getSerise(htmlcode),
            # 作者图片
            'website': url,
            'source': 'mv91.py',
            # 使用
            'series': getSerise(htmlcode)
        }
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4,separators=(',', ':'), )  # .encode('UTF-8')
        return js
    except Exception as e:
        if config.getInstance().debug():
            print(e)
        data = {
            "title": "",
        }
        js = json.dumps(
            data, ensure_ascii=False, sort_keys=True, indent=4, separators=(",", ":")
        )
        return js


if __name__ == '__main__':
    print(main('91CM-121'))
    print(main('91CM-122'))
    print(main('91CM-143'))
    print(main('91MS-006'))
