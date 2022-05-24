import sys
sys.path.append('../')
from ADC_function import *
from WebCrawler.crawler import *
import re
import time
from urllib.parse import quote

JSON_HEADERS = {"Referer": "https://dl.getchu.com/"}
COOKIES_DL = {"adult_check_flag": "1"}
COOKIES_WWW = {'getchu_adalt_flag': 'getchu.com'}

GETCHU_WWW_SEARCH_URL = 'http://www.getchu.com/php/search.phtml?genre=anime_dvd&search_keyword=_WORD_&check_key_dtl=1&submit='
GETCHU_DL_SEARCH_URL = 'https://dl.getchu.com/search/search_list.php?dojin=1&search_category_id=&search_keyword=_WORD_&btnWordSearch=%B8%A1%BA%F7&action=search&set_category_flag=1'
GETCHU_WWW_URL = 'http://www.getchu.com/soft.phtml?id=_WORD_'
GETCHU_DL_URL = 'https://dl.getchu.com/i/item_WORD_'

def get_dl_getchu(number):
    if "item" in number or 'GETCHU' in number.upper():
        number = re.findall('\d+',number)[0]
    else:
        htmlcode = get_html(GETCHU_DL_SEARCH_URL.replace("_WORD_", number),
                            json_headers=JSON_HEADERS, cookies=COOKIES_DL)
        getchu = Crawler(htmlcode)
        url = getchu.getString(
            '/html/body/div[1]/table/tr/td/table[4]/tr/td[2]/table/tr[2]/td/table/tr/td/table/tr/td[2]/div/a[1]/@href')
        if url == "":
            return None
        number = re.findall('\d+', url)[0]
    htmlcode = get_html(GETCHU_DL_URL.replace("_WORD_", number), json_headers=JSON_HEADERS, cookies=COOKIES_DL)
    getchu = Crawler(htmlcode)
    dic = {
        "title": getchu.getString("//div[contains(@style,'color: #333333; padding: 3px 0px 0px 5px;')]/text()"),
        "cover": "https://dl.getchu.com" + getchu.getString("//td[contains(@bgcolor,'#ffffff')]/img/@src"),
        "director": getchu.getString("//td[contains(text(),'作者')]/following-sibling::td/text()").strip(),
        "studio": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()").strip(),
        "actor": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()").strip(),
        "label": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()").strip(),
        "runtime": str(re.findall('\d+', str(getchu.getString(
            "//td[contains(text(),'画像数&ページ数')]/following-sibling::td/text()")))).strip(" ['']"),
        "release": getchu.getString("//td[contains(text(),'配信開始日')]/following-sibling::td/text()").replace("/", "-"),
        "tag": getchu.getStrings("//td[contains(text(),'趣向')]/following-sibling::td/a/text()"),
        "outline": getchu.getStrings("//*[contains(text(),'作品内容')]/following-sibling::td/text()"),
        "extrafanart": getchu.getStrings("//td[contains(@style,'background-color: #444444;')]/a/@href"),
        "series": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()"),
        "number": 'GETCHU-' + re.findall('\d+',number)[0],
        "imagecut": 4,
        "year": str(re.findall('\d{4}', str(getchu.getString(
            "//td[contains(text(),'配信開始日')]/following-sibling::td/text()").replace("/", "-")))).strip(" ['']"),
        "actor_photo": "",
        "website": "https://dl.getchu.com/i/" + number,
        "source": "getchu.py",
        "allow_number_change": True,
    }
    extrafanart = []
    for i in dic['extrafanart']:
        i = "https://dl.getchu.com" + i
        extrafanart.append(i)
    dic['extrafanart'] = extrafanart
    time.sleep(1)
    return dic

def get_www_getchu(number):
    number = quote(number, encoding="euc_jp")
    getchu = Crawler(get_html(GETCHU_WWW_SEARCH_URL.replace("_WORD_", number), cookies=COOKIES_WWW))
    url2 = getchu.getString('//*[@id="detail_block"]/div/table/tr[1]/td/a[1]/@href')
    if url2 == '':
        getchu = Crawler(get_html(GETCHU_WWW_SEARCH_URL.replace("_WORD_", number), cookies=COOKIES_WWW))
        url2 = getchu.getString('//*[@id="detail_block"]/div/table/tr[1]/td/a[1]/@href')
        if url2 == "":
            return None
    url2 = url2.replace('../', 'http://www.getchu.com/')
    getchu = Crawler(get_html(url2, cookies=COOKIES_WWW))
    dic = {
        "title": getchu.getString('//*[@id="soft-title"]/text()').strip(),
        "cover": "http://www.getchu.com" + getchu.getString(
            "/html/body/div[1]/table[2]/tr[1]/td/a/@href").replace("./", '/'),
        "director": getchu.getString("//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"),
        "studio": getchu.getString("//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()").strip(),
        "actor": getchu.getString("//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()").strip(),
        "label": getchu.getString("//td[contains(text(),'ジャンル：')]/following-sibling::td/text()").strip(),
        "runtime": '',
        "release": getchu.getString("//td[contains(text(),'発売日：')]/following-sibling::td/a/text()").replace("/", "-").strip(),
        "tag": getchu.getStrings("//td[contains(text(),'カテゴリ')]/following-sibling::td/a/text()"),
        "outline": getchu.getStrings("//div[contains(text(),'商品紹介')]/following-sibling::div/text()"),
        "extrafanart": getchu.getStrings("//div[contains(text(),'サンプル画像')]/following-sibling::div/a/@href"),
        "series": getchu.getString("//td[contains(text(),'ジャンル：')]/following-sibling::td/text()").strip(),
        "number": 'GETCHU-' + re.findall('\d+', url2.replace("http://www.getchu.com/soft.phtml?id=", ""))[0],
        "imagecut": 0,
        "year": str(re.findall('\d{4}', str(getchu.getString(
            "//td[contains(text(),'発売日：')]/following-sibling::td/a/text()").replace("/", "-")))).strip(" ['']"),
        "actor_photo": "",
        "website": url2,
        "headers": {'referer': url2},
        "source": "getchu.py",
        "allow_number_change": True,
    }
    extrafanart = []
    for i in dic['extrafanart']:
        i = "http://www.getchu.com" + i.replace("./", '/')
        if 'jpg' in i:
            extrafanart.append(i)
    dic['extrafanart'] = extrafanart
    time.sleep(1)
    return dic

def main(number):
    number = number.replace("-C", "")
    dic = {}
    if "item" in number:
        sort = ["get_dl_getchu(number)", "get_www_getchu(number)"]
    else:
        sort = ["get_www_getchu(number)", "get_dl_getchu(number)"]
    for i in sort:
        dic = eval(i)
        if dic != None:
            break
    if dic == None:
        return {"title" : ""}
    outline = ''
    _list = dic['outline']
    for i in _list:
        outline = outline + i
    dic['outline'] = outline

    result = json.dumps(dic,ensure_ascii=False, sort_keys=True, indent=4,separators=(',', ':'), )
    return result

if __name__ == '__main__':
    test = []
    for i in test:
        print(i)
        print(main(i))
