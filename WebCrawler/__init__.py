import json
import re
from multiprocessing.pool import ThreadPool

import ADC_function
import config
from ADC_function import translate
from lxml import etree
from pathlib import Path

# =========website========
from . import airav
from . import avsox
from . import fanza
from . import fc2
from . import jav321
from . import javbus
from . import javdb
from . import mgstage
from . import xcity
# from . import javlib
from . import dlsite
from . import carib
from . import fc2club


def get_data_state(data: dict) -> bool:  # 元数据获取失败检测
    if "title" not in data or "number" not in data:
        return False

    if data["title"] is None or data["title"] == "" or data["title"] == "null":
        return False

    if data["number"] is None or data["number"] == "" or data["number"] == "null":
        return False

    return True

def get_data_from_json(file_number, oCC):  # 从JSON返回元数据
    """
    iterate through all services and fetch the data
    """

    actor_mapping_data = etree.parse(str(Path.home() / '.local' / 'share' / 'mdc' / 'mapping_actor.xml'))
    info_mapping_data = etree.parse(str(Path.home() / '.local' / 'share' / 'mdc' / 'mapping_info.xml'))

    func_mapping = {
        "airav": airav.main,
        "avsox": avsox.main,
        "fc2": fc2.main,
        "fanza": fanza.main,
        "javdb": javdb.main,
        "javbus": javbus.main,
        "mgstage": mgstage.main,
        "jav321": jav321.main,
        "xcity": xcity.main,
        # "javlib": javlib.main,
        "dlsite": dlsite.main,
        "carib": carib.main,
        "fc2club": fc2club.main
    }

    conf = config.getInstance()
    # default fetch order list, from the beginning to the end
    sources = conf.sources().split(',')
    if not len(conf.sources()) > 80:
        # if the input file name matches certain rules,
        # move some web service to the beginning of the list
        lo_file_number = file_number.lower()
        if "carib" in sources and (re.match(r"^\d{6}-\d{3}", file_number)
        ):
            sources.insert(0, sources.pop(sources.index("carib")))
        elif re.match(r"^\d{5,}", file_number) or "heyzo" in lo_file_number:
            if "javdb" in sources:
                sources.insert(0, sources.pop(sources.index("javdb")))
            if "avsox" in sources:
                sources.insert(0, sources.pop(sources.index("avsox")))
        elif "mgstage" in sources and (re.match(r"\d+\D+", file_number) or
                                       "siro" in lo_file_number
        ):
            sources.insert(0, sources.pop(sources.index("mgstage")))
        elif "fc2" in lo_file_number:
            if "javdb" in sources:
                sources.insert(0, sources.pop(sources.index("javdb")))
            if "fc2" in sources:
                sources.insert(0, sources.pop(sources.index("fc2")))
            if "fc2club" in sources:
                sources.insert(0, sources.pop(sources.index("fc2club")))
        elif "dlsite" in sources and (
                "rj" in lo_file_number or "vj" in lo_file_number
        ):
            sources.insert(0, sources.pop(sources.index("dlsite")))
        elif re.match(r"^[a-z0-9]{3,}$", lo_file_number):
            if "javdb" in sources:
                sources.insert(0, sources.pop(sources.index("javdb")))
            if "xcity" in sources:
                sources.insert(0, sources.pop(sources.index("xcity")))

    # check sources in func_mapping
    todel = []
    for s in sources:
        if not s in func_mapping:
            print('[!] Source Not Exist : ' + s)
            todel.append(s)
    for d in todel:
        print('[!] Remove Source : ' + s)
        sources.remove(d)

    json_data = {}

    if conf.multi_threading():
        pool = ThreadPool(processes=len(conf.sources().split(',')))

        # Set the priority of multi-thread crawling and join the multi-thread queue
        for source in sources:
            pool.apply_async(func_mapping[source], (file_number,))

        # Get multi-threaded crawling response
        for source in sources:
            if conf.debug() == True:
                print('[+]select', source)
            json_data = json.loads(pool.apply_async(func_mapping[source], (file_number,)).get())
            # if any service return a valid return, break
            if get_data_state(json_data):
                print(f"[+]Find movie [{file_number}] metadata on website '{source}'")
                break
        pool.close()
        pool.terminate()
    else:
        for source in sources:
            try:
                if conf.debug() == True:
                    print('[+]select', source)
                json_data = json.loads(func_mapping[source](file_number))
                # if any service return a valid return, break
                if get_data_state(json_data):
                    print(f"[+]Find movie [{file_number}] metadata on website '{source}'")
                    break
            except:
                break

    # Return if data not found in all sources
    if not json_data:
        print('[-]Movie Number not found!')
        return None

    # 增加number严格判断，避免提交任何number，总是返回"本橋実来 ADZ335"，这种返回number不一致的数据源故障
    # 目前选用number命名规则是javdb.com Domain Creation Date: 2013-06-19T18:34:27Z
    # 然而也可以跟进关注其它命名规则例如airav.wiki Domain Creation Date: 2019-08-28T07:18:42.0Z
    # 如果将来javdb.com命名规则下不同Studio出现同名碰撞导致无法区分，可考虑更换规则，更新相应的number分析和抓取代码。
    if str(json_data.get('number')).upper() != file_number.upper():
        print('[-]Movie number has changed! [{}]->[{}]'.format(file_number, str(json_data.get('number'))))
        return None

    # ================================================网站规则添加结束================================================

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
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    if title == '' or number == '':
        print('[-]Movie Number or Title not found!')
        return None

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

    if conf.is_transalte():
        translate_values = conf.transalte_values().split(",")
        for translate_value in translate_values:
            if json_data[translate_value] == "":
                continue
            if translate_value == "title":
                title_dict = json.load(
                    open(str(Path.home() / '.local' / 'share' / 'mdc' / 'c_number.json'), 'r', encoding="utf-8"))
                try:
                    json_data[translate_value] = title_dict[number]
                    continue
                except:
                    pass
            if conf.get_transalte_engine() == "azure":
                t = translate(
                    json_data[translate_value],
                    target_language="zh-Hans",
                    engine=conf.get_transalte_engine(),
                    key=conf.get_transalte_key(),
                )
            else:
                t = translate(json_data[translate_value])
            if len(t):
                json_data[translate_value] = special_characters_replacement(t)

    if oCC:
        cc_vars = conf.cc_convert_vars().split(",")
        ccm = conf.cc_convert_mode()
        def convert_list(mapping_data,language,vars):
            total = []
            for i in vars:
                if len(mapping_data.xpath('a[contains(@keyword, $name)]/@' + language, name=i)) != 0:
                    i = mapping_data.xpath('a[contains(@keyword, $name)]/@' + language, name=i)[0]
                total.append(i)
            return total
        def convert(mapping_data,language,vars):
            if len(mapping_data.xpath('a[contains(@keyword, $name)]/@' + language, name=vars)) != 0:
                return mapping_data.xpath('a[contains(@keyword, $name)]/@' + language, name=vars)[0]
            else:
                return vars
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
                    json_data['actor_list'] = [oCC.convert(aa) for aa in json_data['actor_list']]
                    json_data['actor'] = oCC.convert(json_data['actor'])
            elif cc == "tag":
                try:
                    if ccm == 1:
                        json_data[cc] = convert_list(info_mapping_data, "zh_cn", json_data[cc])
                        json_data[cc] = ADC_function.delete_all_elements_in_list("删除", json_data[cc])
                    elif ccm == 2:
                        json_data[cc] = convert_list(info_mapping_data, "zh_tw", json_data[cc])
                        json_data[cc] = ADC_function.delete_all_elements_in_list("删除", json_data[cc])
                    elif ccm == 3:
                        json_data[cc] = convert_list(info_mapping_data, "jp", json_data[cc])
                        json_data[cc] = ADC_function.delete_list_all_elements("删除", json_data[cc])
                except:
                    json_data[cc] = [oCC.convert(t) for t in json_data[cc]]
            else:
                try:
                    if ccm == 1:
                        json_data[cc] = convert(info_mapping_data, "zh_cn", json_data[cc])
                        json_data[cc] = ADC_function.delete_list_all_elements("删除", json_data[cc])
                    elif ccm == 2:
                        json_data[cc] = convert(info_mapping_data, "zh_tw", json_data[cc])
                        json_data[cc] = ADC_function.delete_list_all_elements("删除", json_data[cc])
                    elif ccm == 3:
                        json_data[cc] = convert(info_mapping_data, "jp", json_data[cc])
                        json_data[cc] = ADC_function.delete_list_all_elements("删除", json_data[cc])
                except IndexError:
                    json_data[cc] = oCC.convert(json_data[cc])
                except:
                    pass

    naming_rule=""
    for i in conf.naming_rule().split("+"):
        if i not in json_data:
            naming_rule += i.strip("'").strip('"')
        else:
            naming_rule += json_data.get(i)

    json_data['naming_rule'] = naming_rule
    return json_data

def special_characters_replacement(text) -> str:
    if not isinstance(text, str):
        return text
    return (text.replace('\\', '∖').     # U+2216 SET MINUS @ Basic Multilingual Plane
                replace('/', '∕').       # U+2215 DIVISION SLASH @ Basic Multilingual Plane
                replace(':', '꞉').       # U+A789 MODIFIER LETTER COLON @ Latin Extended-D
                replace('*', '∗').       # U+2217 ASTERISK OPERATOR @ Basic Multilingual Plane
                replace('?', '？').      # U+FF1F FULLWIDTH QUESTION MARK @ Basic Multilingual Plane
                replace('"', '＂').      # U+FF02 FULLWIDTH QUOTATION MARK @ Basic Multilingual Plane
                replace('<', 'ᐸ').       # U+1438 CANADIAN SYLLABICS PA @ Basic Multilingual Plane
                replace('>', 'ᐳ').       # U+1433 CANADIAN SYLLABICS PO @ Basic Multilingual Plane
                replace('|', 'ǀ').       # U+01C0 LATIN LETTER DENTAL CLICK @ Basic Multilingual Plane
                replace('&lsquo;', '‘'). # U+02018 LEFT SINGLE QUOTATION MARK
                replace('&rsquo;', '’'). # U+02019 RIGHT SINGLE QUOTATION MARK
                replace('&hellip;','…').
                replace('&amp;', '＆')
            )
