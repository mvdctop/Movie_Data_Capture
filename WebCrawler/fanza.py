#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
from urllib.parse import urlencode

from ADC_function import *
from WebCrawler.crawler import *

class fanzaCrawler(Crawler):
    def getFanzaString(self,string):
        result1 = str(self.html.xpath("//td[contains(text(),'"+string+"')]/following-sibling::td/a/text()")).strip(" ['']")
        result2 = str(self.html.xpath("//td[contains(text(),'"+string+"')]/following-sibling::td/text()")).strip(" ['']")
        return result1+result2

    def getFanzaStrings(self, string):
        result1 = self.html.xpath("//td[contains(text(),'" + string + "')]/following-sibling::td/a/text()")
        if len(result1) > 0:
            return result1
        result2 = self.html.xpath("//td[contains(text(),'" + string + "')]/following-sibling::td/text()")
        return result2


def getRelease(fanza_Crawler):
    result = fanza_Crawler.getFanzaString('発売日：')
    if result == '' or result == '----':
        result = fanza_Crawler.getFanzaString('配信開始日：')
    return result.replace("/", "-").strip('\\n')


def getCover(html, number):
    cover_number = number
    try:
        result = html.xpath('//*[@id="' + cover_number + '"]/@href')[0]
    except:
        # sometimes fanza modify _ to \u0005f for image id
        if "_" in cover_number:
            cover_number = cover_number.replace("_", r"\u005f")
        try:
            result = html.xpath('//*[@id="' + cover_number + '"]/@href')[0]
        except:
            # (TODO) handle more edge case
            # print(html)
            # raise exception here, same behavior as before
            # people's major requirement is fetching the picture
            raise ValueError("can not find image")
    return result


def getOutline(html):
    try:
        result = str(html.xpath("//div[@class='mg-b20 lh4']/text()")[0]).replace("\n", "")
        if result == "":
            result = str(html.xpath("//div[@class='mg-b20 lh4']//p/text()")[0]).replace("\n", "")
    except:
        # (TODO) handle more edge case
        # print(html)
        return ""
    return result


def getExtrafanart(htmlcode):  # 获取剧照
    html_pather = re.compile(r'<div id=\"sample-image-block\"[\s\S]*?<br></div>\n</div>')
    html = html_pather.search(htmlcode)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<img.*?src=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            s = []
            for img_url in extrafanart_imgs:
                img_urls = img_url.rsplit('-', 1)
                img_url = img_urls[0] + 'jp-' + img_urls[1]
                s.append(img_url)
            return s
    return ''

def main(number):
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
    chosen_url = ""
    fanza_Crawler = ''

    for url in fanza_urls:
        chosen_url = url + fanza_search_number
        htmlcode = get_html(
            "https://www.dmm.co.jp/age_check/=/declared=yes/?{}".format(
                urlencode({"rurl": chosen_url})
            )
        )
        fanza_Crawler = fanzaCrawler(htmlcode)
        if "404 Not Found" not in htmlcode:
            break
    if "404 Not Found" in htmlcode:
        return json.dumps({"title": "",})
    try:
        # for some old page, the input number does not match the page
        # for example, the url will be cid=test012
        # but the hinban on the page is test00012
        # so get the hinban first, and then pass it to following functions
        fanza_hinban = fanza_Crawler.getFanzaString('品番：')
        out_num = fanza_hinban
        number_lo = number.lower()
        html = etree.fromstring(htmlcode, etree.HTMLParser())
        if (re.sub('-|_', '', number_lo) == fanza_hinban or
            number_lo.replace('-', '00') == fanza_hinban or
            number_lo.replace('-', '') + 'so' == fanza_hinban
        ):
            out_num = number

        director = fanza_Crawler.getFanzaString('監督：')
        if "anime" in chosen_url:
            director = ""
        actor = fanza_Crawler.getStrings("//td[contains(text(),'出演者')]/following-sibling::td/span/a/text()")
        if "anime" in chosen_url:
            actor = ""
        # 	----
        series = fanza_Crawler.getFanzaString('シリーズ：')
        if series == "----":
            series = ""
        label = fanza_Crawler.getFanzaString('レーベル')
        if label == "----":
            label = ""

        data = {
            "title": fanza_Crawler.getString('//*[starts-with(@id, "title")]/text()').strip(),
            "studio": fanza_Crawler.getFanzaString('メーカー'),
            "outline": getOutline(html),
            "runtime": str(re.search(r'\d+',fanza_Crawler.getString("//td[contains(text(),'収録時間')]/following-sibling::td/text()")).group()).strip(" ['']"),
            "director": director,
            "actor": actor,
            "release": getRelease(fanza_Crawler),
            "number": out_num,
            "cover": getCover(html, fanza_hinban),
            "imagecut": 1,
            "tag": fanza_Crawler.getFanzaStrings('ジャンル：'),
            "extrafanart": getExtrafanart(htmlcode),
            "label": label,
            "year": re.findall('\d{4}',getRelease(fanza_Crawler))[0],  # str(re.search('\d{4}',getRelease(a)).group()),
            "actor_photo": "",
            "website": chosen_url,
            "source": "fanza.py",
            "series": series,
        }
    except Exception as e:
        data = {
            "title": "",
        }
    js = json.dumps(
        data, ensure_ascii=False, sort_keys=True, indent=4, separators=(",", ":")
    )  # .encode('UTF-8')
    return js


def main_htmlcode(number):
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
    ]
    chosen_url = ""
    for url in fanza_urls:
        chosen_url = url + fanza_search_number
        htmlcode = get_html(chosen_url)
        if "404 Not Found" not in htmlcode:
            break
    if "404 Not Found" in htmlcode:
        return json.dumps({"title": "",})
    return htmlcode


if __name__ == "__main__":
    # print(main("DV-1562"))
    # print(main("96fad1217"))
    print(main("AES-002"))
    print(main("MIAA-391"))
    print(main("OBA-326"))
