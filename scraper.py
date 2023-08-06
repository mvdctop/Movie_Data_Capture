# build-in lib
import json
import secrets
import typing
from pathlib import Path

# third party lib
import opencc
from lxml import etree
# project wide definitions
import config
from ADC_function import (translate,
                          load_cookies,
                          file_modification_days,
                          delete_all_elements_in_str,
                          delete_all_elements_in_list
                          )
from scrapinglib.api import search


def get_data_from_json(
        file_number: str,
        open_cc: opencc.OpenCC,
        specified_source: str, specified_url: str) -> typing.Optional[dict]:
    """
    iterate through all services and fetch the data 从网站上查询片名解析JSON返回元数据
    :param file_number: 影片名称
    :param open_cc: 简繁转换器
    :param specified_source: 指定的媒体数据源
    :param specified_url: 指定的数据查询地址, 目前未使用
    :return 给定影片名称的具体信息
    """
    try:
        actor_mapping_data = etree.parse(str(Path.home() / '.local' / 'share' / 'mdc' / 'mapping_actor.xml'))
        info_mapping_data = etree.parse(str(Path.home() / '.local' / 'share' / 'mdc' / 'mapping_info.xml'))
    except:
        actor_mapping_data = etree.fromstring("<html></html>", etree.HTMLParser())
        info_mapping_data = etree.fromstring("<html></html>", etree.HTMLParser())

    conf = config.getInstance()
    # default fetch order list, from the beginning to the end
    sources = conf.sources()

    # TODO 准备参数
    # - 清理 ADC_function, webcrawler
    proxies: dict = None
    config_proxy = conf.proxy()
    if config_proxy.enable:
        proxies = config_proxy.proxies()

    # javdb website logic
    # javdb have suffix
    javdb_sites = conf.javdb_sites().split(',')
    for i in javdb_sites:
        javdb_sites[javdb_sites.index(i)] = "javdb" + i
    javdb_sites.append("javdb")
    # 不加载过期的cookie，javdb登录界面显示为7天免登录，故假定cookie有效期为7天
    has_valid_cookie = False
    for cj in javdb_sites:
        javdb_site = cj
        cookie_json = javdb_site + '.json'
        cookies_dict, cookies_filepath = load_cookies(cookie_json)
        if isinstance(cookies_dict, dict) and isinstance(cookies_filepath, str):
            cdays = file_modification_days(cookies_filepath)
            if cdays < 7:
                javdb_cookies = cookies_dict
                has_valid_cookie = True
                break
            elif cdays != 9999:
                print(
                    f'[!]Cookies file {cookies_filepath} was updated {cdays} days ago, it will not be used for HTTP requests.')
    if not has_valid_cookie:
        # get real random site from javdb_sites, because random is not really random when the seed value is known
        javdb_site = secrets.choice(javdb_sites)
        javdb_cookies = None

    ca_cert = None
    if conf.cacert_file():
        ca_cert = conf.cacert_file()

    json_data = search(file_number, sources, proxies=proxies, verify=ca_cert,
                        dbsite=javdb_site, dbcookies=javdb_cookies,
                        morestoryline=conf.is_storyline(),
                        specifiedSource=specified_source, specifiedUrl=specified_url,
                        debug = conf.debug())
    # Return if data not found in all sources
    if not json_data:
        print('[-]Movie Number not found!')
        return None

    # 增加number严格判断，避免提交任何number，总是返回"本橋実来 ADZ335"，这种返回number不一致的数据源故障
    # 目前选用number命名规则是javdb.com Domain Creation Date: 2013-06-19T18:34:27Z
    # 然而也可以跟进关注其它命名规则例如airav.wiki Domain Creation Date: 2019-08-28T07:18:42.0Z
    # 如果将来javdb.com命名规则下不同Studio出现同名碰撞导致无法区分，可考虑更换规则，更新相应的number分析和抓取代码。
    if str(json_data.get('number')).upper() != file_number.upper():
        try:
            if json_data.get('allow_number_change'):
                pass
        except:
            print('[-]Movie number has changed! [{}]->[{}]'.format(file_number, str(json_data.get('number'))))
            return None

    # ================================================网站规则添加结束================================================

    if json_data.get('title') == '':
        print('[-]Movie Number or Title not found!')
        return None

    title = json_data.get('title')
    actor_list = str(json_data.get('actor')).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    actor_list = [actor.strip() for actor in actor_list]  # 去除空白
    director = json_data.get('director')
    release = json_data.get('release')
    number = json_data.get('number')
    studio = json_data.get('studio')
    source = json_data.get('source')
    runtime = json_data.get('runtime')
    outline = json_data.get('outline')
    label = json_data.get('label')
    series = json_data.get('series')
    year = json_data.get('year')

    if json_data.get('cover_small'):
        cover_small = json_data.get('cover_small')
    else:
        cover_small = ''

    if json_data.get('trailer'):
        trailer = json_data.get('trailer')
    else:
        trailer = ''

    if json_data.get('extrafanart'):
        extrafanart = json_data.get('extrafanart')
    else:
        extrafanart = ''

    imagecut = json_data.get('imagecut')
    tag = str(json_data.get('tag')).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    while 'XXXX' in tag:
        tag.remove('XXXX')
    while 'xxx' in tag:
        tag.remove('xxx')
    if json_data['source'] =='pissplay': # pissplay actor为英文名，不用去除空格
        actor = str(actor_list).strip("[ ]").replace("'", '')
    else:
        actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    # if imagecut == '3':
    #     DownloadFileWithFilename()

    # ====================处理异常字符====================== #\/:*?"<>|
    actor = special_characters_replacement(actor)
    actor_list = [special_characters_replacement(a) for a in actor_list]
    title = special_characters_replacement(title)
    label = special_characters_replacement(label)
    outline = special_characters_replacement(outline)
    series = special_characters_replacement(series)
    studio = special_characters_replacement(studio)
    director = special_characters_replacement(director)
    tag = [special_characters_replacement(t) for t in tag]
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')
    # ====================处理异常字符 END================== #\/:*?"<>|

    # 处理大写
    if conf.number_uppercase():
        json_data['number'] = number.upper()

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['original_title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    json_data['year'] = year
    json_data['actor_list'] = actor_list
    json_data['trailer'] = trailer
    json_data['extrafanart'] = extrafanart
    json_data['label'] = label
    json_data['outline'] = outline
    json_data['series'] = series
    json_data['studio'] = studio
    json_data['director'] = director

    if conf.is_translate():
        translate_values = conf.translate_values().split(",")
        for translate_value in translate_values:
            if json_data[translate_value] == "":
                continue
            if translate_value == "title":
                title_dict = json.loads(
                    (Path.home() / '.local' / 'share' / 'mdc' / 'c_number.json').read_text(encoding="utf-8"))
                try:
                    json_data[translate_value] = title_dict[number]
                    continue
                except:
                    pass
            if conf.get_translate_engine() == "azure":
                t = translate(
                    json_data[translate_value],
                    target_language="zh-Hans",
                    engine=conf.get_translate_engine(),
                    key=conf.get_translate_key(),
                )
            else:
                if len(json_data[translate_value]):
                    if type(json_data[translate_value]) == str:
                        json_data[translate_value] = special_characters_replacement(json_data[translate_value])
                        json_data[translate_value] = translate(json_data[translate_value])
                    else:
                        for i in range(len(json_data[translate_value])):
                            json_data[translate_value][i] = special_characters_replacement(
                                json_data[translate_value][i])
                        list_in_str = ",".join(json_data[translate_value])
                        json_data[translate_value] = translate(list_in_str).split(',')

    if open_cc:
        cc_vars = conf.cc_convert_vars().split(",")
        ccm = conf.cc_convert_mode()

        def convert_list(mapping_data, language, vars):
            total = []
            for i in vars:
                if len(mapping_data.xpath('a[contains(@keyword, $name)]/@' + language, name=f",{i},")) != 0:
                    i = mapping_data.xpath('a[contains(@keyword, $name)]/@' + language, name=f",{i},")[0]
                total.append(i)
            return total

        def convert(mapping_data, language, vars):
            if len(mapping_data.xpath('a[contains(@keyword, $name)]/@' + language, name=vars)) != 0:
                return mapping_data.xpath('a[contains(@keyword, $name)]/@' + language, name=vars)[0]
            else:
                raise IndexError('keyword not found')

        for cc in cc_vars:
            if json_data[cc] == "" or len(json_data[cc]) == 0:
                continue
            if cc == "actor":
                try:
                    if ccm == 1:
                        json_data['actor_list'] = convert_list(actor_mapping_data, "zh_cn", json_data['actor_list'])
                        json_data['actor'] = convert(actor_mapping_data, "zh_cn", json_data['actor'])
                    elif ccm == 2:
                        json_data['actor_list'] = convert_list(actor_mapping_data, "zh_tw", json_data['actor_list'])
                        json_data['actor'] = convert(actor_mapping_data, "zh_tw", json_data['actor'])
                    elif ccm == 3:
                        json_data['actor_list'] = convert_list(actor_mapping_data, "jp", json_data['actor_list'])
                        json_data['actor'] = convert(actor_mapping_data, "jp", json_data['actor'])
                except:
                    json_data['actor_list'] = [open_cc.convert(aa) for aa in json_data['actor_list']]
                    json_data['actor'] = open_cc.convert(json_data['actor'])
            elif cc == "tag":
                try:
                    if ccm == 1:
                        json_data[cc] = convert_list(info_mapping_data, "zh_cn", json_data[cc])
                        json_data[cc] = delete_all_elements_in_list("删除", json_data[cc])
                    elif ccm == 2:
                        json_data[cc] = convert_list(info_mapping_data, "zh_tw", json_data[cc])
                        json_data[cc] = delete_all_elements_in_list("删除", json_data[cc])
                    elif ccm == 3:
                        json_data[cc] = convert_list(info_mapping_data, "jp", json_data[cc])
                        json_data[cc] = delete_all_elements_in_list("删除", json_data[cc])
                except:
                    json_data[cc] = [open_cc.convert(t) for t in json_data[cc]]
            else:
                try:
                    if ccm == 1:
                        json_data[cc] = convert(info_mapping_data, "zh_cn", json_data[cc])
                        json_data[cc] = delete_all_elements_in_str("删除", json_data[cc])
                    elif ccm == 2:
                        json_data[cc] = convert(info_mapping_data, "zh_tw", json_data[cc])
                        json_data[cc] = delete_all_elements_in_str("删除", json_data[cc])
                    elif ccm == 3:
                        json_data[cc] = convert(info_mapping_data, "jp", json_data[cc])
                        json_data[cc] = delete_all_elements_in_str("删除", json_data[cc])
                except IndexError:
                    json_data[cc] = open_cc.convert(json_data[cc])
                except:
                    pass

    naming_rule = ""
    original_naming_rule = ""
    for i in conf.naming_rule().split("+"):
        if i not in json_data:
            naming_rule += i.strip("'").strip('"')
            original_naming_rule += i.strip("'").strip('"')
        else:
            item = json_data.get(i)
            naming_rule += item if type(item) is not list else "&".join(item)
            # PATCH：处理[title]存在翻译的情况，后续NFO文件的original_name只会直接沿用naming_rule,这导致original_name非原始名
            # 理应在翻译处处理 naming_rule和original_naming_rule
            if i == 'title':
                item = json_data.get('original_title')
            original_naming_rule += item if type(item) is not list else "&".join(item)

    json_data['naming_rule'] = naming_rule
    json_data['original_naming_rule'] = original_naming_rule
    return json_data


def special_characters_replacement(text) -> str:
    if not isinstance(text, str):
        return text
    return (text.replace('\\', '∖').  # U+2216 SET MINUS @ Basic Multilingual Plane
            replace('/', '∕').  # U+2215 DIVISION SLASH @ Basic Multilingual Plane
            replace(':', '꞉').  # U+A789 MODIFIER LETTER COLON @ Latin Extended-D
            replace('*', '∗').  # U+2217 ASTERISK OPERATOR @ Basic Multilingual Plane
            replace('?', '？').  # U+FF1F FULLWIDTH QUESTION MARK @ Basic Multilingual Plane
            replace('"', '＂').  # U+FF02 FULLWIDTH QUOTATION MARK @ Basic Multilingual Plane
            replace('<', 'ᐸ').  # U+1438 CANADIAN SYLLABICS PA @ Basic Multilingual Plane
            replace('>', 'ᐳ').  # U+1433 CANADIAN SYLLABICS PO @ Basic Multilingual Plane
            replace('|', 'ǀ').  # U+01C0 LATIN LETTER DENTAL CLICK @ Basic Multilingual Plane
            replace('&lsquo;', '‘').  # U+02018 LEFT SINGLE QUOTATION MARK
            replace('&rsquo;', '’').  # U+02019 RIGHT SINGLE QUOTATION MARK
            replace('&hellip;', '…').
            replace('&amp;', '＆').
            replace("&", '＆')
            )
