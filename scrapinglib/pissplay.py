# -*- coding: utf-8 -*-

import re
from lxml import etree
from .parser import Parser
from datetime import datetime

# 搜刮 https://pissplay.com/ 中的视频
# pissplay中的视频没有番号，所以要通过文件名搜索
# 只用文件名和网站视频名完全一致时才可以被搜刮
class Pissplay(Parser):
    source = 'pissplay'

    expr_number = '//*[@id="video_title"]/text()' #这个网站上的视频没有番号，因此用标题代替
    expr_title = '//*[@id="video_title"]/text()'
    expr_cover = '/html/head//meta[@property="og:image"]/@content'
    expr_tags = '//div[@id="video_tags"]/a/text()'
    expr_release = '//div[@class="video_date"]/text()'       
    expr_outline = '//*[@id="video_description"]/p//text()'

    def extraInit(self):
        self.imagecut = 0 # 不裁剪封面
        self.specifiedSource = None
        
    def search(self, number):
        self.number = number.strip().upper()
        if self.specifiedUrl:
            self.detailurl = self.specifiedUrl
        else:
            newName = re.sub(r"[^a-zA-Z0-9 ]", "", number) # 删除特殊符号
            self.detailurl = "https://pissplay.com/videos/" + newName.lower().replace(" ","-") + "/"
        self.htmlcode = self.getHtml(self.detailurl)
        if self.htmlcode == 404:
            return 404
        htmltree = etree.fromstring(self.htmlcode, etree.HTMLParser())
        result = self.dictformat(htmltree)
        return result

    def getNum(self, htmltree):
        title = self.getTitle(htmltree)
        return title
    
    def getTitle(self, htmltree):
        title = super().getTitle(htmltree)
        title = re.sub(r"[^a-zA-Z0-9 ]", "", title) # 删除特殊符号
        return title

    def getCover(self, htmltree):
        url = super().getCover(htmltree)
        if not url.startswith('http'):
            url = 'https:' + url
        return url

    def getRelease(self, htmltree):
        releaseDate = super().getRelease(htmltree)
        isoData = datetime.strptime(releaseDate, '%d %b %Y').strftime('%Y-%m-%d')
        return isoData
    
    def getStudio(self, htmltree):
        return 'PissPlay'
    
    def getTags(self, htmltree):
        tags = self.getTreeAll(htmltree, self.expr_tags)
        if 'Guests' in tags:
            if tags[0] == 'Collaboration' or tags[0] == 'Toilet for a Day' or tags[0] == 'Collaboration':
                del tags[1]
            else:
                tags = tags[1:]
        return tags
    
    def getActors(self, htmltree) -> list:
        tags = self.getTreeAll(htmltree, self.expr_tags)
        if 'Guests' in tags:
            if tags[0] == 'Collaboration' or tags[0] == 'Toilet for a Day' or tags[0] == 'Collaboration':
                return [tags[1]]
            else:
                return [tags[0]]
        else:
            return ['Bruce and Morgan']
    
    def getOutline(self, htmltree):
        outline = self.getTreeAll(htmltree, self.expr_outline)
        if '– Morgan xx' in outline:
            num = outline.index('– Morgan xx')
            outline = outline[:num]
        rstring = ''.join(outline).replace("&","and")
        return rstring
