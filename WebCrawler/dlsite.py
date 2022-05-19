import re
from lxml import etree
import json
import sys
sys.path.append('../')
from ADC_function import *

def getTitle(html):
    result = str(html.xpath('/html/head/title/text()')[0])
    result = result[:result.rfind(' | DLsite')]
    result = result[:result.rfind(' [')]
    return result
def getActor(html):  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    try:
        result1 = html.xpath('//th[contains(text(),"声优")]/../td/a/text()')
    except:
        result1 = ''
    return result1
def getActorPhoto(actor): #//*[@id="star_qdt"]/li/a/img
    a = actor.split(',')
    d={}
    for i in a:
        p={i:''}
        d.update(p)
    return d
def getStudio(html):
    try:
        try:
            result = html.xpath('//th[contains(text(),"商标名")]/../td/span[1]/a/text()')[0]
        except:
            result = html.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except:
        result = ''
    return result
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')
def getLabel(html):
    try:
        try:
            result = html.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except:
            result = html.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except:
        result = ''
    return result
def getYear(getRelease):
    try:
        result = str(re.search('\d{4}', getRelease).group())
        return result
    except:
        return getRelease
def getRelease(html):
    result1 = html.xpath('//th[contains(text(),"贩卖日")]/../td/a/text()')[0]
    return result1.replace('年','-').replace('月','-').replace('日','')
def getTag(html):
    try:
        result = html.xpath('//th[contains(text(),"分类")]/../td/div/a/text()')
        return result
    except:
        return ''

def getCover_small(a, index=0):
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
    except: # 2020.7.17 Repair Cover Url crawl
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@data-src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
def getCover(html):
    result = html.xpath('//*[@id="work_left"]/div/div/div[2]/div/div[1]/div[1]/ul/li[1]/picture/source/@srcset')[0]
    return result.replace('.webp', '.jpg')
def getDirector(html):
    try:
        result = html.xpath('//th[contains(text(),"剧情")]/../td/a/text()')[0]
    except:
        result = ''
    return result
def getOutline(html):
    total = []
    result = html.xpath('//*[@class="work_parts_area"]/p/text()')
    for i in result:
        total.append(i.strip('\r\n'))
    return str(total).strip(" ['']").replace("', '', '",r'\n').replace("', '",r'\n').strip(", '', '")
def getSeries(html):
    try:
        try:
            result = html.xpath('//th[contains(text(),"系列名")]/../td/span[1]/a/text()')[0]
        except:
            result = html.xpath('//th[contains(text(),"社团名")]/../td/span[1]/a/text()')[0]
    except:
        result = ''
    return result
#
def getExtrafanart(html):
    try:
        result = []
        for i in html.xpath('//*[@id="work_left"]/div/div/div[1]/div/@data-src'):
            result.append("https:" + i)
    except:
        result = ''
    return result
def main(number):
    try:
        if "RJ" in number or "VJ" in number:
            number = number.upper()
            htmlcode = get_html('https://www.dlsite.com/maniax/work/=/product_id/' + number + '.html/?locale=zh_CN',cookies={'locale': 'zh-cn'})
            html = etree.fromstring(htmlcode, etree.HTMLParser())
        else:
            htmlcode = get_html(f'https://www.dlsite.com/maniax/fsr/=/language/jp/sex_category/male/keyword/{number}/order/trend/work_type_category/movie',cookies={'locale': 'zh-cn'})
            html = etree.HTML(htmlcode)
            a = html.xpath('//*[@id="search_result_img_box"]/li[1]/dl/dd[2]/div[2]/a/@href')[0]
            html = etree.HTML(get_html(a,cookies={'locale': 'zh-cn'}))
            number = str(re.findall("\wJ\w+",a)).strip(" [']")
        dic = {
            'actor': getStudio(html),
            'title': getTitle(html),
            'studio': getStudio(html),
            'outline': getOutline(html),
            'runtime': '',
            'director': getDirector(html),
            'release': getRelease(html),
            'number': number,
            'cover': 'https:' + getCover(html),
            'cover_small': '',
            'imagecut': 1,
            'tag': getTag(html),
            'label': getLabel(html),
            'year': getYear(getRelease(html)),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': '',
            'website': 'https://www.dlsite.com/maniax/work/=/product_id/' + number + '.html',
            'source': 'dlsite.py',
            'series': getSeries(html),
            'extrafanart':getExtrafanart(html),
            'allow_number_change':True,
        }
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
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

# main('DV-1562')
# input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
if __name__ == "__main__":
    config.getInstance().set_override("debug_mode:switch=1")
    print(main('牝教師4～穢された教壇～ 「生意気ドジっ娘女教師・美結～高飛車ハメ堕ち2濁金」'))
    print(main('RJ329607'))
