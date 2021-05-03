import sys
sys.path.append('../')
import json
from bs4 import BeautifulSoup
from lxml import html
from ADC_function import post_html
import re


def main(number: str) -> json:
    try:
        result = post_html(url="https://www.jav321.com/search", query={"sn": number})
        soup = BeautifulSoup(result.text, "html.parser")
        lx = html.fromstring(str(soup))
    except:
        dic = {"title": ""}
        return json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    if "/video/" in result.url:
        data = parse_info(soup)

        dic = {
            "title": get_title(lx),
            "year": get_year(data),
            "outline": get_outline(lx),
            "director": "",
            "cover": get_cover(lx),
            "imagecut": 1,
            "trailer": get_trailer(result.text),
            "extrafanart": get_extrafanart(result.text),
            "actor_photo": "",
            "website": result.url,
            "source": "jav321.py",
            **data,
        }
    else:
        dic = {"title": ""}

    return json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

def get_title(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[1]/div[1]/div[1]/h3/text()")[0].strip()


def parse_info(soup: BeautifulSoup) -> dict:
    data = soup.select_one("div.row > div.col-md-9")

    if data:
        dd = str(data).split("<br/>")
        data_dic = {}
        for d in dd:
            data_dic[get_bold_text(h=d)] = d

        return {
            "actor": get_actor(data_dic),
            "label": get_label(data_dic),
            "studio": get_studio(data_dic),
            "tag": get_tag(data_dic),
            "number": get_number(data_dic),
            "release": get_release(data_dic),
            "runtime": get_runtime(data_dic),
            "series": get_series(data_dic),
        }
    else:
        return {"title": ""}


def get_bold_text(h: str) -> str:
    soup = BeautifulSoup(h, "html.parser")
    if soup.b:
        return soup.b.text
    else:
        return "UNKNOWN_TAG"


def get_anchor_info(h: str) -> str:
    result = []

    data = BeautifulSoup(h, "html.parser").find_all("a", href=True)
    for d in data:
        result.append(d.text)

    return ",".join(result)


def get_text_info(h: str) -> str:
    return h.split(": ")[1]

def get_trailer(html) -> str:
    videourl_pather = re.compile(r'<source src=\"(.*?)\"')
    videourl = videourl_pather.findall(html)
    if videourl:
        url = videourl[0].replace('awscc3001.r18.com', 'cc3001.dmm.co.jp').replace('cc3001.r18.com', 'cc3001.dmm.co.jp')
        return url
    else:
        return ''

def get_extrafanart(htmlcode):  # 获取剧照
    html_pather = re.compile(r'<div class=\"col\-md\-3\"><div class=\"col\-xs\-12 col\-md\-12\">[\s\S]*?</script><script async src=\"\/\/adserver\.juicyads\.com/js/jads\.js\">')
    html = html_pather.search(htmlcode)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<img.*?src=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            return extrafanart_imgs
    return ''

def get_cover(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[2]/div[1]/p/a/img/@src")[0]


def get_outline(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[1]/div[1]/div[2]/div[3]/div/text()")[0]

def get_series2(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/a[11]/text()")[0]


def get_actor(data: hash) -> str:
    if "出演者" in data:
        return get_anchor_info(data["出演者"])
    else:
        return ""


def get_label(data: hash) -> str:
    if "メーカー" in data:
        return get_anchor_info(data["メーカー"])
    else:
        return ""


def get_tag(data: hash) -> str:
    if "ジャンル" in data:
        return get_anchor_info(data["ジャンル"])
    else:
        return ""



def get_studio(data: hash) -> str:
    if "メーカー" in data:
        return get_anchor_info(data["メーカー"])
    else:
        return ""


def get_number(data: hash) -> str:
    if "品番" in data:
        return get_text_info(data["品番"])
    else:
        return ""


def get_release(data: hash) -> str:
    if "配信開始日" in data:
        return get_text_info(data["配信開始日"])
    else:
        return ""


def get_runtime(data: hash) -> str:
    if "収録時間" in data:
        return get_text_info(data["収録時間"])
    else:
        return ""


def get_year(data: hash) -> str:
    if "release" in data:
        return data["release"][:4]
    else:
        return ""


def get_series(data: hash) -> str:
    if "シリーズ" in data:
        return get_anchor_info(data["シリーズ"])
    else:
        return ""


if __name__ == "__main__":
    print(main("jul-404"))
