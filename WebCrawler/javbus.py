import sys
sys.path.append('../')
import re
from pyquery import PyQuery as pq#need install
from lxml import etree#need install
from bs4 import BeautifulSoup#need install
import json
from ADC_function import *
import inspect

def getActorPhoto(htmlcode): #//*[@id="star_qdt"]/li/a/img
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = soup.find_all(attrs={'class': 'star-name'})
    d={}
    for i in a:
        l=i.a['href']
        t=i.get_text()
        html = etree.fromstring(get_html(l), etree.HTMLParser())
        p=urljoin("https://www.javbus.com",
                  str(html.xpath('//*[@id="waterfall"]/div[1]/div/div[1]/img/@src')).strip(" ['']"))
        p2={t:p}
        d.update(p2)
    return d
def getTitle(htmlcode):  #获取标题
    doc = pq(htmlcode)
    title=str(doc('div.container h3').text()).replace(' ','-')
    try:
        title2 = re.sub('n\d+-','',title)
        return title2
    except:
        return title
def getStudio(htmlcode): #获取厂商 已修改
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    # 如果记录中冇导演，厂商排在第4位
    if '製作商:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/a/text()')).strip(" ['']")
    # 如果记录中有导演，厂商排在第5位
    elif '製作商:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[5]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[5]/a/text()')).strip(" ['']")
    else:
        result = ''
    return result
def getYear(htmlcode):   #获取年份
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    return result
def getCover(htmlcode):  #获取封面链接
    doc = pq(htmlcode)
    image = doc('a.bigImage')
    return urljoin("https://www.javbus.com", image.attr('href'))
def getRelease(htmlcode): #获取出版日期
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    return result
def getRuntime(htmlcode): #获取分钟 已修改
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[3]/text()')).strip(" ['']分鐘")
    return result
def getActor(htmlcode):   #获取女优
    b=[]
    soup=BeautifulSoup(htmlcode,'lxml')
    a=soup.find_all(attrs={'class':'star-name'})
    for i in a:
        b.append(i.get_text())
    return b
def getNum(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    return result
def getDirector(htmlcode): #获取导演 已修改
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    if '導演:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/a/text()')).strip(" ['']")
    else:
        result = ''         # 记录中有可能没有导演数据
    return result
def getCID(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    #print(htmlcode)
    string = html.xpath("//a[contains(@class,'sample-box')][1]/@href")[0].replace('https://pics.dmm.co.jp/digital/video/','')
    result = re.sub('/.*?.jpg','',string)
    return result
def getOutline0(number):  #获取剧情介绍 airav.wiki站点404，函数暂时更名，等无法恢复时删除
    if any(caller for caller in inspect.stack() if os.path.basename(caller.filename) == 'airav.py'):
        return ''   # 从airav.py过来的调用不计算outline直接返回，避免重复抓取数据拖慢处理速度
    try:
        htmlcode = get_html('https://cn.airav.wiki/video/' + number)
        from WebCrawler.airav import getOutline as airav_getOutline
        result = airav_getOutline(htmlcode)
        return result
    except:
        pass
    return ''
def getOutline(number):  #获取剧情介绍 从avno1.cc取得
    try:
        url = 'http://www.avno1.cc/cn/' + secrets.choice(['usercenter.php?item=' +
                secrets.choice(['pay_support', 'qa', 'contact', 'guide-vpn']),
                '?top=1&cat=hd', '?top=1', '?cat=hd', 'porn', '?cat=jp', '?cat=us', 'recommend_category.php'
        ]) # 随机选一个，避免网站httpd日志中单个ip的请求太过单一
        number_up = number.upper()
        result, browser = get_html_by_form(url,
            form_select='div.wrapper > div.header > div.search > form',
            fields = {'kw' : number_up},
            return_type = 'browser')
        if not result.ok:
            raise
        title = browser.page.select('div.type_movie > div > ul > li > div > a > h3')[0].text.strip()
        page_number = title[title.rfind(' '):].upper()
        if not number_up in page_number:
            raise
        return browser.page.select('div.type_movie > div > ul > li:nth-child(1) > div')[0]['data-description'].strip()
    except:
        pass
    from WebCrawler.xcity import open_by_browser, getOutline as xcity_getOutline
    try:
        detail_html, browser = open_by_browser(number_up)
        return xcity_getOutline(detail_html)
    except:
        pass
    return ''
def getSerise(htmlcode):   #获取系列 已修改
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    # 如果记录中冇导演，系列排在第6位
    if '系列:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[6]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[6]/a/text()')).strip(" ['']")
    # 如果记录中有导演，系列排在第7位
    elif '系列:' == str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[7]/span/text()')).strip(" ['']"):
        result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[7]/a/text()')).strip(" ['']")
    else:
        result = ''
    return result
def getTag(htmlcode):  # 获取标签
    tag = []
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = soup.find_all(attrs={'class': 'genre'})
    for i in a:
        if 'onmouseout' in str(i) or '多選提交' in str(i):
            continue
        tag.append(translateTag_to_sc(i.get_text()))
    return tag

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
    if getTitle(htmlcode) == '':
        htmlcode = get_html('https://www.javbus.com/ja/' + number.replace('-','_'))
    if "<title>404 Page Not Found" in htmlcode:
        raise Exception('404 page not found')
    dic = {
        'title': str(re.sub('\w+-\d+-','',getTitle(htmlcode))).replace(getNum(htmlcode)+'-',''),
        'studio': getStudio(htmlcode),
        'year': getYear(htmlcode),
        'outline': getOutline(number),
        'runtime': getRuntime(htmlcode),
        'director': getDirector(htmlcode),
        'actor': getActor(htmlcode),
        'release': getRelease(htmlcode),
        'number': getNum(htmlcode),
        'cover': getCover(htmlcode),
        'tag': getTag(htmlcode),
        'extrafanart': getExtrafanart(htmlcode),
        'label': getSerise(htmlcode),
        'imagecut': 0,
        'actor_photo': '',
        'website': 'https://www.javbus.com/ja/' + number,
        'source': 'javbus.py',
        'series': getSerise(htmlcode),
    }
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js


def main(number):
    try:
        try:
            try:
                htmlcode = get_html('https://www.fanbus.us/' + number)
            except:
                htmlcode = get_html('https://www.javbus.com/' + number)
            if "<title>404 Page Not Found" in htmlcode:
                raise Exception('404 page not found')
            dic = {
                'title': str(re.sub('\w+-\d+-', '', getTitle(htmlcode))),
                'studio': getStudio(htmlcode),
                'year': str(re.search('\d{4}', getYear(htmlcode)).group()),
                'outline': getOutline(number),
                'runtime': getRuntime(htmlcode),
                'director': getDirector(htmlcode),
                'actor': getActor(htmlcode),
                'release': getRelease(htmlcode),
                'number': getNum(htmlcode),
                'cover': getCover(htmlcode),
                'imagecut': 1,
                'tag': getTag(htmlcode),
                'extrafanart': getExtrafanart(htmlcode),
                'label': getSerise(htmlcode),
                'actor_photo': getActorPhoto(htmlcode),
                'website': 'https://www.javbus.com/' + number,
                'source': 'javbus.py',
                'series': getSerise(htmlcode),
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
    #print(main('ADV-R0624'))    # 404
    print(main('ipx-292'))
    print(main('CEMD-011'))
    print(main('CJOD-278'))
