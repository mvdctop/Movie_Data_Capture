# -*- coding: utf-8 -*-

import re
import json
from urllib.parse import quote
from .parser import Parser


class Getchu():
    source = 'getchu'

    def scrape(self, number, core: None):
        dl = dlGetchu()
        www = wwwGetchu()
        number = number.replace("-C", "")
        dic = {}
        if "item" in number:
            sort = ["dl.scrape(number, core)", "www.scrape(number, core)"]
        else:
            sort = ["www.scrape(number, core)", "dl.scrape(number, core)"]
        for i in sort:
            try:
                dic = eval(i)
                if dic != None and json.loads(dic).get('title') != '':
                    break
            except:
                pass
        return dic

class wwwGetchu(Parser):
    imagecut = 0
    allow_number_change = True

    cookies = {'getchu_adalt_flag': 'getchu.com', "adult_check_flag": "1"}
    GETCHU_WWW_SEARCH_URL = 'http://www.getchu.com/php/search.phtml?genre=anime_dvd&search_keyword=_WORD_&check_key_dtl=1&submit='

    expr_title = '//*[@id="soft-title"]/text()'
    expr_cover = "/html/body/div[1]/table[2]/tr[1]/td/a/@href"
    expr_director = "//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"
    expr_studio = "//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"
    expr_actor = "//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"
    expr_label = "//td[contains(text(),'ジャンル：')]/following-sibling::td/text()"
    expr_release = "//td[contains(text(),'発売日：')]/following-sibling::td/a/text()"
    expr_tags = "//td[contains(text(),'カテゴリ')]/following-sibling::td/a/text()"
    expr_outline = "//div[contains(text(),'商品紹介')]/following-sibling::div/text()"
    expr_extrafanart = "//div[contains(text(),'サンプル画像')]/following-sibling::div/a/@href"
    expr_series = "//td[contains(text(),'ジャンル：')]/following-sibling::td/text()"

    def queryNumberUrl(self, number):
        self.number = quote(number, encoding="euc_jp")
        queryUrl = self.GETCHU_WWW_SEARCH_URL.replace("_WORD_", self.number)
        # NOTE dont know why will try 2 times
        retry = 2
        for i in range(retry):
            queryTree = self.getHtmlTree(queryUrl)
            detailurl = self.getTreeIndex(queryTree, '//*[@id="detail_block"]/div/table/tr[1]/td/a[1]/@href')
            if detailurl:
                break
        if detailurl == "":
            return None
        return detailurl.replace('../', 'http://www.getchu.com/')

    def getNum(self, htmltree):
        return 'GETCHU-' + re.findall('\d+', self.detailurl.replace("http://www.getchu.com/soft.phtml?id=", ""))[0]

    def getCover(self, htmltree):
        return "http://www.getchu.com" + super().getCover(htmltree).replace("./", '/')

    def getActors(self, htmltree):
        return super().getDirector(htmltree)

    def getTags(self, htmltree):
        return self.getAll(htmltree, self.expr_tags)
    
    def getOutline(self, htmltree):
        outline = ''
        _list = self.getAll(htmltree, self.expr_outline)
        for i in _list:
            outline = outline + i.strip()
        return outline

    def getExtrafanart(self, htmltree):
        arts = super().getExtrafanart(htmltree)
        extrafanart = []
        for i in arts:
            i = "http://www.getchu.com" + i.replace("./", '/')
            if 'jpg' in i:
                extrafanart.append(i)
        return extrafanart

class dlGetchu(wwwGetchu):
    imagecut = 4
    allow_number_change = True

    cookies = {"adult_check_flag": "1"}
    extraheader = {"Referer": "https://dl.getchu.com/"}

    GETCHU_DL_SEARCH_URL = 'https://dl.getchu.com/search/search_list.php?dojin=1&search_category_id=&search_keyword=_WORD_&btnWordSearch=%B8%A1%BA%F7&action=search&set_category_flag=1'
    GETCHU_DL_URL = 'https://dl.getchu.com/i/item_WORD_'

    expr_title = "//div[contains(@style,'color: #333333; padding: 3px 0px 0px 5px;')]/text()"
    expr_cover = "//td[contains(@bgcolor,'#ffffff')]/img/@src"
    expr_director = "//td[contains(text(),'作者')]/following-sibling::td/text()"
    expr_studio = "//td[contains(text(),'サークル')]/following-sibling::td/a/text()"
    expr_label = "//td[contains(text(),'サークル')]/following-sibling::td/a/text()"
    expr_runtime = "//td[contains(text(),'画像数&ページ数')]/following-sibling::td/text()"
    expr_release = "//td[contains(text(),'配信開始日')]/following-sibling::td/text()"
    expr_tags = "//td[contains(text(),'趣向')]/following-sibling::td/a/text()"
    expr_outline = "//*[contains(text(),'作品内容')]/following-sibling::td/text()"
    expr_extrafanart = "//td[contains(@style,'background-color: #444444;')]/a/@href"
    expr_series = "//td[contains(text(),'サークル')]/following-sibling::td/a/text()"

    def queryNumberUrl(self, number):
        if "item" in number or 'GETCHU' in number.upper():
            self.number = re.findall('\d+',number)[0]
        else:
            queryUrl = self.GETCHU_DL_SEARCH_URL.replace("_WORD_", number)
            queryTree = self.getHtmlTree(queryUrl)
            detailurl = self.getTreeIndex(queryTree, '/html/body/div[1]/table/tr/td/table[4]/tr/td[2]/table/tr[2]/td/table/tr/td/table/tr/td[2]/div/a[1]/@href')
            if detailurl == "":
                return None
            self.number = re.findall('\d+', detailurl)[0]
        return self.GETCHU_DL_URL.replace("_WORD_", self.number)    

    def getNum(self, htmltree):
        return 'GETCHU-' + re.findall('\d+', self.number)[0]

    def getCover(self, htmltree):
        return "https://dl.getchu.com" + super().getCover(htmltree)
