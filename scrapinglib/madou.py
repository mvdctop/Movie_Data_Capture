# -*- coding: utf-8 -*-

import re
from lxml import etree
from urllib.parse import urlparse, unquote
from .parser import Parser


NUM_RULES3=[
    r'(mmz{2,4})-?(\d{2,})(-ep\d*|-\d*)?.*',
    r'(msd)-?(\d{2,})(-ep\d*|-\d*)?.*',
    r'(yk)-?(\d{2,})(-ep\d*|-\d*)?.*',
    r'(pm)-?(\d{2,})(-ep\d*|-\d*)?.*',
    r'(mky-[a-z]{2,2})-?(\d{2,})(-ep\d*|-\d*)?.*',
]

# modou提取number
def change_number(number):
    number = number.lower().strip()
    m = re.search(r'(md[a-z]{0,2})-?(\d{2,})(-ep\d*|-\d*)?.*', number, re.I)
    if m:
        return f'{m.group(1)}{m.group(2).zfill(4)}{m.group(3) or ""}'
    for rules in NUM_RULES3:
        m = re.search(rules, number, re.I)
        if m:
            return f'{m.group(1)}{m.group(2).zfill(3)}{m.group(3) or ""}'
    return number



class Madou(Parser):
    source = 'madou'

    expr_url = '//a[@class="share-weixin"]/@data-url'
    expr_title = "/html/head/title/text()"
    expr_studio = '//a[@rel="category tag"]/text()'
    expr_tags = '/html/head/meta[@name="keywords"]/@content'



    def extraInit(self):
        self.imagecut = 4
        self.uncensored = True
        self.allow_number_change = True

    def search(self, number):
        self.number = change_number(number)
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
        else:
            self.detailurl = "https://madou.club/" + number + ".html"
        self.htmlcode = self.getHtml(self.detailurl)
        if self.htmlcode == 404:
            return 404
        htmltree = etree.fromstring(self.htmlcode, etree.HTMLParser())
        self.detailurl = self.getTreeElement(htmltree, self.expr_url)

        result = self.dictformat(htmltree)
        return result

    def getNum(self, htmltree):
        try:
            # 解码url
            filename = unquote(urlparse(self.detailurl).path)
            # 裁剪文件名
            result = filename[1:-5].upper().strip()
            # 移除中文
            if result.upper() != self.number.upper():
                result = re.split(r'[^\x00-\x7F]+', result, 1)[0]
            # 移除多余的符号
            return result.strip('-')
        except:
            return ''

    def getTitle(self, htmltree):
        # <title>MD0140-2 / 家有性事EP2 爱在身边-麻豆社</title>
        # <title>MAD039 机灵可爱小叫花 强诱僧人迫犯色戒-麻豆社</title>
        # <title>MD0094／贫嘴贱舌中出大嫂／坏嫂嫂和小叔偷腥内射受孕-麻豆社</title>
        # <title>TM0002-我的痴女女友-麻豆社</title>
        browser_title = str(super().getTitle(htmltree))
        title = str(re.findall(r'^[A-Z0-9 /／\-]*(.*)-麻豆社$', browser_title)[0]).strip()
        return title

    def getCover(self, htmltree):
        try:
            url = str(re.findall("shareimage      : '(.*?)'", self.htmlcode)[0])
            return url.strip()
        except:
            return ''

    def getTags(self, htmltree):
        studio = self.getStudio(htmltree)
        tags = super().getTags(htmltree)
        return [tag for tag in tags if studio not in tag and '麻豆' not in tag]
