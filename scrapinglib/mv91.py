# -*- coding: utf-8 -*-


import re
from lxml import etree
from .parser import Parser


class Mv91(Parser):
    source = 'mv91'

    expr_number = '//div[@class="player-title"]/text()'
    expr_title = '//div[@class="player-title"]/text()'
    expr_release = '//p[@class="date"]/text()'
    expr_outline = '//div[@class="play-text"]/text()'
    expr_tags = '//div[@class="player-tag"]/text()'
    expr_actor = '//p[@class="player-name"]/text()'

    def extraInit(self):
        self.imagecut = 0
        self.uncensored = True

    def getHtmlTree(self, url, type=None):
        self.htmlcode = self.getHtml(url, type)
        if self.htmlcode == 404:
            return 404
        ret = etree.fromstring(self.htmlcode, etree.HTMLParser())
        return ret

    def queryNumberUrl(self, number):
        keyword = number.replace('91CM-','').replace('91MS-','')
        search_html = self.getHtml('https://www.91mv.org/index/search?keywords=' + keyword)
        html = etree.fromstring(search_html, etree.HTMLParser())
        endurl = html.xpath('//a[@class="video-list"]/@href')[0]
        return 'https://www.91mv.org' + endurl

    def getNum(self, htmltree):
        try:
            num = super().getNum(htmltree)
            finds = re.findall('(.*)(91.*-\d*)',num)
            if finds:
                result = str(finds[0][1])
            else:
                result = ' '.join(num.replace('/',' ').split())
                result = result.split()[1]
                if self.number.upper() != result.upper():
                    raise Exception(f'[!] {self.number}: find {result} in mv91, not match')
            return result.strip()
        except:
            return ''

    def getTitle(self, htmltree):
        try:
            title = super().getTitle(htmltree)
            finds = re.findall('(.*)(91.*-\d*)',title)
            if finds:
                result = str(finds[0][0])
            else:
                result = ' '.join(title.replace('/',' ').split())
                result = result.split()[0]
            return result.replace('「预告」','').strip('/ ')
        except:
            return ''

    def getStudio(self, htmltree):
        return '91制片厂'

    def getActors(self, htmltree):
        b=[]
        for player in self.getTreeAll(htmltree, self.expr_actor):
            player = player.replace('主演：','')
            if '/' in player:
                player = player.split('/')[0]
                player = re.sub(r'[0-9]+', '', player)
            b.append(player)
        return b

    def getRelease(self, htmltree):
        try:
            result = super().getRelease(htmltree)
            date = result.replace('日期：','')
            if isinstance(date, str) and len(date):
                return date
        except:
            pass
        return ''

    def getCover(self, htmltree):
        try:
            url = str(re.findall('var pic_url = "(.*?)"', self.htmlcode)[0])
            return url.strip()
        except:
            return ''

