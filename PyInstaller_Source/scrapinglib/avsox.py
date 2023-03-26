# -*- coding: utf-8 -*-

from .parser import Parser


class Avsox(Parser):
    source = 'avsox'

    expr_number = '//span[contains(text(),"识别码:")]/../span[2]/text()'
    expr_actor = '//a[@class="avatar-box"]'
    expr_actorphoto = '//a[@class="avatar-box"]'
    expr_title = '/html/body/div[2]/h3/text()'
    expr_studio = '//p[contains(text(),"制作商: ")]/following-sibling::p[1]/a/text()'
    expr_release = '//span[contains(text(),"发行时间:")]/../text()'
    expr_cover = '/html/body/div[2]/div[1]/div[1]/a/img/@src'
    expr_smallcover = '//*[@id="waterfall"]/div/a/div[1]/img/@src'
    expr_tags = '/html/head/meta[@name="keywords"]/@content'
    expr_label = '//p[contains(text(),"系列:")]/following-sibling::p[1]/a/text()'
    expr_series = '//span[contains(text(),"系列:")]/../span[2]/text()'

    def extraInit(self):
        self.imagecut = 3
        self.originalnum = ''

    def queryNumberUrl(self, number: str):
        upnum = number.upper()
        if 'FC2' in upnum and 'FC2-PPV' not in upnum:
            number = upnum.replace('FC2', 'FC2-PPV')
            self.number = number
        qurySiteTree = self.getHtmlTree('https://tellme.pw/avsox')
        site = self.getTreeElement(qurySiteTree, '//div[@class="container"]/div/a/@href')
        self.searchtree = self.getHtmlTree(site + '/cn/search/' + number)
        result1 = self.getTreeElement(self.searchtree, '//*[@id="waterfall"]/div/a/@href')
        if result1 == '' or result1 == 'null' or result1 == 'None':
            self.searchtree = self.getHtmlTree(site + '/cn/search/' + number.replace('-', '_'))
            result1 = self.getTreeElement(self.searchtree, '//*[@id="waterfall"]/div/a/@href')
            if result1 == '' or result1 == 'null' or result1 == 'None':
                self.searchtree = self.getHtmlTree(site + '/cn/search/' + number.replace('_', ''))
                result1 = self.getTreeElement(self.searchtree, '//*[@id="waterfall"]/div/a/@href')
        return "https:" + result1

    def getNum(self, htmltree):
        new_number = self.getTreeElement(htmltree, self.expr_number)
        if new_number.upper() != self.number.upper():
            raise ValueError('number not found in ' + self.source)
        self.originalnum = new_number
        if 'FC2-PPV' in new_number.upper():
            new_number = new_number.upper().replace('FC2-PPV', 'FC2')
        self.number = new_number
        return self.number

    def getTitle(self, htmltree):
        return super().getTitle(htmltree).replace('/', '').strip(self.originalnum).strip()

    def getStudio(self, htmltree):
        return super().getStudio(htmltree).replace("', '", ' ')

    def getSmallCover(self, htmltree):
        """ 使用搜索页面的预览小图
        """
        try:
            return self.getTreeElement(self.searchtree, self.expr_smallcover)
        except:
            self.imagecut = 1
            return ''

    def getTags(self, htmltree):
        tags = self.getTreeElement(htmltree, self.expr_tags).split(',')
        return [i.strip() for i in tags[2:]] if len(tags) > 2 else []

    def getOutline(self, htmltree):
        if self.morestoryline:
            from .storyline import getStoryline
            return getStoryline(self.number, proxies=self.proxies, verify=self.verify)
        return ''

    def getActors(self, htmltree):
        a = super().getActors(htmltree)
        d = []
        for i in a:
            d.append(i.find('span').text)
        return d

    def getActorPhoto(self, htmltree):
        a = self.getTreeAll(htmltree, self.expr_actorphoto)
        d = {}
        for i in a:
            l = i.find('.//img').attrib['src']
            t = i.find('span').text
            p2 = {t: l}
            d.update(p2)
        return d
