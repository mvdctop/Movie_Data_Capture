import sys
sys.path.append('../')
import re
from lxml import etree#need install
from bs4 import BeautifulSoup#need install
import json
from ADC_function import *


host = 'https://www.91mv.org'

def getActorPhoto(html):
    return ''

def getTitle(html):  #获取标题
    try:
        title = str(html.xpath('//div[@class="player-title"]/text()')[0])
        result = str(re.findall('(.*)(91.*-\d*)',title)[0][0])
        return result.strip()
    except:
        return ''

def getStudio(html): #获取厂商 已修改
    return '91制片厂'

def getYear(html):   #获取年份
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

def getRelease(html): #获取出版日期
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

def getActor(html):   #获取女优
    b=[]
    for player in html.xpath('//p[@class="player-name"]/text()'):
        player = player.replace('主演：','')
        b.append(player)
    return b

def getNum(html):     #获取番号
    try:
        title = str(html.xpath('//div[@class="player-title"]/text()')[0])
        result = str(re.findall('(.*)(91.*-\d*)',title)[0][1])
        return result.strip()
    except:
        return ''

def getDirector(html): #获取导演 已修改
    return ''

def getOutline(html):  #获取概述
    try:
        result = str(html.xpath('//div[@class="play-text"]/text()')[0])
        return result.strip()
    except:
        return ''


def getSerise(htmlcode):   #获取系列 已修改
    return ''

def getTag(html):  # 获取标签
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
        html = etree.fromstring(htmlcode, etree.HTMLParser())
        dic = {
            # 标题
            'title': getTitle(html),
            # 制作商
            'studio': getStudio(html),
            # 年份
            'year': getYear(html),
            # 简介
            'outline': getOutline(html),
            #
            'runtime': getRuntime(html),
            # 导演
            'director': getDirector(html),
            # 演员
            'actor': getActor(html),
            # 发售日
            'release': getRelease(html),
            # 番号
            'number': getNum(html),
            # 封面链接
            'cover': getCover(htmlcode),
            # 剧照获取
            'extrafanart': getExtrafanart(html),
            'imagecut': 1,
            #
            'tag': getTag(html),
            #
            'label': getSerise(html),
            # 作者图片
            'website': url,
            'source': 'mv91.py',
            # 使用
            'series': getSerise(html)
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
