#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import json
import re
from urllib.parse import urlencode

from lxml import etree

from ADC_function import *

# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)


def getTitle(text):
    html = etree.fromstring(text, etree.HTMLParser())
    result = html.xpath('//*[starts-with(@id, "title")]/text()')[0]
    return result


def getActor(text):
    # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(text, etree.HTMLParser())
    result = (
        str(
            html.xpath(
                "//td[contains(text(),'出演者')]/following-sibling::td/span/a/text()"
            )
        )
        .strip(" ['']")
        .replace("', '", ",")
    )
    return result


def getStudio(text):
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'メーカー')]/following-sibling::td/a/text()"
        )[0]
    except:
        result = html.xpath(
            "//td[contains(text(),'メーカー')]/following-sibling::td/text()"
        )[0]
    return result


def getRuntime(text):
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath("//td[contains(text(),'収録時間')]/following-sibling::td/text()")[0]
    return re.search(r"\d+", str(result)).group()


def getLabel(text):
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'レーベル：')]/following-sibling::td/a/text()"
        )[0]
    except:
        result = html.xpath(
            "//td[contains(text(),'レーベル：')]/following-sibling::td/text()"
        )[0]
    return result


def getNum(text):
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'品番：')]/following-sibling::td/a/text()"
        )[0]
    except:
        result = html.xpath(
            "//td[contains(text(),'品番：')]/following-sibling::td/text()"
        )[0]
    return result


def getYear(getRelease):
    try:
        result = str(re.search(r"\d{4}", getRelease).group())
        return result
    except:
        return getRelease


def getRelease(text):
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'発売日：')]/following-sibling::td/a/text()"
        )[0].lstrip("\n")
    except:
        try:
            result = html.xpath(
                "//td[contains(text(),'発売日：')]/following-sibling::td/text()"
            )[0].lstrip("\n")
        except:
            result = "----"
    if result == "----":
        try:
            result = html.xpath(
                "//td[contains(text(),'配信開始日：')]/following-sibling::td/a/text()"
            )[0].lstrip("\n")
        except:
            try:
                result = html.xpath(
                    "//td[contains(text(),'配信開始日：')]/following-sibling::td/text()"
                )[0].lstrip("\n")
            except:
                pass
    return result.replace("/", "-")


def getTag(text):
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'ジャンル：')]/following-sibling::td/a/text()"
        )
        total = []
        for i in result:
            try:
                total.append(translateTag_to_sc(i))
            except:
                pass
        return total
    except:
        result = html.xpath(
            "//td[contains(text(),'ジャンル：')]/following-sibling::td/text()"
        )
        total = []
        for i in result:
            try:
                total.append(translateTag_to_sc(i))
            except:
                pass
        return total
    return result


def getCover(text, number):
    html = etree.fromstring(text, etree.HTMLParser())
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


def getDirector(text):
    html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath(
            "//td[contains(text(),'監督：')]/following-sibling::td/a/text()"
        )[0]
    except:
        result = html.xpath(
            "//td[contains(text(),'監督：')]/following-sibling::td/text()"
        )[0]
    return result


def getOutline(text):
    html = etree.fromstring(text, etree.HTMLParser())
    try:
        result = str(html.xpath("//div[@class='mg-b20 lh4']/text()")[0]).replace(
            "\n", ""
        )
        if result == "":
            result = str(html.xpath("//div[@class='mg-b20 lh4']//p/text()")[0]).replace(
                "\n", ""
            )
    except:
        # (TODO) handle more edge case
        # print(html)
        return ""
    return result


def getSeries(text):
    try:
        html = etree.fromstring(text, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        try:
            result = html.xpath(
                "//td[contains(text(),'シリーズ：')]/following-sibling::td/a/text()"
            )[0]
        except:
            result = html.xpath(
                "//td[contains(text(),'シリーズ：')]/following-sibling::td/text()"
            )[0]
        return result
    except:
        return ""


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

    for url in fanza_urls:
        chosen_url = url + fanza_search_number
        htmlcode = get_html(
            "https://www.dmm.co.jp/age_check/=/declared=yes/?{}".format(
                urlencode({"rurl": chosen_url})
            )
        )
        if "404 Not Found" not in htmlcode:
            break
    if "404 Not Found" in htmlcode:
        return json.dumps({"title": "",})
    try:
        # for some old page, the input number does not match the page
        # for example, the url will be cid=test012
        # but the hinban on the page is test00012
        # so get the hinban first, and then pass it to following functions
        fanza_hinban = getNum(htmlcode)
        data = {
            "title": getTitle(htmlcode).strip(),
            "studio": getStudio(htmlcode),
            "outline": getOutline(htmlcode),
            "runtime": getRuntime(htmlcode),
            "director": getDirector(htmlcode) if "anime" not in chosen_url else "",
            "actor": getActor(htmlcode) if "anime" not in chosen_url else "",
            "release": getRelease(htmlcode),
            "number": fanza_hinban,
            "cover": getCover(htmlcode, fanza_hinban),
            "imagecut": 1,
            "tag": getTag(htmlcode),
            "label": getLabel(htmlcode),
            "year": getYear(
                getRelease(htmlcode)
            ),  # str(re.search('\d{4}',getRelease(a)).group()),
            "actor_photo": "",
            "website": chosen_url,
            "source": "fanza.py",
            "series": getSeries(htmlcode),
        }
    except:
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
    print(main("DV-1562"))
    print(main("96fad1217"))
