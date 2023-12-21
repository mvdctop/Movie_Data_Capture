# -*- coding: utf-8 -*-

import re
import json
from .parser import Parser
import config
import importlib


def search(number, sources: str = None, **kwargs):
    """ 根据`电影`名搜索信息

    :param number: number/name  depends on type
    :param sources: sources string with `,` Eg: ``
    :param type: `adult`, `general`
    """
    sc = Scraping()
    return sc.search(number, sources, **kwargs)


def getSupportedSources():
    """
    :param tag: `adult`, `general`
    """
    sc = Scraping()
    return ','.join(sc.general_full_sources)


class Scraping:
    """
    """
    adult_full_sources = []

    general_full_sources = ['tmdb', 'imdb']

    debug = False

    proxies = None
    verify = None
    specifiedSource = None
    specifiedUrl = None

    dbcookies = None
    dbsite = None
    # 使用storyline方法进一步获取故事情节
    morestoryline = False

    def search(self, number, sources=None, proxies=None, verify=None, type='adult',
               specifiedSource=None, specifiedUrl=None,
               dbcookies=None, dbsite=None, morestoryline=False,
               debug=False):
        self.debug = debug
        self.proxies = proxies
        self.verify = verify
        self.specifiedSource = specifiedSource
        self.specifiedUrl = specifiedUrl
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
        if self.specifiedSource:
            sources = [self.specifiedSource]
        else:
            sources = self.checkGeneralSources(sources, name)
        json_data = {}
        for source in sources:
            try:
                if self.debug:
                    print('[+]select', source)
                try:
                    module = importlib.import_module('.' + source, 'scrapinglib')
                    parser_type = getattr(module, source.capitalize())
                    parser: Parser = parser_type()
                    data = parser.scrape(name, self)
                    if data == 404:
                        continue
                    json_data = json.loads(data)
                except Exception as e:
                    if config.getInstance().debug():
                        print(e)
                # if any service return a valid return, break
                if self.get_data_state(json_data):
                    if self.debug:
                        print(f"[+]Find movie [{name}] metadata on website '{source}'")
                    break
            except:
                continue

        # Return if data not found in all sources
        if not json_data or json_data['title'] == "":
            return None

        # If actor is anonymous, Fill in Anonymous
        if len(json_data['actor']) == 0:
            if config.getInstance().anonymous_fill() == True:
                if "zh_" in config.getInstance().get_target_language() or "ZH" in config.getInstance().get_target_language():
                    json_data['actor'] = "佚名"
                else:
                    json_data['actor'] = "Anonymous"

        return json_data

    def searchAdult(self, number, sources):
        if self.specifiedSource:
            sources = [self.specifiedSource]
        elif type(sources) is list:
            pass
        else:
            sources = self.checkAdultSources(sources, number)
        json_data = {}
        for source in sources:
            try:
                if self.debug:
                    print('[+]select', source)
                try:
                    module = importlib.import_module('.' + source, 'scrapinglib')
                    parser_type = getattr(module, source.capitalize())
                    parser: Parser = parser_type()
                    data = parser.scrape(number, self)
                    if data == 404:
                        continue
                    json_data = json.loads(data)
                except Exception as e:
                    if config.getInstance().debug():
                        print(e)
                    # json_data = self.func_mapping[source](number, self)
                # if any service return a valid return, break
                if self.get_data_state(json_data):
                    if self.debug:
                        print(f"[+]Find movie [{number}] metadata on website '{source}'")
                    break
            except:
                continue

        # Return if data not found in all sources
        if not json_data or json_data['title'] == "":
            return None

        # If actor is anonymous, Fill in Anonymous
        if len(json_data['actor']) == 0:
            if config.getInstance().anonymous_fill() == True:
                if "zh_" in config.getInstance().get_target_language() or "ZH" in config.getInstance().get_target_language():
                    json_data['actor'] = "佚名"
                else:
                    json_data['actor'] = "Anonymous"

        return json_data

    def checkGeneralSources(self, c_sources, name):
        if not c_sources:
            sources = self.general_full_sources
        else:
            sources = c_sources.split(',')

        # check sources in func_mapping
        todel = []
        for s in sources:
            if not s in self.general_full_sources:
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

        def insert(sources, source):
            if source in sources:
                sources.insert(0, sources.pop(sources.index(source)))
            return sources

        # check sources in func_mapping
        todel = []
        for s in sources:
            if not s in self.adult_full_sources and config.getInstance().debug():
                print('[!] Source Not Exist : ' + s)
                todel.append(s)
        for d in todel:
            if config.getInstance().debug():
                print('[!] Remove Source : ' + d)
            sources.remove(d)
        return sources

    def get_data_state(self, data: dict) -> bool:  # 元数据获取失败检测
        if "title" not in data or "number" not in data:
            return False
        if data["title"] is None or data["title"] == "" or data["title"] == "null":
            return False
        if data["number"] is None or data["number"] == "" or data["number"] == "null":
            return False
        if (data["cover"] is None or data["cover"] == "" or data["cover"] == "null") \
                and (data["cover_small"] is None or data["cover_small"] == "" or
                     data["cover_small"] == "null"):
            return False
        return True