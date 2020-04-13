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


def check_update(current_version):
    if UpdateCheckSwitch() == "1":
        data = json.loads(get_html("https://api.github.com/repos/yoshiko2/AV_Data_Capture/releases/latest"))

        remote_version = data["tag_name"]
        download_url = data["html_url"]

        if current_version != remote_version:
            line1 = "* New update " + remote_version + " *"
            print("[*]" + line1.center(54))
            print("[*]" + "↓ Download ↓".center(54))
            print("[*] " + download_url)
            print("[*]======================================================")
    else:
        print("[+]Update Check disabled!")

def argparse_function(switch):
    parser = argparse.ArgumentParser()
    parser.add_argument("file", default='',nargs='?', help="Single Movie file path.")
    parser.add_argument("-c", "--config", default='config.ini', nargs='?', help="The config file Path.")
    parser.add_argument("-e", "--exit", default='1', nargs='?', help="Exit Switch 1:Press enter key to exit.  2:Auto exit.")
    args = parser.parse_args()
    if switch == 1:
        if args.file == '':
            return ''
    elif switch == 2:
        return args.config
    elif switch == 3:
        return args.exit

def movie_lists(root, escape_folder):
    for folder in escape_folder:
        if folder in root:
            return []
    total = []
    file_type = ['.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.MP4', '.AVI', '.RMVB', '.WMV','.MOV', '.MKV', '.FLV', '.TS', '.WEBM', ]
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.isdir(f):
            total += movie_lists(f, escape_folder)
        elif os.path.splitext(f)[1] in file_type:
            total.append(f)
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
            filename = filename.replace('-PPV', '').replace('PPV-', '').replace('FC2PPV-', 'FC2-').replace('FC2PPV_', 'FC2-')
            filename = filename.replace('-ppv', '').replace('ppv-', '').replace('fc2ppv-', 'FC2-').replace('fc2ppv_', 'FC2-')
        file_number = re.search(r'\w+-\w+', filename, re.A).group()
        return file_number
    else:  # 提取不含减号-的番号，FANZA CID
        try:
            return str(re.findall(r'(.+?)\.', str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filepath).group()))).strip("['']").replace('_', '-')
        except:
            return re.search(r'(.+?)\.', filepath)[0]


if __name__ == '__main__':
    version = '3.1.2'
    config_file = argparse_function(2)
    config = ConfigParser()
    config.read(config_file, encoding='UTF-8')
    success_folder = config['common']['success_output_folder']
    failed_folder = config['common']['failed_output_folder']  # 失败输出目录
    escape_folder = config['escape']['folders']  # 多级目录刮削需要排除的目录
    escape_folder = re.split('[,，]', escape_folder)
    version_print = 'Version ' + version
    print('[*]================== AV Data Capture ===================')
    print('[*]' + version_print.center(54))
    print('[*]======================================================')

    check_update(version)
    CreatFailedFolder(failed_folder)
    os.chdir(os.getcwd())
    movie_list = movie_lists('.', escape_folder)

    #========== 野鸡番号拖动 ==========
    number_argparse = argparse_function(1)
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
            core_main(i, getNumber(i), config_file=config_file)
            print("[*]======================================================")
        except Exception as e:  # 番号提取异常
            print('[-]' + i + ' ERRPR :')
            print('[-]',e)
            if config['common']['soft_link'] == '1':
                print('[-]Link', i, 'to failed folder')
                os.symlink(i, str(os.getcwd()) + '/' + failed_folder + '/')
            else:
                try:
                    print('[-]Move ' + i + ' to failed folder')
                    shutil.move(i, str(os.getcwd()) + '/' + failed_folder + '/')
                except Exception as e2:
                    print('[!]', e2)
            continue

    CEF(success_folder)
    CEF(failed_folder)
    print("[+]All finished!!!")
    if argparse_function(3) == '2':
        os._exit(0)
    input("[+][+]Press enter key exit, you can check the error messge before you exit.")
