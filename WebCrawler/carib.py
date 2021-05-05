import sys
sys.path.append('../')
import json
from bs4 import BeautifulSoup
from lxml import html
import re
import urllib.request
import socket
from ADC_function import *

def get_html(url):
    socket.setdefaulttimeout(10)
    papg = urllib.request.urlopen(url)
    htm = papg.read()
    htm = htm.decode("euc_jp")
    return htm

def main(number: str) -> json:
    try:
        caribhtml = get_html('https://www.caribbeancom.com/moviepages/'+number+'/index.html')

        soup = BeautifulSoup(caribhtml, "html.parser")
        lx = html.fromstring(str(soup))

        if not soup.select_one("#moviepages > div > div:nth-child(1) > div.movie-info.section"):
            raise ValueError("page info not found")
    except:
        dic = {"title": ""}
        return json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
    dic = {
        'title': get_title(lx),
        'studio': '加勒比',
        'year': get_year(lx),
        'outline': '',
        'runtime': get_runtime(lx),
        'director': '',
        'actor': get_actor(lx),
        'release': get_release(lx),
        'number': number,
        'cover': 'https://www.caribbeancom.com/moviepages/' + number + '/images/l_l.jpg',
        'tag': get_tag(lx),
        'extrafanart': get_extrafanart(lx),
        'label': '',
        'imagecut': 0,
        'actor_photo': '',
        'website': 'https://www.caribbeancom.com/moviepages/' + number + '/index.html',
        'source': 'carib.py',
        'series': '',
    }
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

def get_title(lx: html.HtmlElement) -> str:
    return str(lx.xpath("//div[@class='movie-info section']/div[@class='heading']/h1[@itemprop='name']/text()")[0]).strip()

def get_year(lx: html.HtmlElement) -> str:
    return lx.xpath("//li[2]/span[@class='spec-content']/text()")[0][:4]

def get_release(lx: html.HtmlElement) -> str:
    return lx.xpath("//li[2]/span[@class='spec-content']/text()")[0].replace('/','-')

def get_actor(lx: html.HtmlElement) -> str:
    r = []
    actors = lx.xpath("//span[@class='spec-content']/a[@itemprop='actor']/span/text()")
    for act in actors:
        if str(act) != '他':
            r.append(act)
    return r

def get_tag(lx: html.HtmlElement) -> str:
    r = []
    genres = lx.xpath("//span[@class='spec-content']/a[@itemprop='genre']/text()")
    for g in genres:
        r.append(translateTag_to_sc(str(g)))
    return r

def get_extrafanart(lx: html.HtmlElement) -> str:
    r = []
    genres = lx.xpath("//*[@id='sampleexclude']/div[2]/div/div[@class='grid-item']/div/a/@href")
    for g in genres:
        jpg = str(g)
        if '/member/' in jpg:
            break
        else:
            r.append('https://www.caribbeancom.com' + jpg)
    return r

def get_runtime(lx: html.HtmlElement) -> str:
    return str(lx.xpath( "//span[@class='spec-content']/span[@itemprop='duration']/text()")[0]).strip()

if __name__ == "__main__":
    print(main("041721-001"))
    print(main("080520-001"))
