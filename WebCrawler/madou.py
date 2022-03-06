import sys
sys.path.append('../')
from bs4 import BeautifulSoup  # need install
from lxml import etree  # need install
from pyquery import PyQuery as pq  # need install
from ADC_function import *
import json
import re
from lib2to3.pgen2 import parse

from urllib.parse import urlparse, unquote


def getActorPhoto(html):
    return ''


def getTitle(html, number):  # 获取标题
    # <title>MD0140-2 / 家有性事EP2 爱在身边-麻豆社</title>
    # <title>MAD039 机灵可爱小叫花 强诱僧人迫犯色戒-麻豆社</title>
    browser_title = str(html.xpath("/html/head/title/text()")[0])
    browser_title = browser_title[browser_title.find(' '):].replace('/','').strip()
    return browser_title[:browser_title.find('-麻豆社')].strip()


def getStudio(html):  # 获取厂商 已修改
    try:
        category = str(html.xpath('//a[@rel="category tag"]/text()')[0])
        return category.strip()
    except:
        return '麻豆社'


def getYear(html):  # 获取年份
    return ''


def getCover(htmlcode):  # 获取封面图片
    try:
        url = str(re.findall("shareimage      : '(.*?)'", htmlcode)[0])
        return url.strip()
    except:
        return ''


def getRelease(html):  # 获取出版日期
    return ''


def getRuntime(html):  # 获取播放时长
    return ''

def getUrl(html):
    return str(html.xpath('//a[@class="share-weixin"]/@data-url')[0])


def getNum(url, number):  # 获取番号
    try:
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


def getDirector(html):  # 获取导演 已修改
    return ''


def getOutline(html):  # 获取概述
    return ''


def getSerise(html):  # 获取系列 已修改
    return ''


def getTag(html):  # 获取标签
    return html.xpath('//div[@class="article-tags"]/a/text()')


def getExtrafanart(html):  # 获取剧照
    return ''

def cutTags(tags):
    actors = []
    tags = []
    for tag in tags:
        actors.append(tag)
    return actors,tags


def main(number):
    try:
        try:
            number = number.lower().strip()
            url = "https://madou.club/" + number + ".html"
            htmlcode = get_html(url)
        except:
            print(number)

        html = etree.fromstring(htmlcode, etree.HTMLParser())
        url = getUrl(html)
        tags = getTag(html)
        actor,tags = cutTags(tags);
        dic = {
            # 标题
            'title': getTitle(html, number),
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
            'actor': actor,
            # 发售日
            'release': getRelease(html),
            # 番号
            'number': getNum(url, number),
            # 封面链接
            'cover': getCover(htmlcode),
            # 剧照获取
            'extrafanart': getExtrafanart(html),
            'imagecut': 1,
            #
            'tag': tags,
            #
            'label': getSerise(html),
            # 作者图片
            'website': url,
            'source': 'madou.py',
            # 使用
            'series': getSerise(html)
        }
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True,
                        indent=4, separators=(',', ':'), )  # .encode('UTF-8')
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
    print(main('MD0222'))
    print(main('MD0140-2'))
    print(main('MAD039'))
