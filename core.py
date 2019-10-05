# -*- coding: utf-8 -*-

import re
import os
import os.path
import shutil
from PIL import Image
import time
import json
from ADC_function import *
from configparser import ConfigParser
import argparse
#=========website========
import fc2fans_club
import siro
import avsox
import javbus
import javdb
#=========website========

#初始化全局变量
Config = ConfigParser()
Config.read(config_file, encoding='UTF-8')
try:
    option = ReadMediaWarehouse()
except:
    print('[-]Config media_warehouse read failed!')
title=''
studio=''
year=''
outline=''
runtime=''
director=''
actor_list=[]
actor=''
release=''
number=''
cover=''
imagecut=''
tag=[]
cn_sub=''
multi_part=0
part=''
path=''
houzhui=''
website=''
json_data={}
actor_photo={}
cover_small=''
naming_rule  =''#eval(config['Name_Rule']['naming_rule'])
location_rule=''#eval(config['Name_Rule']['location_rule'])
program_mode   = Config['common']['main_mode']
failed_folder  = Config['common']['failed_output_folder']
success_folder = Config['common']['success_output_folder']
#=====================本地文件处理===========================

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
    if not os.path.exists(failed_folder+'/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder+'/')
        except:
            print("[-]failed!can not be make Failed output folder\n[-](Please run as Administrator)")
            os._exit(0)
def getDataState(json_data): #元数据获取失败检测
    if json_data['title'] == '' or json_data['title'] == 'None' or json_data['title'] == 'null':
        return 0
    else:
        return 1
def getDataFromJSON(file_number): #从JSON返回元数据
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
    global cover_small
    global json_data

    global naming_rule
    global location_rule

    # ================================================网站规则添加开始================================================

    if re.match('^\d{5,}', file_number):
        json_data = json.loads(avsox.main(file_number))
        if getDataState(json_data) == 0:  # 如果元数据获取失败，请求番号至其他网站抓取
            json_data = json.loads(javdb.main(file_number))
    #==
    elif re.match('\d+\D+', file_number):
        json_data = json.loads(siro.main(file_number))
        if getDataState(json_data) == 0:  # 如果元数据获取失败，请求番号至其他网站抓取
            json_data = json.loads(javbus.main(file_number))
        elif getDataState(json_data) == 0:  # 如果元数据获取失败，请求番号至其他网站抓取
            json_data = json.loads(javdb.main(file_number))
    # ==
    elif 'fc2' in file_number or 'FC2' in file_number:
        json_data = json.loads(fc2fans_club.main(file_number))
    # ==
    elif 'HEYZO' in number or 'heyzo' in number or 'Heyzo' in number:
        json_data = json.loads(avsox.main(file_number))
    # ==
    elif 'siro' in file_number or 'SIRO' in file_number or 'Siro' in file_number:
        json_data = json.loads(siro.main(file_number))
    # ==
    else:
        json_data = json.loads(javbus.main(file_number))
        if getDataState(json_data) == 0:  # 如果元数据获取失败，请求番号至其他网站抓取
            json_data = json.loads(avsox.main(file_number))
        elif getDataState(json_data) == 0:  # 如果元数据获取失败，请求番号至其他网站抓取
            json_data = json.loads(javdb.main(file_number))

    # ================================================网站规则添加结束================================================

    title       = str(json_data['title']).replace(' ','')
    studio      =     json_data['studio']
    year        =     json_data['year']
    outline     =     json_data['outline']
    runtime     =     json_data['runtime']
    director    =     json_data['director']
    actor_list  = str(json_data['actor']).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    release     =     json_data['release']
    number      =     json_data['number']
    cover       =     json_data['cover']
    try:
        cover_small = json_data['cover_small']
    except:
        cover_small=''
    imagecut    =     json_data['imagecut']
    tag         = str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    actor       = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')
    actor_photo =     json_data['actor_photo']
    website     =     json_data['website']
    source      =     json_data['source']

    if title == '' or number == '':
        print('[-]Movie Data not found!')
        moveFailedFolder()

    if imagecut == '3':
        DownloadFileWithFilename()


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
    # ====================处理异常字符 END================== #\/:*?"<>|

    naming_rule   = eval(config['Name_Rule']['naming_rule'])
    location_rule = eval(config['Name_Rule']['location_rule'])
def smallCoverCheck():
    if imagecut == 3:
        if option == 'emby':
            DownloadFileWithFilename(cover_small, '1.jpg', path)
            img = Image.open(path + '/1.jpg')
            w = img.width
            h = img.height
            img.save(path + '/' + number + '.png')
            time.sleep(1)
            os.remove(path + '/1.jpg')
        if option == 'plex':
            DownloadFileWithFilename(cover_small, '1.jpg', path)
            img = Image.open(path + '/1.jpg')
            w = img.width
            h = img.height
            img.save(path + '/poster.png')
            os.remove(path + '/1.jpg')
def creatFolder(): #创建文件夹
    global actor
    global path
    if len(os.getcwd()+path) > 240:                    #新建成功输出文件夹
        path = success_folder+'/'+location_rule.replace("'actor'","'超多人'",3).replace("actor","'超多人'",3) #path为影片+元数据所在目录
    else:
        path = success_folder+'/'+location_rule
        #print(path)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            path = success_folder+'/'+location_rule.replace('/['+number+']-'+title,"/number")
            #print(path)
            os.makedirs(path)
#=====================资源下载部分===========================
def DownloadFileWithFilename(url,filename,path): #path = examle:photo , video.in the Project Folder!
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
                r = requests.get(url, headers=headers, timeout=timeout,proxies={"http": "http://" + str(proxy), "https": "https://" + str(proxy)})
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
            print('[-]Image Download :  Connect retry '+str(i)+'/'+str(retry_count))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Image Download :  Connect retry '+str(i)+'/'+str(retry_count))
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Image Download :  Connect retry '+str(i)+'/'+str(retry_count))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Image Download :  Connect retry '+str(i)+'/'+str(retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')
    moveFailedFolder()
def imageDownload(filepath): #封面是否下载成功，否则移动到failed
    if option == 'emby':
        if DownloadFileWithFilename(cover, number + '.jpg', path) == 'failed':
            moveFailedFolder()
        DownloadFileWithFilename(cover, number + '.jpg', path)
        if multi_part == 1:
            old_name = os.path.join(path, number + '.jpg')
            new_name = os.path.join(path, number + part + '.jpg')
            os.rename(old_name, new_name)
            print('[+]Image Downloaded!', path + '/' + number + part + '.jpg')
        else:
            print('[+]Image Downloaded!', path + '/' + number + '.jpg')
    elif option == 'plex':
        if DownloadFileWithFilename(cover, 'fanart.jpg', path) == 'failed':
            moveFailedFolder()
        DownloadFileWithFilename(cover, 'fanart.jpg', path)
        print('[+]Image Downloaded!', path + '/fanart.jpg')
def PrintFiles(filepath):
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
                    for i in str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(','):
                        print("  <tag>" + i + "</tag>", file=code)
                except:
                    aaaaa = ''
                try:
                    for i in str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(','):
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
        elif imagecut == 0:
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
                img2.save(path + '/' + number + '.png')
            except:
                print('[-]Cover cut failed!')
        elif imagecut == 0:
            img = Image.open(path + '/' + number + '.jpg')
            w = img.width
            h = img.height
            img.save(path + '/' + number + '.png')
def pasteFileToFolder(filepath, path): #文件路径，番号，后缀，要移动至的位置
    global houzhui
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|avi|rmvb|wmv|mov|mp4|mkv|flv|ts)$', filepath).group())
    try:
        os.rename(filepath, path + '/' + number + houzhui)
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        os._exit(0)
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        os._exit(0)
def renameJpgToBackdrop_copy():
    if option == 'plex':
        shutil.copy(path + '/fanart.jpg', path + '/Backdrop.jpg')
        shutil.copy(path + '/poster.png', path + '/thumb.png')
    if option == 'emby':
        shutil.copy(path + '/' + number + '.jpg', path + '/Backdrop.jpg')
def renameBackdropToJpg_copy():
    if option == 'plex':
        shutil.copy(path + '/fanart.jpg', path + '/Backdrop.jpg')
        shutil.copy(path + '/poster.png', path + '/thumb.png')
    if option == 'emby':
        shutil.copy(path + '/Backdrop.jpg', path + '/' + number + '.jpg')
        print('[+]Image Downloaded!', path + '/' + number + '.jpg')
def get_part(filepath):
    try:
        if re.search('-CD\d+', filepath):
            return re.findall('-CD\d+', filepath)[0]
    except:
        print("[-]failed!Please rename the filename again!")
        moveFailedFolder()
def debug_mode():
    try:
        if config['debug_mode']['switch'] == '1':
            print('[+] ---Debug info---')
            for i, v in json_data.items():
                if i == 'outline':
                    print('[+] -', i, ':', len(v), 'characters')
                    continue
                if i == 'actor_photo' or i == 'year':
                    continue
                print('[+] -', i, ':', v)
            print('[+] ---Debug info---')
    except:
        aaa=''
if __name__ == '__main__':
    filepath=argparse_get_file()[0] #影片的路径

    if '-CD' in filepath or '-cd' in filepath:
        multi_part = 1
    part = get_part(filepath)
    if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
        cn_sub='1'

    if argparse_get_file()[1] == '':    #获取手动拉去影片获取的番号
        try:
            number = str(re.findall(r'(.+?)\.',str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$',filepath).group()))).strip("['']").replace('_','-')
            print("[!]Making Data for   [" + number + "]")
        except:
            print("[-]failed!Please rename the filename again!")
            moveFailedFolder()
    else:
        number = argparse_get_file()[1]
    CreatFailedFolder()
    getDataFromJSON(number)  # 定义番号
    debug_mode()
    creatFolder()  # 创建文件夹
    if program_mode == '1':
        if part == '-CD1' or multi_part == 0:
            smallCoverCheck()
            imageDownload(filepath)  # creatFoder会返回番号路径
            if multi_part == 1:
                number += part
            PrintFiles(filepath)  # 打印文件
            cutImage()  # 裁剪图
            renameJpgToBackdrop_copy()
        else:
            number += part
            renameBackdropToJpg_copy()
        pasteFileToFolder(filepath, path)  # 移动文件
    elif program_mode == '2':
        pasteFileToFolder(filepath, path)  # 移动文件
