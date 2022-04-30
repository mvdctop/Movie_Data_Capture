import sys
sys.path.append('../')
import re
from lxml import etree#need install
import json
import config
import ADC_function
from WebCrawler.crawler import *
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

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

def getTrailer(htmlcode, number):
    video_pather = re.compile(r'\'[a-zA-Z0-9]{32}\'')
    video = video_pather.findall(htmlcode)
    if video:
        try:
            video_url = video[0].replace('\'', '')
            video_url = 'https://adult.contents.fc2.com/api/v2/videos/' + number + '/sample?key=' + video_url
            url_json = eval(ADC_function.get_html(video_url))['path'].replace('\\', '')
            return url_json
        except:
            return ''
    else:
        return ''

def main(number):
    try:
        number = number.replace('FC2-', '').replace('fc2-', '')
        htmlcode2 = ADC_function.get_html('https://adult.contents.fc2.com/article/' + number + '/', encoding='utf-8')
        fc2_crawler = Crawler(htmlcode2)
        actor = fc2_crawler.getString('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()')
        if actor == "":
            actor = '素人'
        lx = etree.fromstring(htmlcode2, etree.HTMLParser())
        cover = fc2_crawler.getString("//div[@class='items_article_MainitemThumb']/span/img/@src")
        cover = ADC_function.urljoin('https://adult.contents.fc2.com', cover)
        release = fc2_crawler.getString('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/div[2]/p/text()').\
            strip(" ['販売日 : ']").replace('/','-')
        dic = {
            'title': fc2_crawler.getString('/html/head/title/text()'),
            'studio': fc2_crawler.getString('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()'),
            'year': re.findall('\d{4}',release)[0],
            'outline': '',  # getOutline_fc2com(htmlcode2),
            'runtime': str(lx.xpath("//p[@class='items_article_info']/text()")[0]),
            'director': fc2_crawler.getString('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()'),
            'actor': actor,
            'release': release,
            'number': 'FC2-' + number,
            'label': '',
            'cover': cover,
            'thumb': cover,
            'extrafanart': getExtrafanart(htmlcode2),
            "trailer": getTrailer(htmlcode2, number),
            'imagecut': 0,
            'tag': fc2_crawler.getStrings("//a[@class='tag tagTag']/text()"),
            'actor_photo': '',
            'website': 'https://adult.contents.fc2.com/article/' + number + '/',
            'source': 'https://adult.contents.fc2.com/article/' + number + '/',
            'series': '',
        }
    except Exception as e:
        if ADC_function.config.getInstance().debug():
            print(e)
        dic = {"title": ""}
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

if __name__ == '__main__':
    config.getInstance().set_override("debug_mode:switch=1")
    #print(main('FC2-2182382'))
    #print(main('FC2-607854'))
    print(main('FC2-2787433'))
