import re
from lxml import etree#need install
import json
import ADC_function

def getTitle(htmlcode): #获取厂商
    #print(htmlcode)
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[2]/div/div[1]/h3/text()')).strip(" ['']")
    result2 = str(re.sub('\D{2}2-\d+','',result)).replace(' ','',1)
    #print(result2)
    return result2
def getStudio(htmlcode): #获取厂商
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[2]/div/div[1]/h5[3]/a[1]/text()')).strip(" ['']")
    return result
def getNum(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    #print(result)
    return result
def getRelease(number):
    a=ADC_function.get_html('http://adult.contents.fc2.com/article_search.php?id='+str(number).lstrip("FC2-").lstrip("fc2-").lstrip("fc2_").lstrip("fc2-")+'&utm_source=aff_php&utm_medium=source_code&utm_campaign=from_aff_php')
    html=etree.fromstring(a,etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/div/div[2]/dl/dd[4]/text()')).strip(" ['']")
    return result
def getCover(htmlcode,number): #获取厂商
    a = ADC_function.get_html('http://adult.contents.fc2.com/article_search.php?id=' + str(number).lstrip("FC2-").lstrip("fc2-").lstrip("fc2_").lstrip("fc2-") + '&utm_source=aff_php&utm_medium=source_code&utm_campaign=from_aff_php')
    html = etree.fromstring(a, etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/div/div[1]/a/img/@src')).strip(" ['']")
    return 'http:'+result
def getOutline(htmlcode,number):     #获取番号
    a = ADC_function.get_html('http://adult.contents.fc2.com/article_search.php?id=' + str(number).lstrip("FC2-").lstrip("fc2-").lstrip("fc2_").lstrip("fc2-") + '&utm_source=aff_php&utm_medium=source_code&utm_campaign=from_aff_php')
    html = etree.fromstring(a, etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[4]/p/text()')).replace("\\n",'',10000).strip(" ['']").replace("'",'',10000)
    return result
# def getTag(htmlcode,number):     #获取番号
#     a = ADC_function.get_html('http://adult.contents.fc2.com/article_search.php?id=' + str(number).lstrip("FC2-").lstrip("fc2-").lstrip("fc2_").lstrip("fc2-") + '&utm_source=aff_php&utm_medium=source_code&utm_campaign=from_aff_php')
#     html = etree.fromstring(a, etree.HTMLParser())
#     result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[4]/p/text()')).replace("\\n",'',10000).strip(" ['']").replace("'",'',10000)
#     return result

def main(number2):
    number=number2.replace('PPV','').replace('ppv','')
    htmlcode = ADC_function.get_html('http://fc2fans.club/html/FC2-' + number + '.html')
    dic = {
        'title': getTitle(htmlcode),
        'studio': getStudio(htmlcode),
        'year': str(re.search('\d{4}',getRelease(number)).group()),
        'outline': getOutline(htmlcode,number),
        'runtime': '',
        'director': getStudio(htmlcode),
        'actor': '',
        'release': getRelease(number),
        'number': 'FC2-'+number,
        'cover': getCover(htmlcode,number),
        'imagecut': 0,
        'tag':" ",
    }
    #print(getTitle(htmlcode))
    #print(getNum(htmlcode))
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),)#.encode('UTF-8')
    return js

#print(main('1104989'))