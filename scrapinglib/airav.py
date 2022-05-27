# -*- coding: utf-8 -*-

import json
import re
from lxml import etree
from bs4 import BeautifulSoup
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

    def search(self, number):
        self.number = number
        self.detailurl = 'https://cn.airav.wiki/video/' + number
        engine = Javbus()
        javbusinfo = engine.search(number, self)
        if javbusinfo == 404:
            self.javbus = {"title": ""}
        else:
            self.javbus = json.loads(javbusinfo)
        self.htmlcode = self.getHtml(self.detailurl)
        htmltree = etree.fromstring(self.htmlcode, etree.HTMLParser())
        result = self.dictformat(htmltree)
        return result

    def getNum(self, htmltree):
        # return super().getNum(htmltree)
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
        result = self.javbus.get('studio')
        if isinstance(result, str) and len(result):
            return result
        return super().getStudio(htmltree)

    def getRelease(self, htmltree):
        result = self.javbus.get('release')
        if isinstance(result, str) and len(result):
            return result
        try:
            return re.search(r'\d{4}-\d{2}-\d{2}', str(super().getRelease(htmltree))).group()
        except:
            return ''

    def getYear(self, htmltree):
        result = self.javbus.get('year')
        if isinstance(result, str) and len(result):
            return result
        release = self.getRelease(htmltree)
        return str(re.findall('\d{4}', release)).strip(" ['']")

    def getOutline(self, htmltree):
        return self.getAll(htmltree, self.expr_outline).replace('\n','').strip()

    def getRuntime(self, htmltree):
        result = self.javbus.get('runtime')
        if isinstance(result, str) and len(result):
            return result
        return ''

    def getDirector(self, htmltree):
        result = self.javbus.get('director')
        if isinstance(result, str) and len(result):
            return result
        return ''

    def getActors(self, htmltree):
        b=[]
        a = super().getActors(htmltree)
        for v in a:
            v = v.strip()
            if len(v):
                b.append(v)
        if len(b):
            return b
        result = self.javbus.get('actor')
        if isinstance(result, list) and len(result):
            return result
        return []

    def getCover(self, htmltree):
        result = self.javbus.get('cover')
        if isinstance(result, str) and len(result):
            return result
        return super().getCover(htmltree)

    def getExtrafanart(self, htmltree):
        html_pather = re.compile(r'<div class=\"mobileImgThumbnail\">[\s\S]*?</div></div></div></div>')
        html = html_pather.search(self.htmlcode)
        if html:
            html = html.group()
            extrafanart_pather = re.compile(r'<img.*?src=\"(.*?)\"')
            extrafanart_imgs = extrafanart_pather.findall(html)
            if extrafanart_imgs:
                return extrafanart_imgs
        return ''

    def getTags(self, htmltree):
        tag = []
        soup = BeautifulSoup(self.htmlcode, 'lxml')
        x = soup.find_all(attrs={'class': 'tagBtnMargin'})
        a = x[0].find_all('a')

        for i in a:
            tag.append(i.get_text())
        return tag

    def getSeries(self, htmltree):
        result = self.javbus.get('series')
        if isinstance(result, str) and len(result):
            return result
        return ''
