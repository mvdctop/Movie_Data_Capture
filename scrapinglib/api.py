# -*- coding: utf-8 -*-

import re
import json

from .airav import Airav
from .carib import Carib
from .dlsite import Dlsite
from .fanza import Fanza
from .gcolle import Gcolle
from .getchu import Getchu
from .jav321 import Jav321
from .javdb import Javdb
from .mv91 import Mv91
from .fc2 import Fc2
from .madou import Madou
from .mgstage import Mgstage
from .javbus import Javbus
from .xcity import Xcity
from .avsox import Avsox

from .tmdb import Tmdb


def search(number, sources: str=None, proxies=None, verify=None, type='adult',
            dbcookies=None, dbsite=None, morestoryline=False):
    """ 根据``番号/电影``名搜索信息

    :param number: number/name  depends on type
    :param sources: sources string with `,` like ``avsox,javbus``
    :param type: ``adult``, ``general``
    """
    sc = Scraping()
    return sc.search(number, sources, proxies=proxies, verify=verify, type=type,
                     dbcookies=dbcookies, dbsite=dbsite, morestoryline=morestoryline)

class Scraping():
    """

    只爬取内容,不经修改

    如果需要翻译等,再针对此方法封装一层
    也不做 naming rule 处理

    可以指定刮削库,可查询当前支持的刮削库

    参数:
        number
        cookies
        proxy
        sources
        TODO multi threading (加速是否会触发反爬？)

        [x] translate
        [x] naming rule
        [x] convert: actress name/tags

    """

    adult_full_sources = ['avsox', 'javbus', 'xcity', 'mgstage', 'madou', 'fc2', 
                    'dlsite', 'jav321', 'fanza', 'airav', 'carib', 'mv91',
                    'gcolle', 'javdb', 'getchu']
    adult_func_mapping = {
        'avsox': Avsox().scrape,
        'javbus': Javbus().scrape,
        'xcity': Xcity().scrape,
        'mgstage': Mgstage().scrape,
        'madou': Madou().scrape,
        'fc2': Fc2().scrape,
        'dlsite': Dlsite().scrape,
        'jav321': Jav321().scrape,
        'fanza': Fanza().scrape,
        'airav': Airav().scrape,
        'carib': Carib().scrape,
        'mv91': Mv91().scrape,
        'gcolle': Gcolle().scrape,
        'javdb': Javdb().scrape,
        'getchu': Getchu().scrape,
    }

    general_full_sources = ['tmdb']
    general_func_mapping = {
        'tmdb': Tmdb().scrape,
    }

    proxies = None
    verify = None

    dbcookies = None
    dbsite = None
    # 使用storyline方法进一步获取故事情节
    morestoryline = False

    def search(self, number, sources=None, proxies=None, verify=None, type='adult',
               dbcookies=None, dbsite=None, morestoryline=False):
        self.proxies = proxies
        self.verify = verify
        self.dbcookies = dbcookies
        self.dbsite = dbsite
        self.morestoryline = morestoryline
        if type == 'adult':
            return self.searchAdult(number, sources)
        else:
            return self.searchGeneral(number, sources)

    def searchGeneral(self, name, sources):
        """ 查询电影电视剧
        imdb,tmdb
        """
        sources = self.checkGeneralSources(sources, name)
        json_data = {}
        for source in sources:
            try:
                print('[+]select', source)
                try:
                    data = self.general_func_mapping[source](name, self)
                    if data == 404:
                        continue
                    json_data = json.loads(data)
                except Exception as e:
                    print('[!] 出错啦')
                    print(e)
                # if any service return a valid return, break
                if self.get_data_state(json_data):
                    print(f"[+]Find movie [{name}] metadata on website '{source}'")
                    break
            except:
                continue

        # Return if data not found in all sources
        if not json_data:
            print(f'[-]Movie Number [{name}] not found!')
            return None

        return json_data

    def searchAdult(self, number, sources):
        sources = self.checkAdultSources(sources, number)
        json_data = {}
        for source in sources:
            try:
                print('[+]select', source)
                try:
                    data = self.adult_func_mapping[source](number, self)
                    if data == 404:
                        continue
                    json_data = json.loads(data)
                except Exception as e:
                    print('[!] 出错啦')
                    print(e)
                    # json_data = self.func_mapping[source](number, self)
                # if any service return a valid return, break
                if self.get_data_state(json_data):
                    print(f"[+]Find movie [{number}] metadata on website '{source}'")
                    break
            except:
                continue

        # Return if data not found in all sources
        if not json_data:
            print(f'[-]Movie Number [{number}] not found!')
            return None

        return json_data

    def checkGeneralSources(self, c_sources, name):
        if not c_sources:
            sources = self.general_full_sources
        else:
            sources = c_sources.split(',')

        # check sources in func_mapping
        todel = []
        for s in sources:
            if not s in self.general_func_mapping:
                print('[!] Source Not Exist : ' + s)
                todel.append(s)
        for d in todel:
            print('[!] Remove Source : ' + s)
            sources.remove(d)
        return sources

    def checkAdultSources(self, c_sources, file_number):
        if not c_sources:
            sources = self.adult_full_sources
        else:
            sources = c_sources.split(',')
        def insert(sources,source):
            if source in sources:
                sources.insert(0, sources.pop(sources.index(source)))
            return sources

        if len(sources) <= len(self.adult_func_mapping):
            # if the input file name matches certain rules,
            # move some web service to the beginning of the list
            lo_file_number = file_number.lower()
            if "carib" in sources and (re.search(r"^\d{6}-\d{3}", file_number)
            ):
                sources = insert(sources,"carib")
            elif "item" in file_number or "GETCHU" in file_number.upper():
                sources = insert(sources,"getchu")
            elif "rj" in lo_file_number or "vj" in lo_file_number or re.search(r"[\u3040-\u309F\u30A0-\u30FF]+", file_number):
                sources = insert(sources, "getchu")
                sources = insert(sources, "dlsite")
            elif re.search(r"^\d{5,}", file_number) or "heyzo" in lo_file_number:
                if "avsox" in sources:
                    sources = insert(sources,"avsox")
            elif "mgstage" in sources and \
                    (re.search(r"\d+\D+", file_number) or "siro" in lo_file_number):
                sources = insert(sources,"mgstage")
            elif "fc2" in lo_file_number:
                if "fc2" in sources:
                    sources = insert(sources,"fc2")
            elif "gcolle" in sources and (re.search("\d{6}", file_number)):
                sources = insert(sources,"gcolle")
            elif re.search(r"^[a-z0-9]{3,}$", lo_file_number):
                if "xcity" in sources:
                    sources = insert(sources,"xcity")
                if "madou" in sources:
                    sources = insert(sources,"madou")
            elif "madou" in sources and (
                    re.search(r"^[a-z0-9]{3,}-[0-9]{1,}$", lo_file_number)
            ):
                sources = insert(sources,"madou")

        # check sources in func_mapping
        todel = []
        for s in sources:
            if not s in self.adult_func_mapping:
                print('[!] Source Not Exist : ' + s)
                todel.append(s)
        for d in todel:
            print('[!] Remove Source : ' + s)
            sources.remove(d)
        return sources

    def get_data_state(self, data: dict) -> bool:  # 元数据获取失败检测
        if "title" not in data or "number" not in data:
            return False
        if data["title"] is None or data["title"] == "" or data["title"] == "null":
            return False
        if data["number"] is None or data["number"] == "" or data["number"] == "null":
            return False
        return True
