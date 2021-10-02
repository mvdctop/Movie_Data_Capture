import json
import os.path
import pathlib
import re
import shutil
import platform
import errno
import sys

from PIL import Image
from io import BytesIO
from pathlib import Path
from datetime import datetime

from ADC_function import *
from WebCrawler import get_data_from_json


def escape_path(path, escape_literals: str):  # Remove escape literals
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def moveFailedFolder(filepath, conf):
    failed_folder = conf.failed_folder()
    soft_link = conf.soft_link()
    # 模式3或软连接，改为维护一个失败列表，启动扫描时加载用于排除该路径，以免反复处理
    # 原先的创建软连接到失败目录，并不直观，不方便找到失败文件位置，不如直接记录该文件路径
    if conf.main_mode() == 3 or soft_link:
        ftxt = os.path.abspath(os.path.join(failed_folder, 'failed_list.txt'))
        print("[-]Add to Failed List file, see '%s'" % ftxt)
        with open(ftxt, 'a', encoding='utf-8') as flt:
            flt.write(f'{filepath}\n')
            flt.close()
    elif conf.failed_move() and not soft_link:
        failed_name = os.path.join(failed_folder, os.path.basename(filepath))
        mtxt = os.path.abspath(os.path.join(failed_folder, 'where_was_i_before_being_moved.txt'))
        print("'[-]Move to Failed output folder, see '%s'" % mtxt)
        with open(mtxt, 'a', encoding='utf-8') as wwibbmt:
            tmstr = datetime.now().strftime("%Y-%m-%d %H:%M")
            wwibbmt.write(f'{tmstr} FROM[{filepath}]TO[{failed_name}]\n')
            wwibbmt.close()
        shutil.move(filepath, failed_name)


def get_info(json_data):  # 返回json里的数据
    title = json_data.get('title')
    studio = json_data.get('studio')
    year = json_data.get('year')
    outline = json_data.get('outline')
    runtime = json_data.get('runtime')
    director = json_data.get('director')
    actor_photo = json_data.get('actor_photo')
    release = json_data.get('release')
    number = json_data.get('number')
    cover = json_data.get('cover')
    trailer = json_data.get('trailer')
    website = json_data.get('website')
    series = json_data.get('series')
    label = json_data.get('label', "")
    return title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label


def small_cover_check(path, number, cover_small, leak_word, c_word, conf: config.Config, filepath):
    filename = f"{number}{leak_word}{c_word}-poster.jpg"
    download_file_with_filename(cover_small, filename, path, conf, filepath)
    print('[+]Image Downloaded! ' + os.path.join(path, filename))


def create_folder(json_data, conf: config.Config):  # 创建文件夹
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(json_data)
    success_folder = conf.success_folder()
    actor = json_data.get('actor')
    location_rule = eval(conf.location_rule(), json_data)
    if 'actor' in conf.location_rule() and len(actor) > 100:
        print(conf.location_rule())
        location_rule = eval(conf.location_rule().replace("actor","'多人作品'"), json_data)
    maxlen = conf.max_title_len()
    if 'title' in conf.location_rule() and len(title) > maxlen:
        shorttitle = title[0:maxlen]
        location_rule = location_rule.replace(title, shorttitle)

    path = os.path.join(success_folder, location_rule).strip()
    if not os.path.isdir(path):
        path = escape_path(path, conf.escape_literals())
        try:
            os.makedirs(path)
            if not os.path.isdir(path):
                raise
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + ')-' + title, "/number")
            path = escape_path(path, conf.escape_literals())

            os.makedirs(path)
    return os.path.normpath(path)


# =====================资源下载部分===========================

# path = examle:photo , video.in the Project Folder!
def download_file_with_filename(url, filename, path, conf: config.Config, filepath):
    configProxy = conf.proxy()

    for i in range(configProxy.retry):
        try:
            if configProxy.enable:
                if not os.path.isdir(path):
                    os.makedirs(path)
                    if not os.path.isdir(path):
                        raise IOError
                proxies = configProxy.proxies()
                headers = {
                    'User-Agent': G_USER_AGENT}
                r = requests.get(url, headers=headers, timeout=configProxy.timeout, proxies=proxies)
                if r == '':
                    print('[-]Movie Download Data not found!')
                    return
                with open(os.path.join(path, filename), "wb") as code:
                    code.write(r.content)
                return
            else:
                if not os.path.isdir(path):
                    os.makedirs(path)
                    if not os.path.isdir(path):
                        raise IOError
                headers = {
                    'User-Agent': G_USER_AGENT}
                r = requests.get(url, timeout=configProxy.timeout, headers=headers)
                if r == '':
                    print('[-]Movie Download Data not found!')
                    return
                with open(os.path.join(path, filename), "wb") as code:
                    code.write(r.content)
                return
        except requests.exceptions.RequestException:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(configProxy.retry))
        except IOError:
            print(f"[-]Create Directory '{path}' failed!")
            moveFailedFolder(filepath, conf)
            return
    print('[-]Connect Failed! Please check your Proxy or Network!')
    moveFailedFolder(filepath, conf)
    return

def trailer_download(trailer, leak_word, c_word, number, path, filepath, conf: config.Config):
    if download_file_with_filename(trailer, number + leak_word + c_word + '-trailer.mp4', path, conf, filepath) == 'failed':
        return
    configProxy = conf.proxy()
    for i in range(configProxy.retry):
        if os.path.getsize(path+'/' + number + leak_word + c_word + '-trailer.mp4') == 0:
            print('[!]Video Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(trailer, number + leak_word + c_word + '-trailer.mp4', path, conf, filepath)
            continue
        else:
            break
    if os.path.getsize(path + '/' + number + leak_word + c_word + '-trailer.mp4') == 0:
        return
    print('[+]Video Downloaded!', path + '/' + number + leak_word + c_word + '-trailer.mp4')

# 剧照下载成功，否则移动到failed
def extrafanart_download(data, path, conf: config.Config, filepath):
    j = 1
    path = os.path.join(path, conf.get_extrafanart())
    for url in data:
        jpg_filename = f'extrafanart-{j}.jpg'
        jpg_fullpath = os.path.join(path, jpg_filename)
        if download_file_with_filename(url, jpg_filename, path, conf, filepath) == 'failed':
            moveFailedFolder(filepath, conf)
            return
        configProxy = conf.proxy()
        for i in range(configProxy.retry):
            if os.path.getsize(jpg_fullpath) == 0:
                print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
                download_file_with_filename(url, jpg_filename, path, conf, filepath)
                continue
            else:
                break
        if os.path.getsize(jpg_fullpath) == 0:
            return
        print('[+]Image Downloaded!', jpg_fullpath)
        j += 1



# 封面是否下载成功，否则移动到failed
def image_download(cover, number, leak_word, c_word, path, conf: config.Config, filepath):
    filename = f"{number}{leak_word}{c_word}-fanart.jpg"
    full_filepath = os.path.join(path, filename)
    if download_file_with_filename(cover, filename, path, conf, filepath) == 'failed':
        moveFailedFolder(filepath, conf)
        return

    configProxy = conf.proxy()
    for i in range(configProxy.retry):
        if os.path.getsize(full_filepath) == 0:
            print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(cover, filename, path, conf, filepath)
            continue
        else:
            break
    if os.path.getsize(full_filepath) == 0:
        return
    print('[+]Image Downloaded!', full_filepath)
    shutil.copyfile(full_filepath, os.path.join(path, f"{number}{leak_word}{c_word}-thumb.jpg"))


def print_files(path, leak_word, c_word, naming_rule, part, cn_sub, json_data, filepath, tag, actor_list, liuchu, uncensored, conf):
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(json_data)
    failed_folder = conf.failed_folder()
    if conf.main_mode() == 3:  # 模式3下，由于视频文件不做任何改变，.nfo文件必须和视频文件名称除后缀外完全一致，KODI等软件方可支持
        nfo_path = str(Path(filepath).with_suffix('.nfo'))
    else:
        nfo_path = os.path.join(path,f"{number}{part}{leak_word}{c_word}.nfo")
    try:
        if not os.path.isdir(path):
            os.makedirs(path)
            if not os.path.isdir(path):
                raise IOError
        with open(nfo_path, "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
            print("<movie>", file=code)
            print(" <title>" + naming_rule + "</title>", file=code)
            print("  <set>", file=code)
            print("  </set>", file=code)
            print("  <studio>" + studio + "</studio>", file=code)
            print("  <year>" + year + "</year>", file=code)
            print("  <outline>" + outline + "</outline>", file=code)
            print("  <plot>" + outline + "</plot>", file=code)
            print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
            print("  <director>" + director + "</director>", file=code)
            print("  <poster>" + number + leak_word + c_word + "-poster.jpg</poster>", file=code)
            print("  <thumb>" + number + leak_word + c_word + "-thumb.jpg</thumb>", file=code)
            print("  <fanart>" + number + leak_word + c_word + '-fanart.jpg' + "</fanart>", file=code)
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
            if uncensored == 1:
                print("  <tag>无码</tag>", file=code)
            try:
                for i in tag:
                    print("  <tag>" + i + "</tag>", file=code)
                print("  <tag>" + series + "</tag>", file=code)
            except:
                aaaaa = ''
            if cn_sub == '1':
                print("  <genre>中文字幕</genre>", file=code)
            if liuchu == '流出':
                print("  <genre>流出</genre>", file=code)
            if uncensored == 1:
                print("  <genre>无码</genre>", file=code)
            try:
                for i in tag:
                    print("  <genre>" + i + "</genre>", file=code)
                print("  <genre>" + series + "</genre>", file=code)
            except:
                aaaaaaaa = ''
            print("  <num>" + number + "</num>", file=code)
            print("  <premiered>" + release + "</premiered>", file=code)
            print("  <cover>" + cover + "</cover>", file=code)
            if config.Config().is_trailer():
                print("  <trailer>" + trailer + "</trailer>", file=code)
            print("  <website>" + website + "</website>", file=code)
            print("</movie>", file=code)
            print("[+]Wrote!            " + nfo_path)
    except IOError as e:
        print("[-]Write Failed!")
        print("[-]", e)
        moveFailedFolder(filepath, conf)
        return
    except Exception as e1:
        print("[-]Write Failed!")
        print("[-]", e1)
        moveFailedFolder(filepath, conf)
        return


def cutImage(imagecut, path, number, leak_word, c_word):
    fullpath_noext = os.path.join(path, f"{number}{leak_word}{c_word}")
    if imagecut == 1: # 剪裁大封面
        try:
            img = Image.open(fullpath_noext + '-fanart.jpg')
            imgSize = img.size
            w = img.width
            h = img.height
            img2 = img.crop((w / 1.9, 0, w, h))
            img2.save(fullpath_noext + '-poster.jpg')
            print('[+]Image Cutted!     ' + fullpath_noext + '-poster.jpg')
        except:
            print('[-]Cover cut failed!')
    elif imagecut == 0: # 复制封面
        shutil.copyfile(fullpath_noext + '-fanart.jpg', fullpath_noext + '-poster.jpg')
        print('[+]Image Copyed!     ' + fullpath_noext + '-poster.jpg')

# 此函数从gui版copy过来用用
# 参数说明
# poster_path
# thumb_path
# cn_sub   中文字幕  参数值为 1  0
# leak     流出     参数值为 1   0
# uncensored 无码   参数值为 1   0
# ========================================================================加水印
def add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, conf:config.Config):
    mark_type = ''
    if cn_sub:
        mark_type += ',字幕'
    if leak:
        mark_type += ',流出'
    if uncensored:
        mark_type += ',无码'
    if mark_type == '':
        return
    add_mark_thread(thumb_path, cn_sub, leak, uncensored, conf)
    print('[+]Thumb Add Mark:   ' + mark_type.strip(','))
    add_mark_thread(poster_path, cn_sub, leak, uncensored, conf)
    print('[+]Poster Add Mark:  ' + mark_type.strip(','))

def add_mark_thread(pic_path, cn_sub, leak, uncensored, conf):
    size = 14
    img_pic = Image.open(pic_path)
    # 获取自定义位置，取余配合pos达到顺时针添加的效果
    # 左上 0, 右上 1, 右下 2， 左下 3
    count = conf.watermark_type()
    if cn_sub == 1 or cn_sub == '1':
        add_to_pic(pic_path, img_pic, size, count, 1)  # 添加
        count = (count + 1) % 4
    if leak == 1 or leak == '1':
        add_to_pic(pic_path, img_pic, size, count, 2)
        count = (count + 1) % 4
    if uncensored == 1 or uncensored == '1':
        add_to_pic(pic_path, img_pic, size, count, 3)
    img_pic.close()

def add_to_pic(pic_path, img_pic, size, count, mode):
    mark_pic_path = ''
    pngpath = ''
    if mode == 1:
        pngpath = "Img/SUB.png"
    elif mode == 2:
        pngpath = "Img/LEAK.png"
    elif mode == 3:
        pngpath = "Img/UNCENSORED.png"
    else:
        print('[-]Error: watermark image param mode invalid!')
        return
    # 先找pyinstaller打包的图片
    if hasattr(sys, '_MEIPASS') and os.path.isfile(os.path.join(getattr(sys, '_MEIPASS'), pngpath)):
        mark_pic_path = os.path.join(getattr(sys, '_MEIPASS'), pngpath)
    # 再找py脚本所在路径的图片
    elif os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), pngpath)):
        mark_pic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), pngpath)
    # 如果没有本地图片才通过网络下载
    else:
        mark_pic_path = BytesIO(
            get_html("https://raw.githubusercontent.com/yoshiko2/AV_Data_Capture/master/" + pngpath,
            return_type="content"))
    img_subt = Image.open(mark_pic_path)
    scroll_high = int(img_pic.height / size)
    scroll_wide = int(scroll_high * img_subt.width / img_subt.height)
    img_subt = img_subt.resize((scroll_wide, scroll_high), Image.ANTIALIAS)
    r, g, b, a = img_subt.split()  # 获取颜色通道，保持png的透明性
    # 封面四个角的位置
    pos = [
        {'x': 0, 'y': 0},
        {'x': img_pic.width - scroll_wide, 'y': 0},
        {'x': img_pic.width - scroll_wide, 'y': img_pic.height - scroll_high},
        {'x': 0, 'y': img_pic.height - scroll_high},
    ]
    img_pic.paste(img_subt, (pos[count]['x'], pos[count]['y']), mask=a)
    img_pic.save(pic_path, quality=95)
# ========================结束=================================

def paste_file_to_folder(filepath, path, number, leak_word, c_word, conf: config.Config):  # 文件路径，番号，后缀，要移动至的位置
    filepath_obj = pathlib.Path(filepath)
    houzhui = filepath_obj.suffix
    file_parent_origin_path = str(filepath_obj.parent)
    try:
        targetpath = os.path.join(path, f"{number}{leak_word}{c_word}{houzhui}")
        # 如果soft_link=1 使用软链接
        if conf.soft_link() == 0:
            shutil.move(filepath, targetpath)
        elif conf.soft_link() == 1:
            # 采用相对路径，以便网络访问时能正确打开视频
            filerelpath = os.path.relpath(filepath, path)
            os.symlink(filerelpath, targetpath)
        elif conf.soft_link() == 2:
            shutil.move(filepath, targetpath)
            # 移走文件后，在原来位置增加一个可追溯的软链接，指向文件新位置
            # 以便追查文件从原先位置被移动到哪里了，避免因为得到错误番号后改名移动导致的文件失踪
            # 便于手工找回文件。并将软连接文件名后缀修改，以避免再次被搜刮。
            targetabspath = os.path.abspath(targetpath)
            if targetabspath != os.path.abspath(filepath):
                targetrelpath = os.path.relpath(targetabspath, file_parent_origin_path)
                os.symlink(targetrelpath, filepath + '#sym')
        sub_res = conf.sub_rule()

        for subname in sub_res:
            sub_filepath = str(filepath_obj.with_suffix(subname))
            if os.path.isfile(sub_filepath):  # 字幕移动
                shutil.move(sub_filepath, os.path.join(path, f"{number}{leak_word}{c_word}{subname}"))
                print('[+]Sub moved!')
                return True

    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return
    except OSError as oserr:
        print(f'[-]OS Error errno {oserr.errno}')
        return


def paste_file_to_folder_mode2(filepath, path, multi_part, number, part, leak_word, c_word, conf):  # 文件路径，番号，后缀，要移动至的位置
    if multi_part == 1:
        number += part  # 这时number会被附加上CD1后缀
    filepath_obj = pathlib.Path(filepath)
    houzhui = filepath_obj.suffix
    file_parent_origin_path = str(filepath_obj.parent)
    try:
        if conf.soft_link():
            os.symlink(filepath, os.path.join(path, f"{number}{part}{leak_word}{c_word}{houzhui}"))
        else:
            shutil.move(filepath, os.path.join(path, f"{number}{part}{leak_word}{c_word}{houzhui}"))

        sub_res = conf.sub_rule()
        for subname in sub_res:
            sub_filepath = str(filepath_obj.with_suffix(subname))
            if os.path.isfile(sub_filepath):  # 字幕移动
                shutil.move(sub_filepath, os.path.join(path, f"{number}{part}{leak_word}{c_word}{subname}"))
                print('[+]Sub moved!')
                print('[!]Success')
                return True
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return
    except OSError as oserr:
        print(f'[-]OS Error errno  {oserr.errno}')
        return

def get_part(filepath, conf):
    try:
        if re.search('-CD\d+', filepath):
            return re.findall('-CD\d+', filepath)[0]
        if re.search('-cd\d+', filepath):
            return re.findall('-cd\d+', filepath)[0]
    except:
        print("[-]failed!Please rename the filename again!")
        moveFailedFolder(filepath, conf)
        return


def debug_print(data: json):
    try:
        print("[+] ---Debug info---")
        for i, v in data.items():
            if i == 'outline':
                print('[+]  -', i, '    :', len(v), 'characters')
                continue
            if i == 'actor_photo' or i == 'year':
                continue
            print('[+]  -', "%-11s" % i, ':', v)

        print("[+] ---Debug info---")
    except:
        pass


def core_main(file_path, number_th, conf: config.Config):
    # =======================================================================初始化所需变量
    multi_part = 0
    part = ''
    leak_word = ''
    c_word = ''
    cn_sub = ''
    liuchu = ''


    filepath = file_path  # 影片的路径 绝对路径
    # 下面被注释的变量不需要
    #rootpath= os.getcwd
    number = number_th
    json_data = get_data_from_json(number, conf)  # 定义番号

    # Return if blank dict returned (data not found)
    if not json_data:
        moveFailedFolder(filepath, conf)
        return

    if json_data["number"] != number:
        # fix issue #119
        # the root cause is we normalize the search id
        # print_files() will use the normalized id from website,
        # but paste_file_to_folder() still use the input raw search id
        # so the solution is: use the normalized search id
        number = json_data["number"]
    imagecut =  json_data.get('imagecut')
    tag =  json_data.get('tag')
    # =======================================================================判断-C,-CD后缀
    if '-CD' in filepath or '-cd' in filepath:
        multi_part = 1
        part = get_part(filepath, conf)
    if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
        cn_sub = '1'
        c_word = '-C'  # 中文字幕影片后缀

    # 判断是否无码
    if is_uncensored(number):
        uncensored = 1
    else:
        uncensored = 0


    if '流出' in filepath or 'uncensored' in filepath:
        liuchu = '流出'
        leak = 1
        leak_word = '-流出' # 流出影片后缀
    else:
        leak = 0

    # 调试模式检测
    if conf.debug():
        debug_print(json_data)

    # 创建文件夹
    #path = create_folder(rootpath + '/' + conf.success_folder(),  json_data.get('location_rule'), json_data, conf)

    # main_mode
    #  1: 刮削模式 / Scraping mode
    #  2: 整理模式 / Organizing mode
    #  3：不改变路径刮削
    if conf.main_mode() == 1:
        # 创建文件夹
        path = create_folder(json_data, conf)
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(path, number,  json_data.get('cover_small'), leak_word, c_word, conf, filepath)

        # creatFolder会返回番号路径
        image_download( json_data.get('cover'), number, leak_word, c_word, path, conf, filepath)

        if not multi_part or part.lower() == '-cd1':
            try:
                # 下载预告片
                if conf.is_trailer() and json_data.get('trailer'):
                    trailer_download(json_data.get('trailer'), leak_word, c_word, number, path, filepath, conf)
            except:
                pass
            try:
                # 下载剧照 data, path, conf: config.Config, filepath
                if conf.is_extrafanart() and json_data.get('extrafanart'):
                    extrafanart_download(json_data.get('extrafanart'), path, conf, filepath)
            except:
                pass

        # 裁剪图
        cutImage(imagecut, path, number, leak_word, c_word)

        # 打印文件
        print_files(path, leak_word, c_word,  json_data.get('naming_rule'), part, cn_sub, json_data, filepath, tag,  json_data.get('actor_list'), liuchu, uncensored, conf)

        # 移动文件
        paste_file_to_folder(filepath, path, number, leak_word, c_word, conf)

        poster_path = os.path.join(path, f"{number}{leak_word}{c_word}-poster.jpg")
        thumb_path = os.path.join(path, f"{number}{leak_word}{c_word}-thumb.jpg")
        if conf.is_watermark():
            add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, conf)

    elif conf.main_mode() == 2:
        # 创建文件夹
        path = create_folder(json_data, conf)
        # 移动文件
        paste_file_to_folder_mode2(filepath, path, multi_part, number, part, leak_word, c_word, conf)
        poster_path = os.path.join(path, f"{number}{leak_word}{c_word}-poster.jpg")
        thumb_path = os.path.join(path, f"{number}{leak_word}{c_word}-thumb.jpg")
        if conf.is_watermark():
            add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, conf)

    elif conf.main_mode() == 3:
        path = str(Path(file_path).parent)
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(path, number, json_data.get('cover_small'), leak_word, c_word, conf, filepath)

        # creatFolder会返回番号路径
        image_download(json_data.get('cover'), number, leak_word, c_word, path, conf, filepath)

        if not multi_part or part.lower() == '-cd1':
            # 下载预告片
            if conf.is_trailer() and json_data.get('trailer'):
                trailer_download(json_data.get('trailer'), leak_word, c_word, number, path, filepath, conf)

            # 下载剧照 data, path, conf: config.Config, filepath
            if conf.is_extrafanart() and json_data.get('extrafanart'):
                extrafanart_download(json_data.get('extrafanart'), path, conf, filepath)

        # 裁剪图
        cutImage(imagecut, path, number, leak_word, c_word)

        # 打印文件
        print_files(path, leak_word, c_word, json_data.get('naming_rule'), part, cn_sub, json_data, filepath,
                    tag, json_data.get('actor_list'), liuchu, uncensored, conf)

        poster_path = os.path.join(path, f"{number}{leak_word}{c_word}-poster.jpg")
        thumb_path = os.path.join(path, f"{number}{leak_word}{c_word}-thumb.jpg")
        if conf.is_watermark():
            add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, conf)
