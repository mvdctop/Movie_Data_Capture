# -*- coding: utf-8 -*-

import re
from urllib.parse import urljoin
from lxml import html
from .parser import Parser


class Caribpr(Parser):
    source = 'caribpr'

    expr_title = "//div[@class='movie-info']/div[@class='section is-wide']/div[@class='heading']/h1/text()"
    expr_release = "//li[2]/span[@class='spec-content']/text()"
    expr_runtime = "//li[3]/span[@class='spec-content']/text()"
    expr_actor = "//li[1]/span[@class='spec-content']/a[@class='spec-item']/text()"
    expr_tags = "//li[5]/span[@class='spec-content']/a[@class='spec-item']/text()"
    expr_extrafanart = "//div[@class='movie-gallery']/div[@class='section is-wide']/div[2]/div[@class='grid-item']/div/a/@href"
    # expr_label = "//span[@class='spec-title'][contains(text(),'シリーズ')]/../span[@class='spec-content']/a/text()"
    # expr_series = "//span[@class='spec-title'][contains(text(),'シリーズ')]/../span[@class='spec-content']/a/text()"
    expr_outline = "//div[@class='movie-info']/div[@class='section is-wide']/p/text()"

    def extraInit(self):
        self.imagecut = 1
        self.uncensored = True

    def search(self, number):
        self.number = number
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
        else:
            self.detailurl = f'https://www.caribbeancompr.com/moviepages/{number}/index.html'
        htmlcode = self.getHtml(self.detailurl)
        if htmlcode == 404 or 'class="movie-info"' not in htmlcode:
            return 404
        htmltree = html.fromstring(htmlcode)
        result = self.dictformat(htmltree)
        return result

    def getStudio(self, htmltree):
        return '加勒比'

    def getActors(self, htmltree):
        r = []
        actors = super().getActors(htmltree)
        for act in actors:
            if str(act) != '他':
                r.append(act)
        return r

    def getNum(self, htmltree):
        return self.number

    def getCover(self, htmltree):
        return f'https://www.caribbeancompr.com/moviepages/{self.number}/images/l_l.jpg'

    def getExtrafanart(self, htmltree):
        r = []
        genres = self.getTreeAll(htmltree, self.expr_extrafanart)
        for g in genres:
            jpg = str(g)
            if '/member/' in jpg:
                break
            else:
                r.append(jpg)
        return r

    def getTrailer(self, htmltree):
        return f'https://smovie.caribbeancompr.com/sample/movies/{self.number}/480p.mp4'

    def getActorPhoto(self, htmltree):
        htmla = htmltree.xpath("//*[@id='moviepages']/div[@class='container']/div[@class='inner-container']/div[@class='movie-info section']/ul/li[@class='movie-spec']/span[@class='spec-content']/a[@itemprop='actor']")
        names = htmltree.xpath("//*[@id='moviepages']/div[@class='container']/div[@class='inner-container']/div[@class='movie-info section']/ul/li[@class='movie-spec']/span[@class='spec-content']/a[@itemprop='actor']/span[@itemprop='name']/text()")
        t = {}
        for name, a in zip(names, htmla):
            if name.strip() == '他':
                continue
            p = {name.strip(): a.attrib['href']}
            t.update(p)
        o = {}
        for k, v in t.items():
            if '/search_act/' not in v:
                continue
            r = self.getHtml(urljoin('https://www.caribbeancompr.com', v), type='object')
            if not r.ok:
                continue
            html = r.text
            pos = html.find('.full-bg')
            if pos<0:
                continue
            css = html[pos:pos+100]
            cssBGjpgs = re.findall(r'background: url\((.+\.jpg)', css, re.I)
            if not cssBGjpgs or not len(cssBGjpgs[0]):
                continue
            p = {k: urljoin(r.url, cssBGjpgs[0])}
            o.update(p)
        return o

    def getOutline(self, htmltree):
        if self.morestoryline:
            from .storyline import getStoryline
            result = getStoryline(self.number, uncensored=self.uncensored,
                                  proxies=self.proxies, verify=self.verify)
            if len(result):
                return result
        return super().getOutline(htmltree)

