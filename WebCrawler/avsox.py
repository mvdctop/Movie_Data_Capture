import sys
sys.path.append('..')
import re
from lxml import etree
import json
from ADC_function import *
from WebCrawler.storyline import getStoryline
from crawler import *
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

def getActor(html):
    a = html.xpath('//a[@class="avatar-box"]')
    d = []
    for i in a:
        d.append(i.find('span').text)
    return d

def getCover_small(html):
    result = str(html.xpath('//*[@id="waterfall"]/div/a/div[1]/img/@src')).strip(" ['']")
    return result
def getTag(html):
    x = html.xpath('/html/head/meta[@name="keywords"]/@content')[0].split(',')
    return [i.strip() for i in x[2:]]  if len(x) > 2 else []

def main(number):
    html = get_html('https://tellme.pw/avsox')
    site = Crawler(html).getString('//div[@class="container"]/div/a/@href')
    a = get_html(site + '/cn/search/' + number)
    html = Crawler(a)
    result1 = html.getString('//*[@id="waterfall"]/div/a/@href')
    if result1 == '' or result1 == 'null' or result1 == 'None':
        a = get_html(site + '/cn/search/' + number.replace('-', '_'))
        html = Crawler(a)
        result1 = html.getString('//*[@id="waterfall"]/div/a/@href')
        if result1 == '' or result1 == 'null' or result1 == 'None':
            a = get_html(site + '/cn/search/' + number.replace('_', ''))
            html = Crawler(a)
            result1 = html.getString('//*[@id="waterfall"]/div/a/@href')
    detail = get_html("https:" + result1)
    lx = etree.fromstring(detail, etree.HTMLParser())
    avsox_crawler2 = Crawler(a)
    avsox_crawler = Crawler(detail)
    try:
        new_number = avsox_crawler.getString('//span[contains(text(),"识别码:")]/../span[2]/text()')
        if new_number.upper() != number.upper():
            raise ValueError('number not found')
        title = avsox_crawler.getString('/html/body/div[2]/h3/text()').replace('/','').strip(new_number)
        dic = {
            'actor': getActor(lx),
            'title': title,
            'studio': avsox_crawler.getString('//p[contains(text(),"制作商: ")]/following-sibling::p[1]/a/text()').replace("', '",' '),
            'outline': getStoryline(number, title),
            'runtime': avsox_crawler.getString('//span[contains(text(),"长度:")]/../text()').replace('分钟',''),
            'director': '',  #
            'release': avsox_crawler.getString('//span[contains(text(),"发行时间:")]/../text()'),
            'number': new_number,
            'cover': avsox_crawler.getString('/html/body/div[2]/div[1]/div[1]/a/img/@src'),
            #'cover_small' : getCover_small(html),
            'cover_small': avsox_crawler2.getString('//*[@id="waterfall"]/div/a/div[1]/img/@src'),
            'imagecut': 3,
            'tag': getTag(lx),
            'label': avsox_crawler.getString('//p[contains(text(),"系列:")]/following-sibling::p[1]/a/text()'),
            'year': re.findall('\d{4}',avsox_crawler.getString('//span[contains(text(),"发行时间:")]/../text()'))[0],
            'actor_photo': getActorPhoto(lx),
            'website': "https:" + result1,
            'source': 'avsox.py',
            'series': avsox_crawler.getString('//span[contains(text(),"系列:")]/../span[2]/text()'),
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
