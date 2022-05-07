import sys
sys.path.append('../')
from ADC_function import *
from WebCrawler.crawler import *
import re

def main(number):
    getchu = Crawler(get_html("https://dl.getchu.com/i/" + number))
    dic = {
        "title": getchu.getString("//div[contains(@style,'color: #333333; padding: 3px 0px 0px 5px;')]/text()"),
        "cover":  "https://dl.getchu.com" + getchu.getString("//td[contains(@bgcolor,'#ffffff')]/img/@src"),
        "director": getchu.getString("//td[contains(text(),'作者')]/following-sibling::td/text()"),
        "studio": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()"),
        "actor": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()"),
        "label": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()"),
        "runtime": str(re.findall('\d+', str(getchu.getString("//td[contains(text(),'画像数&ページ数')]/following-sibling::td/text()")))).strip(" ['']"),
        "release": getchu.getString("//td[contains(text(),'配信開始日')]/following-sibling::td/text()").replace("/","-"),
        "tag": getchu.getStrings("//td[contains(text(),'趣向')]/following-sibling::td/a/text()"),
        "outline": getchu.getStrings("//*[contains(text(),'作品内容')]/following-sibling::td/text()"),
        "extrafanart": getchu.getStrings("//td[contains(@style,'background-color: #444444;')]/a/@href"),
        "series": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()"),
        "number": number,
        "imagecut": 4,
        "year": str(re.findall('\d{4}', str(getchu.getString("//td[contains(text(),'配信開始日')]/following-sibling::td/text()").replace("/","-")))).strip(" ['']"),
        "actor_photo": "",
        "website": "https://dl.getchu.com/i/" + number,
        "source": "getchu.py",
    }

    extrafanart = []
    for i in dic['extrafanart']:
        i = "https://dl.getchu.com" + i
        extrafanart.append(i)
    dic['extrafanart'] = extrafanart

    outline = ''
    _list = dic['outline']
    for i in _list:
        outline = outline + i
    dic['outline'] = outline

    result = json.dumps(dic,ensure_ascii=False, sort_keys=True, indent=4,separators=(',', ':'), )
    return result

if __name__ == '__main__':
    test = ['item4040774','item4039026']
    for i in test:
        print(main(i))
