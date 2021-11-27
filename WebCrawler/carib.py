import sys
sys.path.append('../')
import json
from lxml import html
import re
from ADC_function import *
from WebCrawler.storyline import getStoryline


G_SITE = 'https://www.caribbeancom.com'


def main(number: str) -> json:
    try:
        url = f'{G_SITE}/moviepages/{number}/index.html'
        result, session = get_html_session(url, return_type='session')
        htmlcode = result.content.decode('euc-jp')
        if not result or not htmlcode or '<title>404' in htmlcode or 'class="movie-info section"' not in htmlcode:
            raise ValueError("page not found")

        lx = html.fromstring(htmlcode)
        title = get_title(lx)

        dic = {
            'title': title,
            'studio': '加勒比',
            'year': get_year(lx),
            'outline': get_outline(lx, number, title),
            'runtime': get_runtime(lx),
            'director': '',
            'actor': get_actor(lx),
            'release': get_release(lx),
            'number': number,
            'cover': f'{G_SITE}/moviepages/{number}/images/l_l.jpg',
            'tag': get_tag(lx),
            'extrafanart': get_extrafanart(lx),
            'label': get_series(lx),
            'imagecut': 1,
#            'actor_photo': get_actor_photo(lx, session),
            'website': f'{G_SITE}/moviepages/{number}/index.html',
            'source': 'carib.py',
            'series': get_series(lx),
        }
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )
        return js

    except Exception as e:
        if config.getInstance().debug():
            print(e)
        dic = {"title": ""}
        return json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))


def get_title(lx: html.HtmlElement) -> str:
    return str(lx.xpath("//div[@class='movie-info section']/div[@class='heading']/h1[@itemprop='name']/text()")[0]).strip()

def get_year(lx: html.HtmlElement) -> str:
    return lx.xpath("//li[2]/span[@class='spec-content']/text()")[0][:4]

def get_outline(lx: html.HtmlElement, number: str, title: str) -> str:
    o = lx.xpath("//div[@class='movie-info section']/p[@itemprop='description']/text()")[0].strip()
    g = getStoryline(number, title)
    if len(g):
        return g
    return o

def get_release(lx: html.HtmlElement) -> str:
    return lx.xpath("//li[2]/span[@class='spec-content']/text()")[0].replace('/','-')

def get_actor(lx: html.HtmlElement):
    r = []
    actors = lx.xpath("//span[@class='spec-content']/a[@itemprop='actor']/span/text()")
    for act in actors:
        if str(act) != '他':
            r.append(act)
    return r

def get_tag(lx: html.HtmlElement) -> str:
    genres = lx.xpath("//span[@class='spec-content']/a[@itemprop='genre']/text()")
    return genres

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

def get_series(lx: html.HtmlElement) -> str:
    try:
        return str(lx.xpath("//span[@class='spec-title'][contains(text(),'シリーズ')]/../span[@class='spec-content']/a/text()")[0]).strip()
    except:
        return ''

def get_runtime(lx: html.HtmlElement) -> str:
    return str(lx.xpath("//span[@class='spec-content']/span[@itemprop='duration']/text()")[0]).strip()

def get_actor_photo(lx, session):
    htmla = lx.xpath("//*[@id='moviepages']/div[@class='container']/div[@class='inner-container']/div[@class='movie-info section']/ul/li[@class='movie-spec']/span[@class='spec-content']/a[@itemprop='actor']")
    names = lx.xpath("//*[@id='moviepages']/div[@class='container']/div[@class='inner-container']/div[@class='movie-info section']/ul/li[@class='movie-spec']/span[@class='spec-content']/a[@itemprop='actor']/span[@itemprop='name']/text()")
    t = {}
    for name, a in zip(names, htmla):
        if name.strip() == '他':
            continue
        p = {name.strip(): a.attrib['href']}
        t.update(p)
    o = {}
    for k, v in t.items():
        if '/search_act/' not in v:
            continue
        r = session.get(urljoin(G_SITE, v))
        if not r.ok:
            continue
        html = r.text
        pos = html.find('.full-bg')
        if pos<0:
            continue
        css = html[pos:pos+100]
        cssBGjpgs = re.findall(r'background: url\((.+\.jpg)', css, re.I)
        if not cssBGjpgs or not len(cssBGjpgs[0]):
            continue
        p = {k: urljoin(r.url, cssBGjpgs[0])}
        o.update(p)
    return o

if __name__ == "__main__":
    print(main("070116-197")) # actor have photo
    print(main("041721-001"))
    print(main("080520-001"))
