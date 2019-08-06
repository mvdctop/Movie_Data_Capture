#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import os.path
import shutil
from PIL import Image
import time
import javbus
import json
import fc2fans_club
import siro
from ADC_function import *
from configparser import ConfigParser
import argparse
import javdb

#初始化全局变量
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
path=''
houzhui=''
website=''
json_data={}
actor_photo={}
naming_rule  =''#eval(config['Name_Rule']['naming_rule'])
location_rule=''#eval(config['Name_Rule']['location_rule'])

Config = ConfigParser()
Config.read(config_file, encoding='UTF-8')
try:
    option = ReadMediaWarehouse()
except:
    print('[-]Config media_warehouse read failed!')

#=====================本地文件处理===========================
def moveFailedFolder():
    global filepath
    print('[-]Move to "failed"')
    #print('[-]' + filepath + ' -> ' + output_dir + '/failed/')
    #os.rename(filepath, output_dir + '/failed/')
    os._exit(0)
def argparse_get_file():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Write the file path on here")
    parser.add_argument("--number", help="Enter Number on here", default='')
    args = parser.parse_args()
    return (args.file, args.number)
def CreatFailedFolder():
    if not os.path.exists('/failed/'):  # 新建failed文件夹
        try:
            os.makedirs('/failed/')
        except:
            print("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            os._exit(0)
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

    global naming_rule
    global location_rule


    # ================================================网站规则添加开始================================================

    try:    # 添加 需要 正则表达式的规则
        # =======================javdb.py=======================
        if re.search('^\d{5,}', file_number).group() in file_number:
            json_data = json.loads(javbus.main_uncensored(file_number))
    except:  # 添加 无需 正则表达式的规则
        # ====================fc2fans_club.py====================
        if 'fc2' in file_number:
            json_data = json.loads(fc2fans_club.main(
                file_number.strip('fc2_').strip('fc2-').strip('ppv-').strip('PPV-').strip('FC2_').strip('FC2-').strip('ppv-').strip('PPV-')))
        elif 'FC2' in file_number:
            json_data = json.loads(fc2fans_club.main(
                file_number.strip('FC2_').strip('FC2-').strip('ppv-').strip('PPV-').strip('fc2_').strip('fc2-').strip('ppv-').strip('PPV-')))
        # =======================javbus.py=======================
        else:
            json_data = json.loads(javbus.main(file_number))

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
    imagecut    =     json_data['imagecut']
    tag         = str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表
    actor       = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')
    actor_photo =     json_data['actor_photo']
    website     =     json_data['website']

    if title == '' or number == '':
        print('[-]Movie Data not found!')
        moveFailedFolder()

    # ====================处理异常字符====================== #\/:*?"<>|
    if '\\' in title:
        title=title.replace('\\', ' ')
    elif '/' in title:
        title=title.replace('/', '')
    elif ':' in title:
        title=title.replace('/', '')
    elif '*' in title:
        title=title.replace('*', '')
    elif '?' in title:
        title=title.replace('?', '')
    elif '"' in title:
        title=title.replace('"', '')
    elif '<' in title:
        title=title.replace('<', '')
    elif '>' in title:
        title=title.replace('>', '')
    elif '|' in title:
        title=title.replace('|', '')
    # ====================处理异常字符 END================== #\/:*?"<>|

    naming_rule   = eval(config['Name_Rule']['naming_rule'])
    location_rule = eval(config['Name_Rule']['location_rule'])
def creatFolder(): #创建文件夹
    global actor
    global path
    if len(actor) > 240:                    #新建成功输出文件夹
        path = location_rule.replace("'actor'","'超多人'",3).replace("actor","'超多人'",3) #path为影片+元数据所在目录
        #print(path)
    else:
        path = location_rule
        #print(path)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            path = location_rule.replace('/['+number+']-'+title,"/number")
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
        print('[+]Image Downloaded!', path + '/' + number + '.jpg')
    elif option == 'plex':
        if DownloadFileWithFilename(cover, 'fanart.jpg', path) == 'failed':
            moveFailedFolder()
        DownloadFileWithFilename(cover, 'fanart.jpg', path)
        print('[+]Image Downloaded!', path + '/fanart.jpg')
def PrintFiles(filepath):
    #global path
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
                img2.save(path + '/' + number + '.png')
            except:
                print('[-]Cover cut failed!')
        else:
            img = Image.open(path + '/' + number + '.jpg')
            w = img.width
            h = img.height
            img.save(path + '/' + number + '.png')
def pasteFileToFolder(filepath, path): #文件路径，番号，后缀，要移动至的位置
    global houzhui
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|avi|rmvb|wmv|mov|mp4|mkv|flv|ts)$', filepath).group())
    os.rename(filepath, number + houzhui)
    try:
        shutil.move(number + houzhui, path)
    except:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        os._exit(0)
def moveJpgToBackdrop_copy():
    if option == 'plex':
        shutil.copy(path + '/fanart.jpg', path + '/Backdrop.jpg')
        shutil.copy(path + '/poster.png', path + '/thumb.png')
    if option == 'emby':
        shutil.copy(path + '/' + number + '.jpg', path + '/Backdrop.jpg')

if __name__ == '__main__':
    filepath=argparse_get_file()[0] #影片的路径

    if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
        cn_sub='1'

    if argparse_get_file()[1] == '':    #获取手动拉去影片获取的番号
        try:
            number = str(re.findall(r'(.+?)\.',str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$',filepath).group()))).strip("['']").replace('_','-')
            print("[!]Making Data for   [" + number + "]")
        except:
            print("[-]failed!Please move the filename again!")
            moveFailedFolder()
    else:
        number = argparse_get_file()[1]
    CreatFailedFolder()
    getDataFromJSON(number)  # 定义番号
    creatFolder()  # 创建文件夹
    imageDownload(filepath)  # creatFoder会返回番号路径
    PrintFiles(filepath)  # 打印文件
    cutImage()  # 裁剪图
    pasteFileToFolder(filepath, path)  # 移动文件
    moveJpgToBackdrop_copy()
