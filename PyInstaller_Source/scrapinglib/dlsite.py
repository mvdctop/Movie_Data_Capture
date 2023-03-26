# -*- coding: utf-8 -*-

import re
from .parser import Parser


class Dlsite(Parser):
    source = 'dlsite'

    expr_title = '/html/head/title/text()'
    expr_actor = '//th[contains(text(),"声优")]/../td/a/text()'
    expr_studio = '//th[contains(text(),"商标名")]/../td/span[1]/a/text()'
    expr_studio2 = '//th[contains(text(),"社团名")]/../td/span[1]/a/text()'
    expr_runtime = '//strong[contains(text(),"時長")]/../span/text()'
    expr_runtime2 = '//strong[contains(text(),"時長")]/../span/a/text()'
    expr_outline = '//*[@class="work_parts_area"]/p/text()'
    expr_series = '//th[contains(text(),"系列名")]/../td/span[1]/a/text()'
    expr_series2 = '//th[contains(text(),"社团名")]/../td/span[1]/a/text()'
    expr_director = '//th[contains(text(),"剧情")]/../td/a/text()'
    expr_release = '//th[contains(text(),"贩卖日")]/../td/a/text()'
    expr_cover = '//*[@id="work_left"]/div/div/div[2]/div/div[1]/div[1]/ul/li[1]/picture/source/@srcset'
    expr_tags = '//th[contains(text(),"分类")]/../td/div/a/text()'
    expr_label = '//th[contains(text(),"系列名")]/../td/span[1]/a/text()'
    expr_label2 = '//th[contains(text(),"社团名")]/../td/span[1]/a/text()'
    expr_extrafanart = '//*[@id="work_left"]/div/div/div[1]/div/@data-src'

    def extraInit(self):
        self.imagecut = 4
        self.allow_number_change = True

    def search(self, number):
        self.cookies = {'locale': 'zh-cn'}
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
            # TODO 应该从页面内获取 number
            self.number = str(re.findall("\wJ\w+", self.detailurl)).strip(" [']")
            htmltree = self.getHtmlTree(self.detailurl)
        elif "RJ" in number or "VJ" in number:
            self.number = number.upper()
            self.detailurl = 'https://www.dlsite.com/maniax/work/=/product_id/' + self.number + '.html/?locale=zh_CN'
            htmltree = self.getHtmlTree(self.detailurl)
        else:
            self.detailurl = f'https://www.dlsite.com/maniax/fsr/=/language/jp/sex_category/male/keyword/{number}/order/trend/work_type_category/movie'
            htmltree = self.getHtmlTree(self.detailurl)
            search_result = self.getTreeAll(htmltree, '//*[@id="search_result_img_box"]/li[1]/dl/dd[2]/div[2]/a/@href')
            if len(search_result) == 0:
                number = number.replace("THE ANIMATION", "").replace("he Animation", "").replace("t", "").replace("T","")
                htmltree = self.getHtmlTree(f'https://www.dlsite.com/maniax/fsr/=/language/jp/sex_category/male/keyword/{number}/order/trend/work_type_category/movie')
                search_result = self.getTreeAll(htmltree, '//*[@id="search_result_img_box"]/li[1]/dl/dd[2]/div[2]/a/@href')
                if len(search_result) == 0:
                    if "～" in number:
                        number = number.replace("～","〜")
                    elif "〜" in number:
                        number = number.replace("〜","～")
                    htmltree = self.getHtmlTree(f'https://www.dlsite.com/maniax/fsr/=/language/jp/sex_category/male/keyword/{number}/order/trend/work_type_category/movie')
                    search_result = self.getTreeAll(htmltree, '//*[@id="search_result_img_box"]/li[1]/dl/dd[2]/div[2]/a/@href')
                    if len(search_result) == 0:
                        number = number.replace('上巻', '').replace('下巻', '').replace('前編', '').replace('後編', '')
                        htmltree = self.getHtmlTree(f'https://www.dlsite.com/maniax/fsr/=/language/jp/sex_category/male/keyword/{number}/order/trend/work_type_category/movie')
                        search_result = self.getTreeAll(htmltree, '//*[@id="search_result_img_box"]/li[1]/dl/dd[2]/div[2]/a/@href')
            self.detailurl = search_result[0]
            htmltree = self.getHtmlTree(self.detailurl)
            self.number = str(re.findall("\wJ\w+", self.detailurl)).strip(" [']")

        result = self.dictformat(htmltree)
        return result

    def getNum(self, htmltree):
        return self.number

    def getTitle(self, htmltree):
        result = super().getTitle(htmltree)
        result = result[:result.rfind(' | DLsite')]
        result = result[:result.rfind(' [')]
        if 'OFF】' in result:
            result = result[result.find('】')+1:]
        result = result.replace('【HD版】', '')
        return result

    def getOutline(self, htmltree):
        total = []
        result = self.getTreeAll(htmltree, self.expr_outline)
        total = [ x.strip() for x in result if x.strip()]
        return '\n'.join(total)

    def getRelease(self, htmltree):
        return super().getRelease(htmltree).replace('年','-').replace('月','-').replace('日','')

    def getCover(self, htmltree):
        return 'https:' + super().getCover(htmltree).replace('.webp', '.jpg')

    def getExtrafanart(self, htmltree):
        try:
            result = []
            for i in self.getTreeAll(self.expr_extrafanart):
                result.append("https:" + i)
        except:
            result = ''
        return result
