import sys
sys.path.append('..')
import re
from lxml import etree
import json
from ADC_function import *
from WebCrawler.storyline import getStoryline
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

def getActorPhoto(html):
    a = html.xpath('//a[@class="avatar-box"]')
    d = {}
    for i in a:
        l = i.find('.//img').attrib['src']
        t = i.find('span').text
        p2 = {t: l}
        d.update(p2)
    return d
def getTitle(html):
    try:
        result = str(html.xpath('/html/body/div[2]/h3/text()')).strip(" ['']") #[0]
        return result.replace('/', '')
    except:
        return ''
def getActor(html):
    a = html.xpath('//a[@class="avatar-box"]')
    d = []
    for i in a:
        d.append(i.find('span').text)
    return d
def getStudio(html):
    result1 = str(html.xpath('//p[contains(text(),"制作商: ")]/following-sibling::p[1]/a/text()')).strip(" ['']").replace("', '",' ')
    return result1
def getRuntime(html):
    result1 = str(html.xpath('//span[contains(text(),"长度:")]/../text()')).strip(" ['分钟']")
    return result1
def getLabel(html):
    result1 = str(html.xpath('//p[contains(text(),"系列:")]/following-sibling::p[1]/a/text()')).strip(" ['']")
    return result1
def getNum(html):
    result1 = str(html.xpath('//span[contains(text(),"识别码:")]/../span[2]/text()')).strip(" ['']")
    return result1
def getYear(release):
    try:
        result = str(re.search('\d{4}',release).group())
        return result
    except:
        return release
def getRelease(html):
    result1 = str(html.xpath('//span[contains(text(),"发行时间:")]/../text()')).strip(" ['']")
    return result1
def getCover(html):
    result = str(html.xpath('/html/body/div[2]/div[1]/div[1]/a/img/@src')).strip(" ['']")
    return result
def getCover_small(html):
    result = str(html.xpath('//*[@id="waterfall"]/div/a/div[1]/img/@src')).strip(" ['']")
    return result
def getTag(html):
    x = html.xpath('/html/head/meta[@name="keywords"]/@content')[0].split(',')
    return [i.strip() for i in x[2:]]  if len(x) > 2 else []
def getSeries(html):
    try:
        result1 = str(html.xpath('//span[contains(text(),"系列:")]/../span[2]/text()')).strip(" ['']")
        return result1
    except:
        return ''

def main(number):
    html = get_html('https://tellme.pw/avsox')
    site = etree.HTML(html).xpath('//div[@class="container"]/div/a/@href')[0]
    a = get_html(site + '/cn/search/' + number)
    html = etree.fromstring(a, etree.HTMLParser())
    result1 = str(html.xpath('//*[@id="waterfall"]/div/a/@href')).strip(" ['']")
    if result1 == '' or result1 == 'null' or result1 == 'None':
        a = get_html(site + '/cn/search/' + number.replace('-', '_'))
        html = etree.fromstring(a, etree.HTMLParser())
        result1 = str(html.xpath('//*[@id="waterfall"]/div/a/@href')).strip(" ['']")
        if result1 == '' or result1 == 'null' or result1 == 'None':
            a = get_html(site + '/cn/search/' + number.replace('_', ''))
            html = etree.fromstring(a, etree.HTMLParser())
            result1 = str(html.xpath('//*[@id="waterfall"]/div/a/@href')).strip(" ['']")
    detail = get_html("https:" + result1)
    lx = etree.fromstring(detail, etree.HTMLParser())
    try:
        new_number = getNum(lx)
        if new_number.upper() != number.upper():
            raise ValueError('number not found')
        title = getTitle(lx).strip(new_number)
        dic = {
            'actor': getActor(lx),
            'title': title,
            'studio': getStudio(lx),
            'outline': getStoryline(number, title),
            'runtime': getRuntime(lx),
            'director': '',  #
            'release': getRelease(lx),
            'number': new_number,
            'cover': getCover(lx),
            'cover_small': getCover_small(html),
            'imagecut': 3,
            'tag': getTag(lx),
            'label': getLabel(lx),
            'year': getYear(getRelease(lx)),
            'actor_photo': getActorPhoto(lx),
            'website': "https:" + result1,
            'source': 'avsox.py',
            'series': getSeries(lx),
        }
    except Exception as e:
        if config.getInstance().debug():
            print(e)
        dic = {"title": ""}
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

if __name__ == "__main__":
    print(main('012717_472'))
    print(main('1')) # got fake result raise 'number not found'
