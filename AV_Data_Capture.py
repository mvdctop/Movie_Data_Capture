import argparse
import json
import os
import re
import sys
import shutil
import urllib3

import config
import time
from ADC_function import get_html, is_link
from number_parser import get_number
from core import core_main


def check_update(local_version):
    try:
        data = json.loads(get_html("https://api.github.com/repos/yoshiko2/AV_Data_Capture/releases/latest"))
    except:
        print("[-]Failed to update! Please check new version manually:")
        print("[-] https://github.com/yoshiko2/AV_Data_Capture/releases")
        print("[*]======================================================")
        return

    remote = int(data["tag_name"].replace(".",""))
    local_version = int(local_version.replace(".", ""))
    if local_version < remote:
        print("[*]" + ("* New update " + str(data["tag_name"]) + " *").center(54))
        print("[*]" + "↓ Download ↓".center(54))
        print("[*]https://github.com/yoshiko2/AV_Data_Capture/releases")
        print("[*]======================================================")


def argparse_function(ver: str) -> [str, str, bool]:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", default='', nargs='?', help="Single Movie file path.")
    parser.add_argument("-p","--path",default='',nargs='?',help="Analysis folder path.")
    # parser.add_argument("-c", "--config", default='config.ini', nargs='?', help="The config file Path.")
    parser.add_argument("-n", "--number", default='', nargs='?', help="Custom file number")
    parser.add_argument("-a", "--auto-exit", dest='autoexit', action="store_true",
                        help="Auto exit after program complete")
    parser.add_argument("-v", "--version", action="version", version=ver)
    args = parser.parse_args()

    return args.file, args.path, args.number, args.autoexit

def movie_lists(root, escape_folder):
    if os.path.basename(root) in escape_folder:
        return []
    total = []
    file_type = conf.media_type().upper().split(",")
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.isdir(f):
            total += movie_lists(f, escape_folder)
        elif os.path.splitext(f)[1].upper() in file_type:
            absf = os.path.abspath(f)
            if conf.main_mode() == 3 or not is_link(absf):
                total.append(absf)
    return total


def create_failed_folder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            sys.exit(0)


def rm_empty_folder(path):
    try:
        files = os.listdir(path)  # 获取路径下的子文件(夹)列表
    except:
        return
    for file in files:
        try:
            os.rmdir(path + '/' + file)  # 删除这个空文件夹
            print('[+]Deleting empty folder', path + '/' + file)
        except:
            pass


def create_data_and_move(file_path: str, c: config.Config, debug):
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    file_name = os.path.basename(file_path)
    n_number = get_number(debug, file_name)
    file_path = os.path.abspath(file_path)

    if debug == True:
        print("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
        if n_number:
            core_main(file_path, n_number, c)
        else:
            print("[-] number empty ERROR")
        print("[*]======================================================")
    else:
        try:
            print("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
            if n_number:
                core_main(file_path, n_number, c)
            else:
                raise ValueError("number empty")
            print("[*]======================================================")
        except Exception as err:
            print("[-] [{}] ERROR:".format(file_path))
            print('[-]', err)

            # 3.7.2 New: Move or not move to failed folder.
            if c.failed_move() == False:
                if c.soft_link():
                    print("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, conf.failed_folder() + "/" + file_name)
            elif c.failed_move() == True:
                if c.soft_link():
                    print("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, conf.failed_folder() + "/" + file_name)
                else:
                    try:
                        print("[-]Move [{}] to failed folder".format(file_path))
                        shutil.move(file_path, conf.failed_folder() + "/")
                    except Exception as err:
                        print('[!]', err)


def create_data_and_move_with_custom_number(file_path: str, c: config.Config, custom_number):
    try:
        print("[!]Making Data for [{}], the number is [{}]".format(file_path, custom_number))
        core_main(file_path, custom_number, c)
        print("[*]======================================================")
    except Exception as err:
        print("[-] [{}] ERROR:".format(file_path))
        print('[-]', err)

        if c.soft_link():
            print("[-]Link {} to failed folder".format(file_path))
            os.symlink(file_path, conf.failed_folder() + "/")
        else:
            try:
                print("[-]Move [{}] to failed folder".format(file_path))
                shutil.move(file_path, conf.failed_folder() + "/")
            except Exception as err:
                print('[!]', err)


if __name__ == '__main__':
    version = '4.6.7'
    urllib3.disable_warnings() #Ignore http proxy warning
    # Parse command line args
    single_file_path, folder_path, custom_number, auto_exit = argparse_function(version)

    print('[*]================== AV Data Capture ===================')
    print('[*]' + version.center(54))
    print('[*]======================================================')

    # Read config.ini
    conf = config.Config("config.ini")


    if conf.update_check():
        check_update(version)

    if conf.debug():
        print('[+]Enable debug')
    if conf.soft_link():
        print('[!]Enable soft link')

    create_failed_folder(conf.failed_folder())
    start_time = time.time()

    if not single_file_path == '': #Single File
        print('[+]==================== Single File =====================')
        if custom_number == '':
            create_data_and_move_with_custom_number(single_file_path, conf, get_number(conf.debug(), os.path.basename(single_file_path)))
        else:
            create_data_and_move_with_custom_number(single_file_path, conf, custom_number)
    else:
        if folder_path == '':
            folder_path = os.path.abspath(".")

        movie_list = movie_lists(folder_path, re.split("[,，]", conf.escape_folder()))

        count = 0
        count_all = str(len(movie_list))
        print('[+]Find', count_all, 'movies')

        for movie_path in movie_list:  # 遍历电影列表 交给core处理
            count = count + 1
            percentage = str(count / int(count_all) * 100)[:4] + '%'
            print('[!] - ' + percentage + ' [' + str(count) + '/' + count_all + '] -')
            create_data_and_move(movie_path, conf, conf.debug())

    rm_empty_folder(conf.success_folder())
    rm_empty_folder(conf.failed_folder())
    rm_empty_folder(os.getcwd())

    end_time = time.time()
    total_time = end_time - start_time
    print("[+]Used " + str(round(total_time,2)) + "s")

    print("[+]All finished!!!")
    if not (conf.auto_exit() or auto_exit):
        input("Press enter key exit, you can check the error message before you exit...")
    sys.exit(0)
