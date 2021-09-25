import argparse
import json
import os
import re
import sys
import shutil
import typing
import urllib3

import config
import datetime
import time
from pathlib import Path
from ADC_function import  file_modification_days, get_html, is_link
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


def argparse_function(ver: str) -> typing.Tuple[str, str, bool]:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("file", default='', nargs='?', help="Single Movie file path.")
    parser.add_argument("-p","--path",default='',nargs='?',help="Analysis folder path.")
    # parser.add_argument("-c", "--config", default='config.ini', nargs='?', help="The config file Path.")
    default_logdir = os.path.join(Path.home(),'.avlogs')
    parser.add_argument("-o","--log-dir",dest='logdir',default=default_logdir,nargs='?',
        help=f"""Duplicate stdout and stderr to logfiles
in logging folder, default on.
default for current user: {default_logdir}
Use --log-dir= to turn off logging feature.""")
    parser.add_argument("-n", "--number", default='', nargs='?', help="Custom file number")
    parser.add_argument("-a", "--auto-exit", dest='autoexit', action="store_true",
                        help="Auto exit after program complete")
    parser.add_argument("-v", "--version", action="version", version=ver)
    args = parser.parse_args()

    return args.file, args.path, args.number, args.autoexit, args.logdir


class OutLogger(object):
    def __init__(self, logfile) -> None:
        self.term = sys.stdout
        self.log = open(logfile,"w",encoding='utf-8')
    def __del__(self):
        self.close()
    def __enter__(self):
        pass
    def __exit__(self, *args):
        self.close()
    def write(self,msg):
        self.term.write(msg)
        self.log.write(msg)
    def flush(self):
        self.term.flush()
        self.log.flush()
        os.fsync(self.log.fileno())
    def close(self):
        if self.term != None:
            sys.stdout = self.term
            self.term = None
        if self.log != None:
            self.log.close()
            self.log = None


class ErrLogger(OutLogger):
    def __init__(self, logfile) -> None:
        self.term = sys.stderr
        self.log = open(logfile,"w",encoding='utf-8')
    def close(self):
        if self.term != None:
            sys.stderr = self.term
            self.term = None
        if self.log != None:
            self.log.close()
            self.log = None


def dupe_stdout_to_logfile(logdir: str):
    if not isinstance(logdir, str) or len(logdir) == 0:
        return
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
        if not os.path.isdir(logdir):
            return

    log_tmstr = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    logfile = os.path.join(logdir, f'avdc_{log_tmstr}.txt')
    errlog = os.path.join(logdir, f'avdc_{log_tmstr}_err.txt')

    sys.stdout = OutLogger(logfile)
    sys.stderr = ErrLogger(errlog)


def close_logfile(logdir: str):
    if not isinstance(logdir, str) or len(logdir) == 0 or not os.path.isdir(logdir):
        return
    sys.stdout.close()
    sys.stderr.close()
    # 清理空文件
    for current_dir, subdirs, files in os.walk(logdir, topdown=False):
        try:
            for f in files:
                full_name = os.path.join(current_dir, f)
                if os.path.getsize(full_name) == 0:
                    os.remove(full_name)
        except:
            pass



# 重写视频文件扫描，消除递归，取消全局变量，新增失败文件列表跳过处理
def movie_lists(root, conf):
    escape_folder = re.split("[,，]", conf.escape_folder())
    main_mode = conf.main_mode()
    debug = conf.debug()
    nfo_skip_days = conf.nfo_skip_days()
    total = []
    file_type = conf.media_type().upper().split(",")
    trailerRE = re.compile(r'-trailer\.', re.IGNORECASE)
    try:
        failed_list = open(os.path.join(conf.failed_folder(), 'failed_list.txt'),
            'r', encoding='utf-8').read().splitlines()
    except:
        failed_list = []
        pass
    for current_dir, subdirs, files in os.walk(root, topdown=False):
        if current_dir in escape_folder:
            continue
        for f in files:
            full_name = os.path.join(current_dir, f)
            if not os.path.splitext(full_name)[1].upper() in file_type:
                continue
            absf = os.path.abspath(full_name)
            if absf in failed_list:
                if debug:
                    print('[!]Skip failed file:', absf)
                continue
            if main_mode == 3 and nfo_skip_days > 0:
                nfo = Path(absf).with_suffix('.nfo')
                if file_modification_days(nfo) <= nfo_skip_days:
                    continue
            if (main_mode == 3 or not is_link(absf)) and not trailerRE.search(f):
                total.append(absf)
    if nfo_skip_days <= 0 or not conf.soft_link() or main_mode == 3:
        return total
    # 软连接方式，已经成功削刮的也需要从成功目录中检查.nfo更新天数，跳过N天内更新过的
    skip_numbers = set()
    success_folder = conf.success_folder()
    for current_dir, subdirs, files in os.walk(success_folder, topdown=False):
        for f in files:
            if not os.path.splitext(f)[1].upper() in file_type:
                continue
            nfo_file = os.path.join(current_dir, str(Path(f).with_suffix('.nfo')))
            if file_modification_days(nfo_file) > nfo_skip_days:
                continue
            number = get_number(False, os.path.basename(f))
            if number:
                skip_numbers.add(number.upper())
    for f in total:
        n_number = get_number(False, os.path.basename(f))
        if n_number and n_number.upper() in skip_numbers:
            total.pop(total.index(f))
    return total


def create_failed_folder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            sys.exit(0)


def rm_empty_folder(path):
    abspath = os.path.abspath(path)
    deleted = set()
    for current_dir, subdirs, files in os.walk(abspath, topdown=False):
        try:
            still_has_subdirs = any(
                 _ for subdir in subdirs if os.path.join(current_dir, subdir) not in deleted
            )
            if not any(files) and not still_has_subdirs and not os.path.samefile(path, current_dir):
                os.rmdir(current_dir)
                deleted.add(current_dir)
                print('[+]Deleting empty folder', current_dir)
        except:
            pass


def create_data_and_move(file_path: str, c: config.Config, debug):
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    file_name = os.path.basename(file_path)
    n_number = get_number(debug, file_name)
    file_path = os.path.abspath(file_path)

    if debug == True:
        print(f"[!]Making Data for [{file_path}], the number is [{n_number}]")
        if n_number:
            core_main(file_path, n_number, c)
        else:
            print("[-] number empty ERROR")
        print("[*]======================================================")
    else:
        try:
            print(f"[!]Making Data for [{file_path}], the number is [{n_number}]")
            if n_number:
                core_main(file_path, n_number, c)
            else:
                raise ValueError("number empty")
            print("[*]======================================================")
        except Exception as err:
            print(f"[-] [{file_path}] ERROR:")
            print('[-]', err)

            # 3.7.2 New: Move or not move to failed folder.
            if c.failed_move() == False:
                if c.soft_link():
                    print("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, os.path.join(conf.failed_folder(), file_name))
            elif c.failed_move() == True:
                if c.soft_link():
                    print("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, os.path.join(conf.failed_folder(), file_name))
                else:
                    try:
                        print("[-]Move [{}] to failed folder".format(file_path))
                        shutil.move(file_path, os.path.join(conf.failed_folder(), file_name))
                    except Exception as err:
                        print('[!]', err)


def create_data_and_move_with_custom_number(file_path: str, c: config.Config, custom_number):
    file_name = os.path.basename(file_path)
    try:
        print("[!]Making Data for [{}], the number is [{}]".format(file_path, custom_number))
        core_main(file_path, custom_number, c)
        print("[*]======================================================")
    except Exception as err:
        print("[-] [{}] ERROR:".format(file_path))
        print('[-]', err)

        if c.soft_link():
            print("[-]Link {} to failed folder".format(file_path))
            os.symlink(file_path, os.path.join(conf.failed_folder(), file_name))
        else:
            try:
                print("[-]Move [{}] to failed folder".format(file_path))
                shutil.move(file_path, os.path.join(conf.failed_folder(), file_name))
            except Exception as err:
                print('[!]', err)


if __name__ == '__main__':
    version = '4.7.2'
    urllib3.disable_warnings() #Ignore http proxy warning
    # Parse command line args
    single_file_path, folder_path, custom_number, auto_exit, logdir = argparse_function(version)

    dupe_stdout_to_logfile(logdir)

    print('[*]================== AV Data Capture ===================')
    print('[*]' + version.center(54))
    print('[*]======================================================')
    print('[*]严禁在墙内宣传本项目')

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

        movie_list = movie_lists(folder_path, conf)

        count = 0
        count_all = str(len(movie_list))
        print('[+]Find', count_all, 'movies')
        main_mode = conf.main_mode()
        stop_count = conf.stop_counter()
        if stop_count<1:
            stop_count = 999999
        else:
            count_all = str(min(len(movie_list), stop_count))
        if main_mode == 3:
            print(
f'[!]运行模式：**维护模式**，本程序将在处理{count_all}个视频文件后停止，如需后台执行自动退出请结合 -a 参数。')
        for movie_path in movie_list:  # 遍历电影列表 交给core处理
            count = count + 1
            percentage = str(count / int(count_all) * 100)[:4] + '%'
            print('[!] - ' + percentage + ' [' + str(count) + '/' + count_all + '] -')
            create_data_and_move(movie_path, conf, conf.debug())
            if count >= stop_count:
                print("[!]Stop counter triggered!")
                break

    if conf.del_empty_folder():
        rm_empty_folder(conf.success_folder())
        rm_empty_folder(conf.failed_folder())
        if len(folder_path):
            rm_empty_folder(folder_path)

    end_time = time.time()
    total_time = end_time - start_time
    print("[+]Used " + str(round(total_time,2)) + "s")

    print("[+]All finished!!!")
    if not (conf.auto_exit() or auto_exit):
        input("Press enter key exit, you can check the error message before you exit...")

    close_logfile(logdir)

    sys.exit(0)
