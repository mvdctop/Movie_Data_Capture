# -*- coding: utf-8 -*-

import re
from lxml import etree
from urllib.parse import urlparse, unquote
from .parser import Parser


class Madou(Parser):
    source = 'madou'

    expr_url = '//a[@class="share-weixin"]/@data-url'
    expr_title = "/html/head/title/text()"
    expr_studio = '//a[@rel="category tag"]/text()'
    expr_tags = '/html/head/meta[@name="keywords"]/@content'

    def extraInit(self):
        self.imagecut = 0
        self.uncensored = True

    def search(self, number):
        self.number = number.lower().strip()
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
        x = super().getTags(htmltree)
        return [i.strip() for i in x if len(i.strip()) and studio not in i and '麻豆' not in i]
