# -*- coding: utf-8 -*-


import re
from urllib.parse import urljoin
from lxml import etree
from requests import session
from .httprequest import get_html_session
from .parser import Parser


class Javdb(Parser):
    source = 'javdb'

    fixstudio = False

    expr_number = '//strong[contains(text(),"番號")]/../span/text()'
    expr_number2 = '//strong[contains(text(),"番號")]/../span/a/text()'
    expr_title = "/html/head/title/text()"
    expr_runtime = '//strong[contains(text(),"時長")]/../span/text()'
    expr_runtime2 = '//strong[contains(text(),"時長")]/../span/a/text()'
    expr_uncensored = '//strong[contains(text(),"類別")]/../span/a[contains(@href,"/tags/uncensored?") or contains(@href,"/tags/western?")]'
    expr_actor = '//span[@class="value"]/a[contains(@href,"/actors/")]/text()'
    expr_actor2 = '//span[@class="value"]/a[contains(@href,"/actors/")]/../strong/@class'
    expr_release = '//strong[contains(text(),"日期")]/../span/text()'
    expr_studio = '//strong[contains(text(),"片商")]/../span/a/text()'
    expr_studio2 = '//strong[contains(text(),"賣家:")]/../span/a/text()'
    expr_director = '//strong[contains(text(),"導演")]/../span/text()'
    expr_director2 = '//strong[contains(text(),"導演")]/../span/a/text()'
    expr_cover = "//div[contains(@class, 'column-video-cover')]/a/img/@src"
    expr_cover2 = "//div[contains(@class, 'column-video-cover')]/img/@src"
    expr_extrafanart = "//article[@class='message video-panel']/div[@class='message-body']/div[@class='tile-images preview-images']/a[contains(@href,'/samples/')]/@href"
    expr_tags = '//strong[contains(text(),"類別")]/../span/a/text()'
    expr_tags2 = '//strong[contains(text(),"類別")]/../span/text()'
    expr_series = '//strong[contains(text(),"系列")]/../span/text()'
    expr_series2 = '//strong[contains(text(),"系列")]/../span/a/text()'
    expr_label = '//strong[contains(text(),"系列")]/../span/text()'
    expr_label2 = '//strong[contains(text(),"系列")]/../span/a/text()'
    expr_userrating = '//span[@class="score-stars"]/../text()'
    expr_uservotes = '//span[@class="score-stars"]/../text()'
    expr_actorphoto = '//strong[contains(text(),"演員:")]/../span/a[starts-with(@href,"/actors/")]'

    def updateCore(self, core):
        if core.proxies:
            self.proxies = core.proxies
        if core.verify:
            self.verify = core.verify
        if core.morestoryline:
            self.morestoryline = True
        # special
        if core.dbcookies:
            self.cookies = core.dbcookies
        else:
            self.cookies =  {'over18':'1', 'theme':'auto', 'locale':'zh'}
        if core.dbsite:
            self.dbsite = core.dbsite
        else:
            self.dbsite = 'javdb'

    def search(self, number):
        self.number = number
        self.session = get_html_session(cookies=self.cookies, proxies=self.proxies, verify=self.verify)
        self.detailurl = self.queryNumberUrl(number)

        self.deatilpage = self.session.get(self.detailurl).text
        htmltree = etree.fromstring(self.deatilpage, etree.HTMLParser())
        result = self.dictformat(htmltree)
        return result

    def queryNumberUrl(self, number):
        javdb_url = 'https://' + self.dbsite + '.com/search?q=' + number + '&f=all'
        try:
            resp = self.session.get(javdb_url)
        except Exception as e:
            print(e)
            raise Exception(f'[!] {self.number}: page not fond in javdb')

        htmltree = etree.fromstring(resp.text, etree.HTMLParser()) 
        # javdb sometime returns multiple results,
        # and the first elememt maybe not the one we are looking for
        # iterate all candidates and find the match one
        urls = self.getAll(htmltree, '//*[contains(@class,"movie-list")]/div/a/@href')
        # 记录一下欧美的ids  ['Blacked','Blacked']
        if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', number):
            correct_url = urls[0]
        else:
            ids = self.getAll(htmltree, '//*[contains(@class,"movie-list")]/div/a/div[contains(@class, "video-title")]/strong/text()')
            try:
                correct_url = urls[ids.index(number)]
            except:
                # 为避免获得错误番号，只要精确对应的结果
                if ids[0].upper() != number:
                    raise ValueError("number not found in javdb")
                correct_url = urls[0]
        return urljoin(resp.url, correct_url)

    def getNum(self, htmltree):
        result1 = str(self.getAll(htmltree, self.expr_number)).strip(" ['']")
        result2 = str(self.getAll(htmltree, self.expr_number2)).strip(" ['']")
        dp_number = str(result2 + result1).strip('+')
        # NOTE 检测匹配与更新 self.number
        if dp_number.upper() != self.number.upper():
            raise Exception(f'[!] {self.number}: find [{dp_number}] in javdb, not match')
        self.number = dp_number
        return self.number

    def getTitle(self, htmltree):
        browser_title = super().getTitle(htmltree)
        title = browser_title[:browser_title.find(' | JavDB')].strip()
        return title.replace(self.number, '').strip()

    def getRuntime(self, htmltree):
        result1 = str(self.getAll(htmltree, self.expr_runtime)).strip(" ['']")
        result2 = str(self.getAll(htmltree, self.expr_runtime2)).strip(" ['']")
        return str(result1 + result2).strip('+').rstrip('mi')

    def getDirector(self, htmltree):
        result1 = str(self.getAll(htmltree, self.expr_director)).strip(" ['']")
        result2 = str(self.getAll(htmltree, self.expr_director2)).strip(" ['']")
        return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
    
    def getSeries(self, htmltree):
        result1 = str(self.getAll(htmltree, self.expr_series)).strip(" ['']")
        result2 = str(self.getAll(htmltree, self.expr_series2)).strip(" ['']")
        result = str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
        if not result and self.fixstudio:
            result = self.getStudio(htmltree)
        return result

    def getLabel(self, htmltree):
        result1 = str(self.getAll(htmltree, self.expr_label)).strip(" ['']")
        result2 = str(self.getAll(htmltree, self.expr_label2)).strip(" ['']")
        result = str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
        if not result and self.fixstudio:
            result = self.getStudio(htmltree)
        return result

    def getActors(self, htmltree):
        actors = self.getAll(htmltree, self.expr_actor)
        genders = self.getAll(htmltree, self.expr_actor2)
        r = []
        idx = 0
        # NOTE only female, we dont care others
        actor_gendor = 'female'
        for act in actors:
            if((actor_gendor == 'all')
            or (actor_gendor == 'both' and genders[idx] in ['symbol female', 'symbol male'])
            or (actor_gendor == 'female' and genders[idx] == 'symbol female')
            or (actor_gendor == 'male' and genders[idx] == 'symbol male')):
                r.append(act)
            idx = idx + 1
        if re.match(r'FC2-[\d]+', self.number, re.A) and not r:
            r = '素人'
            self.fixstudio = True
        return r

    def getOutline(self, htmltree):
        if self.morestoryline:
            from .storyline import getStoryline
            return getStoryline(self.number, self.getUncensored(htmltree))
        return ''

    def getStudio(self, htmltree):
        try:
            return self.getAll(htmltree, self.expr_studio).strip(" ['']")
        except:
            pass
        try:
            return self.getAll(htmltree, self.expr_studio2).strip(" ['']")
        except:
            return ''

    def getTrailer(self, htmltree):
        video_pather = re.compile(r'<video id\=\".*?>\s*?<source src=\"(.*?)\"')
        video = video_pather.findall(self.deatilpage)
        # 加上数组判空
        if video and video[0] != "":
            if not 'https:' in video[0]:
                video_url = 'https:' + video[0]
            else:
                video_url = video[0]
        else:
            video_url = ''
        return video_url
    
    def getTags(self, htmltree):
        try:
            return self.getAll(htmltree, self.expr_tags)
        except:
            pass
        try:
            return self.getAll(htmltree, self.expr_tags2)
        except:
            return ''

    def getUserRating(self, htmltree):
        try:
            result = str(self.getTreeIndex(htmltree, self.expr_userrating))
            v = re.findall(r'(\d+|\d+\.\d+)分, 由(\d+)人評價', result)
            return float(v[0][0])
        except:
            return

    def getUserVotes(self, htmltree):
        try:
            result = str(self.getTreeIndex(htmltree, self.expr_uservotes))
            v = re.findall(r'(\d+|\d+\.\d+)分, 由(\d+)人評價', result)
            return int(v[0][1])
        except:
            return

    def getaphoto(self, url, session):
        html_page = session.get(url).text
        img_url = re.findall(r'<span class\=\"avatar\" style\=\"background\-image\: url\((.*?)\)', html_page)
        return img_url[0] if img_url else ''

    def getActorPhoto(self, htmltree):
        actorall = self.getAll(htmltree, self.expr_actorphoto)
        if not actorall:
            return {}
        actors = self.getActors(htmltree)
        actor_photo = {}
        for i in actorall:
            x = re.findall(r'/actors/(.*)', i.attrib['href'], re.A)
            if not len(x) or not len(x[0]) or i.text not in actors:
                continue
            # NOTE: https://c1.jdbstatic.com 会经常变动，直接使用页面内的地址获取
            # actor_id = x[0]
            # pic_url = f"https://c1.jdbstatic.com/avatars/{actor_id[:2].lower()}/{actor_id}.jpg"
            # if not self.session.head(pic_url).ok:
            try:
                pic_url = self.getaphoto(urljoin('https://javdb.com', i.attrib['href']), self.session)
                if len(pic_url):
                    actor_photo[i.text] = pic_url
            except:
                pass
        return actor_photo

