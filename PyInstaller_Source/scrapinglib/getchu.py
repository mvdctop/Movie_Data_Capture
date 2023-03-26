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
    expr_title = '//*[@id="soft-title"]/text()'
    expr_cover = '//head/meta[@property="og:image"]/@content'
    expr_director = "//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"
    expr_studio = "//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"
    expr_actor = "//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"
    expr_label = "//td[contains(text(),'ジャンル：')]/following-sibling::td/text()"
    expr_release = "//td[contains(text(),'発売日：')]/following-sibling::td/a/text()"
    expr_tags = "//td[contains(text(),'カテゴリ')]/following-sibling::td/a/text()"
    expr_outline = "//div[contains(text(),'商品紹介')]/following-sibling::div/text()"
    expr_extrafanart = "//div[contains(text(),'サンプル画像')]/following-sibling::div/a/@href"
    expr_series = "//td[contains(text(),'ジャンル：')]/following-sibling::td/text()"

    def extraInit(self):
        self.imagecut = 0
        self.allow_number_change = True

        self.cookies = {'getchu_adalt_flag': 'getchu.com', "adult_check_flag": "1"}
        self.GETCHU_WWW_SEARCH_URL = 'http://www.getchu.com/php/search.phtml?genre=anime_dvd&search_keyword=_WORD_&check_key_dtl=1&submit='

    def queryNumberUrl(self, number):
        if 'GETCHU' in number.upper():
            idn = re.findall('\d+',number)[0]
            return "http://www.getchu.com/soft.phtml?id=" + idn
        else:
            queryUrl = self.GETCHU_WWW_SEARCH_URL.replace("_WORD_", quote(number, encoding="euc_jp"))
        # NOTE dont know why will try 2 times
        retry = 2
        for i in range(retry):
            queryTree = self.getHtmlTree(queryUrl)
            detailurl = self.getTreeElement(queryTree, '//*[@id="detail_block"]/div/table/tr[1]/td/a[1]/@href')
            if detailurl:
                break
        if detailurl == "":
            return None
        return detailurl.replace('../', 'http://www.getchu.com/')

    def getNum(self, htmltree):
        return 'GETCHU-' + re.findall('\d+', self.detailurl.replace("http://www.getchu.com/soft.phtml?id=", ""))[0]

    def getActors(self, htmltree):
        return super().getDirector(htmltree)

    def getOutline(self, htmltree):
        outline = ''
        _list = self.getTreeAll(htmltree, self.expr_outline)
        for i in _list:
            outline = outline + i.strip()
        return outline

    def getCover(self, htmltree):
        url = super().getCover(htmltree)
        if "getchu.com" in url:
            return url
        return "http://www.getchu.com" + url

    def getExtrafanart(self, htmltree):
        arts = super().getExtrafanart(htmltree)
        extrafanart = []
        for i in arts:
            i = "http://www.getchu.com" + i.replace("./", '/')
            if 'jpg' in i:
                extrafanart.append(i)
        return extrafanart

    def extradict(self, dic: dict):
        """ 额外新增的  headers
        """
        dic['headers'] =  {'referer': self.detailurl}
        return dic

class dlGetchu(wwwGetchu):
    """ 二者基本一致
    headers extrafanart 略有区别
    """
    expr_title = "//div[contains(@style,'color: #333333; padding: 3px 0px 0px 5px;')]/text()"
    expr_director = "//td[contains(text(),'作者')]/following-sibling::td/text()"
    expr_studio = "//td[contains(text(),'サークル')]/following-sibling::td/a/text()"
    expr_label = "//td[contains(text(),'サークル')]/following-sibling::td/a/text()"
    expr_runtime = "//td[contains(text(),'画像数&ページ数')]/following-sibling::td/text()"
    expr_release = "//td[contains(text(),'配信開始日')]/following-sibling::td/text()"
    expr_tags = "//td[contains(text(),'趣向')]/following-sibling::td/a/text()"
    expr_outline = "//*[contains(text(),'作品内容')]/following-sibling::td/text()"
    expr_extrafanart = "//td[contains(@style,'background-color: #444444;')]/a/@href"
    expr_series = "//td[contains(text(),'サークル')]/following-sibling::td/a/text()"

    def extraInit(self):
        self.imagecut = 4
        self.allow_number_change = True

        self.cookies = {"adult_check_flag": "1"}
        self.extraheader = {"Referer": "https://dl.getchu.com/"}

        self.GETCHU_DL_SEARCH_URL = 'https://dl.getchu.com/search/search_list.php?dojin=1&search_category_id=&search_keyword=_WORD_&btnWordSearch=%B8%A1%BA%F7&action=search&set_category_flag=1'
        self.GETCHU_DL_URL = 'https://dl.getchu.com/i/item_WORD_'

    def queryNumberUrl(self, number):
        if "item" in number or 'GETCHU' in number.upper():
            self.number = re.findall('\d+',number)[0]
        else:
            queryUrl = self.GETCHU_DL_SEARCH_URL.replace("_WORD_", quote(number, encoding="euc_jp"))
            queryTree = self.getHtmlTree(queryUrl)
            detailurl = self.getTreeElement(queryTree, '/html/body/div[1]/table/tr/td/table[4]/tr/td[2]/table/tr[2]/td/table/tr/td/table/tr/td[2]/div/a[1]/@href')
            if detailurl == "":
                return None
            self.number = re.findall('\d+', detailurl)[0]
        return self.GETCHU_DL_URL.replace("_WORD_", self.number)    

    def getNum(self, htmltree):
        return 'GETCHU-' + re.findall('\d+', self.number)[0]

    def extradict(self, dic: dict):
        return dic
    
    def getExtrafanart(self, htmltree):
        arts = self.getTreeAll(htmltree, self.expr_extrafanart)
        extrafanart = []
        for i in arts:
            i = "https://dl.getchu.com" + i
            extrafanart.append(i)
        return extrafanart
