# -*- coding: utf-8 -*-

from lxml import etree
from .httprequest import request_session
from .parser import Parser


class Javlibrary(Parser):
    source = 'javlibrary'

    expr_number = '//div[@id="video_id"]/table/tr/td[@class="text"]/text()'
    expr_title = '//div[@id="video_title"]/h3/a/text()'
    expr_actor = '//div[@id="video_cast"]/table/tr/td[@class="text"]/span/span[@class="star"]/a/text()'
    expr_tags = '//div[@id="video_genres"]/table/tr/td[@class="text"]/span/a/text()'
    expr_cover = '//img[@id="video_jacket_img"]/@src'
    expr_release = '//div[@id="video_date"]/table/tr/td[@class="text"]/text()'
    expr_studio = '//div[@id="video_maker"]/table/tr/td[@class="text"]/span/a/text()'
    expr_runtime = '//div[@id="video_length"]/table/tr/td/span[@class="text"]/text()'
    expr_userrating = '//div[@id="video_review"]/table/tr/td/span[@class="score"]/text()'
    expr_director = '//div[@id="video_director"]/table/tr/td[@class="text"]/span/a/text()'
    expr_extrafanart = '//div[@class="previewthumbs"]/img/@src'

    def extraInit(self):
        self.htmltree = None

    def updateCore(self, core):
        if core.proxies:
            self.proxies = core.proxies
        if core.verify:
            self.verify = core.verify
        if core.morestoryline:
            self.morestoryline = True
        if core.specifiedSource == self.source:
            self.specifiedUrl = core.specifiedUrl
        self.cookies =  {'over18':'1'}

    def search(self, number):
        self.number = number.upper()
        self.session = request_session(cookies=self.cookies, proxies=self.proxies, verify=self.verify)
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
        else:
            self.detailurl = self.queryNumberUrl(self.number)
        if not self.detailurl:
            return 404
        if self.htmltree is None:
            deatils = self.session.get(self.detailurl)
            self.htmltree = etree.fromstring(deatils.text, etree.HTMLParser())
        result = self.dictformat(self.htmltree)
        return result

    def queryNumberUrl(self, number:str):
        queryUrl = "http://www.javlibrary.com/cn/vl_searchbyid.php?keyword=" + number
        queryResult = self.session.get(queryUrl)
        
        if queryResult and "/?v=jav" in queryResult.url:
            self.htmltree = etree.fromstring(queryResult.text, etree.HTMLParser())
            return queryResult.url
        else:
            queryTree = etree.fromstring(queryResult.text, etree.HTMLParser())
            numbers = queryTree.xpath('//div[@class="id"]/text()')
            if number in numbers:
                urls = queryTree.xpath('//div[@class="id"]/../@href')
                detailurl = urls[numbers.index(number)]
                return "http://www.javlibrary.com/cn" + detailurl.strip('.')
        return None

    def getTitle(self, htmltree):
        title = super().getTitle(htmltree)
        title = title.replace(self.getNum(htmltree), '').strip()
        return title

    def getCover(self, htmltree):
        url = super().getCover(htmltree)
        if not url.startswith('http'):
            url = 'https:' + url
        return url
   
    def getOutline(self, htmltree):
        if self.morestoryline:
            from .storyline import getStoryline
            return getStoryline(self.number, self.getUncensored(htmltree),
                                proxies=self.proxies, verify=self.verify)
        return ''
