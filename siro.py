import re
from lxml import etree
import json
import requests
from bs4 import BeautifulSoup

def get_html(url):#网页请求核心
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    cookies = {'adc':'1'}
    getweb = requests.get(str(url),timeout=5,cookies=cookies,headers=headers).text
    try:
        return getweb
    except:
        print("[-]Connect Failed! Please check your Proxy.")

def getTitle(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result = str(html.xpath('//*[@id="center_column"]/div[2]/h1/text()')).strip(" ['']")
    return result
def getActor(a): #//*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())
    result=str(html.xpath('//table[2]/tr[1]/td/a/text()')).strip(" ['\\n                                        ']")
    return result
def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result=str(html.xpath('//table[2]/tr[2]/td/a/text()')).strip(" ['\\n                                        ']")
    return result
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result=str(html.xpath('//table[2]/tr[3]/td/text()')).strip(" ['\\n                                        ']")
    return result
def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result=str(html.xpath('//table[2]/tr[4]/td/text()')).strip(" ['\\n                                        ']")
    return result
def getYear(a):
    html = etree.fromstring(a, etree.HTMLParser())
    #result=str(html.xpath('//table[2]/tr[5]/td/text()')).strip(" ['\\n                                        ']")
    result=str(html.xpath('//table[2]/tr[5]/td/text()')).strip(" ['\\n                                        ']")
    return result
def getRelease(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result=str(html.xpath('//table[2]/tr[5]/td/text()')).strip(" ['\\n                                        ']")
    return result
def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result=str(html.xpath('//table[2]/tr[9]/td/text()')).strip(" ['\\n                                        ']")
    return result
def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="center_column"]/div[2]/div[1]/div/div/h2/img/@src')).strip(" ['']")
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result = str(html.xpath('//table[2]/tr[7]/td/a/text()')).strip(" ['\\n                                        ']")
    return result
def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="introduction"]/dd/p[1]/text()')).strip(" ['']")
    return result

def main(number):
    htmlcode=get_html('https://www.mgstage.com/product/product_detail/'+str(number))
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = str(soup.find(attrs={'class': 'detail_data'})).replace('\n                                        ','')
    dic = {
        'title': getTitle(htmlcode).replace("\\n",'').replace('        ',''),
        'studio': getStudio(a),
        'year': getYear(a),
        'outline': getOutline(htmlcode),
        'runtime': getRuntime(a),
        'director': getDirector(a),
        'actor': getActor(a),
        'release': getRelease(a),
        'number': number,
        'cover': getCover(htmlcode),
        'imagecut': 0,
        'tag':' ',
    }
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),)#.encode('UTF-8')
    return js