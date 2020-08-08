import json
import os.path
import re
import shutil
import platform

from PIL import Image
from ADC_function import *

# =========website========
import avsox
import fanza
import fc2fans_club
import jav321
import javbus
import javdb
import mgstage
import xcity
import javlib


def escape_path(path, escape_literals: str):  # Remove escape literals
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def moveFailedFolder(filepath, failed_folder):
    print('[-]Move to Failed output folder')
    shutil.move(filepath, str(os.getcwd()) + '/' + failed_folder + '/')
    return 


def CreatFailedFolder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make Failed output folder\n[-](Please run as Administrator)")
            return 


def get_data_from_json(file_number, filepath, conf: config.Config):  # 从JSON返回元数据
    """
    iterate through all services and fetch the data
    """

    func_mapping = {
        "avsox": avsox.main,
        "fc2": fc2fans_club.main,
        "fanza": fanza.main,
        "javdb": javdb.main,
        "javbus": javbus.main,
        "mgstage": mgstage.main,
        "jav321": jav321.main,
        "xcity": xcity.main,
        "javlib": javlib.main,
    }

    # default fetch order list, from the beginning to the end
    sources = conf.sources().split(',')

    # if the input file name matches certain rules,
    # move some web service to the beginning of the list
    if re.match(r"^\d{5,}", file_number) or (
        "HEYZO" in file_number or "heyzo" in file_number or "Heyzo" in file_number
    ):
        sources.insert(0, sources.pop(sources.index("avsox")))
    elif re.match(r"\d+\D+", file_number) or (
        "siro" in file_number or "SIRO" in file_number or "Siro" in file_number
    ):
        sources.insert(0, sources.pop(sources.index("fanza")))
    elif "fc2" in file_number or "FC2" in file_number:
        sources.insert(0, sources.pop(sources.index("fc2")))

    json_data = {}
    for source in sources:
        json_data = json.loads(func_mapping[source](file_number))
        # if any service return a valid return, break
        if get_data_state(json_data):
            break

    # Return if data not found in all sources
    if not json_data:
        print('[-]Movie Data not found!')
        moveFailedFolder(filepath, conf.failed_folder())
        return

    # ================================================网站规则添加结束================================================

    title = json_data['title']
    actor_list = str(json_data['actor']).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    release = json_data['release']
    number = json_data['number']
    studio = json_data['studio']
    source = json_data['source']
    runtime = json_data['runtime']
    outline = json_data['outline']
    label = json_data['label']
    series = json_data['series']
    year = json_data['year']
    try:
        cover_small = json_data['cover_small']
    except:
        cover_small = ''
    imagecut = json_data['imagecut']
    tag = str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    if title == '' or number == '':
        print('[-]Movie Data not found!')
        moveFailedFolder(filepath, conf.failed_folder())
        return

    # if imagecut == '3':
    #     DownloadFileWithFilename()

    # ====================处理异常字符====================== #\/:*?"<>|
    title = title.replace('\\', '')
    title = title.replace('/', '')
    title = title.replace(':', '')
    title = title.replace('*', '')
    title = title.replace('?', '')
    title = title.replace('"', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('|', '')
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')
    # ====================处理异常字符 END================== #\/:*?"<>|

    location_rule = eval(conf.location_rule())

    # Process only Windows.
    if platform.system() == "Windows":
        if 'actor' in conf.location_rule() and len(actor) > 100:
            print(conf.location_rule())
            location_rule = eval(conf.location_rule().replace("actor","'多人作品'"))
        if 'title' in conf.location_rule() and len(title) > 100:
            location_rule = eval(conf.location_rule().replace("title",'number'))

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    json_data['naming_rule'] = eval(conf.naming_rule())
    json_data['location_rule'] = location_rule
    json_data['year'] = year
    json_data['actor_list'] = actor_list
    return json_data


def get_info(json_data):  # 返回json里的数据
    title = json_data['title']
    studio = json_data['studio']
    year = json_data['year']
    outline = json_data['outline']
    runtime = json_data['runtime']
    director = json_data['director']
    actor_photo = json_data['actor_photo']
    release = json_data['release']
    number = json_data['number']
    cover = json_data['cover']
    website = json_data['website']
    series = json_data['series']
    label = json_data.get('label', "")
    return title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website, series, label


def small_cover_check(path, number, cover_small, c_word, conf: config.Config, filepath, failed_folder):
    download_file_with_filename(cover_small, number + c_word + '-poster.jpg', path, conf, filepath, failed_folder)
    print('[+]Image Downloaded! ' + path + '/' + number + c_word + '-poster.jpg')


def create_folder(success_folder, location_rule, json_data, conf: config.Config):  # 创建文件夹
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website, series, label = get_info(json_data)
    if len(location_rule) > 240:  # 新建成功输出文件夹
        path = success_folder + '/' + location_rule.replace("'actor'", "'manypeople'", 3).replace("actor","'manypeople'",3)  # path为影片+元数据所在目录
    else:
        path = success_folder + '/' + location_rule
    if not os.path.exists(path):
        path = escape_path(path, conf.escape_literals())
        try:
            os.makedirs(path)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + ']-' + title, "/number")
            path = escape_path(path, conf.escape_literals())

            os.makedirs(path)
    return path


# =====================资源下载部分===========================

# path = examle:photo , video.in the Project Folder!
def download_file_with_filename(url, filename, path, conf: config.Config, filepath, failed_folder):
    proxy, timeout, retry_count, proxytype = config.Config().proxy()

    for i in range(retry_count):
        try:
            if not proxy == '':
                if not os.path.exists(path):
                    os.makedirs(path)
                proxies = get_proxy(proxy, proxytype)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                r = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
                if r == '':
                    print('[-]Movie Data not found!')
                    return 
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
            else:
                if not os.path.exists(path):
                    os.makedirs(path)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                r = requests.get(url, timeout=timeout, headers=headers)
                if r == '':
                    print('[-]Movie Data not found!')
                    return 
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
        except requests.exceptions.RequestException:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')
    moveFailedFolder(filepath, failed_folder)
    return


# 封面是否下载成功，否则移动到failed
def image_download(cover, number, c_word, path, conf: config.Config, filepath, failed_folder):
    if download_file_with_filename(cover, number + c_word + '-fanart.jpg', path, conf, filepath, failed_folder) == 'failed':
        moveFailedFolder(filepath, failed_folder)
        return

    _proxy, _timeout, retry, _proxytype = conf.proxy()
    for i in range(retry):
        if os.path.getsize(path + '/' + number + c_word + '-fanart.jpg') == 0:
            print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(cover, number + c_word + '-fanart.jpg', path, conf, filepath, failed_folder)
            continue
        else:
            break
    if os.path.getsize(path + '/' + number + c_word + '-fanart.jpg') == 0:
        return
    print('[+]Image Downloaded!', path + '/' + number + c_word + '-fanart.jpg')
    shutil.copyfile(path + '/' + number + c_word + '-fanart.jpg',path + '/' + number + c_word + '-thumb.jpg')


def print_files(path, c_word, naming_rule, part, cn_sub, json_data, filepath, failed_folder, tag, actor_list, liuchu):
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website, series, label = get_info(json_data)

    try:
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + "/" + number + part + c_word + ".nfo", "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
            print("<movie>", file=code)
            print(" <title>" + naming_rule + "</title>", file=code)
            print("  <set>", file=code)
            print("  </set>", file=code)
            print("  <studio>" + studio + "+</studio>", file=code)
            print("  <year>" + year + "</year>", file=code)
            print("  <outline>" + outline + "</outline>", file=code)
            print("  <plot>" + outline + "</plot>", file=code)
            print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
            print("  <director>" + director + "</director>", file=code)
            print("  <poster>" + number + c_word + "-poster.jpg</poster>", file=code)
            print("  <thumb>" + number + c_word + "-thumb.jpg</thumb>", file=code)
            print("  <fanart>" + number + c_word + '-fanart.jpg' + "</fanart>", file=code)
            try:
                for key in actor_list:
                    print("  <actor>", file=code)
                    print("   <name>" + key + "</name>", file=code)
                    print("  </actor>", file=code)
            except:
                aaaa = ''
            print("  <maker>" + studio + "</maker>", file=code)
            print("  <label>" + label + "</label>", file=code)
            if cn_sub == '1':
                print("  <tag>中文字幕</tag>", file=code)
            if liuchu == '流出':
                print("  <tag>流出</tag>", file=code)
            try:
                for i in tag:
                    print("  <tag>" + i + "</tag>", file=code)
                print("  <tag>" + series + "</tag>", file=code)
            except:
                aaaaa = ''
            try:
                for i in tag:
                    print("  <genre>" + i + "</genre>", file=code)
            except:
                aaaaaaaa = ''
            if cn_sub == '1':
                print("  <genre>中文字幕</genre>", file=code)
            print("  <num>" + number + "</num>", file=code)
            print("  <premiered>" + release + "</premiered>", file=code)
            print("  <cover>" + cover + "</cover>", file=code)
            print("  <website>" + website + "</website>", file=code)
            print("</movie>", file=code)
            print("[+]Wrote!            " + path + "/" + number + part + c_word + ".nfo")
    except IOError as e:
        print("[-]Write Failed!")
        print(e)
        moveFailedFolder(filepath, failed_folder)
        return
    except Exception as e1:
        print(e1)
        print("[-]Write Failed!")
        moveFailedFolder(filepath, failed_folder)
        return


def cutImage(imagecut, path, number, c_word):
    if imagecut == 1: # 剪裁大封面
        try:
            img = Image.open(path + '/' + number + c_word + '-fanart.jpg')
            imgSize = img.size
            w = img.width
            h = img.height
            img2 = img.crop((w / 1.9, 0, w, h))
            img2.save(path + '/' + number + c_word + '-poster.jpg')
            print('[+]Image Cutted!     ' + path + '/' + number + c_word + '-poster.jpg')
        except:
            print('[-]Cover cut failed!')
    elif imagecut == 0: # 复制封面
        shutil.copyfile(path + '/' + number + c_word + '-fanart.jpg',path + '/' + number + c_word + '-poster.jpg')
        print('[+]Image Copyed!     ' + path + '/' + number + c_word + '-poster.jpg')


def paste_file_to_folder(filepath, path, number, c_word, conf: config.Config):  # 文件路径，番号，后缀，要移动至的位置
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|WEBM|ISO|avi|rmvb|wmv|mov|mp4|mkv|flv|ts|webm|iso)$', filepath).group())

    try:
        # 如果soft_link=1 使用软链接
        if conf.soft_link():
            os.symlink(filepath, path + '/' + number + c_word + houzhui)
        else:
            os.rename(filepath, path + '/' + number + c_word + houzhui)
        if os.path.exists(os.getcwd() + '/' + number + c_word + '.srt'):  # 字幕移动
            os.rename(os.getcwd() + '/' + number + c_word + '.srt', path + '/' + number + c_word + '.srt')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + number + c_word + '.ssa'):
            os.rename(os.getcwd() + '/' + number + c_word + '.ssa', path + '/' + number + c_word + '.ssa')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + number + c_word + '.sub'):
            os.rename(os.getcwd() + '/' + number + c_word + '.sub', path + '/' + number + c_word + '.sub')
            print('[+]Sub moved!')
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return 
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return 


def paste_file_to_folder_mode2(filepath, path, multi_part, number, part, c_word, conf):  # 文件路径，番号，后缀，要移动至的位置
    if multi_part == 1:
        number += part  # 这时number会被附加上CD1后缀
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|WEBM|avi|rmvb|wmv|mov|mp4|mkv|flv|ts|webm)$', filepath).group())

    try:
        if conf.soft_link():
            os.symlink(filepath, path + '/' + number + part + c_word + houzhui)
        else:
            os.rename(filepath, path + '/' + number + part + c_word + houzhui)
        if os.path.exists(number + '.srt'):  # 字幕移动
            os.rename(number + part + c_word + '.srt', path + '/' + number + part + c_word + '.srt')
            print('[+]Sub moved!')
        elif os.path.exists(number + part + c_word + '.ass'):
            os.rename(number + part + c_word + '.ass', path + '/' + number + part + c_word + '.ass')
            print('[+]Sub moved!')
        elif os.path.exists(number + part + c_word + '.sub'):
            os.rename(number + part + c_word + '.sub', path + '/' + number + part + c_word + '.sub')
            print('[+]Sub moved!')
        print('[!]Success')
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return 
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return

def get_part(filepath, failed_folder):
    try:
        if re.search('-CD\d+', filepath):
            return re.findall('-CD\d+', filepath)[0]
        if re.search('-cd\d+', filepath):
            return re.findall('-cd\d+', filepath)[0]
    except:
        print("[-]failed!Please rename the filename again!")
        moveFailedFolder(filepath, failed_folder)
        return


def debug_print(data: json):
    try:
        print("[+] ---Debug info---")
        for i, v in data.items():
            if i == "outline":
                print("[+]  -", i, "    :", len(v), "characters")
                continue
            if i == "actor_photo" or i == "year":
                continue
            print("[+]  -", "%-11s" % i, ":", v)
        print("[+] ---Debug info---")
    except:
        pass


def core_main(file_path, number_th, conf: config.Config):
    # =======================================================================初始化所需变量
    multi_part = 0
    part = ''
    c_word = ''
    cn_sub = ''
    liuchu = ''

    filepath = file_path  # 影片的路径
    number = number_th
    json_data = get_data_from_json(number, filepath, conf)  # 定义番号

    # Return if blank dict returned (data not found)
    if not json_data:
        return

    if json_data["number"] != number:
        # fix issue #119
        # the root cause is we normalize the search id
        # print_files() will use the normalized id from website,
        # but paste_file_to_folder() still use the input raw search id
        # so the solution is: use the normalized search id
        number = json_data["number"]
    imagecut = json_data['imagecut']
    tag = json_data['tag']
    # =======================================================================判断-C,-CD后缀
    if '-CD' in filepath or '-cd' in filepath:
        multi_part = 1
        part = get_part(filepath, conf.failed_folder())
    if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
        cn_sub = '1'
        c_word = '-C'  # 中文字幕影片后缀
    if '流出' in filepath:
        liuchu = '流出'

    # 创建输出失败目录
    CreatFailedFolder(conf.failed_folder())

    # 调试模式检测
    if conf.debug():
        debug_print(json_data)

    # 创建文件夹
    path = create_folder(conf.success_folder(), json_data['location_rule'], json_data, conf)

    # main_mode
    #  1: 刮削模式 / Scraping mode
    #  2: 整理模式 / Organizing mode
    if conf.main_mode() == 1:
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(path, number, json_data['cover_small'], c_word, conf, filepath, conf.failed_folder())

        # creatFolder会返回番号路径
        image_download(json_data['cover'], number, c_word, path, conf, filepath, conf.failed_folder())

        # 裁剪图
        cutImage(imagecut, path, number, c_word)

        # 打印文件
        print_files(path, c_word, json_data['naming_rule'], part, cn_sub, json_data, filepath, conf.failed_folder(), tag, json_data['actor_list'], liuchu)

        # 移动文件
        paste_file_to_folder(filepath, path, number, c_word, conf)
    elif conf.main_mode() == 2:
        # 移动文件
        paste_file_to_folder_mode2(filepath, path, multi_part, number, part, c_word, conf)
