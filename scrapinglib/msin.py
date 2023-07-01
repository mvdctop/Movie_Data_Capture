# -*- coding: utf-8 -*-

import re
from lxml import etree
from .httprequest import request_session
from .parser import Parser


class Msin(Parser):
    source = 'msin'

    expr_number = '//div[@class="mv_fileName"]/text()'
    expr_title = '//div[@class="mv_title"]/text()'
    expr_title_unsubscribe = '//div[@class="mv_title unsubscribe"]/text()'
    expr_studio = '//a[@class="mv_writer"]/text()'
    expr_director = '//a[@class="mv_writer"]/text()'
    expr_actor = '//div[contains(text(),"出演者：")]/following-sibling::div[1]/div/div[@class="performer_text"]/a/text()'
    expr_label = '//a[@class="mv_mfr"]/text()'
    expr_series = '//a[@class="mv_mfr"]/text()'
    expr_release = '//a[@class="mv_createDate"]/text()'
    expr_cover = '//div[@class="movie_top"]/img/@src'
    expr_tags = '//div[@class="mv_tag"]/label/text()'
    expr_genres = '//div[@class="mv_genre"]/label/text()'

    # expr_outline = '//p[@class="fo-14"]/text()'
    # expr_extrafanart = '//*[@class="item-nav"]/ul/li/a/img/@src'
    # expr_extrafanart2 = '//*[@id="cart_quantity"]/table/tr[3]/td/div/a/img/@src'

    def extraInit(self):
        self.imagecut = 4

    def search(self, number: str):
        self.number = number.lower().replace('fc2-ppv-', '').replace('fc2-', '')
        self.cookies = {"age": "off"}
        self.detailurl = 'https://db.msin.jp/search/movie?str=fc2-ppv-' + self.number
        session = request_session(cookies=self.cookies, proxies=self.proxies, verify=self.verify)
        htmlcode = session.get(self.detailurl).text
        htmltree = etree.HTML(htmlcode)
        # if title are null, use unsubscribe title
        if super().getTitle(htmltree) == "":
            self.expr_title = self.expr_title_unsubscribe
        # if tags are null, use genres
        if len(super().getTags(htmltree)) == 0:
            self.expr_tags = self.expr_genres
        if len(super().getActors(htmltree)) == 0:
            self.expr_actor = self.expr_director
        result = self.dictformat(htmltree)
        return result

    def getActors(self, htmltree):
        actors = super().getActors(htmltree)
        i = 0
        while i < len(actors):
            actors[i] = actors[i].replace("（FC2動画）", "")
            i = i + 1
        return actors

    def getTags(self, htmltree) -> list:
        return super().getTags(htmltree)

    def getRelease(self, htmltree):
        return super().getRelease(htmltree).replace('年', '-').replace('月', '-').replace('日', '')

    def getCover(self, htmltree):
        if ".gif" in super().getCover(htmltree) and len(super().getExtrafanart(htmltree)) != 0:
            return super().getExtrafanart(htmltree)[0]
        return super().getCover(htmltree)

    def getNum(self, htmltree):
        return 'FC2-' + self.number
