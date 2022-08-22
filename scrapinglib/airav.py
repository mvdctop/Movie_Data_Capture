# -*- coding: utf-8 -*-

import json
import re
from lxml import etree
from .parser import Parser
from .javbus import Javbus

class Airav(Parser):
    source = 'airav'

    expr_title = '/html/head/title/text()'
    expr_number = '/html/head/title/text()'
    expr_studio = '//a[contains(@href,"?video_factory=")]/text()'
    expr_release = '//li[contains(text(),"發片日期")]/text()'
    expr_outline = "string(//div[@class='d-flex videoDataBlock']/div[@class='synopsis']/p)"
    expr_actor = '//ul[@class="videoAvstarList"]/li/a[starts-with(@href,"/idol/")]/text()'
    expr_cover = '//img[contains(@src,"/storage/big_pic/")]/@src'
    expr_tags = '//div[@class="tagBtnMargin"]/a/text()'
    expr_extrafanart = '//div[@class="mobileImgThumbnail"]/a/@href'

    def extraInit(self):
        # for javbus
        self.specifiedSource = None
        self.addtion_Javbus = True

    def search(self, number):
        self.number = number
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
        else:
            self.detailurl = self.queryNumberUrl(self.number)
        if self.addtion_Javbus:
            engine = Javbus()
            javbusinfo = engine.scrape(self.number, self)
            if javbusinfo == 404:
                self.javbus = {"title": ""}
            else:
                self.javbus = json.loads(javbusinfo)
        self.htmlcode = self.getHtml(self.detailurl)
        htmltree = etree.fromstring(self.htmlcode, etree.HTMLParser())
        result = self.dictformat(htmltree)
        return result

    def queryNumberUrl(self, number):
        queryUrl =  "https://cn.airav.wiki/?search=" + number
        queryTree = self.getHtmlTree(queryUrl)
        results = self.getTreeAll(queryTree, '//div[contains(@class,"videoList")]/div/a')
        for i in results:
            num = self.getTreeElement(i, '//div/div[contains(@class,"videoNumber")]/p[1]/text()')
            if num.replace('-','') == number.replace('-','').upper():
                self.number = num
                return "https://cn.airav.wiki" + i.attrib['href']
        return 'https://cn.airav.wiki/video/' + number

    def getNum(self, htmltree):
        if self.addtion_Javbus:
            result = self.javbus.get('number')
            if isinstance(result, str) and len(result):
                return result
        number = super().getNum(htmltree)
        result = str(re.findall('^\[(.*?)]', number)[0])
        return result

    def getTitle(self, htmltree):
        title = super().getTitle(htmltree)
        result = str(re.findall('](.*?)- AIRAV-WIKI', title)[0]).strip()
        return result

    def getStudio(self, htmltree):
        if self.addtion_Javbus:
            result = self.javbus.get('studio')
            if isinstance(result, str) and len(result):
                return result
        return super().getStudio(htmltree)

    def getRelease(self, htmltree):
        if self.addtion_Javbus:
            result = self.javbus.get('release')
            if isinstance(result, str) and len(result):
                return result
        try:
            return re.search(r'\d{4}-\d{2}-\d{2}', str(super().getRelease(htmltree))).group()
        except:
            return ''

    def getYear(self, htmltree):
        if self.addtion_Javbus:
            result = self.javbus.get('year')
            if isinstance(result, str) and len(result):
                return result
        release = self.getRelease(htmltree)
        return str(re.findall('\d{4}', release)).strip(" ['']")

    def getOutline(self, htmltree):
        return self.getTreeAll(htmltree, self.expr_outline).replace('\n','').strip()

    def getRuntime(self, htmltree):
        if self.addtion_Javbus:
            result = self.javbus.get('runtime')
            if isinstance(result, str) and len(result):
                return result
        return ''

    def getDirector(self, htmltree):
        if self.addtion_Javbus:
            result = self.javbus.get('director')
            if isinstance(result, str) and len(result):
                return result
        return ''

    def getActors(self, htmltree):
        a = super().getActors(htmltree)
        b = [ i.strip() for i in a if len(i)]
        if len(b):
            return b
        if self.addtion_Javbus:
            result = self.javbus.get('actor')
            if isinstance(result, list) and len(result):
                return result
        return []

    def getCover(self, htmltree):
        if self.addtion_Javbus:
            result = self.javbus.get('cover')
            if isinstance(result, str) and len(result):
                return result
        return super().getCover(htmltree)

    def getSeries(self, htmltree):
        if self.addtion_Javbus:
            result = self.javbus.get('series')
            if isinstance(result, str) and len(result):
                return result
        return ''
