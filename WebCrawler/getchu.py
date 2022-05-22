import sys
sys.path.append('../')
from ADC_function import *
from WebCrawler.crawler import *
import re
from urllib.parse import quote

def get_itemxxx_web(number):
    getchu = Crawler(get_html("https://dl.getchu.com/i/" + number))
    dic = {
        "title": getchu.getString("//div[contains(@style,'color: #333333; padding: 3px 0px 0px 5px;')]/text()"),
        "cover": "https://dl.getchu.com" + getchu.getString("//td[contains(@bgcolor,'#ffffff')]/img/@src"),
        "director": getchu.getString("//td[contains(text(),'作者')]/following-sibling::td/text()"),
        "studio": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()"),
        "actor": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()"),
        "label": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()"),
        "runtime": str(re.findall('\d+', str(getchu.getString(
            "//td[contains(text(),'画像数&ページ数')]/following-sibling::td/text()")))).strip(" ['']"),
        "release": getchu.getString("//td[contains(text(),'配信開始日')]/following-sibling::td/text()").replace("/",
                                                                                                           "-"),
        "tag": getchu.getStrings("//td[contains(text(),'趣向')]/following-sibling::td/a/text()"),
        "outline": getchu.getStrings("//*[contains(text(),'作品内容')]/following-sibling::td/text()"),
        "extrafanart": getchu.getStrings("//td[contains(@style,'background-color: #444444;')]/a/@href"),
        "series": getchu.getString("//td[contains(text(),'サークル')]/following-sibling::td/a/text()"),
        "number": number,
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
    return dic

def main(number):
    if "item" in number:
        dic = get_itemxxx_web(number)
    else:
        display_number = number #quote(number,encoding="GBK")
        htmlcode = get_html(f'http://www.getchu.com/php/search.phtml?genre=anime_dvd&search_keyword={number}&'
                            f'check_key_dtl=1&submit=',cookies={'getchu_adalt_flag':'getchu.com'})
        getchu = Crawler(htmlcode)
        url2 = getchu.getString('//*[@id="detail_block"]/div/table/tr[1]/td/a[1]/@href')
        if url2 == '':
            number = quote(number,encoding="euc_jp")
            htmlcode = get_html(f'http://www.getchu.com/php/search.phtml?genre=anime_dvd&search_keyword={number}'
                                f'&check_key_dtl=1&submit=', cookies={'getchu_adalt_flag': 'getchu.com'})
            getchu = Crawler(htmlcode)
            url2 = getchu.getString('//*[@id="detail_block"]/div/table/tr[1]/td/a[1]/@href')
        if "id=" in url2:
            url2 = url2.replace('../', 'http://www.getchu.com/')
            htmlcode = get_html(url2,cookies={'getchu_adalt_flag':'getchu.com'})
            getchu = Crawler(htmlcode)
            dic = {
                "title": getchu.getString('//*[@id="soft-title"]/text()').strip(),
                "cover": "http://www.getchu.com" + getchu.getString(
                    "/html/body/div[1]/table[2]/tr[1]/td/a/@href").replace("./", '/'),
                "director": getchu.getString("//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"),
                "studio": getchu.getString("//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"),
                "actor": getchu.getString("//td[contains(text(),'ブランド')]/following-sibling::td/a[1]/text()"),
                "label": getchu.getString("//td[contains(text(),'ジャンル：')]/following-sibling::td/text()").strip(),
                "runtime": '',
                "release": getchu.getString("//td[contains(text(),'発売日：')]/following-sibling::td/a/text()").replace("/","-").strip(),
                "tag": getchu.getStrings("//td[contains(text(),'カテゴリ')]/following-sibling::td/a/text()"),
                "outline": getchu.getStrings("//div[contains(text(),'商品紹介')]/following-sibling::div/text()"),
                "extrafanart": getchu.getStrings("//div[contains(text(),'サンプル画像')]/following-sibling::div/a/@href"),
                "series": getchu.getString("//td[contains(text(),'ジャンル：')]/following-sibling::td/text()").strip(),
                "number": display_number,
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
        else:
            #number = quote(number, encoding="euc_jp")
            htmlcode = get_html(f'https://dl.getchu.com/search/search_list.php?dojin=1&search_category_id=&'
                                f'search_keyword={number}&btnWordSearch=%B8%A1%BA%F7&action=search&set_category_flag=1',
                                json_headers = {"Referer": "https://dl.getchu.com/"},cookies={"adult_check_flag":"1"})
            getchu = Crawler(htmlcode)
            url2 = getchu.getString('/html/body/div[1]/table/tr/td/table[4]/tr/td[2]/table/tr[2]/td/table/tr/td/table/tr/td[2]/div/a[1]/@href')
            if "i/item" in url2:
                dic = get_itemxxx_web(re.findall('item\d+',url2)[0])
            else:
                number = quote(number, encoding="euc_jp")
                htmlcode = get_html(f'https://dl.getchu.com/search/search_list.php?dojin=1&search_category_id=&'
                                    f'search_keyword={number}&btnWordSearch=%B8%A1%BA%F7&action=search&set_category_flag=1',
                                    json_headers={"Referer": "https://dl.getchu.com/"},cookies={"adult_check_flag": "1"})
                getchu = Crawler(htmlcode)
                url2 = getchu.getString(
                    '/html/body/div[1]/table/tr/td/table[4]/tr/td[2]/table/tr[2]/td/table/tr/td/table/tr/td[2]/div/a[1]/@href')
                if "i/item" in url2:
                    dic = get_itemxxx_web(re.findall('item\d+', url2)[0])
                else:
                    return {'title':''}
    outline = ''
    _list = dic['outline']
    for i in _list:
        outline = outline + i
    dic['outline'] = outline

    result = json.dumps(dic,ensure_ascii=False, sort_keys=True, indent=4,separators=(',', ':'), )
    return result

if __name__ == '__main__':
    test = ['こすっち094','なちゅらるばけーしょん','item4039026']
    for i in test:
        print(main(i))
