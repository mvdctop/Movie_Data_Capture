# -*- coding: utf-8 -*-

import re
from lxml import etree
from urllib.parse import urlencode
from .parser import Parser


class Fanza(Parser):
    source = 'fanza'

    expr_title = '//*[starts-with(@id, "title")]/text()'
    expr_actor = "//td[contains(text(),'出演者')]/following-sibling::td/span/a/text()"
    # expr_cover = './/head/meta[@property="og:image"]/@content'
    # expr_extrafanart = '//a[@name="sample-image"]/img/@src'
    expr_outline = "//div[@class='mg-b20 lh4']/text()"
    expr_outline2 = "//div[@class='mg-b20 lh4']//p/text()"
    expr_outline_og = '//head/meta[@property="og:description"]/@content'
    expr_runtime = "//td[contains(text(),'収録時間')]/following-sibling::td/text()"

    def search(self, number):
        self.number = number
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
            durl = "https://www.dmm.co.jp/age_check/=/declared=yes/?"+ urlencode({"rurl": self.detailurl})
            self.htmltree = self.getHtmlTree(durl)
            result = self.dictformat(self.htmltree)
            return result
        # fanza allow letter + number + underscore, normalize the input here
        # @note: I only find the usage of underscore as h_test123456789
        fanza_search_number = number
        # AV_Data_Capture.py.getNumber() over format the input, restore the h_ prefix
        if fanza_search_number.startswith("h-"):
            fanza_search_number = fanza_search_number.replace("h-", "h_")

        fanza_search_number = re.sub(r"[^0-9a-zA-Z_]", "", fanza_search_number).lower()

        fanza_urls = [
            "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=",
            "https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=",
            "https://www.dmm.co.jp/digital/anime/-/detail/=/cid=",
            "https://www.dmm.co.jp/mono/anime/-/detail/=/cid=",
            "https://www.dmm.co.jp/digital/videoc/-/detail/=/cid=",
            "https://www.dmm.co.jp/digital/nikkatsu/-/detail/=/cid=",
            "https://www.dmm.co.jp/rental/-/detail/=/cid=",
        ]

        for url in fanza_urls:
            self.detailurl = url + fanza_search_number
            url = "https://www.dmm.co.jp/age_check/=/declared=yes/?"+ urlencode({"rurl": self.detailurl})
            self.htmlcode = self.getHtml(url)
            if self.htmlcode != 404:
                self.htmltree = etree.HTML(self.htmlcode)
                break
        if self.htmlcode == 404:
            return 404
        result = self.dictformat(self.htmltree)
        return result

    def getNum(self, htmltree):
        # for some old page, the input number does not match the page
        # for example, the url will be cid=test012
        # but the hinban on the page is test00012
        # so get the hinban first, and then pass it to following functions
        self.fanza_hinban = self.getFanzaString('品番：')
        self.number = self.fanza_hinban
        number_lo = self.number.lower()
        if (re.sub('-|_', '', number_lo) == self.fanza_hinban or
            number_lo.replace('-', '00') == self.fanza_hinban or
            number_lo.replace('-', '') + 'so' == self.fanza_hinban
        ):
            self.number = self.number
        return self.number

    def getStudio(self, htmltree):
        return self.getFanzaString('メーカー')

    def getOutline(self, htmltree):
        try:
            result = self.getTreeElement(htmltree, self.expr_outline).replace("\n", "")
            if result == '':
                result = self.getTreeElement(htmltree, self.expr_outline2).replace("\n", "")
            if "※ 配信方法によって収録内容が異なる場合があります。" == result:
                result = self.getTreeElement(htmltree, self.expr_outline_og)
            return result
        except:
            return ''

    def getRuntime(self, htmltree):
        return str(re.search(r'\d+', super().getRuntime(htmltree)).group()).strip(" ['']")

    def getDirector(self, htmltree):
        if "anime" not in self.detailurl:
            return self.getFanzaString('監督：')
        return ''

    def getActors(self, htmltree):
        if "anime" not in self.detailurl:
            return super().getActors(htmltree)
        return ''

    def getRelease(self, htmltree):
        result = self.getFanzaString('発売日：')
        if result == '' or result == '----':
            result = self.getFanzaString('配信開始日：')
        return result.replace("/", "-").strip('\\n')

    def getTags(self, htmltree):
        return self.getFanzaStrings('ジャンル：')

    def getLabel(self, htmltree):
        ret = self.getFanzaString('レーベル')
        if ret == "----":
            return ''
        return ret

    def getSeries(self, htmltree):
        ret = self.getFanzaString('シリーズ：')
        if ret == "----":
            return ''
        return ret
    
    def getCover(self, htmltree):
        cover_number = self.number
        try:
            result = htmltree.xpath('//*[@id="' + cover_number + '"]/@href')[0]
        except:
            # sometimes fanza modify _ to \u0005f for image id
            if "_" in cover_number:
                cover_number = cover_number.replace("_", r"\u005f")
            try:
                result = htmltree.xpath('//*[@id="' + cover_number + '"]/@href')[0]
            except:
                # (TODO) handle more edge case
                # print(html)
                # raise exception here, same behavior as before
                # people's major requirement is fetching the picture
                raise ValueError("can not find image")
        return result

    def getExtrafanart(self, htmltree):
        htmltext = re.search(r'<div id=\"sample-image-block\"[\s\S]*?<br></div>\s*?</div>', self.htmlcode)
        if htmltext:
            htmltext = htmltext.group()
            extrafanart_images = re.findall(r'<img.*?src=\"(.*?)\"', htmltext)
            if extrafanart_images:
                sheet = []
                for img_url in extrafanart_images:
                    url_cuts = img_url.rsplit('-', 1)
                    sheet.append(url_cuts[0] + 'jp-' + url_cuts[1])
                return sheet
        return ''

    def getTrailer(self, htmltree):
        htmltext = re.search(r'<script type=\"application/ld\+json\">[\s\S].*}\s*?</script>', self.htmlcode)
        if htmltext:
            htmltext = htmltext.group()
            url = re.search(r'\"contentUrl\":\"(.*?)\"', htmltext)
            if url:
                url = url.group(1)
                url = url.rsplit('_', 2)[0] + '_mhb_w.mp4'
                return url
        return ''

    def getFanzaString(self, expr):
        result1 = str(self.htmltree.xpath("//td[contains(text(),'"+expr+"')]/following-sibling::td/a/text()")).strip(" ['']")
        result2 = str(self.htmltree.xpath("//td[contains(text(),'"+expr+"')]/following-sibling::td/text()")).strip(" ['']")
        return result1+result2

    def getFanzaStrings(self, string):
        result1 = self.htmltree.xpath("//td[contains(text(),'" + string + "')]/following-sibling::td/a/text()")
        if len(result1) > 0:
            return result1
        result2 = self.htmltree.xpath("//td[contains(text(),'" + string + "')]/following-sibling::td/text()")
        return result2
