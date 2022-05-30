# -*- coding: utf-8 -*-

import re
from lxml import etree
from . import httprequest
from .parser import Parser


class Jav321(Parser):
    source = 'jav321'

    expr_title = "/html/body/div[2]/div[1]/div[1]/div[1]/h3/text()"
    expr_cover = "/html/body/div[2]/div[2]/div[1]/p/a/img/@src"
    expr_outline = "/html/body/div[2]/div[1]/div[1]/div[2]/div[3]/div/text()"
    # NOTE: 统一使用 xpath
    expr_number = '//b[contains(text(),"品番")]/following-sibling::node()'
    expr_actor = '//b[contains(text(),"出演者")]/following-sibling::a[starts-with(@href,"/star")]'
    expr_label = '//b[contains(text(),"メーカー")]/following-sibling::a[starts-with(@href,"/company")]'
    expr_tags = '//b[contains(text(),"ジャンル")]/following-sibling::a[starts-with(@href,"/genre")]'
    expr_studio = '//b[contains(text(),"メーカー")]/following-sibling::a[starts-with(@href,"/company")]'
    expr_release = '//b[contains(text(),"配信開始日")]/following-sibling::node()'
    expr_runtime = '//b[contains(text(),"収録時間")]/following-sibling::node()'
    # expr_series = '//b[contains(text(),"シリーズ")]'

    def queryNumberUrl(self, number):
        return 'https://www.jav321.com/search'

    def getHtmlTree(self, url):
        resp = httprequest.post(url, data={"sn": self.number}, cookies=self.cookies, proxies=self.proxies, verify=self.verify)
        if "/video/" in resp.url:
            self.detailurl = resp.url
            self.detailhtml = resp.text
            return etree.fromstring(resp.text, etree.HTMLParser())
        return None

    def getNum(self, htmltree):
        return super().getNum(htmltree).split(": ")[1]

    def getTrailer(self, htmltree):
        videourl_pather = re.compile(r'<source src=\"(.*?)\"')
        videourl = videourl_pather.findall(self.detailhtml)
        if videourl:
            url = videourl[0].replace('awscc3001.r18.com', 'cc3001.dmm.co.jp').replace('cc3001.r18.com', 'cc3001.dmm.co.jp')
            return url
        else:
            return ''

    def getExtrafanart(self, htmltree):
        html_pather = re.compile(r'<div class=\"col\-md\-3\"><div class=\"col\-xs\-12 col\-md\-12\">[\s\S]*?</script><script async src=\"\/\/adserver\.juicyads\.com/js/jads\.js\">')
        html = html_pather.search(self.detailhtml)
        if html:
            html = html.group()
            extrafanart_pather = re.compile(r'<img.*?src=\"(.*?)\"')
            extrafanart_imgs = extrafanart_pather.findall(html)
            if extrafanart_imgs:
                return extrafanart_imgs
        return ''

    def getRelease(self, htmltree):
        return super().getRelease(htmltree).split(": ")[1]
    
    def getRuntime(self, htmltree):
        return super().getRuntime(htmltree).split(": ")[1]

    def parseElement(self, all):
        if all:
            ret = []
            for si in all:
                ret.append(si.text)
            return ",".join(ret)
        return ''

    def getActors(self, htmltree):
        return self.parseElement(super().getActors(htmltree))

    def getLabel(self, htmltree):
        return self.parseElement(self.getAll(htmltree, self.expr_label))

    def getTags(self, htmltree):
        return self.parseElement(self.getAll(htmltree, self.expr_tags))
    
    def getStudio(self, htmltree):
        return self.parseElement(self.getAll(htmltree, self.expr_studio))
