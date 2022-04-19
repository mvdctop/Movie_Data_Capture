import sys
sys.path.append('../')
import re
from lxml import etree
import json
from bs4 import BeautifulSoup
from ADC_function import *
from WebCrawler.crawler import *
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

class MgsCrawler(Crawler):
    def getMgsString(self, _xpath):
        html = self.html
        result1 = str(html.xpath(_xpath)).strip(" ['']").strip('\\n    ').strip('\\n').strip(" ['']").replace(u'\\n', '').replace("', '', '", '')
        result2 = str(html.xpath(_xpath.replace('td/a/','td/'))).strip(" ['']").strip('\\n    ').strip('\\n')
        return str(result1 + result2).strip('+').replace("', '",'').replace('"','')

def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"ジャンル：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip('\\n')
    result2 = str(html.xpath('//th[contains(text(),"ジャンル：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip('\\n')
    result = str(result1 + result2).strip('+').replace("', '\\n",",").replace("', '","").replace('"','').replace(',,','').split(',')
    return result

def getExtrafanart(htmlcode2):  # 获取剧照
    html_pather = re.compile(r'<dd>\s*?<ul>[\s\S]*?</ul>\s*?</dd>')
    html = html_pather.search(htmlcode2)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<a class=\"sample_image\" href=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            return extrafanart_imgs
    return ''

def main(number2):
    number=number2.upper()
    htmlcode2=str(get_html('https://www.mgstage.com/product/product_detail/'+str(number)+'/',cookies={'adc':'1'}))
    soup = BeautifulSoup(htmlcode2, 'lxml')
    a2 = str(soup.find(attrs={'class': 'detail_data'})).replace('\n                                        ','').replace('                                ','').replace('\n                            ','').replace('\n                        ','')
    b2 = str(soup.find(attrs={'id': 'introduction'})).replace('\n                                        ','').replace('                                ','').replace('\n                            ','').replace('\n                        ','')
    htmlcode = MgsCrawler(htmlcode2)
    a = MgsCrawler(a2)
    b = MgsCrawler(b2)
    #print(b)
    dic = {
        'title': htmlcode.getString('//*[@id="center_column"]/div[1]/h1/text()').replace('/', ',').replace("\\n",'').replace('        ', '').strip(),
        'studio': a.getMgsString('//th[contains(text(),"メーカー：")]/../td/a/text()'),
        'outline': b.getString('//p/text()').strip(" ['']").replace(u'\\n', '').replace("', '', '", ''),
        'runtime': a.getMgsString('//th[contains(text(),"収録時間：")]/../td/a/text()').rstrip('mi'),
        'director': a.getMgsString('//th[contains(text(),"シリーズ")]/../td/a/text()'),
        'actor': a.getMgsString('//th[contains(text(),"出演：")]/../td/a/text()'),
        'release': a.getMgsString('//th[contains(text(),"配信開始日：")]/../td/a/text()').replace('/','-'),
        'number': a.getMgsString('//th[contains(text(),"品番：")]/../td/a/text()'),
        'cover': htmlcode.getString('//*[@id="EnlargeImage"]/@href'),
        'imagecut': 1,
        'tag': getTag(a2),
        'label': a.getMgsString('//th[contains(text(),"シリーズ：")]/../td/a/text()'),
        'extrafanart': getExtrafanart(htmlcode2),
        'year': str(re.findall('\d{4}',a.getMgsString('//th[contains(text(),"配信開始日：")]/../td/a/text()'))).strip(" ['']"),
        # str(re.search('\d{4}',getRelease(a)).group()),
        'actor_photo': '',
        'website': 'https://www.mgstage.com/product/product_detail/' + str(number) + '/',
        'source': 'mgstage.py',
        'series': a.getMgsString('//th[contains(text(),"シリーズ")]/../td/a/text()'),
    }

    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

if __name__ == '__main__':
    print(main('SIRO-4149'))
