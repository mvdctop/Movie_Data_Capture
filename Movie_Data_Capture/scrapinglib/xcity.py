# -*- coding: utf-8 -*-

import re
import secrets
from urllib.parse import urljoin
from .httprequest import get_html_by_form
from .parser import Parser


class Xcity(Parser):
    source = 'xcity'

    expr_number = '//*[@id="hinban"]/text()'
    expr_title = '//*[@id="program_detail_title"]/text()'
    expr_actor = '//ul/li[@class="credit-links"]/a/text()'
    expr_actor_link = '//ul/li[@class="credit-links"]/a'
    expr_actorphoto = '//div[@class="frame"]/div/p/img/@src'
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
    expr_extrafanart = '//div[@id="sample_images"]/div/a/@href'
    expr_outline = '//head/meta[@property="og:description"]/@content'

    def queryNumberUrl(self, number):
        xcity_number = number.replace('-','')
        query_result, browser = get_html_by_form(
            'https://xcity.jp/' + secrets.choice(['sitemap/','policy/','law/','help/','main/']),
            fields = {'q' : xcity_number.lower()},
            cookies=self.cookies, proxies=self.proxies, verify=self.verify,
            return_type = 'browser')
        if not query_result or not query_result.ok:
            raise ValueError("xcity.py: page not found")
        prelink = browser.links('avod\/detail')[0]['href']
        return urljoin('https://xcity.jp', prelink)

    def getStudio(self, htmltree):
        return super().getStudio(htmltree).strip('+').replace("', '", '').replace('"', '')

    def getRuntime(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_runtime, 1).strip()

    def getRelease(self, htmltree):
        try:
            result = self.getTreeElement(htmltree, self.expr_release, 1)
            return re.findall('\d{4}/\d{2}/\d{2}', result)[0].replace('/','-')
        except:
            return ''

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

    def getActorPhoto(self, htmltree):
        treea = self.getTreeAll(htmltree, self.expr_actor_link)
        t = {i.text.strip(): i.attrib['href'] for i in treea}
        o = {}
        for k, v in t.items():
            actorpageUrl = "https://xcity.jp" + v
            try:
                adtree = self.getHtmlTree(actorpageUrl)
                picUrl = self.getTreeElement(adtree, self.expr_actorphoto)
                if 'noimage.gif' in picUrl:
                    continue
                o[k] = urljoin("https://xcity.jp", picUrl)
            except:
                pass
        return o

    def getExtrafanart(self, htmltree):
        arts = self.getTreeAll(htmltree, self.expr_extrafanart)
        extrafanart = []
        for i in arts:
            i = "https:" + i
            extrafanart.append(i)
        return extrafanart
