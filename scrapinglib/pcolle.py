# -*- coding: utf-8 -*-

import re
from lxml import etree
from .httprequest import request_session
from .parser import Parser


class Pcolle(Parser):
    source = 'pcolle'

    expr_number = '//th[contains(text(),"商品ID")]/../td/text()'
    expr_title = '//div[@class="title-04"]/div/text()'
    expr_studio = '//th[contains(text(),"販売会員")]/../td/a/text()'
    expr_director = '//th[contains(text(),"販売会員")]/../td/a/text()'
    expr_actor = '//th[contains(text(),"販売会員")]/../td/a/text()'
    expr_label = '//th[contains(text(),"カテゴリー")]/../td/ul/li/a/text()'
    expr_series = '//th[contains(text(),"カテゴリー")]/../td/ul/li/a/text()'
    expr_release = '//th[contains(text(),"販売開始日")]/../td/text()'
    expr_cover = '/html/body/div[1]/div/div[4]/div[2]/div/div[1]/div/article/a/img/@src'
    expr_tags = '//p[contains(text(),"商品タグ")]/../ul/li/a/text()'
    expr_outline = '//p[@class="fo-14"]/text()'
    expr_extrafanart = '//*[@class="item-nav"]/ul/li/a/img/@src'

    # expr_extrafanart2 = '//*[@id="cart_quantity"]/table/tr[3]/td/div/a/img/@src'

    def extraInit(self):
        self.imagecut = 4

    def search(self, number: str):
        self.number = number.upper().replace('PCOLLE-', '')
        self.detailurl = 'https://www.pcolle.com/product/detail/?product_id=' + self.number
        session = request_session(cookies=self.cookies, proxies=self.proxies, verify=self.verify)
        htmlcode = session.get(self.detailurl).text
        htmltree = etree.HTML(htmlcode)
        result = self.dictformat(htmltree)
        return result

    def getNum(self, htmltree):
        num = super().getNum(htmltree).upper()
        if self.number != num:
            raise Exception(f'[!] {self.number}: find [{num}] in pcolle, not match')
        return "PCOLLE-" + str(num)

    def getOutline(self, htmltree):
        result = self.getTreeAll(htmltree, self.expr_outline)
        try:
            return "\n".join(result)
        except:
            return ""

    def getRelease(self, htmltree):
        return super().getRelease(htmltree).replace('年', '-').replace('月', '-').replace('日', '')

    def getCover(self, htmltree):
        if ".gif" in super().getCover(htmltree) and len(super().getExtrafanart(htmltree)) != 0:
            return super().getExtrafanart(htmltree)[0]
        return super().getCover(htmltree)
