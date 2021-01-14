import json
import os.path
import pathlib
import re
import shutil
import platform

from PIL import Image
from io import BytesIO

from ADC_function import *

# =========website========
from WebCrawler import airav
from WebCrawler import avsox
from WebCrawler import fanza
from WebCrawler import fc2
from WebCrawler import jav321
from WebCrawler import javbus
from WebCrawler import javdb
from WebCrawler import mgstage
from WebCrawler import xcity
from WebCrawler import javlib
from WebCrawler import dlsite


def escape_path(path, escape_literals: str):  # Remove escape literals
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def moveFailedFolder(filepath, failed_folder):
    if config.Config().failed_move():
        root_path = str(pathlib.Path(filepath).parent)
        file_name = pathlib.Path(filepath).name
        destination_path = root_path + '/' + failed_folder + '/'
        if config.Config().soft_link():
            print('[-]Create symlink to Failed output folder')
            os.symlink(filepath, destination_path + '/' + file_name)
        else:
            print('[-]Move to Failed output folder')
            shutil.move(filepath, destination_path)
    return


def get_data_from_json(file_number, filepath, conf: config.Config):  # 从JSON返回元数据
    """
    iterate through all services and fetch the data 
    """

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
        "javlib": javlib.main,
        "dlsite": dlsite.main,
    }

    # default fetch order list, from the beginning to the end
    sources = conf.sources().split(',')

    # if the input file name matches certain rules,
    # move some web service to the beginning of the list
    if "avsox" in sources and (re.match(r"^\d{5,}", file_number) or
        "HEYZO" in file_number or "heyzo" in file_number or "Heyzo" in file_number
    ):
        # if conf.debug() == True:
        #     print('[+]select avsox')
        sources.insert(0, sources.pop(sources.index("avsox")))
    elif "mgstage" in sources and (re.match(r"\d+\D+", file_number) or
        "siro" in file_number or "SIRO" in file_number or "Siro" in file_number
    ):
        # if conf.debug() == True:
            # print('[+]select fanza')
        sources.insert(0, sources.pop(sources.index("mgstage")))
    elif "fc2" in sources and ("fc2" in file_number or "FC2" in file_number
    ):
        # if conf.debug() == True:
        #     print('[+]select fc2')
        sources.insert(0, sources.pop(sources.index("fc2")))
    elif "dlsite" in sources and (
        "RJ" in file_number or "rj" in file_number or "VJ" in file_number or "vj" in file_number
    ):
        # if conf.debug() == True:
        #     print('[+]select dlsite')
        sources.insert(0, sources.pop(sources.index("dlsite")))

    json_data = {}
    for source in sources:
        try:
            if conf.debug() == True:
                print('[+]select',source)
            json_data = json.loads(func_mapping[source](file_number))
            # if any service return a valid return, break
            if get_data_state(json_data):
                break
        except:
            break

    # Return if data not found in all sources
    if not json_data:
        print('[-]Movie Data not found!')
        moveFailedFolder(filepath, conf.failed_folder())
        return

    # ================================================网站规则添加结束================================================

    title = json_data.get('title')
    actor_list = str(json_data.get('actor')).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    actor_list = [actor.strip() for actor in actor_list]  # 去除空白
    release = json_data.get('release')
    number = json_data.get('number')
    studio = json_data.get('studio')
    source = json_data.get('source')
    runtime = json_data.get('runtime')
    outline = json_data.get('outline')
    label = json_data.get('label')
    series = json_data.get('series')
    year = json_data.get('year')

    if json_data.get('cover_small') == None:
        cover_small = ''
    else:
        cover_small = json_data.get('cover_small')
    
    if json_data.get('trailer') == None:
        trailer = ''
    else:
        trailer = json_data.get('trailer')
        
    if json_data.get('extrafanart') == None:
        extrafanart = ''
    else:
        extrafanart = json_data.get('extrafanart')
    
    imagecut = json_data.get('imagecut')
    tag = str(json_data.get('tag')).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
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

    # ===  替换Studio片假名
    studio = studio.replace('アイエナジー','Energy')
    studio = studio.replace('アイデアポケット','Idea Pocket')
    studio = studio.replace('アキノリ','AKNR')
    studio = studio.replace('アタッカーズ','Attackers')
    studio = re.sub('アパッチ.*','Apache',studio)
    studio = studio.replace('アマチュアインディーズ','SOD')
    studio = studio.replace('アリスJAPAN','Alice Japan')
    studio = studio.replace('オーロラプロジェクト・アネックス','Aurora Project Annex')
    studio = studio.replace('クリスタル映像','Crystal 映像')
    studio = studio.replace('グローリークエスト','Glory Quest')
    studio = studio.replace('ダスッ！','DAS！')
    studio = studio.replace('ディープス','DEEP’s')
    studio = studio.replace('ドグマ','Dogma')
    studio = studio.replace('プレステージ','PRESTIGE')
    studio = studio.replace('ムーディーズ','MOODYZ')
    studio = studio.replace('メディアステーション','宇宙企画')
    studio = studio.replace('ワンズファクトリー','WANZ FACTORY')
    studio = studio.replace('エスワン ナンバーワンスタイル','S1')
    studio = studio.replace('エスワンナンバーワンスタイル','S1')
    studio = studio.replace('SODクリエイト','SOD')
    studio = studio.replace('サディスティックヴィレッジ','SOD')
    studio = studio.replace('V＆Rプロダクツ','V＆R PRODUCE')
    studio = studio.replace('V＆RPRODUCE','V＆R PRODUCE')
    studio = studio.replace('レアルワークス','Real Works')
    studio = studio.replace('マックスエー','MAX-A')
    studio = studio.replace('ピーターズMAX','PETERS MAX')
    studio = studio.replace('プレミアム','PREMIUM')
    studio = studio.replace('ナチュラルハイ','NATURAL HIGH')
    studio = studio.replace('マキシング','MAXING')
    studio = studio.replace('エムズビデオグループ','M’s Video Group')
    studio = studio.replace('ミニマム','Minimum')
    studio = studio.replace('ワープエンタテインメント','WAAP Entertainment')
    studio = re.sub('.*/妄想族','妄想族',studio)
    studio = studio.replace('/',' ')
    # ===  替换Studio片假名 END
    
    location_rule = eval(conf.location_rule())

    if 'actor' in conf.location_rule() and len(actor) > 100:
        print(conf.location_rule())
        location_rule = eval(conf.location_rule().replace("actor","'多人作品'"))
    maxlen = conf.max_title_len()
    if 'title' in conf.location_rule() and len(title) > maxlen:
        shorttitle = title[0:maxlen]
        location_rule = location_rule.replace(title, shorttitle)

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    json_data['location_rule'] = location_rule
    json_data['year'] = year
    json_data['actor_list'] = actor_list
    if conf.is_transalte():
        translate_values = conf.transalte_values().split(",")
        for translate_value in translate_values:
            if json_data[translate_value] == "":
                continue
            # if conf.get_transalte_engine() == "baidu":
            #     json_data[translate_value] = translate(
            #         json_data[translate_value],
            #         target_language="zh",
            #         engine=conf.get_transalte_engine(),
            #         app_id=conf.get_transalte_appId(),
            #         key=conf.get_transalte_key(),
            #         delay=conf.get_transalte_delay(),
            #     )
            if conf.get_transalte_engine() == "azure":
                json_data[translate_value] = translate(
                    json_data[translate_value],
                    target_language="zh-Hans",
                    engine=conf.get_transalte_engine(),
                    key=conf.get_transalte_key(),
                )
            else:
                json_data[translate_value] = translate(json_data[translate_value])

    if conf.is_trailer():
        if trailer:
            json_data['trailer'] = trailer
        else:
            json_data['trailer'] = ''
    else:
        json_data['trailer'] = ''
        
    if conf.is_extrafanart():
        if extrafanart:
            json_data['extrafanart'] = extrafanart
        else:
            json_data['extrafanart'] = ''
    else:
        json_data['extrafanart'] = ''
        
    naming_rule=""
    for i in conf.naming_rule().split("+"):
        if i not in json_data:
            naming_rule += i.strip("'").strip('"')
        else:
            naming_rule += json_data.get(i)
    json_data['naming_rule'] = naming_rule
    return json_data


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


def small_cover_check(path, number, cover_small, c_word, conf: config.Config, filepath, failed_folder):
    download_file_with_filename(cover_small, number + c_word + '-poster.jpg', path, conf, filepath, failed_folder)
    print('[+]Image Downloaded! ' + path + '/' + number + c_word + '-poster.jpg')


def create_folder(success_folder, location_rule, json_data, conf: config.Config):  # 创建文件夹
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(json_data)
    if len(location_rule) > 240:  # 新建成功输出文件夹
        path = success_folder + '/' + location_rule.replace("'actor'", "'manypeople'", 3).replace("actor","'manypeople'",3)  # path为影片+元数据所在目录
    else:
        path = success_folder + '/' + location_rule
    path = trimblank(path)
    if not os.path.exists(path):
        path = escape_path(path, conf.escape_literals())
        try:
            os.makedirs(path)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + ')-' + title, "/number")
            path = escape_path(path, conf.escape_literals())

            os.makedirs(path)
    return path


def trimblank(s: str):
    """
    Clear the blank on the right side of the folder name
    """
    if s[-1] == " ":
        return trimblank(s[:-1])
    else:
        return s

# =====================资源下载部分===========================

# path = examle:photo , video.in the Project Folder!
def download_file_with_filename(url, filename, path, conf: config.Config, filepath, failed_folder):
    switch, proxy, timeout, retry_count, proxytype = config.Config().proxy()

    for i in range(retry_count):
        try:
            if switch == 1 or switch == '1':
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

def trailer_download(trailer, c_word, number, path, filepath, conf: config.Config, failed_folder):
    if download_file_with_filename(trailer, number + c_word + '-trailer.mp4', path, conf, filepath, failed_folder) == 'failed':
        return
    switch, _proxy, _timeout, retry, _proxytype = conf.proxy()
    for i in range(retry):
        if os.path.getsize(path+'/' + number + c_word + '-trailer.mp4') == 0:
            print('[!]Video Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(trailer, number + c_word + '-trailer.mp4', path, conf, filepath, failed_folder)
            continue
        else:
            break
    if os.path.getsize(path + '/' + number + c_word + '-trailer.mp4') == 0:
        return
    print('[+]Video Downloaded!', path + '/' + number + c_word + '-trailer.mp4')

# 剧照下载成功，否则移动到failed
def extrafanart_download(data, path, conf: config.Config, filepath, failed_folder):
    j = 1
    path = path + '/' + conf.get_extrafanart()
    for url in data:
        if download_file_with_filename(url, '/extrafanart-' + str(j)+'.jpg', path, conf, filepath, failed_folder) == 'failed':
            moveFailedFolder(filepath, failed_folder)
            return
        switch, _proxy, _timeout, retry, _proxytype = conf.proxy()
        for i in range(retry):
            if os.path.getsize(path + '/extrafanart-' + str(j) + '.jpg') == 0:
                print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
                download_file_with_filename(url, '/extrafanart-' + str(j)+'.jpg', path, conf, filepath,
                                            failed_folder)
                continue
            else:
                break
        if os.path.getsize(path + '/extrafanart-' + str(j) + '.jpg') == 0:
            return
        print('[+]Image Downloaded!', path + '/extrafanart-' + str(j) + '.jpg')
        j += 1



# 封面是否下载成功，否则移动到failed
def image_download(cover, number, c_word, path, conf: config.Config, filepath, failed_folder):
    if download_file_with_filename(cover, number + c_word + '-fanart.jpg', path, conf, filepath, failed_folder) == 'failed':
        moveFailedFolder(filepath, failed_folder)
        return

    switch, _proxy, _timeout, retry, _proxytype = conf.proxy()
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
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(json_data)

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
            if config.Config().is_trailer():
                print("  <trailer>" + trailer + "</trailer>", file=code)
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
            img2 = img.crop((w - h / 1.5, 0, w, h))
            img2.save(path + '/' + number + c_word + '-poster.jpg')
            print('[+]Image Cutted!     ' + path + '/' + number + c_word + '-poster.jpg')
        except:
            print('[-]Cover cut failed!')
    elif imagecut == 0: # 复制封面
        shutil.copyfile(path + '/' + number + c_word + '-fanart.jpg',path + '/' + number + c_word + '-poster.jpg')
        print('[+]Image Copyed!     ' + path + '/' + number + c_word + '-poster.jpg')

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
    if mode == 1:
        mark_pic_path = BytesIO(get_html("https://raw.githubusercontent.com/yoshiko2/AV_Data_Capture/master/Img/SUB.png",return_type="content"))
    elif mode == 2:
        mark_pic_path = BytesIO(get_html("https://raw.githubusercontent.com/yoshiko2/AV_Data_Capture/master/Img/LEAK.png",return_type="content"))
    elif mode == 3:
        mark_pic_path = BytesIO(get_html("https://raw.githubusercontent.com/yoshiko2/AV_Data_Capture/master/Img/UNCENSORED.png",return_type="content"))
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

def paste_file_to_folder(filepath, path, number, c_word, conf: config.Config):  # 文件路径，番号，后缀，要移动至的位置
    houzhui = os.path.splitext(filepath)[1].replace(",","")
    file_parent_origin_path = str(pathlib.Path(filepath).parent)
    try:
        # 如果soft_link=1 使用软链接
        if conf.soft_link():
            os.symlink(filepath, path + '/' + number + c_word + houzhui)
        else:
            os.rename(filepath, path + '/' + number + c_word + houzhui)
        sub_res = conf.sub_rule()
        
        for subname in sub_res:
            if os.path.exists(number + c_word + subname):  # 字幕移动
                os.rename(number + c_word + subname, path + '/' + number + c_word + subname)
                print('[+]Sub moved!')
                return True
        
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
    houzhui = os.path.splitext(filepath)[1].replace(",","")
    file_parent_origin_path = str(pathlib.Path(filepath).parent)
    try:
        if conf.soft_link():
            os.symlink(filepath, path + '/' + number + part + c_word + houzhui)
        else:
            os.rename(filepath, path + '/' + number + part + c_word + houzhui)
        
        sub_res = conf.sub_rule()
        for subname in sub_res:
            if os.path.exists(os.getcwd() + '/' + number + c_word + subname):  # 字幕移动
                os.rename(os.getcwd() + '/' + number + c_word + subname, path + '/' + number + c_word + subname)
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
    c_word = ''
    cn_sub = ''
    liuchu = ''


    filepath = file_path  # 影片的路径 绝对路径
    # 下面被注释的变量不需要
    #rootpath= os.getcwd
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
    imagecut =  json_data.get('imagecut')
    tag =  json_data.get('tag')
    # =======================================================================判断-C,-CD后缀
    if '-CD' in filepath or '-cd' in filepath:
        multi_part = 1
        part = get_part(filepath, conf.failed_folder())
    if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
        cn_sub = '1'
        c_word = '-C'  # 中文字幕影片后缀
    
    # 判断是否无码
    if is_uncensored(number):
        uncensored = 1
    else:
        uncensored = 0
    
    
    if '流出' in filepath:
        liuchu = '流出'
        leak = 1
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
        path = create_folder(conf.success_folder(),  json_data.get('location_rule'), json_data, conf)
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(path, number,  json_data.get('cover_small'), c_word, conf, filepath, conf.failed_folder())

        # creatFolder会返回番号路径
        image_download( json_data.get('cover'), number, c_word, path, conf, filepath, conf.failed_folder())
        try:
            # 下载预告片
            if json_data.get('trailer'):
                trailer_download(json_data.get('trailer'), c_word, number, path, filepath, conf, conf.failed_folder())
        except:
            pass
        
        try:
            # 下载剧照 data, path, conf: config.Config, filepath, failed_folder
            if json_data.get('extrafanart'):
                extrafanart_download(json_data.get('extrafanart'), path, conf, filepath, conf.failed_folder())
        except:
            pass
        # 裁剪图
        cutImage(imagecut, path, number, c_word)

        # 打印文件
        print_files(path, c_word,  json_data.get('naming_rule'), part, cn_sub, json_data, filepath, conf.failed_folder(), tag,  json_data.get('actor_list'), liuchu)

        # 移动文件
        paste_file_to_folder(filepath, path, number, c_word, conf)
        
        poster_path = path + '/' + number + c_word + '-poster.jpg'
        thumb_path = path + '/' + number + c_word + '-thumb.jpg'
        if conf.is_watermark():
            add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, conf)
        
    elif conf.main_mode() == 2:
        # 创建文件夹
        path = create_folder(conf.success_folder(), json_data.get('location_rule'), json_data, conf)
        # 移动文件
        paste_file_to_folder_mode2(filepath, path, multi_part, number, part, c_word, conf)
        poster_path = path + '/' + number + c_word + '-poster.jpg'
        thumb_path = path + '/' + number + c_word + '-thumb.jpg'
        if conf.is_watermark():
            add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, conf)
        
    elif conf.main_mode() == 3:
        path = file_path.rsplit('/', 1)[0]
        path = path.rsplit('\\', 1)[0]
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(path, number, json_data.get('cover_small'), c_word, conf, filepath, conf.failed_folder())

        # creatFolder会返回番号路径
        image_download(json_data.get('cover'), number, c_word, path, conf, filepath, conf.failed_folder())

        # 下载预告片
        if json_data.get('trailer'):
            trailer_download(json_data.get('trailer'), c_word, number, path, filepath, conf, conf.failed_folder())

        # 下载剧照 data, path, conf: config.Config, filepath, failed_folder
        if json_data.get('extrafanart'):
            extrafanart_download(json_data.get('extrafanart'), path, conf, filepath, conf.failed_folder())

        # 裁剪图
        cutImage(imagecut, path, number, c_word)

        # 打印文件
        print_files(path, c_word, json_data.get('naming_rule'), part, cn_sub, json_data, filepath, conf.failed_folder(),
                    tag, json_data.get('actor_list'), liuchu)

        poster_path = path + '/' + number + c_word + '-poster.jpg'
        thumb_path = path + '/' + number + c_word + '-thumb.jpg'
        if conf.is_watermark():
            add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, conf)
