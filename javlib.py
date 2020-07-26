import json
import bs4
from bs4 import BeautifulSoup
from lxml import html
from http.cookies import SimpleCookie

from ADC_function import get_javlib_cookie, get_html


def main(number: str):
    raw_cookies, user_agent = get_javlib_cookie()

    # Blank cookies mean javlib site return error
    if not raw_cookies:
        return json.dumps({}, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))

    # Manually construct a dictionary
    s_cookie = SimpleCookie()
    s_cookie.load(raw_cookies)
    cookies = {}
    for key, morsel in s_cookie.items():
        cookies[key] = morsel.value

    # Scraping
    result = get_html(
        "http://www.javlibrary.com/cn/vl_searchbyid.php?keyword={}".format(number),
        cookies=cookies,
        ua=user_agent,
        return_type="object"
    )
    soup = BeautifulSoup(result.text, "html.parser")
    lx = html.fromstring(str(soup))

    if "/?v=jav" in result.url:
        dic = {
            "title": get_title(lx, soup),
            "studio": get_table_el_single_anchor(soup, "video_maker"),
            "year": get_table_el_td(soup, "video_date")[:4],
            "outline": "",
            "director": get_table_el_single_anchor(soup, "video_director"),
            "cover": get_cover(lx),
            "imagecut": 1,
            "actor_photo": "",
            "website": result.url,
            "source": "javlib.py",
            "actor": get_table_el_multi_anchor(soup, "video_cast"),
            "label": get_table_el_td(soup, "video_label"),
            "tag": get_table_el_multi_anchor(soup, "video_genres"),
            "number": get_table_el_td(soup, "video_id"),
            "release": get_table_el_td(soup, "video_date"),
            "runtime": get_from_xpath(lx, '//*[@id="video_length"]/table/tr/td[2]/span/text()'),
            "series":'',
        }
    else:
        dic = {}

    return json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))


def get_from_xpath(lx: html.HtmlElement, xpath: str) -> str:
    return lx.xpath(xpath)[0].strip()


def get_table_el_single_anchor(soup: BeautifulSoup, tag_id: str) -> str:
    tag = soup.find(id=tag_id).find("a")

    if tag is not None:
        return tag.string.strip()
    else:
        return ""


def get_table_el_multi_anchor(soup: BeautifulSoup, tag_id: str) -> str:
    tags = soup.find(id=tag_id).find_all("a")

    return process(tags)


def get_table_el_td(soup: BeautifulSoup, tag_id: str) -> str:
    tags = soup.find(id=tag_id).find_all("td", class_="text")

    return process(tags)


def process(tags: bs4.element.ResultSet) -> str:
    values = []
    for tag in tags:
        value = tag.string
        if value is not None and value != "----":
            values.append(value)

    return ",".join(x for x in values if x)


def get_title(lx: html.HtmlElement, soup: BeautifulSoup) -> str:
    title = get_from_xpath(lx, '//*[@id="video_title"]/h3/a/text()')
    number = get_table_el_td(soup, "video_id")

    return title.replace(number, "").strip()


def get_cover(lx: html.HtmlComment) -> str:
    return "http:{}".format(get_from_xpath(lx, '//*[@id="video_jacket_img"]/@src'))


if __name__ == "__main__":
    lists = ["DVMC-003", "GS-0167", "JKREZ-001", "KMHRS-010", "KNSD-023"]
    #lists = ["DVMC-003"]
    for num in lists:
        print(main(num))
