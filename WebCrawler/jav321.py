import sys
sys.path.append('../')
import json
from bs4 import BeautifulSoup
from lxml import html
from ADC_function import post_html


def main(number: str) -> json:
    result = post_html(url="https://www.jav321.com/search", query={"sn": number})
    soup = BeautifulSoup(result.text, "html.parser")
    lx = html.fromstring(str(soup))

    if "/video/" in result.url:
        data = parse_info(soup)
        dic = {
            "title": get_title(lx),
            "year": get_year(data),
            "outline": get_outline(lx),
            "director": "",
            "cover": get_cover(lx),
            "imagecut": 1,
            "actor_photo": "",
            "website": result.url,
            "source": "jav321.py",
            **data,
        }
    else:
        dic = {}

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
        return {}


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


def get_cover(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[2]/div[1]/p/a/img/@src")[0]


def get_outline(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[1]/div[1]/div[2]/div[3]/div/text()")[0]

def get_series2(lx: html.HtmlElement) -> str:
    return lx.xpath("/html/body/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/a[11]/text()")[0]


def get_actor(data: hash) -> str:
    if "女优" in data:
        return get_anchor_info(data["女优"])
    else:
        return ""


def get_label(data: hash) -> str:
    if "片商" in data:
        return get_anchor_info(data["片商"])
    else:
        return ""


def get_tag(data: hash) -> str:
    if "标签" in data:
        return get_anchor_info(data["标签"])
    else:
        return ""


def get_studio(data: hash) -> str:
    if "片商" in data:
        return get_anchor_info(data["片商"])
    else:
        return ""


def get_number(data: hash) -> str:
    if "番号" in data:
        return get_text_info(data["番号"])
    else:
        return ""


def get_release(data: hash) -> str:
    if "发行日期" in data:
        return get_text_info(data["发行日期"])
    else:
        return ""


def get_runtime(data: hash) -> str:
    if "播放时长" in data:
        return get_text_info(data["播放时长"])
    else:
        return ""


def get_year(data: hash) -> str:
    if "release" in data:
        return data["release"][:4]
    else:
        return ""


def get_series(data: hash) -> str:
    if "系列" in data:
        return get_anchor_info(data["系列"])
    else:
        return ""


if __name__ == "__main__":
    print(main("soe-259"))
