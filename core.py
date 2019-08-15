# -*- coding: utf-8 -*-
from aip import AipBodyAnalysis
import os.path
import shutil
from PIL import Image
import javbus
import json
import fc2fans_club
import siro
from ADC_function import *
from configparser import ConfigParser
import argparse


Config = ConfigParser()
Config.read(config_file, encoding='UTF-8')
try:
    option = ReadMediaWarehouse()
except:
    print('[-]Config media_warehouse read failed!')

# 初始化全局变量
title = ''
studio = ''
year = ''
outline = ''
runtime = ''
director = ''
actor_list = []
actor = ''
release = ''
number = ''
cover = ''
imagecut = ''
tag = []
cn_sub = ''
multi_part = 0
path = ''
website = ''
json_data = {}
actor_photo = {}
naming_rule = ''  # eval(config['Name_Rule']['naming_rule'])
location_rule = ''  # eval(config['Name_Rule']['location_rule'])
program_mode = Config['common']['main_mode']
failed_folder = Config['common']['failed_output_folder']
success_folder = Config['common']['success_output_folder']


# =====================本地文件处理===========================
def moveFailedFolder():
    global filepath
    print('[-]Move to Failed output folder')
    shutil.move(filepath, str(os.getcwd()) + '/' + failed_folder + '/')
    os._exit(0)


def argparse_get_file():
    parser = argparse.ArgumentParser()
    parser.add_argument("--number", help="Enter Number on here", default='')
    parser.add_argument("file", help="Write the file path on here")
    args = parser.parse_args()
    return (args.file, args.number)


def CreatFailedFolder():
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make Failed output folder\n[-](Please run as Administrator)")
            os._exit(0)


def getDataFromJSON(file_number):  # 从JSON返回元数据
    global title
    global studio
    global year
    global outline
    global runtime
    global director
    global actor_list
    global actor
    global release
    global number
    global cover
    global imagecut
    global tag
    global image_main
    global cn_sub
    global website
    global actor_photo

    global naming_rule
    global location_rule

    # ================================================网站规则添加开始================================================

    try:  # 添加 需要 正则表达式的规则
        # =======================javdb.py=======================
        if re.search('^\d{5,}', file_number).group() in file_number:
            json_data = json.loads(javbus.main_uncensored(file_number))
    except:  # 添加 无需 正则表达式的规则
        # ====================fc2fans_club.py====================
        if 'fc2' in file_number:
            json_data = json.loads(fc2fans_club.main(
                file_number.strip('fc2_').strip('fc2-').strip('ppv-').strip('PPV-').strip('FC2_').strip('FC2-').strip(
                    'ppv-').strip('PPV-')))
        elif 'FC2' in file_number:
            json_data = json.loads(fc2fans_club.main(
                file_number.strip('FC2_').strip('FC2-').strip('ppv-').strip('PPV-').strip('fc2_').strip('fc2-').strip(
                    'ppv-').strip('PPV-')))
        # =======================siro.py=========================
        elif 'siro' in file_number or 'SIRO' in file_number or 'Siro' in file_number:
            json_data = json.loads(siro.main(file_number))
        # =======================javbus.py=======================
        else:
            json_data = json.loads(javbus.main(file_number))

    # ================================================网站规则添加结束================================================

    title = str(json_data['title']).replace(' ', '')
    studio = json_data['studio']
    year = json_data['year']
    outline = json_data['outline']
    runtime = json_data['runtime']
    director = json_data['director']
    actor_list = str(json_data['actor']).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    release = json_data['release']
    number = json_data['number']
    cover = json_data['cover']
    imagecut = json_data['imagecut']
    tag = str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')
    actor_photo = json_data['actor_photo']
    website = json_data['website']

    if title == '' or number == '':
        print('[-]Movie Data not found!')
        moveFailedFolder()

    # ====================处理异常字符====================== #\/:*?"<>|
    if '\\' in title:
        title = title.replace('\\', ' ')
    elif r'/' in title:
        title = title.replace(r'/', '')
    elif ':' in title:
        title = title.replace(':', '')
    elif '*' in title:
        title = title.replace('*', '')
    elif '?' in title:
        title = title.replace('?', '')
    elif '"' in title:
        title = title.replace('"', '')
    elif '<' in title:
        title = title.replace('<', '')
    elif '>' in title:
        title = title.replace('>', '')
    elif '|' in title:
        title = title.replace('|', '')
    if r'/' in release:
        release = release.replace(r'/', '-')
    # ====================处理异常字符 END================== #\/:*?"<>|

    naming_rule = eval(config['Name_Rule']['naming_rule'])
    location_rule = eval(config['Name_Rule']['location_rule'])


def get_path():  # 创建文件夹
    global actor
    global path
    if len(actor) > 240:  # 新建成功输出文件夹
        path = success_folder + '/' + location_rule.replace("'actor'", "'超多人'", 3).replace("actor", "'超多人'",
                                                                                           3)  # path为影片+元数据所在目录
        # print(path)
    else:
        path = success_folder + '/' + location_rule
    return path
    # print(path)


def creatFolder(path_1):
    if not os.path.exists(path_1):
        try:
            os.makedirs(path_1)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + ']-' + title, "/number")
            # print(path)
            os.makedirs(path)


# =====================资源下载部分===========================
def DownloadFileWithFilename(url, filename, path):  # path = examle:photo , video.in the Project Folder!
    try:
        proxy = Config['proxy']['proxy']
        timeout = int(Config['proxy']['timeout'])
        retry_count = int(Config['proxy']['retry'])
    except:
        print('[-]Proxy config error! Please check the config.')
    i = 0

    while i < retry_count:
        try:
            if not proxy == '':
                if not os.path.exists(path):
                    os.makedirs(path)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                r = requests.get(url, headers=headers, timeout=timeout,
                                 proxies={"http": "http://" + str(proxy), "https": "https://" + str(proxy)})
                if r == '':
                    print('[-]Movie Data not found!')
                    os._exit(0)
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
                    os._exit(0)
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
    moveFailedFolder()


def imageDownload(filepath):  # 封面是否下载成功，否则移动到failed
    if option == 'emby':
        if DownloadFileWithFilename(cover, number + '.jpg', path) == 'failed':
            moveFailedFolder()
        DownloadFileWithFilename(cover, number + '.jpg', path)
        print('[+]Image Downloaded!', path + '/' + number + '.jpg')
    elif option == 'plex':
        if DownloadFileWithFilename(cover, 'fanart.jpg', path) == 'failed':
            moveFailedFolder()
        DownloadFileWithFilename(cover, 'fanart.jpg', path)
        print('[+]Image Downloaded!', path + '/fanart.jpg')


def PrintFiles(filepath):
    # global path
    global title
    global cn_sub
    global actor_photo
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        if option == 'plex':
            with open(path + "/" + number + ".nfo", "wt", encoding='UTF-8') as code:
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
                print("  <poster>poster.png</poster>", file=code)
                print("  <thumb>thumb.png</thumb>", file=code)
                print("  <fanart>fanart.jpg</fanart>", file=code)
                try:
                    for key, value in actor_photo.items():
                        print("  <actor>", file=code)
                        print("   <name>" + key + "</name>", file=code)
                        if not actor_photo == '':  # or actor_photo == []:
                            print("   <thumb>" + value + "</thumb>", file=code)
                        print("  </actor>", file=code)
                except:
                    aaaa = ''
                print("  <maker>" + studio + "</maker>", file=code)
                print("  <label>", file=code)
                print("  </label>", file=code)
                if cn_sub == '1':
                    print("  <tag>中文字幕</tag>", file=code)
                try:
                    for i in tag:
                        print("  <tag>" + i + "</tag>", file=code)
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
                print("  <release>" + release + "</release>", file=code)
                print("  <cover>" + cover + "</cover>", file=code)
                print("  <website>" + website + "</website>", file=code)
                print("</movie>", file=code)
                print("[+]Writeed!          " + path + "/" + number + ".nfo")
        elif option == 'emby':
            with open(path + "/" + number + ".nfo", "wt", encoding='UTF-8') as code:
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
                print("  <poster>" + number + ".png</poster>", file=code)
                print("  <thumb>" + number + ".png</thumb>", file=code)
                print("  <fanart>" + number + '.jpg' + "</fanart>", file=code)
                try:
                    for key, value in actor_photo.items():
                        print("  <actor>", file=code)
                        print("   <name>" + key + "</name>", file=code)
                        if not actor_photo == '':  # or actor_photo == []:
                            print("   <thumb>" + value + "</thumb>", file=code)
                        print("  </actor>", file=code)
                except:
                    aaaa = ''
                print("  <maker>" + studio + "</maker>", file=code)
                print("  <label>", file=code)
                print("  </label>", file=code)
                if cn_sub == '1':
                    print("  <tag>中文字幕</tag>", file=code)
                try:
                    for i in tag:
                        print("  <tag>" + i + "</tag>", file=code)
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
                print("  <release>" + release + "</release>", file=code)
                print("  <cover>" + cover + "</cover>", file=code)
                print("  <website>" + "https://www.javbus.com/" + number + "</website>", file=code)
                print("</movie>", file=code)
                print("[+]Writeed!          " + path + "/" + number + ".nfo")
    except IOError as e:
        print("[-]Write Failed!")
        print(e)
        moveFailedFolder()
    except Exception as e1:
        print(e1)
        print("[-]Write Failed!")
        moveFailedFolder()


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def image_cut(file_name):
    """ 你的 APPID AK SK """
    APP_ID = '17013175'
    API_KEY = 'IQs1mkG4FerdtmNh6qKDI4fW'
    SECRET_KEY = 'dLr9GTqqutqP9nWKKRaEinVDhxYlPbnD'

    client = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)

    """ 获取图片分辨率 """
    im = Image.open(file_name)  # 返回一个Image对象
    width, height = im.size

    """ 读取图片 """
    image = get_file_content(file_name)

    """ 调用人体检测与属性识别 """
    result = client.bodyAnalysis(image)
    ewidth = int(0.661538 * height)
    ex = int(result["person_info"][0]['body_parts']['nose']['x'])
    if width - ex < ewidth / 2:
        ex = width - ewidth
    else:
        ex -= int(ewidth / 2)
    ey = 0
    ew = ewidth
    eh = height
    img = Image.open(file_name)
    img2 = img.crop((ex, ey, ew + ex, eh + ey))
    img2.save(path + '/' + number + '.png')



def cutImage():
    if option == 'plex':
        if imagecut == 1:
            try:
                img = Image.open(path + '/fanart.jpg')
                imgSize = img.size
                w = img.width
                h = img.height
                img2 = img.crop((w / 1.9, 0, w, h))
                img2.save(path + '/poster.png')
            except:
                print('[-]Cover cut failed!')
        else:
            img = Image.open(path + '/fanart.jpg')
            w = img.width
            h = img.height
            img.save(path + '/poster.png')
    elif option == 'emby':
        if imagecut == 1:
            try:
                img = Image.open(path + '/' + number + '.jpg')
                imgSize = img.size
                w = img.width
                h = img.height
                img2 = img.crop((w / 1.9, 0, w, h))
                if multi_part == 1:
                    img2.save(path + '/' + number + '-CD1.png')
                else:
                    img2.save(path + '/' + number + '.png')
            except:
                print('[-]Cover cut failed!')
        else:
            file_name = path + '/' + number + '.jpg'
            image_cut(file_name)


# 获取视频后缀
def get_video_suffix(file):
    if file.split('.')[-1] in ['AVI', 'RMVB', 'WMV', 'MOV', 'MP4', 'MKV', 'FLV', 'TS', 'avi', 'rmvb', 'wmv', 'mov',
                               'mp4', 'mkv', 'flv', 'ts']:
        return file.split('.')[-1]
    else:
        return ''


# 获取其他文件后缀
def get_other_suffix(file):
    return file.split('.')[-1]


def pasteFileToFolder(filepath, path):  # 文件路径，番号，后缀，要移动至的位置
    video_suffix = get_video_suffix(filepath)
    try:
        if multi_part == 0:
            if os.path.exists(path + '/' + number + '.' + video_suffix):
                print('[-]File Exists! Please check your movie!')
                print('[-]move to the root folder of the program.')
                os._exit(0)
            os.rename(filepath, path + '/' + number + '.' + video_suffix)
        else:
            num_video = 0
            for file in os.listdir(path):
                if get_video_suffix(file) != '':
                    num_video += 1
            count_video = 0
            count_jpg = 0
            for file in os.listdir(path):
                if get_video_suffix(file) != '':
                    count_video += 1
                    os.rename(path + '/' + file, path + '/' + number + "-CD" + str(count_video) + '.' + video_suffix)
                elif get_other_suffix(file) == 'nfo':
                    get_other_suffix(file)
                    os.rename(path + '/' + file, path + '/' + number + "-CD1." + get_other_suffix(file))
                elif 'Backdrop' not in file and get_other_suffix(file) == 'jpg':
                    count_jpg += 1
                    os.rename(path + '/' + file, path + '/' + number + "-CD" + str(count_jpg) + ".jpg")
            os.rename(filepath, path + '/' + number + "-CD" + str(count_video + 1) + '.' + video_suffix)
            if num_video != 0:
                shutil.copy(path + '/Backdrop.jpg', path + '/' + number + "-CD" + str(count_jpg + 1) + '.jpg')
                print('[+]Image Downloaded!', path + '/' + number + "-CD" + str(count_jpg + 1) + '.jpg')
    except FileExistsError:
        os._exit(0)


def pasteFileToFolder_mode2(filepath, path):  # 文件路径，番号，后缀，要移动至的位置
    global suffix
    suffix = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|avi|rmvb|wmv|mov|mp4|mkv|flv|ts)$', filepath).group())
    try:
        os.rename(filepath, path + suffix)
        print('[+]Movie ' + number + ' move to target folder Finished!')
    except:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        os._exit(0)


def renameJpgToBackdrop_copy():
    if option == 'plex':
        shutil.copy(path + '/fanart.jpg', path + '/Backdrop.jpg')
        shutil.copy(path + '/poster.png', path + '/thumb.png')
    if option == 'emby':
        shutil.copy(path + '/' + number + '.jpg', path + '/Backdrop.jpg')


if __name__ == '__main__':
    filepath = argparse_get_file()[0]  # 影片的路径
    if '-CD' in filepath or '-cd' in filepath:
        multi_part = 1
    if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
        cn_sub = '1'

    if argparse_get_file()[1] == '':  # 获取手动拉去影片获取的番号
        try:
            number = str(
                re.findall(r'(.+?)\.', str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filepath).group()))).strip(
                "['']").replace('_', '-')
            print("[!]Making Data for   [" + number + "]")
        except:
            print("[-]failed!Please rename the filename again!")
            moveFailedFolder()
    else:
        number = argparse_get_file()[1]
    CreatFailedFolder()
    getDataFromJSON(number)  # 定义番号
    path = get_path()
    if program_mode == '1':
        if not os.path.exists(path):
            creatFolder(path)  # 创建文件夹
            imageDownload(filepath)  # creatFoder会返回番号路径
            PrintFiles(filepath)  # 打印文件
            cutImage()  # 裁剪图
            renameJpgToBackdrop_copy()
        pasteFileToFolder(filepath, path)  # 移动文件
    elif program_mode == '2':
        pasteFileToFolder_mode2(filepath, path)  # 移动文件
