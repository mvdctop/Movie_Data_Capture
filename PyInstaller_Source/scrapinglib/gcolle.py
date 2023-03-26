# -*- coding: utf-8 -*-

import re
from lxml import etree
from .httprequest import request_session
from .parser import Parser


class Gcolle(Parser):
    source = 'gcolle'

    expr_r18 = '//*[@id="main_content"]/table[1]/tbody/tr/td[2]/table/tbody/tr/td/h4/a[2]/@href'
    expr_number = '//td[contains(text(),"商品番号")]/../td[2]/text()'
    expr_title = '//*[@id="cart_quantity"]/table/tr[1]/td/h1/text()'
    expr_studio = '//td[contains(text(),"アップロード会員名")]/b/text()'
    expr_director = '//td[contains(text(),"アップロード会員名")]/b/text()'
    expr_actor = '//td[contains(text(),"アップロード会員名")]/b/text()'
    expr_label = '//td[contains(text(),"アップロード会員名")]/b/text()'
    expr_series = '//td[contains(text(),"アップロード会員名")]/b/text()'
    expr_release = '//td[contains(text(),"商品登録日")]/../td[2]/time/@datetime'
    expr_cover = '//*[@id="cart_quantity"]/table/tr[3]/td/table/tr/td/a/@href'
    expr_tags = '//*[@id="cart_quantity"]/table/tr[4]/td/a/text()'
    expr_outline = '//*[@id="cart_quantity"]/table/tr[3]/td/p/text()'
    expr_extrafanart = '//*[@id="cart_quantity"]/table/tr[3]/td/div/img/@src'
    expr_extrafanart2 = '//*[@id="cart_quantity"]/table/tr[3]/td/div/a/img/@src'

    def extraInit(self):
        self.imagecut = 4

    def search(self, number: str):
        self.number = number.upper().replace('GCOLLE-', '')
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
        else:
            self.detailurl = 'https://gcolle.net/product_info.php/products_id/' + self.number
        session = request_session(cookies=self.cookies, proxies=self.proxies, verify=self.verify)
        htmlcode = session.get(self.detailurl).text
        htmltree = etree.HTML(htmlcode)

        r18url = self.getTreeElement(htmltree, self.expr_r18)
        if r18url and r18url.startswith('http'):
            htmlcode = session.get(r18url).text
            htmltree = etree.HTML(htmlcode)
        result = self.dictformat(htmltree)
        return result

    def getNum(self, htmltree):
        num = super().getNum(htmltree)
        if self.number != num:
            raise Exception(f'[!] {self.number}: find [{num}] in gcolle, not match')
        return "GCOLLE-" + str(num)

    def getOutline(self, htmltree):
        result = self.getTreeAll(htmltree, self.expr_outline)
        try:
            return "\n".join(result)
        except:
            return ""

    def getRelease(self, htmltree):
        return re.findall('\d{4}-\d{2}-\d{2}', super().getRelease(htmltree))[0]

    def getCover(self, htmltree):
        return "https:" + super().getCover(htmltree)

    def getExtrafanart(self, htmltree):
        extrafanart = self.getTreeAll(htmltree, self.expr_extrafanart)
        if len(extrafanart) == 0:
            extrafanart = self.getTreeAll(htmltree, self.expr_extrafanart2)
        # Add "https:" in each extrafanart url
        for i in range(len(extrafanart)):
            extrafanart[i] = 'https:' + extrafanart[i]
        return extrafanart
