import re
from lxml import etree
import json
from bs4 import BeautifulSoup
from ADC_function import *


# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

def getTitle(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath('//*[@id="program_detail_title"]/text()')[0]
    return result


def getActor(a):  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[3]/a/text()')[0]
    return result1


def getActorPhoto(actor):  # //*[@id="star_qdt"]/li/a/img
    a = actor.split(',')
    d = {}
    for i in a:
        p = {i: ''}
        d.update(p)
    return d


def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[4]/a/span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"片商")]/../following-sibling::span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')


def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[2]/li[3]/text()')).strip(" ['']")
    try:
        return re.findall('\d+',result1)[0]
    except:
        return ''


def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[5]/a/span/text()')).strip(" ['']")
    return result1


def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result1 = str(html.xpath('//*[@id="hinban"]/text()')).strip(" ['']")
    return result1


def getYear(getRelease):
    try:
        result = str(re.search('\d{4}', getRelease).group())
        return result
    except:
        return getRelease


def getRelease(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[2]/li[4]/text()')).strip(" ['']")
    try:
        return re.findall('\d{4}/\d{2}/\d{2}', result1)[0]
    except:
        return ''


def getTag(a):
    result2=[]
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[1]/li[6]/a/text()')
    for i in result1:
        i=i.replace(u'\n','')
        i=i.replace(u'\t','')
        result2.append(i)
    return result2


def getCover_small(a, index=0):
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
    if not 'https' in result:
        result = 'https:' + result
    return result


def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[1]/p/a/@href')).strip(" ['']")
    return 'https:'+result


def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//*[@id="program_detail_director"]/text()')).strip(" ['']").replace(u'\\n','').replace(u'\\t','')
    return result1


def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="avodDetails"]/div/div[3]/div[2]/div/ul[2]/li[5]/p/text()')).strip(" ['']")
    try:
        return re.sub('\\\\\w*\d+','',result)
    except:
        return result


def main(number):
    try:
        number = number.upper()
        query_result = get_html(
            'https://xcity.jp/result_published/?genre=%2Fresult_published%2F&q=' + number.replace('-',
                                                                                                  '') + '&sg=main&num=30')
        html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        urls = html.xpath("//table[contains(@class, 'resultList')]/tr[2]/td[1]/a/@href")[0]
        detail_page = get_html('https://xcity.jp' + urls)
        dic = {
            'actor': getActor(detail_page),
            'title': getTitle(detail_page),
            'studio': getStudio(detail_page),
            'outline': getOutline(detail_page),
            'runtime': getRuntime(detail_page),
            'director': getDirector(detail_page),
            'release': getRelease(detail_page),
            'number': getNum(detail_page),
            'cover': getCover(detail_page),
            'cover_small': '',
            'imagecut': 1,
            'tag': getTag(detail_page),
            'label': getLabel(detail_page),
            'year': getYear(getRelease(detail_page)),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': getActorPhoto(getActor(detail_page)),
            'website': 'https://javdb.com' + urls,
            'source': 'xcity.py',
        }
    except Exception as e:
        # print(e)
        dic = {"title": ""}

    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

if __name__ == '__main__':
    print(main('VNDS-2624'))
