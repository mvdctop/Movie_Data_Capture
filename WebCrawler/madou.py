from lib2to3.pgen2 import parse
import sys

from urllib.parse import urlparse,unquote
sys.path.append('../')
import re
from pyquery import PyQuery as pq#need install
from lxml import etree#need install
from bs4 import BeautifulSoup#need install
import json
from ADC_function import *

def getActorPhoto(htmlcode):
    return ''

def getTitle(htmlcode,number):  #获取标题
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    title = str(html.xpath('//h1[@class="article-title"]/text()')[0])
    try:
        result = str(re.split(r'[/|／|-]',title)[1])
        return result.strip()
    except:
        return title.replace(number.upper(),'').strip()

def getStudio(htmlcode): #获取厂商 已修改
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        category = str(html.xpath('//a[@rel="category tag"]/text()')[0])
        return category.strip()
    except:
        return '麻豆社'

def getYear(htmlcode):   #获取年份
    return ''

def getCover(htmlcode):  #获取封面图片
    try:
        url = str(re.findall("shareimage      : '(.*?)'",htmlcode)[0])
        return url.strip()
    except:
        return ''

def getRelease(htmlcode): #获取出版日期
    return ''

def getRuntime(htmlcode): #获取播放时长
    return ''

def getActor(htmlcode):   #获取女优
    b=[]
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    for player in html.xpath('//div[@class="article-tags"]/a/text()'):
        b.append(player)
    return b

def getNum(htmlcode,number):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        url = str(html.xpath('//a[@class="share-weixin"]/@data-url')[0])
        # 解码url
        filename = unquote(urlparse(url).path)
        # 裁剪文件名
        result = filename[1:-5].upper().strip()
        print(result)
        # 移除中文
        if result.upper() != number.upper():
            result = re.split(r'[^\x00-\x7F]+', result, 1)[0]
        # 移除多余的符号
        return result.strip('-')
    except:
        return ''

def getDirector(htmlcode): #获取导演 已修改
    return ''

def getOutline(htmlcode):  #获取概述
    return ''
  

def getSerise(htmlcode):   #获取系列 已修改
    return ''

def getTag(htmlcode):  # 获取标签
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    return html.xpath('//div[@class="article-tags"]/a/text()')

def getExtrafanart(htmlcode):  # 获取剧照
    return ''

def main(number):
    try:
        try:
            number = number.lower().replace('md-','md').replace('mdx-','mdx').replace('mky-ap-','mkyap')
            url = "https://madou.club/" + number + ".html"
            htmlcode = get_html(url)
        except:
            print(number)

        dic = {
            # 标题
            'title': getTitle(htmlcode,number),
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
            'number': getNum(htmlcode,number),
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
            'source': 'madou.py',
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
    print(main('MD-0147'))
    print(main('number'))
    
