import re
from lxml import etree
import json
import requests
from bs4 import BeautifulSoup
from ADC_function import *

def getTitle(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result = str(html.xpath('//*[@id="center_column"]/div[2]/h1/text()')).strip(" ['']")
    return result
def getActor(a): #//*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser()) #//table/tr[1]/td[1]/text()
    result2=str(html.xpath('//table/tr[1]/td[1]/text()')).strip(" ['\\n                                        ']")
    result1 = str(html.xpath('//table/tr[1]/td[1]/a/text()')).strip(" ['\\n                                        ']")
    return str(result1+result2).strip('+')
def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result2=str(html.xpath('//table[2]/tr[2]/td/text()')).strip(" ['\\n                                        ']")
    result1 = str(html.xpath('//table/tr[2]/td[1]/a/text()')).strip(" ['\\n                                        ']")
    return str(result1+result2).strip('+')
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result2=str(html.xpath('//table/tr[3]/td[1]/text()')).strip(" ['\\n                                        ']")
    result1 = str(html.xpath('//table/tr[3]/td[1]/a/text()')).strip(" ['\\n                                        ']")
    return str(result1 + result2).strip('+').strip('mi')
def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result2=str(html.xpath('//table/tr[6]/td[1]/text()')).strip(" ['\\n                                        ']")
    result1 = str(html.xpath('//table/tr[6]/td[1]/a/text()')).strip(" ['\\n                                        ']")
    return str(result1 + result2).strip('+')
def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result2=str(html.xpath('//table/tr[2]/td[4]/a/text()')).strip(" ['\\n                                        ']")
    result1 = str(html.xpath('//table/tr[2]/td[4]/text()')).strip(" ['\\n                                        ']")
    return str(result1 + result2).strip('+')
def getYear(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result2=str(html.xpath('//table/tr[2]/td[5]/a/text()')).strip(" ['\\n                                        ']")
    result1=str(html.xpath('//table/tr[2]/td[5]/text()')).strip(" ['\\n                                        ']")
    return result2+result1
def getRelease(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result2=str(html.xpath('//table/tr[5]/td[1]/text()')).strip(" ['\\n                                        ']")
    result1 = str(html.xpath('//table/tr[5]/a/td[1]/text()')).strip(" ['\\n                                        ']")
    return str(result1 + result2).strip('+')
def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result2=str(html.xpath('//table/tr[8]/td[1]/a/text()')).strip(" ['\\n                                        ']")
    result1=str(html.xpath('//table/tr[8]/td[1]/text()')).strip(" ['\\n                                        ']")
    return str(result1 + result2).strip('+')
def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="center_column"]/div[2]/div[1]/div/div/h2/img/@src')).strip(" ['']")
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result1 = str(html.xpath('//table/tr[2]/td[1]/text()')).strip(" ['\\n                                        ']")
    result2 = str(html.xpath('//table/tr[2]/td[1]/a/text()')).strip(" ['\\n                                        ']")
    return str(result1 + result2).strip('+')
def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="introduction"]/dd/p[1]/text()')).strip(" ['']")
    return result
def main(number):
    htmlcode=get_html('https://www.mgstage.com/product/product_detail/'+str(number),cookies={'adc':'1'})
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = str(soup.find(attrs={'class': 'detail_data'})).replace('\n                                        ','')
    #print(a)
    dic = {
        'title': getTitle(htmlcode).replace("\\n",'').replace('        ',''),
        'studio': getStudio(a),
        'year': str(re.search('\d{4}',getRelease(a)).group()),
        'outline': getOutline(htmlcode),
        'runtime': getRuntime(a),
        'director': getDirector(a),
        'actor': getActor(a),
        'release': getRelease(a),
        'number': number,
        'cover': getCover(htmlcode),
        'imagecut': 0,
        'tag': getTag(a).replace("'\\n',",'').replace(' ', '').replace("\\n','\\n",','),
        'label':getLabel(a)
    }
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),)#.encode('UTF-8')
    #print('https://www.mgstage.com/product/product_detail/'+str(number))
    return js
#print(main('SIRO-3552'))