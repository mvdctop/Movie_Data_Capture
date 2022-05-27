# -*- coding: utf-8 -*-

import re
import secrets
from urllib.parse import urljoin
from lxml import etree
from .httprequest import get_html_by_form
from .parser import Parser


class Xcity(Parser):
    source = 'xcity'

    expr_number = '//*[@id="hinban"]/text()'
    expr_title = '//*[@id="program_detail_title"]/text()'
    expr_studio = '//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[4]/a/span/text()'
    expr_studio2 = '//strong[contains(text(),"片商")]/../following-sibling::span/a/text()'
    expr_runtime = '//span[@class="koumoku" and text()="収録時間"]/../text()'
    expr_label = '//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[5]/a/span/text()'
    expr_release = '//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[2]/text()'
    expr_tags = '//span[@class="koumoku" and text()="ジャンル"]/../a[starts-with(@href,"/avod/genre/")]/text()'
    expr_cover = '//*[@id="avodDetails"]/div/div[3]/div[1]/p/a/@href'
    expr_director = '//*[@id="program_detail_director"]/text()'
    expr_series = "//span[contains(text(),'シリーズ')]/../a/span/text()"
    expr_series2 = "//span[contains(text(),'シリーズ')]/../span/text()"

    def getStudio(self, htmltree):
        return super().getStudio(htmltree).strip('+').replace("', '", '').replace('"', '')

    def getRuntime(self, htmltree):
        return self.getAll(htmltree, self.expr_runtime)[1].strip()

    def getRelease(self, htmltree):
        try:
            result = self.getTreeIndex(htmltree, self.expr_release, 1)
            return re.findall('\d{4}/\d{2}/\d{2}', result)[0].replace('/','-')
        except:
            return ''

    def getTags(self, htmltree):
        result = self.getAll(htmltree, self.expr_tags)
        total = []
        for i in result:
            total.append(i.replace("\n","").replace("\t",""))
        return total

    def getCover(self, htmltree):
        try:
            result = super().getCover(htmltree)
            return 'https:' + result
        except:
            return ''
    
    def getDirector(self, htmltree):
        try:
            result = super().getDirector(htmltree).replace(u'\n','').replace(u'\t', '')
            return result
        except:
            return ''

    def getOutline(self, htmltree):
        if self.morestoryline:
            from .storyline import getStoryline
            return getStoryline(self.number, uncensored=False)
        return ''

    def getActors(self, htmltree):
        htmla = self.browser.page.select('#avodDetails > div > div.frame > div.content > div > ul.profileCL > li.credit-links > a')
        t = []
        for i in htmla:
            t.append(i.text.strip())
        return t

    def getActorPhoto(self, htmltree):
        htmla = self.browser.page.select('#avodDetails > div > div.frame > div.content > div > ul.profileCL > li.credit-links > a')
        t = {i.text.strip(): i['href'] for i in htmla}
        o = {}
        for k, v in t.items():
            r = self.browser.open_relative(v)
            if not r.ok:
                continue
            pic = self.browser.page.select_one('#avidolDetails > div > div.frame > div > p > img')
            if 'noimage.gif' in pic['src']:
                continue
            o[k] = urljoin(self.browser.url, pic['src'])
        return o

    def getExtrafanart(self, htmltree):
        html_pather = re.compile(r'<div id="sample_images".*?>[\s\S]*?</div>')
        html = html_pather.search(self.detail_page)
        if html:
            html = html.group()
            extrafanart_pather = re.compile(r'<a.*?href=\"(.*?)\"')
            extrafanart_imgs = extrafanart_pather.findall(html)
            if extrafanart_imgs:
                s = []
                for urli in extrafanart_imgs:
                    urli = 'https:' + urli.replace('/scene/small', '')
                    s.append(urli)
                return s
        return ''

    def open_by_browser(self, number):
        xcity_number = number.replace('-','')
        query_result, browser = get_html_by_form(
            'https://xcity.jp/' + secrets.choice(['about/','sitemap/','policy/','law/','help/','main/']),
            fields = {'q' : xcity_number.lower()},
            return_type = 'browser')
        if not query_result or not query_result.ok:
            raise ValueError("xcity.py: page not found")
        result = browser.follow_link(browser.links('avod\/detail')[0])
        if not result.ok:
            raise ValueError("xcity.py: detail page not found")
        return str(browser.page), browser

    def search(self, number):
        self.number = number
        self.detail_page, self.browser = self.open_by_browser(number)
        self.detailurl = self.browser.url
        lx = etree.fromstring(self.detail_page, etree.HTMLParser())
        result = self.dictformat(lx)
        return result
