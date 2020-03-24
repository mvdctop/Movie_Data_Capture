import re
from lxml import etree#need install
import json
import ADC_function
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

def getTitle(htmlcode): #获取厂商
    #print(htmlcode)
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[2]/div/div[1]/h3/text()')).strip(" ['']")
    result2 = str(re.sub('\D{2}2-\d+','',result)).replace(' ','',1)
    #print(result2)
    return result2
def getActor(htmlcode):
    try:
        html = etree.fromstring(htmlcode, etree.HTMLParser())
        result = str(html.xpath('/html/body/div[2]/div/div[1]/h5[5]/a/text()')).strip(" ['']")
        return result
    except:
        return ''
def getStudio(htmlcode): #获取厂商
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[2]/div/div[1]/h5[3]/a[1]/text()')).strip(" ['']")
    return result
def getNum(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    #print(result)
    return result
def getRelease(htmlcode2): #
    #a=ADC_function.get_html('http://adult.contents.fc2.com/article_search.php?id='+str(number).lstrip("FC2-").lstrip("fc2-").lstrip("fc2_").lstrip("fc2-")+'&utm_source=aff_php&utm_medium=source_code&utm_campaign=from_aff_php')
    html=etree.fromstring(htmlcode2,etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/div/div[2]/dl/dd[4]/text()')).strip(" ['']")
    return result
def getCover(htmlcode,number,htmlcode2): #获取厂商 #
    #a = ADC_function.get_html('http://adult.contents.fc2.com/article_search.php?id=' + str(number).lstrip("FC2-").lstrip("fc2-").lstrip("fc2_").lstrip("fc2-") + '&utm_source=aff_php&utm_medium=source_code&utm_campaign=from_aff_php')
    html = etree.fromstring(htmlcode2, etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/div/div[1]/a/img/@src')).strip(" ['']")
    if result == '':
        html = etree.fromstring(htmlcode, etree.HTMLParser())
        result2 = str(html.xpath('//*[@id="slider"]/ul[1]/li[1]/img/@src')).strip(" ['']")
        return 'https://fc2club.com' +  result2
    return 'http:' + result
def getOutline(htmlcode2):     #获取番号 #
    html = etree.fromstring(htmlcode2, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[1]/div[2]/div[2]/div[1]/div/article/section[4]/p/text()')).strip(" ['']").replace("\\n",'',10000).replace("'",'',10000).replace(', ,','').strip('  ').replace('。,',',')
    return result
def getTag(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[2]/div/div[1]/h5[4]/a/text()'))
    return result.strip(" ['']").replace("'",'').replace(' ','')
def getYear(release):
    try:
        result = re.search('\d{4}',release).group()
        return result
    except:
        return ''

def getTitle_fc2com(htmlcode): #获取厂商
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/h3/text()')[0]
    return result
def getActor_fc2com(htmlcode):
    try:
        html = etree.fromstring(htmlcode, etree.HTMLParser())
        result = html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()')[0]
        return result
    except:
        return ''
def getStudio_fc2com(htmlcode): #获取厂商
    try:
        html = etree.fromstring(htmlcode, etree.HTMLParser())
        result = str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()')).strip(" ['']")
        return result
    except:
        return ''
def getNum_fc2com(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    return result
def getRelease_fc2com(htmlcode2): #
    html=etree.fromstring(htmlcode2,etree.HTMLParser())
    result = str(html.xpath('//*[@id="container"]/div[1]/div/article/section[1]/div/div[2]/dl/dd[4]/text()')).strip(" ['']")
    return result
def getCover_fc2com(htmlcode2): #获取厂商 #
    html = etree.fromstring(htmlcode2, etree.HTMLParser())
    result = str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[1]/span/img/@src')).strip(" ['']")
    return 'http:' + result
def getOutline_fc2com(htmlcode2):     #获取番号 #
    html = etree.fromstring(htmlcode2, etree.HTMLParser())
    result = str(html.xpath('/html/body/div/text()')).strip(" ['']").replace("\\n",'',10000).replace("'",'',10000).replace(', ,','').strip('  ').replace('。,',',')
    return result
def getTag_fc2com(number):     #获取番号
    htmlcode = str(bytes(ADC_function.get_html('http://adult.contents.fc2.com/api/v4/article/'+number+'/tag?'),'utf-8').decode('unicode-escape'))
    result = re.findall('"tag":"(.*?)"', htmlcode)
    return result
def getYear_fc2com(release):
    try:
        result = re.search('\d{4}',release).group()
        return result
    except:
        return ''

def main(number):
    try:
        htmlcode2 = ADC_function.get_html('https://adult.contents.fc2.com/article/'+number+'/')
        htmlcode = ADC_function.get_html('https://fc2club.com//html/FC2-' + number + '.html')
        actor = getActor(htmlcode)
        if getActor(htmlcode) == '':
            actor = 'FC2系列'
        dic = {
            'title':    getTitle(htmlcode),
            'studio':   getStudio(htmlcode),
            'year': '',#str(re.search('\d{4}',getRelease(number)).group()),
            'outline':  '',#getOutline(htmlcode2),
            'runtime':  getYear(getRelease(htmlcode)),
            'director': getStudio(htmlcode),
            'actor':    actor,
            'release':  getRelease(number),
            'number':  'FC2-'+number,
            'label': '',
            'cover':    getCover(htmlcode,number,htmlcode2),
            'imagecut': 0,
            'tag':      getTag(htmlcode),
            'actor_photo':'',
            'website':  'https://fc2club.com//html/FC2-' + number + '.html',
            'source':'https://fc2club.com//html/FC2-' + number + '.html',
        }
        if dic['title'] == '':
            htmlcode2 = ADC_function.get_html('https://adult.contents.fc2.com/article/' + number + '/',cookies={'wei6H':'1'})
            actor = getActor(htmlcode)
            if getActor(htmlcode) == '':
                actor = 'FC2系列'
            dic = {
                'title': getTitle_fc2com(htmlcode2),
                'studio': getStudio_fc2com(htmlcode2),
                'year': '',  # str(re.search('\d{4}',getRelease(number)).group()),
                'outline': getOutline_fc2com(htmlcode2),
                'runtime': getYear_fc2com(getRelease(htmlcode2)),
                'director': getStudio_fc2com(htmlcode2),
                'actor': actor,
                'release': getRelease_fc2com(number),
                'number': 'FC2-' + number,
                'cover': getCover_fc2com(htmlcode2),
                'imagecut': 0,
                'tag': getTag_fc2com(number),
                'label': '',
                'actor_photo': '',
                'website': 'http://adult.contents.fc2.com/article/' + number + '/',
                'source': 'http://adult.contents.fc2.com/article/' + number + '/',
            }
    except Exception as e:
        # (TODO) better handle this
        # print(e)
        dic = {"title": ""}
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'),)#.encode('UTF-8')
    return js


#print(main('1252953'))
