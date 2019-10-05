import re
from lxml import etree#need install
import json
import ADC_function

def getTitle(htmlcode): #获取厂商
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/h2/text()')).strip(" ['']")
    return result
def getActor(htmlcode):
    try:
        html = etree.fromstring(htmlcode, etree.HTMLParser())
        result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/div/div[2]/dl/dd[5]/a/text()')).strip(" ['']")
        return result
    except:
        return ''
def getStudio(htmlcode): #获取厂商
    try:
        html = etree.fromstring(htmlcode, etree.HTMLParser())
        result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/div/div[2]/dl/dd[5]/a/text()')).strip(" ['']")
        return result
    except:
        return ''
def getNum(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    return result
def getRelease(htmlcode2): #
    html=etree.fromstring(htmlcode2,etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/div/div[2]/dl/dd[4]/text()')).strip(" ['']")
    return result
def getCover(htmlcode2): #获取厂商 #
    html = etree.fromstring(htmlcode2, etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/div/div[1]/a/img/@src')).strip(" ['']")
    return 'http:' + result
def getOutline(htmlcode2):     #获取番号 #
    html = etree.fromstring(htmlcode2, etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[4]/p/text()')).strip(" ['']").replace("\\n",'',10000).replace("'",'',10000).replace(', ,','').strip('  ').replace('。,',',')
    return result
def getTag(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = html.xpath('//*[@id="container"]/div[1]/div/article/section[6]/ul/li/a/text()')
    return result
def getYear(release):
    try:
        result = re.search('\d{4}',release).group()
        return result
    except:
        return ''

def main(number):
    number=number.replace('PPV','').replace('ppv','').strip('fc2_').strip('fc2-').strip('ppv-').strip('PPV-').strip('FC2_').strip('FC2-').strip('ppv-').strip('PPV-').replace('fc2ppv-','').replace('FC2PPV-','')
    htmlcode2 = ADC_function.get_html('http://adult.contents.fc2.com/article_search.php?id='+str(number).lstrip("FC2-").lstrip("fc2-").lstrip("fc2_").lstrip("fc2-")+'')
    #htmlcode = ADC_function.get_html('http://fc2fans.club/html/FC2-' + number + '.html')
    dic = {
        'title':    getTitle(htmlcode2),
        'studio':   getStudio(htmlcode2),
        'year':     getYear(getRelease(htmlcode2)),
        'outline':  getOutline(htmlcode2),
        'runtime':  getYear(getRelease(htmlcode2)),
        'director': getStudio(htmlcode2),
        'actor':    getStudio(htmlcode2),
        'release':  getRelease(htmlcode2),
        'number':  'FC2-'+number,
        'cover':    getCover(htmlcode2),
        'imagecut': 0,
        'tag':      getTag(htmlcode2),
        'actor_photo':'',
        'website':  'http://adult.contents.fc2.com/article_search.php?id=' + number,
        'source': 'fc2fans_club.py',
    }
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),)#.encode('UTF-8')
    return js

#print(main('1145465'))