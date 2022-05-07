import sys
sys.path.append('../')
import re
from lxml import etree#need install
from bs4 import BeautifulSoup#need install
import json
from ADC_function import *
from WebCrawler import javbus

'''
API
注册：https://www.airav.wiki/api/auth/signup
设置：https://www.airav.wiki/api/get_web_settings
搜索：https://www.airav.wiki/api/video/list?lng=zh-CN&search=
搜索：https://www.airav.wiki/api/video/list?lang=zh-TW&lng=zh-TW&search=
'''
host = 'https://www.airav.wiki'

# airav这个网站没有演员图片，所以直接使用javbus的图
def getActorPhoto(javbus_json):
    result = javbus_json.get('actor_photo')
    if isinstance(result, dict) and len(result):
        return result
    return ''

def getTitle(htmlcode):  #获取标题
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    title = str(html.xpath('/html/head/title/text()')[0])
    result = str(re.findall('](.*?)- AIRAV-WIKI', title)[0]).strip()
    return result

def getStudio(htmlcode, javbus_json): #获取厂商 已修改
    # javbus如果有数据以它为准
    result = javbus_json.get('studio')
    if isinstance(result, str) and len(result):
        return result
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    return str(html.xpath('//a[contains(@href,"?video_factory=")]/text()')).strip(" ['']")
def getYear(htmlcode, javbus_json):   #获取年份
    result = javbus_json.get('year')
    if isinstance(result, str) and len(result):
        return result
    release = getRelease(htmlcode, javbus_json)
    if len(release) != len('2000-01-01'):
        return ''
    return release[:4]
def getCover(htmlcode, javbus_json):  #获取封面图片
    result = javbus_json.get('cover')
    if isinstance(result, str) and len(result):
        return result
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    return html.xpath('//img[contains(@src,"/storage/big_pic/")]/@src')[0]
def getRelease(htmlcode, javbus_json): #获取出版日期
    result = javbus_json.get('release')
    if isinstance(result, str) and len(result):
        return result
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = re.search(r'\d{4}-\d{2}-\d{2}', str(html.xpath('//li[contains(text(),"發片日期")]/text()'))).group()
    except:
        return ''
    return result
def getRuntime(javbus_json): #获取播放时长
    result = javbus_json.get('runtime')
    if isinstance(result, str) and len(result):
        return result
    return ''
# airav女优数据库较多日文汉字姓名，javbus较多日语假名，因此airav优先
def getActor(htmlcode, javbus_json):   #获取女优
    b=[]
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    a = html.xpath('//ul[@class="videoAvstarList"]/li/a[starts-with(@href,"/idol/")]/text()')
    for v in a:
        v = v.strip()
        if len(v):
            b.append(v)
    if len(b):
        return b
    result = javbus_json.get('actor')
    if isinstance(result, list) and len(result):
        return result
    return []
def getNum(htmlcode, javbus_json):     #获取番号
    result = javbus_json.get('number')
    if isinstance(result, str) and len(result):
        return result
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    title = str(html.xpath('/html/head/title/text()')[0])
    result = str(re.findall('^\[(.*?)]', title)[0])
    return result
def getDirector(javbus_json): #获取导演 已修改
    result = javbus_json.get('director')
    if isinstance(result, str) and len(result):
        return result
    return ''
def getOutline(htmlcode):  #获取概述
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = html.xpath("string(//div[@class='d-flex videoDataBlock']/div[@class='synopsis']/p)").replace('\n','').strip()
        return result
    except:
        return ''
def getSerise(javbus_json):   #获取系列 已修改
    result = javbus_json.get('series')
    if isinstance(result, str) and len(result):
        return result
    return ''
def getTag(htmlcode):  # 获取标签
    tag = []
    soup = BeautifulSoup(htmlcode, 'lxml')
    x = soup.find_all(attrs={'class': 'tagBtnMargin'})
    a = x[0].find_all('a')

    for i in a:
        tag.append(i.get_text())
    return tag

def getExtrafanart(htmlcode):  # 获取剧照
    html_pather = re.compile(r'<div class=\"mobileImgThumbnail\">[\s\S]*?</div></div></div></div>')
    html = html_pather.search(htmlcode)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<img.*?src=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            return extrafanart_imgs
    return ''

def search(keyword): #搜索，返回结果
    result = []
    page = 1
    while page > 0:
        # search_result = {"offset": 0,"count": 4,"result": [
        #     {"vid": "99-07-15076","slug": "Wrop6o","name": "朝ゴミ出しする近所の遊び好きノーブラ奥さん 江波りゅう",
        #     "url": "","view": 98,"img_url": "https://wiki-img.airav.wiki/storage/big_pic/99-07-15076.jpg","barcode": "_1pondo_012717_472"},
        #     {"vid": "99-27-00286","slug": "DlPEua","name": "放課後に、仕込んでください 〜優等生は無言でスカートを捲り上げる〜",
        #     "url": "","view": 69,"img_url": "https://wiki-img.airav.wiki/storage/big_pic/99-27-00286.jpg","barcode": "caribbeancom012717-360"},
        #     {"vid": "99-07-15070","slug": "VLS3WY","name": "放課後に、仕込んでください ～優等生は無言でスカートを捲り上げる～ ももき希",
        #     "url": "","view": 58,"img_url": "https://wiki-img.airav.wiki/storage/big_pic/99-07-15070.jpg","barcode": "caribbeancom_012717-360"},
        #     {"vid": "99-27-00287","slug": "YdMVb3","name": "朝ゴミ出しする近所の遊び好きノーブラ奥さん 江波りゅう",
        #     "url": "","view": 56,"img_url": "https://wiki-img.airav.wiki/storage/big_pic/99-27-00287.jpg","barcode": "1pondo_012717_472"}
        # ],"status": "ok"}
        search_result = get_html(host + '/api/video/list?lang=zh-TW&lng=jp&search=' + keyword + '&page=' + str(page))

        try:
            json_data = json.loads(search_result)
        except json.decoder.JSONDecodeError:
            print("[-]Json decoder error!")
            return []

        result_offset = int(json_data["offset"])
        result_count = int(json_data["count"])
        result_size = len(json_data["result"])
        if result_count <= 0 or result_size <= 0:
            return result
        elif result_count > result_offset + result_size: #请求下一页内容
            result.extend(json_data["result"])
            page += 1
        elif result_count == result_offset + result_size: #请求最后一页内容
            result.extend(json_data["result"])
            page = 0
        else:
            page = 0

    return result

def main(number):
    try:
        try:
            htmlcode = get_html('https://cn.airav.wiki/video/' + number)
            javbus_json = json.loads(javbus.main(number))

        except:
            print(number)

        dic = {
            # 标题可使用airav
            'title': getTitle(htmlcode),
            # 制作商先找javbus，如果没有再找本站
            'studio': getStudio(htmlcode, javbus_json),
            # 年份先试javbus，如果没有再找本站
            'year': getYear(htmlcode, javbus_json),
            #  简介 使用 airav
            'outline': getOutline(htmlcode),
            # 使用javbus
            'runtime': getRuntime(javbus_json),
            # 导演 使用javbus
            'director': getDirector(javbus_json),
            # 演员 先试airav
            'actor': getActor(htmlcode, javbus_json),
            # 发售日先试javbus
            'release': getRelease(htmlcode, javbus_json),
            # 番号使用javbus
            'number': getNum(htmlcode, javbus_json),
            # 封面链接 使用javbus
            'cover': getCover(htmlcode, javbus_json),
            # 剧照获取
            'extrafanart': getExtrafanart(htmlcode),
            'imagecut': 1,
            # 使用 airav
            'tag': getTag(htmlcode),
            # 使用javbus
            'label': getSerise(javbus_json),
            'actor_photo': getActorPhoto(javbus_json),
            'website': 'https://www.airav.wiki/video/' + number,
            'source': 'airav.py',
            # 使用javbus
            'series': getSerise(javbus_json)
        }
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4,separators=(',', ':'), )  # .encode('UTF-8')
        return js
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


if __name__ == '__main__':
    config.getInstance().set_override("actor_photo:download_for_kodi=1")
    config.getInstance().set_override("debug_mode:switch=1")
    print(main('ADV-R0624'))  # javbus页面返回404, airav有数据
    print(main('ADN-188'))    # 一人
    print(main('CJOD-278'))   # 多人 javbus演员名称采用日语假名，airav采用日文汉字
