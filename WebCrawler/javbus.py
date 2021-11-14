import sys
sys.path.append('../')
import re
from lxml import etree#need install
import json
from ADC_function import *
from WebCrawler.storyline import getStoryline
import inspect

def getActorPhoto(html):
    actors = html.xpath('//div[@class="star-name"]/a')
    d={}
    for i in actors:
        url=i.attrib['href']
        t=i.attrib['title']
        html = etree.fromstring(get_html(url), etree.HTMLParser())
        p=urljoin("https://www.javbus.com",
                  str(html.xpath('//*[@id="waterfall"]/div[1]/div/div[1]/img/@src')).strip(" ['']"))
        p2={t:p}
        d.update(p2)
    return d
def getTitle(html):  #获取标题
    title = str(html.xpath('/html/head/title/text()')[0])
    title = str(re.findall('^.+?\s+(.*) - JavBus$', title)[0]).strip()
    return title
def getStudioJa(html):
    x = html.xpath('//span[contains(text(),"メーカー:")]/../a/text()')
    return str(x[0]) if len(x) else ''
def getStudio(html): #获取厂商
    x = html.xpath('//span[contains(text(),"製作商:")]/../a/text()')
    return str(x[0]) if len(x) else ''
def getYear(html):   #获取年份
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']").strip()
    return result[:4] if len(result)>=len('2000-01-01') else ''
def getCover(html):  #获取封面链接
    image = str(html.xpath('//a[@class="bigImage"]/@href')[0])
    return urljoin("https://www.javbus.com", image)
def getRelease(html): #获取出版日期
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    return result
def getRuntime(html): #获取分钟 已修改
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[3]/text()')).strip(" ['']分鐘")
    return result
def getActor(html):   #获取女优
    b=[]
    actors = html.xpath('//div[@class="star-name"]/a')
    for i in actors:
        b.append(i.attrib['title'])
    return b
def getNum(html):     #获取番号
    kwdlist = html.xpath('/html/head/meta[@name="keywords"]/@content')[0].split(',')
    return kwdlist[0]
def getDirectorJa(html):
    x = html.xpath('//span[contains(text(),"監督:")]/../a/text()')
    return str(x[0]) if len(x) else ''
def getDirector(html): #获取导演
    x = html.xpath('//span[contains(text(),"導演:")]/../a/text()')
    return str(x[0]) if len(x) else ''
def getCID(html):
    string = html.xpath("//a[contains(@class,'sample-box')][1]/@href")[0].replace('https://pics.dmm.co.jp/digital/video/','')
    result = re.sub('/.*?.jpg','',string)
    return result
def getOutline(number, title):  #获取剧情介绍 多进程并发查询
    if any(caller for caller in inspect.stack() if os.path.basename(caller.filename) == 'airav.py'):
        return ''   # 从airav.py过来的调用不计算outline直接返回，避免重复抓取数据拖慢处理速度
    return getStoryline(number,title)
def getSeriseJa(html):
    x = html.xpath('//span[contains(text(),"シリーズ:")]/../a/text()')
    return str(x[0]) if len(x) else ''
def getSerise(html):   #获取系列
    x = html.xpath('//span[contains(text(),"系列:")]/../a/text()')
    return str(x[0]) if len(x) else ''
def getTag(html):  # 获取标签
    klist = html.xpath('/html/head/meta[@name="keywords"]/@content')[0].split(',')
    return klist[1:]
def getExtrafanart(htmlcode):  # 获取剧照
    html_pather = re.compile(r'<div id=\"sample-waterfall\">[\s\S]*?</div></a>\s*?</div>')
    html = html_pather.search(htmlcode)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<a class=\"sample-box\" href=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            return [urljoin('https://www.javbus.com',img) for img in extrafanart_imgs]
    return ''

def main_uncensored(number):
    htmlcode = get_html('https://www.javbus.com/ja/' + number)
    if "<title>404 Page Not Found" in htmlcode:
        raise Exception('404 page not found')
    lx = etree.fromstring(htmlcode, etree.HTMLParser())
    title = getTitle(lx)
    dic = {
        'title': title,
        'studio': getStudioJa(lx),
        'year': getYear(lx),
        'outline': getOutline(number, title),
        'runtime': getRuntime(lx),
        'director': getDirectorJa(lx),
        'actor': getActor(lx),
        'release': getRelease(lx),
        'number': getNum(lx),
        'cover': getCover(lx),
        'tag': getTag(lx),
        'extrafanart': getExtrafanart(htmlcode),
        'label': getSeriseJa(lx),
        'imagecut': 0,
#        'actor_photo': '',
        'website': 'https://www.javbus.com/ja/' + number,
        'source': 'javbus.py',
        'series': getSeriseJa(lx),
    }
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js


def main(number):
    try:
        try:
            url = "https://www." + secrets.choice([
                'buscdn.fun', 'busdmm.fun', 'busfan.fun', 'busjav.fun',
                'cdnbus.fun',
                'dmmbus.fun', 'dmmsee.fun',
                'fanbus.us',
                'seedmm.fun',
                ]) + "/"
            try:
                htmlcode = get_html(url + number)
            except:
                htmlcode = get_html('https://www.javbus.com/' + number)
            if "<title>404 Page Not Found" in htmlcode:
                raise Exception('404 page not found')
            lx = etree.fromstring(htmlcode,etree.HTMLParser())
            title = getTitle(lx)
            dic = {
                'title': title,
                'studio': getStudio(lx),
                'year': getYear(lx),
                'outline': getOutline(number, title),
                'runtime': getRuntime(lx),
                'director': getDirector(lx),
                'actor': getActor(lx),
                'release': getRelease(lx),
                'number': getNum(lx),
                'cover': getCover(lx),
                'imagecut': 1,
                'tag': getTag(lx),
                'extrafanart': getExtrafanart(htmlcode),
                'label': getSerise(lx),
#                'actor_photo': getActorPhoto(lx),
                'website': 'https://www.javbus.com/' + number,
                'source': 'javbus.py',
                'series': getSerise(lx),
            }
            js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4,separators=(',', ':'), )  # .encode('UTF-8')
            return js
        except:
            return main_uncensored(number)
    except Exception as e:
        if config.getInstance().debug():
            print(e)
        data = {
            "title": "",
        }
        js = json.dumps(
            data, ensure_ascii=False, sort_keys=True, indent=4, separators=(",", ":")
        )
        return js

if __name__ == "__main__" :
    config.G_conf_override['debug_mode:switch'] = True
    print(main('ABP-888'))
    print(main('ABP-960'))
    print(main('ADV-R0624'))    # 404
    print(main('MMNT-010'))
    print(main('ipx-292'))
    print(main('CEMD-011'))
    print(main('CJOD-278'))
    print(main('100221_001'))
    print(main('AVSW-061'))
