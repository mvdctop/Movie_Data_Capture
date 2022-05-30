# -*- coding: utf-8 -*-


from .parser import Parser


class Tmdb(Parser):
    """
    两种实现,带apikey与不带key
    apikey
    """
    source = 'tmdb'
    imagecut = 0
    apikey = None

    expr_title = './/head/meta[@property="og:title"]'
    expr_release = '//div/span[@class="release"]/text()'
    expr_cover = './/head/meta[@property="og:image"]'
    expr_outline = './/head/meta[@property="og:description"]'

    # def search(self, number):
    #     self.detailurl = self.queryNumberUrl(number)
    #     detailpage = self.getHtml(self.detailurl)

    def queryNumberUrl(self, number):
        """
        TODO 区分 ID 与 名称
        """
        id  = number
        movieUrl = "https://www.themoviedb.org/movie/" + id + "?language=zh-CN"
        return movieUrl

    def getTitle(self, htmltree):
        return self.getTreeIndex(htmltree, self.expr_title).get('content')

    def getCover(self, htmltree):
        return "https://www.themoviedb.org" + self.getTreeIndex(htmltree, self.expr_cover).get('content')

    def getOutline(self, htmltree):
        return self.getTreeIndex(htmltree, self.expr_outline).get('content')
