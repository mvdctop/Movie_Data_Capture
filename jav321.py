import json
from bs4 import BeautifulSoup
from lxml import html
from ADC_function import post_html


def main(number: str) -> json:
    result = post_html(url="https://www.jav321.com/search", query={"sn": number})
    soup = BeautifulSoup(result.text, "html.parser")
    lx = html.fromstring(str(soup))

    if "/video/" in result.url:
        data = parse_info(soup=soup)
        dic = {
            "title": get_title(lx=lx),
            "studio": "",
            "year": data["release"][:4],
            "outline": get_outline(lx=lx),
            "director": "",
            "cover": get_cover(lx=lx),
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
    data = str(soup.select_one("div.row > div.col-md-9")).split("<br/>")

    return {
        "actor": get_anchor_info(h=data[0]),
        "label": get_anchor_info(h=data[1]),
        "tag": get_anchor_info(h=data[2]),
        "number": get_text_info(h=data[3]),
        "release": get_text_info(h=data[4]),
        "runtime": get_text_info(h=data[5]),
    }


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


if __name__ == "__main__":
    print(main("wmc-002"))
