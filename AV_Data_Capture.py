#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import time
import re
from ADC_function import *
from core import *
import json
import shutil
from configparser import ConfigParser
import argparse


def UpdateCheck(version):
    if UpdateCheckSwitch() == '1':
        html2 = get_html('https://raw.githubusercontent.com/yoshiko2/AV_Data_Capture/master/update_check.json')
        html = json.loads(str(html2))

        if not version == html['version']:
            print('[*]                  * New update ' + html['version'] + ' *')
            print('[*]                     ↓ Download ↓')
            print('[*] ' + html['download'])
            print('[*]======================================================')
    else:
        print('[+]Update Check disabled!')

def argparse_get_file():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", default='',nargs='?', help="Write the file path on here")
    args = parser.parse_args()
    if args.file == '':
        return ''
    else:
        return args.file

def movie_lists(escape_folder):
    escape_folder = re.split('[,，]', escape_folder)
    total = []
    file_type = ['.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.MP4', '.AVI', '.RMVB', '.WMV','.MOV', '.MKV', '.FLV', '.TS', '.WEBM', ]
    file_root = os.getcwd()
    for root, dirs, files in os.walk(file_root):
        flag_escape = 0
        for folder in escape_folder:
            if folder in root:
                flag_escape = 1
                break
        if flag_escape == 1:
            continue
        for f in files:
            if os.path.splitext(f)[1] in file_type:
                path = os.path.join(root, f)
                path = path.replace(file_root, '.')
                total.append(path)
    return total


def CreatFailedFolder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            os._exit(0)


def CEF(path):
    try:
        files = os.listdir(path)  # 获取路径下的子文件(夹)列表
        for file in files:
            os.removedirs(path + '/' + file)  # 删除这个空文件夹
            print('[+]Deleting empty folder', path + '/' + file)
    except:
        a = ''


def getNumber(filepath,absolute_path = False):
    if absolute_path == True:
        filepath=filepath.replace('\\','/')
        file_number = str(re.findall(r'(.+?)\.', str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filepath).group()))).strip("['']").replace('_', '-')
        return file_number
    if '-' in filepath or '_' in filepath:  # 普通提取番号 主要处理包含减号-和_的番号
        filepath = filepath.replace("_", "-")
        filepath.strip('22-sht.me').strip('-HD').strip('-hd')
        filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filepath))  # 去除文件名中时间
        if 'FC2' or 'fc2' in filename:
            filename = filename.replace('-PPV', '').replace('PPV-', '').replace('FC2PPV-','FC2-').replace('FC2PPV_','FC2-')
        file_number = re.search(r'\w+-\w+', filename, re.A).group()
        return file_number
    else:  # 提取不含减号-的番号，FANZA CID
        try:
            return str(re.findall(r'(.+?)\.', str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filepath).group()))).strip("['']").replace('_', '-')
        except:
            return re.search(r'(.+?)\.', filepath)[0]


if __name__ == '__main__':
    version = '2.8.2'
    config_file = 'config.ini'
    config = ConfigParser()
    config.read(config_file, encoding='UTF-8')
    success_folder = config['common']['success_output_folder']
    failed_folder = config['common']['failed_output_folder']  # 失败输出目录
    escape_folder = config['escape']['folders']  # 多级目录刮削需要排除的目录
    print('[*]================== AV Data Capture ===================')
    print('[*]                    Version ' + version)
    print('[*]======================================================')

    UpdateCheck(version)
    CreatFailedFolder(failed_folder)
    os.chdir(os.getcwd())
    movie_list = movie_lists(escape_folder)

    #========== 野鸡番号拖动 ==========
    number_argparse=argparse_get_file()
    if not number_argparse == '':
        print("[!]Making Data for   [" + number_argparse + "], the number is [" + getNumber(number_argparse,absolute_path = True) + "]")
        core_main(number_argparse, getNumber(number_argparse,absolute_path = True))
        print("[*]======================================================")
        CEF(success_folder)
        CEF(failed_folder)
        print("[+]All finished!!!")
        input("[+][+]Press enter key exit, you can check the error messge before you exit.")
        os._exit(0)
    # ========== 野鸡番号拖动 ==========

    count = 0
    count_all = str(len(movie_list))
    print('[+]Find', count_all, 'movies')
    if config['common']['soft_link'] == '1':
        print('[!] --- Soft link mode is ENABLE! ----')
    for i in movie_list:  # 遍历电影列表 交给core处理
        count = count + 1
        percentage = str(count / int(count_all) * 100)[:4] + '%'
        print('[!] - ' + percentage + ' [' + str(count) + '/' + count_all + '] -')
        # print("[!]Making Data for   [" + i + "], the number is [" + getNumber(i) + "]")
        # core_main(i, getNumber(i))
        # print("[*]======================================================")
        try:
            print("[!]Making Data for   [" + i + "], the number is [" + getNumber(i) + "]")
            core_main(i, getNumber(i))
            print("[*]======================================================")
        except:  # 番号提取异常
            print('[-]' + i + ' Cannot catch the number :')
            if config['common']['soft_link'] == '1':
                print('[-]Link', i, 'to failed folder')
                os.symlink(i, str(os.getcwd()) + '/' + failed_folder + '/')
            else:
                try:
                    print('[-]Move ' + i + ' to failed folder')
                    shutil.move(i, str(os.getcwd()) + '/' + failed_folder + '/')
                except FileExistsError:
                    print('[!]File exists in failed!')
                except:
                    print('[+]skip')
            continue

    CEF(success_folder)
    CEF(failed_folder)
    print("[+]All finished!!!")
    input("[+][+]Press enter key exit, you can check the error messge before you exit.")
