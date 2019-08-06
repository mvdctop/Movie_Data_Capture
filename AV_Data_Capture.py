#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import time
import re
import sys
from ADC_function import *
import json
import subprocess
import shutil
from configparser import ConfigParser

version='0.11.7'
os.chdir(os.getcwd())

input_dir='.' # 电影的读取与输出路径, 默认为当前路径

config = ConfigParser()
config.read(config_file, encoding='UTF-8')

def UpdateCheck():
    if UpdateCheckSwitch() == '1':
        html = json.loads(get_html('https://raw.githubusercontent.com/wenead99/AV_Data_Capture/master/update_check.json'))
        if not version == html['version']:
            print('[*]        * New update ' + html['version'] + ' *')
            print('[*]             * Download *')
            print('[*] ' + html['download'])
            print('[*]=====================================')
    else:
        print('[+]Update Check disabled!')

def set_directory(): # 设置读取与存放路径
    global input_dir
    # 配置项switch为1且定义了新的路径时, 更改默认存取路径
    if config['directory_capture']['switch'] == '1': 
        custom_input = config['directory_capture']['input_directory']
        if custom_input != '': # 自定义了输入路径
            input_dir = format_path(custom_input)
            # 若自定义了输入路径, 输出路径默认在输入路径下
    CreatFolder(input_dir)
    #print('[+]Working directory is "' + os.getcwd() + '".')
    #print('[+]Using "' + input_dir + '" as input directory.')

def format_path(path): # 使路径兼容Linux与MacOS
    if path.find('\\'): # 是仅兼容Windows的路径格式
        path_list=path.split('\\')
        path='/'.join(path_list) # 转换为可移植的路径格式
    return path


def movie_lists():
    a2 = glob.glob( input_dir + "/*.mp4")
    b2 = glob.glob( input_dir + "/*.avi")
    c2 = glob.glob( input_dir + "/*.rmvb")
    d2 = glob.glob( input_dir + "/*.wmv")
    e2 = glob.glob( input_dir + "/*.mov")
    f2 = glob.glob( input_dir + "/*.mkv")
    g2 = glob.glob( input_dir + "/*.flv")
    h2 = glob.glob( input_dir + "/*.ts")
    total = a2 + b2 + c2 + d2 + e2 + f2 + g2 + h2
    return total
def CreatFolder(folder_path):
    if not os.path.exists(folder_path):  # 新建文件夹
        try:
            print('[+]Creating ' + folder_path)
            os.makedirs(folder_path)
        except:
            print("[-]failed!can not be make folder '"+folder_path+"'\n[-](Please run as Administrator)")
            os._exit(0)
def lists_from_test(custom_nuber): #电影列表
    a=[]
    a.append(custom_nuber)
    return a
def CEF(path):
    files = os.listdir(path)  # 获取路径下的子文件(夹)列表
    for file in files:
        try: #试图删除空目录,非空目录删除会报错
            os.removedirs(path + '/' + file)  # 删除这个空文件夹
            print('[+]Deleting empty folder',path + '/' + file)
        except:
            a=''
def rreplace(self, old, new, *max):
#从右开始替换文件名中内容，源字符串，将被替换的子字符串， 新字符串，用于替换old子字符串，可选字符串, 替换不超过 max 次
    count = len(self)
    if max and str(max[0]).isdigit():
        count = max[0]
    return new.join(self.rsplit(old, count))
def getNumber(filepath):
    try:  # 试图提取番号
        # ====番号获取主程序====
        try:  # 普通提取番号 主要处理包含减号-的番号
            filepath1 = filepath.replace("_", "-")
            filepath1.strip('22-sht.me').strip('-HD').strip('-hd')
            filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filepath1))  # 去除文件名中时间
            file_number = re.search('\w+-\d+', filename).group()
            return file_number
        except:  # 提取不含减号-的番号
            try:  # 提取东京热番号格式 n1087
                filename1 = str(re.sub("h26\d", "", filepath)).strip('Tokyo-hot').strip('tokyo-hot')
                filename0 = str(re.sub(".*?\.com-\d+", "", filename1)).strip('_')
                if '-C.' in filepath or '-c.' in filepath:
                    cn_sub = '1'
                file_number = str(re.search('n\d{4}', filename0).group(0))
                return file_number
            except:  # 提取无减号番号
                filename1 = str(re.sub("h26\d", "", filepath))  # 去除h264/265
                filename0 = str(re.sub(".*?\.com-\d+", "", filename1))
                file_number2 = str(re.match('\w+', filename0).group())
                if '-C.' in filepath or '-c.' in filepath:
                    cn_sub = '1'
                file_number = str(file_number2.replace(re.match("^[A-Za-z]+", file_number2).group(),
                                                       re.match("^[A-Za-z]+", file_number2).group() + '-'))
                return file_number
                # if not re.search('\w-', file_number).group() == 'None':
                # file_number = re.search('\w+-\w+', filename).group()
                # 上面是插入减号-到番号中
    # ====番号获取主程序=结束===
    except Exception as e:  # 番号提取异常
        print('[-]' + str(os.path.basename(filepath)) + ' Cannot catch the number :')
        print('[-]' + str(os.path.basename(filepath)) + ' :', e)
        print('[-]Move ' + os.path.basename(filepath) + ' to failed folder')
        #print('[-]' + filepath + ' -> ' + output_dir + '/failed/')
        #shutil.move(filepath, output_dir + '/failed/')
    except IOError as e2:
        print('[-]' + str(os.path.basename(filepath)) + ' Cannot catch the number :')
        print('[-]' + str(os.path.basename(filepath)) + ' :', e2)
        #print('[-]' + filepath + ' -> ' + output_dir + '/failed/')
        #shutil.move(filepath, output_dir + '/failed/')

def RunCore(movie):
    # 异步调用core.py, core.py作为子线程执行, 本程序继续执行.
    if os.path.exists('core.py'):
        cmd_arg=[sys.executable,'core.py',movie,'--number',getNumber(movie)] #从py文件启动（用于源码py）
    elif os.path.exists('core.exe'):
        cmd_arg=['core.exe',movie,'--number',getNumber(movie)] #从exe启动（用于EXE版程序）
    elif os.path.exists('core.py') and os.path.exists('core.exe'):
        cmd_arg=[sys.executable,'core.py',movie,'--number',getNumber(movie)] #从py文件启动（用于源码py）
    process=subprocess.Popen(cmd_arg)
    return process

if __name__ =='__main__':
    print('[*]===========AV Data Capture===========')
    print('[*]           Version  '+version)
    print('[*]=====================================')
    UpdateCheck()
    os.chdir(os.getcwd())
    set_directory()


    count = 0
    movies = movie_lists()
    count_all = str(len(movies))
    print('[+]Find ' + str(len(movies)) + ' movies.')
    process_list=[]
    for movie in movies: #遍历电影列表 交给core处理
        num=getNumber(movie) # 获取番号
        if num is None:
            movies.remove(movie) # 未获取到番号, 则将影片从列表移除
            count_all=count_all-1
            continue
        print("[!]Making Data for   [" + movie + "], the number is [" + num + "]")
        process=RunCore(movie)
        process_list.append(process)
    print("[*]=====================================")
    for i in range(len(movies)):
        process_list[i].communicate()
        percentage = str((i+1)/int(count_all)*100)[:4]+'%'
        print('[!] - '+percentage+' ['+str(count)+'/'+count_all+'] -')
        print("[!]The [" + getNumber(movies[i]) + "] process is done.")
    print("[*]=====================================")
        
    CEF(input_dir)
    print("[+]All finished!!!")
    input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
