import sys
sys.path.append('../')
import re
from pyquery import PyQuery as pq#need install
from lxml import etree#need install
from bs4 import BeautifulSoup#need install
import json
from ADC_function import *



# airav这个网站没有演员图片，所以直接使用javbus的图
def getActorPhoto(htmlcode): #//*[@id="star_qdt"]/li/a/img
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = soup.find_all(attrs={'class': 'star-name'})
    d={}
    for i in a:
        l=i.a['href']
        t=i.get_text()
        html = etree.fromstring(get_html(l), etree.HTMLParser())
        p=str(html.xpath('//*[@id="waterfall"]/div[1]/div/div[1]/img/@src')).strip(" ['']")
        p2={t:p}
        d.update(p2)
    return d

def getTitle(htmlcode):  #获取标题
    doc = pq(htmlcode)
    # h5:first-child定位第一个h5标签，妈的找了好久才找到这个语法
    title = str(doc('div.d-flex.videoDataBlock h5.d-none.d-md-block:nth-child(2)').text()).replace(' ', '-')
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
    return image.attr('href')
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
    a=soup.find_all(attrs={'class':'videoAvstarListItem'})
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

def getOutline(htmlcode):  #获取演员
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = html.xpath("string(//div[@class='d-flex videoDataBlock']/div[@class='synopsis']/p)").replace('\n','')
        return result
    except:
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
    x = soup.find_all(attrs={'class': 'tagBtnMargin'})
    a = x[0].find_all('a')

    for i in a:
        tag.append(i.get_text())
    return tag

def main(number):
    try:
        try:
            try:
                htmlcode = get_html('https://cn.airav.wiki/video/' + number)
                javbus_htmlcode = get_html('https://www.javbus.com/ja/' + number)


            except:
                print(number)

            dic = {
                # 标题可使用airav
                'title': str(re.sub('\w+-\d+-', '', getTitle(htmlcode))),
                # 制作商选择使用javbus
                'studio': getStudio(javbus_htmlcode),
                # 年份也是用javbus
                'year': str(re.search('\d{4}', getYear(javbus_htmlcode)).group()),
                #  简介 使用 airav
                'outline': getOutline(htmlcode),
                # 使用javbus
                'runtime': getRuntime(javbus_htmlcode),
                # 导演 使用javbus
                'director': getDirector(javbus_htmlcode),
                # 作者 使用airav
                'actor': getActor(htmlcode),
                # 发售日使用javbus
                'release': getRelease(javbus_htmlcode),
                # 番号使用javbus
                'number': getNum(javbus_htmlcode),
                # 封面链接 使用javbus
                'cover': getCover(javbus_htmlcode),

                'imagecut': 1,
                # 使用 airav
                'tag': getTag(htmlcode),
                # 使用javbus
                'label': getSerise(javbus_htmlcode),
                # 妈的，airav不提供作者图片
                'actor_photo': getActorPhoto(javbus_htmlcode),

                'website': 'https://www.airav.wiki/video/' + number,
                'source': 'airav.py',
                # 使用javbus
                'series': getSerise(javbus_htmlcode),
            }
            js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4,separators=(',', ':'), )  # .encode('UTF-8')
            return js
        except:
            return main_uncensored(number)
    except:
        data = {
            "title": "",
        }
        js = json.dumps(
            data, ensure_ascii=False, sort_keys=True, indent=4, separators=(",", ":")
        )
        return js


if __name__ == '__main__':
    print(main('sdsi-019'))
