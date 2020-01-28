#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import time
import re
from ADC_function import *
import json
import shutil
import fnmatch
from configparser import ConfigParser
os.chdir(os.getcwd())

# ============global var===========

version='2.3'

config = ConfigParser()
config.read(config_file, encoding='UTF-8')

Platform = sys.platform

# ==========global var end=========

def UpdateCheck():
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
def movie_lists():
    global exclude_directory_1
    global exclude_directory_2
    total=[]
    file_type = ['.mp4','.avi','.rmvb','.wmv','.mov','.mkv','.flv','.ts','.MP4', '.AVI', '.RMVB', '.WMV', '.MOV', '.MKV', '.FLV', '.TS',]
    exclude_directory_1 = config['common']['failed_output_folder']
    exclude_directory_2 = config['common']['success_output_folder']
    file_root=os.getcwd()
    for root,dirs,files in os.walk(file_root):
        if exclude_directory_1 not in root and exclude_directory_2 not in root:
            for f in files:
                if os.path.splitext(f)[1] in file_type:
                    path = os.path.join(root,f)
                    path = path.replace(file_root,'.')
                    total.append(path)
    return total
def CreatFailedFolder():
    if not os.path.exists('failed/'):  # 新建failed文件夹
        try:
            os.makedirs('failed/')
        except:
            print("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            os._exit(0)
def lists_from_test(custom_nuber): #电影列表
    a=[]
    a.append(custom_nuber)
    return a
def CEF(path):
    try:
        files = os.listdir(path)  # 获取路径下的子文件(夹)列表
        for file in files:
            os.removedirs(path + '/' + file)  # 删除这个空文件夹
            print('[+]Deleting empty folder', path + '/' + file)
    except:
        a=''
def rreplace(self, old, new, *max):
#从右开始替换文件名中内容，源字符串，将被替换的子字符串， 新字符串，用于替换old子字符串，可选字符串, 替换不超过 max 次
    count = len(self)
    if max and str(max[0]).isdigit():
        count = max[0]
    return new.join(self.rsplit(old, count))
def getNumber(filepath):
    filepath = filepath.replace('.\\','')
    if '-' in filepath or '_' in filepath:  # 普通提取番号 主要处理包含减号-和_的番号
        filepath = filepath.replace("_", "-")
        filepath.strip('22-sht.me').strip('-HD').strip('-hd')
        filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filepath))  # 去除文件名中时间
        if 'FC2' or 'fc2' in filename:
            filename=filename.replace('-PPV','').replace('PPV-','')
        if '1000giri' in filename:
            filename = filename.replace('1000giri-','').replace('-1000giri','')
            file_number = re.search('\d+-\w+', filename).group()
            return file_number
        try:
            file_number = re.search('\w+-\d+', filename).group()
        except:  # 提取类似mkbd-s120番号
            file_number = re.search('\w+-\w+\d+', filename).group()
        return file_number
    else:  # 提取不含减号-的番号，FANZA CID
        try:
            return str(re.findall(r'(.+?)\.', str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filepath).group()))).strip("['']").replace('_', '-')
        except:
            return re.search(r'(.+?)\.',filepath)[0]

def RunCore():
    if Platform == 'win32':
        if os.path.exists('core.py'):
            os.system('python core.py' + '   "' + i + '" --number "' + getNumber(i) + '"')  # 从py文件启动（用于源码py）
        elif os.path.exists('core.exe'):
            os.system('core.exe' + '   "' + i + '" --number "' + getNumber(i) + '"')  # 从exe启动（用于EXE版程序）
        elif os.path.exists('core.py') and os.path.exists('core.exe'):
            os.system('python core.py' + '   "' + i + '" --number "' + getNumber(i) + '"')  # 从py文件启动（用于源码py）
    else:
        if os.path.exists('core.py'):
            try:
                os.system('python3 core.py' + '   "' + i + '" --number "' + getNumber(i) + '"')  # 从py文件启动（用于源码py）
            except:
                os.system('python core.py' + '   "' + i + '" --number "' + getNumber(i) + '"')  # 从py文件启动（用于源码py）
        elif os.path.exists('core.exe'):
            os.system('core.exe' + '   "' + i + '" --number "' + getNumber(i) + '"')  # 从exe启动（用于EXE版程序）
        elif os.path.exists('core.py') and os.path.exists('core.exe'):
            os.system('python3 core.py' + '   "' + i + '" --number "' + getNumber(i) + '"')  # 从py文件启动（用于源码py）

if __name__ =='__main__':
    print('[*]================== AV Data Capture ===================')
    print('[*]                     Version '+version)
    print('[*]======================================================')

    CreatFailedFolder()
    UpdateCheck()
    os.chdir(os.getcwd())
    movie_list=movie_lists()

    count = 0
    count_all = str(len(movie_list))
    print('[+]Find',count_all,'movies')
    if config['common']['soft_link'] == '1':
        print('[!] --- Soft link mode is ENABLE! ----')
    for i in movie_list: #遍历电影列表 交给core处理
        count = count + 1
        percentage = str(count/int(count_all)*100)[:4]+'%'
        print('[!] - '+percentage+' ['+str(count)+'/'+count_all+'] -')
        try:
            print("[!]Making Data for   [" + i + "], the number is [" + getNumber(i) + "]")
            RunCore()
            print("[*]======================================================")
        except:  # 番号提取异常
            print('[-]' + i + ' Cannot catch the number :')
            if config['common']['soft_link'] == '1':
                print('[-]Link',i,'to failed folder')
                os.symlink(i,str(os.getcwd()) + '/' + 'failed/')
            else:
                print('[-]Move ' + i + ' to failed folder')
                shutil.move(i, str(os.getcwd()) + '/' + 'failed/')
            continue

    CEF(exclude_directory_1)
    CEF(exclude_directory_2)
    print("[+]All finished!!!")
    input("[+][+]Press enter key exit, you can check the error messge before you exit.")
