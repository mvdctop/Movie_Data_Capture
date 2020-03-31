#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests, os
from configparser import RawConfigParser
from base64 import b64encode
from traceback import format_exc
from json import loads
from os.path import exists

# 检查“actor_photos”文件夹是否就绪
if not exists('actor_photos'):
    print('\n“actor_photos” folder lost！Please put it to the same location with program\n')
    os.system('pause')
# 读取配置文件，这个ini文件用来给用户设置emby网址和api id
print('Reading ini Setting...')
config_settings = RawConfigParser()
try:
    config_settings.read('ap_config.ini', encoding='utf-8-sig')
    url_emby = config_settings.get("emby/jellyfin", "website")
    api_key = config_settings.get("emby/jellyfin", "api id")
    bool_replace = True if config_settings.get("emby/jellyfin", "是否覆盖以前上传的头像？") == '是' else False
except:
    print(format_exc())
    print('Cannot read ini files!')
    os.system('pause')
print('Read Success!\n')
# 修正用户输入的emby网址，无论是不是带“/”
if not url_emby.endswith('/'):
    url_emby += '/'
# 成功的个数
num_suc = 0
num_fail = 0
num_exist = 0
sep = os.sep
try:
    print('Getting emby/jellyfin Person`s form...')
    # curl -X GET "http://localhost:8096/emby/Persons?api_key=3291434710e342089565ad05b6b2f499" -H "accept: application/json"
    # 得到所有“人员” emby api没有细分“演员”还是“导演”“编剧”等等 下面得到的是所有“有关人员”
    url_emby_persons = url_emby + 'emby/Persons?api_key=' + api_key  # &PersonTypes=Actor
    try:
        rqs_emby = requests.get(url=url_emby_persons)
    except requests.exceptions.ConnectionError:
        print('Cannot connect to emby/jellyfin server ,Please check：', url_emby, '\n')
        os.system('pause')
    except:
        print(format_exc())
        print('Unkown Error ,Please submit screenshot to issues', url_emby, '\n')
        os.system('pause')
    # 401，无权访问
    if rqs_emby.status_code == 401:
        print('Please check API KEY！\n')
        os.system('pause')
    # print(rqs_emby.text)
    try:
        list_persons = loads(rqs_emby.text)['Items']
    except:
        print(rqs_emby.text)
        print('Error! emby response：')
        print('Please submit screenshot to issues！')
        os.system('pause')
    num_persons = len(list_persons)
    print('There are currently' + str(num_persons) + ' People！\n')
    # os.system('pause')
    # 用户emby中的persons，在“actor_photos”文件夹中，已有头像的，记录下来
    f_txt = open("included.txt", 'w', encoding="utf-8")
    f_txt.close()
    f_txt = open("no_included.txt", 'w', encoding="utf-8")
    f_txt.close()
    for dic_each_actor in list_persons:
        actor_name = dic_each_actor['Name']
        # 头像jpg/png在“actor_photos”中的路径
        actor_pic_path = 'actor_photos' + sep + actor_name[0] + sep + actor_name
        if exists(actor_pic_path + '.jpg'):
            actor_pic_path = actor_pic_path + '.jpg'
            header = {"Content-Type": 'image/jpeg', }
        elif exists(actor_pic_path + '.png'):
            actor_pic_path = actor_pic_path + '.png'
            header = {"Content-Type": 'image/png', }
        else:
            print('>>No image：', actor_name)
            f_txt = open("no_included.txt", 'a', encoding="utf-8")
            f_txt.write(actor_name + '\n')
            f_txt.close()
            num_fail += 1
            continue
        # emby有某个演员，“actor_photos”文件夹也有这个演员的头像，记录一下
        f_txt = open("included.txt", 'a', encoding="utf-8")
        f_txt.write(actor_name + '\n')
        f_txt.close()
        # emby有某个演员，已经有他的头像，不再进行下面“上传头像”的操作
        if dic_each_actor['ImageTags']:  # emby已经收录头像
            num_exist += 1
            if not bool_replace:  # 不需要覆盖已有头像
                continue          # 那么不进行下面的上传操作
        f_pic = open(actor_pic_path, 'rb')  # 二进制方式打开图文件
        b6_pic = b64encode(f_pic.read())  # 读取文件内容，转换为base64编码
        f_pic.close()
        url_post_img = url_emby + 'emby/Items/' + dic_each_actor['Id'] + '/Images/Primary?api_key=' + api_key
        requests.post(url=url_post_img, data=b6_pic, headers=header)
        print('>>Success：', actor_name)
        num_suc += 1

    print('\nemby/jellyfin people: ', num_persons, '')
    print('include photos: ', num_exist, '')
    if bool_replace:
        print('Mode：Overwrite existed images')
    else:
        print('Mode：Skip existed images')
    print('Success Upload', num_suc, '个！')
    print('No images', num_fail, '个！')
    print('Saved to “no_included.txt”\n')
    os.system('pause')
except:
    print(format_exc())
    os.system('pause')


