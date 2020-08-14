import re
from lxml import etree
import json
from bs4 import BeautifulSoup
import sys
sys.path.append('../')
from ADC_function import *
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)
#print(get_html('https://www.dlsite.com/pro/work/=/product_id/VJ013152.html'))
#title //*[@id="work_name"]/a/text()
#studio //th[contains(text(),"ブランド名")]/../td/span[1]/a/text()
#release //th[contains(text(),"販売日")]/../td/a/text()
#story //th[contains(text(),"シナリオ")]/../td/a/text()
#senyo //th[contains(text(),"声優")]/../td/a/text()
#tag //th[contains(text(),"ジャンル")]/../td/div/a/text()
#jianjie //*[@id="main_inner"]/div[3]/text()
#photo //*[@id="work_left"]/div/div/div[2]/div/div[1]/div[1]/ul/li/img/@src

#https://www.dlsite.com/pro/work/=/product_id/VJ013152.html

def getTitle(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath('//*[@id="work_name"]/a/text()')[0]
    return result
def getActor(a):  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result1 = html.xpath('//th[contains(text(),"声优")]/../td/a/text()')
    except:
        result1 = ''
    return result1
def getActorPhoto(actor): #//*[@id="star_qdt"]/li/a/img
    a = actor.split(',')
    d={}
    for i in a:
        p={i:''}
        d.update(p)
    return d
def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        try:
            result = html.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except:
            result = html.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except:
        result = ''
    return result
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')
def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        try:
            result = html.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except:
            result = html.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except:
        result = ''
    return result
def getYear(getRelease):
    try:
        result = str(re.search('\d{4}', getRelease).group())
        return result
    except:
        return getRelease
def getRelease(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//th[contains(text(),"贩卖日")]/../td/a/text()')[0]
    return result1.replace('年','-').replace('月','-').replace('日','')
def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//th[contains(text(),"分类")]/../td/div/a/text()')
        return result
    except:
        return ''

def getCover_small(a, index=0):
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
    except: # 2020.7.17 Repair Cover Url crawl
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@data-src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = html.xpath('//*[@id="work_left"]/div/div/div[2]/div/div[1]/div[1]/ul/li/img/@src')[0]
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//th[contains(text(),"剧情")]/../td/a/text()')[0]
    except:
        result = ''
    return result
def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    total = []
    result = html.xpath('//*[@id="main_inner"]/div[3]/text()')
    for i in result:
        total.append(i.strip('\r\n'))
    return str(total).strip(" ['']").replace("', '', '",r'\n').replace("', '",r'\n').strip(", '', '")
def getSeries(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        try:
            result = html.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except:
            result = html.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except:
        result = ''
    return result
def main(number):
    try:
        number = number.upper()
        htmlcode = get_html('https://www.dlsite.com/pro/work/=/product_id/' + number + '.html',
                            cookies={'locale': 'zh-cn'})

        dic = {
            'actor': getActor(htmlcode),
            'title': getTitle(htmlcode),
            'studio': getStudio(htmlcode),
            'outline': getOutline(htmlcode),
            'runtime': '',
            'director': getDirector(htmlcode),
            'release': getRelease(htmlcode),
            'number': number,
            'cover': 'https:' + getCover(htmlcode),
            'cover_small': '',
            'imagecut': 0,
            'tag': getTag(htmlcode),
            'label': getLabel(htmlcode),
            'year': getYear(getRelease(htmlcode)),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': '',
            'website': 'https://www.dlsite.com/pro/work/=/product_id/' + number + '.html',
            'source': 'dlsite.py',
            'series': getSeries(htmlcode),
        }
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
        return js
    except:
        data = {
            "title": "",
        }
        js = json.dumps(
            data, ensure_ascii=False, sort_keys=True, indent=4, separators=(",", ":")
        )
        return js

# main('DV-1562')
# input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
if __name__ == "__main__":
    print(main('VJ013178'))
