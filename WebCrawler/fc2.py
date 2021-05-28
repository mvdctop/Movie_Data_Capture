import sys
sys.path.append('../')
import re
from lxml import etree#need install
import json
import ADC_function
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

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
    result = str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/div[2]/p/text()')).strip(" ['販売日 : ']").replace('/','-')
    return result
def getCover_fc2com(htmlcode2): #获取厂商 #
    html = etree.fromstring(htmlcode2, etree.HTMLParser())
    result = str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[1]/span/img/@src')).strip(" ['']")
    return 'http:' + result
# def getOutline_fc2com(htmlcode2):     #获取番号 #
#     xpath_html = etree.fromstring(htmlcode2, etree.HTMLParser())
#     path = str(xpath_html.xpath('//*[@id="top"]/div[1]/section[4]/iframe/@src')).strip(" ['']")
#     html = etree.fromstring(ADC_function.get_html('https://adult.contents.fc2.com/'+path), etree.HTMLParser())
#     print('https://adult.contents.fc2.com'+path)
#     print(ADC_function.get_html('https://adult.contents.fc2.com'+path,cookies={'wei6H':'1'}))
#     result = str(html.xpath('/html/body/div/text()')).strip(" ['']").replace("\\n",'',10000).replace("'",'',10000).replace(', ,','').strip('  ').replace('。,',',')
#     return result
def getTag_fc2com(number):     #获取番号
    htmlcode = str(bytes(ADC_function.get_html('http://adult.contents.fc2.com/api/v4/article/'+number+'/tag?'),'utf-8').decode('unicode-escape'))
    result = re.findall('"tag":"(.*?)"', htmlcode)
    tag = []
    for i in result:
        tag.append(ADC_function.translateTag_to_sc(i))
    return tag
def getYear_fc2com(release):
    try:
        result = re.search('\d{4}',release).group()
        return result
    except:
        return ''

def getExtrafanart(htmlcode):  # 获取剧照
    html_pather = re.compile(r'<ul class=\"items_article_SampleImagesArea\"[\s\S]*?</ul>')
    html = html_pather.search(htmlcode)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<a href=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            return extrafanart_imgs
    return ''

def getTrailer(htmlcode):
    video_pather = re.compile(r'\'[a-zA-Z0-9]{32}\'')
    video = video_pather.findall(htmlcode)
    if video:
        video_url = video[0].replace('\'', '')
        video_url = 'https://adult.contents.fc2.com/api/v2/videos/1603395/sample?key=' + video_url
        url_json = eval(ADC_function.get_html(video_url))['path'].replace('\\', '')
        return url_json
    else:
        video_url = ''

def main(number):
    try:
        number = number.replace('FC2-', '').replace('fc2-', '')
        htmlcode2 = ADC_function.get_html('https://adult.contents.fc2.com/article/' + number + '/')
        #print(htmlcode2)
        actor = getActor_fc2com(htmlcode2)
        if getActor_fc2com(htmlcode2) == '':
            actor = 'FC2系列'
        dic = {
            'title': getTitle_fc2com(htmlcode2),
            'studio': getStudio_fc2com(htmlcode2),
            'year': getYear_fc2com(getRelease_fc2com(htmlcode2)),   
            'outline': '',  # getOutline_fc2com(htmlcode2),
            'runtime': '',
            'director': getStudio_fc2com(htmlcode2),
            'actor': actor,
            'release': getRelease_fc2com(htmlcode2),
            'number': 'FC2-' + number,
            'label': '',
            'cover': getCover_fc2com(htmlcode2),
            'extrafanart': getExtrafanart(htmlcode2),
            "trailer": getTrailer(htmlcode2),
            'imagecut': 0,
            'tag': getTag_fc2com(number),
            'actor_photo': '',
            'website': 'https://adult.contents.fc2.com/article/' + number + '/',
            'source': 'https://adult.contents.fc2.com/article/' + number + '/',
            'series': '',
        }
    except Exception as e:
        if ADC_function.config.Config().debug():
            print(e)
        dic = {"title": ""}
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

if __name__ == '__main__':
    print(main('FC2-1787685'))

