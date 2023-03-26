# -*- coding: utf-8 -*-

from .parser import Parser


class Mgstage(Parser):
    source = 'mgstage'

    expr_number = '//th[contains(text(),"品番：")]/../td/a/text()'
    expr_title = '//*[@id="center_column"]/div[1]/h1/text()'
    expr_studio = '//th[contains(text(),"メーカー：")]/../td/a/text()'
    expr_outline = '//dl[@id="introduction"]/dd/p/text()'
    expr_runtime = '//th[contains(text(),"収録時間：")]/../td/a/text()'
    expr_director = '//th[contains(text(),"シリーズ")]/../td/a/text()'
    expr_actor = '//th[contains(text(),"出演：")]/../td/a/text()'
    expr_release = '//th[contains(text(),"配信開始日：")]/../td/a/text()'
    expr_cover = '//*[@id="EnlargeImage"]/@href'
    expr_label = '//th[contains(text(),"レーベル：")]/../td/a/text()'
    expr_tags = '//th[contains(text(),"ジャンル：")]/../td/a/text()'
    expr_tags2 = '//th[contains(text(),"ジャンル：")]/../td/text()'
    expr_series = '//th[contains(text(),"シリーズ")]/../td/a/text()'
    expr_extrafanart = '//a[@class="sample_image"]/@href'

    def search(self, number):
        self.number = number.upper()
        self.cookies = {'adc':'1'}
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
        else:
            self.detailurl = 'https://www.mgstage.com/product/product_detail/'+str(self.number)+'/'
        htmltree =self.getHtmlTree(self.detailurl)
        result = self.dictformat(htmltree)
        return result

    def getTitle(self, htmltree):
        return super().getTitle(htmltree).replace('/', ',').strip()

    def getTags(self, htmltree):
        return self.getTreeAllbyExprs(htmltree, self.expr_tags, self.expr_tags2)

    def getTreeAll(self, tree, expr):
        alls = super().getTreeAll(tree, expr)
        return [ x.strip() for x in alls if x.strip()]

    def getTreeElement(self, tree, expr, index=0):
        if expr == '':
            return ''
        result1 = ''.join(self.getTreeAll(tree, expr))
        result2 = ''.join(self.getTreeAll(tree, expr.replace('td/a/','td/')))
        if result1 == result2:
            return result1
        return result1 + result2
