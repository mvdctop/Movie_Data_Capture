import argparse
import json
import os
import re
import sys
import shutil
import typing
import urllib3

import config
from datetime import datetime, timedelta
import time
from pathlib import Path
from ADC_function import  file_modification_days, get_html, is_link
from number_parser import get_number
from core import core_main, moveFailedFolder


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
    parser.add_argument("-q","--regex-query",dest='regexstr',default='',nargs='?',help="python re module regex filepath filtering.")
    parser.add_argument("-v", "--version", action="version", version=ver)
    args = parser.parse_args()

    return args.file, args.path, args.number, args.autoexit, args.logdir, args.regexstr


class OutLogger(object):
    def __init__(self, logfile) -> None:
        self.term = sys.stdout
        self.log = open(logfile,"w",encoding='utf-8',buffering=1)
        self.filepath = logfile
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
        self.log = open(logfile,"w",encoding='utf-8',buffering=1)
        self.filepath = logfile
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
    log_dir = Path(logdir)
    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True,exist_ok=True)
        except:
            pass
    if not log_dir.is_dir():
        return  # Tips for disabling logs by change directory to a same name empty regular file
    abslog_dir = log_dir.resolve()
    log_tmstr = datetime.now().strftime("%Y%m%dT%H%M%S")
    logfile = abslog_dir / f'avdc_{log_tmstr}.txt'
    errlog = abslog_dir / f'avdc_{log_tmstr}_err.txt'

    sys.stdout = OutLogger(logfile)
    sys.stderr = ErrLogger(errlog)


def close_logfile(logdir: str):
    if not isinstance(logdir, str) or len(logdir) == 0 or not os.path.isdir(logdir):
        return
    #日志关闭前保存日志路径
    filepath = None
    try:
        filepath = sys.stdout.filepath
    except:
        pass
    sys.stdout.close()
    sys.stderr.close()
    log_dir = Path(logdir).resolve()
    if isinstance(filepath, Path):
        print(f"Log file '{filepath}' saved.")
        assert(filepath.parent.samefile(log_dir))
    # 清理空文件
    for f in log_dir.glob(r'*_err.txt'):
        if f.stat().st_size == 0:
            try:
                f.unlink(missing_ok=True)
            except:
                pass
    # 合并日志 只检测日志目录内的文本日志，忽略子目录。三个月前的日志，按月合并为一个月志，
    # 去年及以前的月志，今年4月以后将之按年合并为年志
    # 测试步骤：
    """
    LOGDIR=/tmp/avlog
    mkdir -p $LOGDIR
    for f in {2016..2020}{01..12}{01..28};do;echo $f>$LOGDIR/avdc_${f}T235959.txt;done
    for f in {01..09}{01..28};do;echo 2021$f>$LOGDIR/avdc_2021${f}T235959.txt;done
    echo "$(ls -1 $LOGDIR|wc -l) files in $LOGDIR"
    # 1932 files in /tmp/avlog
    avdc -zgic1 -d0 -m3 -o $LOGDIR
    # python3 ./AV_Data_Capture.py -zgic1 -o $LOGDIR
    ls $LOGDIR
    # rm -rf $LOGDIR
    """
    # 第一步，合并到月
    for i in range(1):  # 利用1次循环的break跳到第二步，避免大块if缩进或者使用goto语法
        txts = [f for f in log_dir.glob(r'*.txt') if re.match(r'avdc_\d{8}T\d{6}', f.stem, re.A)]
        if not txts or not len(txts):
            break
        txts.sort()
        today = datetime.today()
        tmstr_3_month_ago = (today.replace(day=1) - timedelta(days=3*30)).strftime("%Y%m32T")
        deadline_month = f'avdc_{tmstr_3_month_ago}'
        month_merge = [f for f in txts if f.stem < deadline_month]
        if not month_merge or not len(month_merge):
            break
        tomonth = len('01T235959.txt')  # cut length avdc_202012|01T235959.txt
        for f in month_merge:
            try:
                month_file_name = str(f)[:-tomonth] + '.txt' # avdc_202012.txt
                with open(month_file_name, 'a', encoding='utf-8') as m:
                    m.write(f.read_text(encoding='utf-8'))
                f.unlink(missing_ok=True)
            except:
                pass
    # 第二步，月合并到年
    if today.month < 4:
        return
    mons = [f for f in log_dir.glob(r'*.txt') if re.match(r'avdc_\d{6}', f.stem, re.A)]
    if not mons or not len(mons):
        return
    mons.sort()
    deadline_year = f'avdc_{today.year-1}13'
    year_merge = [f for f in mons if f.stem < deadline_year]
    if not year_merge or not len(year_merge):
        return
    toyear = len('12.txt')   # cut length avdc_2020|12.txt
    for f in year_merge:
        try:
            year_file_name = str(f)[:-toyear] + '.txt' # avdc_2020.txt
            with open(year_file_name, 'a', encoding='utf-8') as y:
                y.write(f.read_text(encoding='utf-8'))
            f.unlink(missing_ok=True)
        except:
            pass
    # 第三步，压缩年志 如果有压缩需求，请自行手工压缩，或者使用外部脚本来定时完成。推荐nongnu的lzip，对于
    # 这种粒度的文本日志，压缩比是目前最好的。lzip -9的运行参数下，日志压缩比要高于xz -9，而且内存占用更少，
    # 多核利用率更高(plzip多线程版本)，解压速度更快。压缩后的大小差不多是未压缩时的2.4%到3.7%左右，
    # 100MB的日志文件能缩小到3.7MB。


# 重写视频文件扫描，消除递归，取消全局变量，新增失败文件列表跳过处理
def movie_lists(root, conf, regexstr):
    escape_folder = re.split("[,，]", conf.escape_folder())
    main_mode = conf.main_mode()
    debug = conf.debug()
    nfo_skip_days = conf.nfo_skip_days()
    soft_link = conf.soft_link()
    total = []
    file_type = conf.media_type().upper().split(",")
    trailerRE = re.compile(r'-trailer\.', re.IGNORECASE)
    cliRE = None
    if isinstance(regexstr, str) and len(regexstr):
        try:
            cliRE = re.compile(regexstr, re.IGNORECASE)
        except:
            pass
    failed_set = set()
    if main_mode == 3 or soft_link:
        try:
            with open(os.path.join(conf.failed_folder(), 'failed_list.txt'), 'r', encoding='utf-8')  as flt:
                flist = flt.read().splitlines()
                failed_set = set(flist)
                flt.close()
            if len(flist) != len(failed_set):
                with open(os.path.join(conf.failed_folder(), 'failed_list.txt'), 'w', encoding='utf-8')  as flt:
                    flt.writelines([line + '\n' for line in failed_set])
                    flt.close()
        except:
            pass
    for current_dir, subdirs, files in os.walk(root, topdown=False):
        if len(set(current_dir.replace("\\","/").split("/")) & set(escape_folder)) > 0:
            continue
        for f in files:
            full_name = os.path.join(current_dir, f)
            if not os.path.splitext(full_name)[1].upper() in file_type:
                continue
            absf = os.path.abspath(full_name)
            if absf in failed_set:
                if debug:
                    print('[!]Skip failed file:', absf)
                continue
            if cliRE and not cliRE.search(absf):
                continue
            if main_mode == 3 and nfo_skip_days > 0:
                nfo = Path(absf).with_suffix('.nfo')
                if file_modification_days(nfo) <= nfo_skip_days:
                    continue
            if (main_mode == 3 or not is_link(absf)) and not trailerRE.search(f):
                total.append(absf)
    if nfo_skip_days <= 0 or not soft_link or main_mode == 3:
        return total
    # 软连接方式，已经成功削刮的也需要从成功目录中检查.nfo更新天数，跳过N天内更新过的
    skip_numbers = set()
    success_folder = conf.success_folder()
    for current_dir, subdirs, files in os.walk(success_folder, topdown=False):
        for f in files:
            f_obj = Path(f)
            if f_obj.suffix.lower() != '.nfo':
                continue
            if file_modification_days(Path(current_dir) / f_obj) > nfo_skip_days:
                continue
            number = get_number(False, f_obj.stem)
            if number:
                skip_numbers.add(number.upper())
    rm_list = []
    for f in total:
        n_number = get_number(False, os.path.basename(f))
        if n_number and n_number.upper() in skip_numbers:
            rm_list.append(f)
    for f in rm_list:
        total.remove(f)
    return total


def create_failed_folder(failed_folder):
    if not os.path.exists(failed_folder):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder)
        except:
            print(f"[-]Fatal error! Can not make folder '{failed_folder}'")
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
        print(f"[!] [{n_number}] As Number making data for '{file_path}'")
        if n_number:
            core_main(file_path, n_number, c)
        else:
            print("[-] number empty ERROR")
        print("[*]======================================================")
    else:
        try:
            print(f"[!] [{n_number}] As Number making data for '{file_path}'")
            if n_number:
                core_main(file_path, n_number, c)
            else:
                raise ValueError("number empty")
            print("[*]======================================================")
        except Exception as err:
            print(f"[-] [{file_path}] ERROR:")
            print('[-]', err)

            try:
                moveFailedFolder(file_path, conf)
            except Exception as err:
                print('[!]', err)


def create_data_and_move_with_custom_number(file_path: str, c: config.Config, custom_number):
    file_name = os.path.basename(file_path)
    try:
        print("[!] [{1}] As Number making data for '{0}'".format(file_path, custom_number))
        if custom_number:
            core_main(file_path, custom_number, c)
        else:
            print("[-] number empty ERROR")
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
    version = '5.0.1'
    urllib3.disable_warnings() #Ignore http proxy warning
    # Parse command line args
    single_file_path, folder_path, custom_number, auto_exit, logdir, regexstr = argparse_function(version)

    dupe_stdout_to_logfile(logdir)

    print('[*]================== AV Data Capture ===================')
    print('[*]' + version.center(54))
    print('[*]' + "PRC国庆限定版".center(50))
    print('[*]======================================================')
    print('[*]严禁在墙内宣传本项目')

    # Read config.ini
    conf = config.Config("config.ini")


    if conf.update_check():
        check_update(version)

    print(f"[+]Load Config file '{conf.ini_path}'.")
    if conf.debug():
        print('[+]Enable debug')
    if conf.soft_link():
        print('[!]Enable soft link')
    if len(sys.argv)>1:
        print('[!]CmdLine:'," ".join(sys.argv[1:]))

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

        movie_list = movie_lists(folder_path, conf, regexstr)

        count = 0
        count_all = str(len(movie_list))
        print('[+]Find', count_all, 'movies. Start at', time.strftime("%Y-%m-%d %H:%M:%S"))
        main_mode = conf.main_mode()
        stop_count = conf.stop_counter()
        if stop_count<1:
            stop_count = 999999
        else:
            count_all = str(min(len(movie_list), stop_count))
        if main_mode == 3:
            print(f'[!]运行模式：**维护模式**，本程序将在处理{count_all}个视频文件后停止，如需后台执行自动退出请结合 -a 参数。')
        for movie_path in movie_list:  # 遍历电影列表 交给core处理
            count = count + 1
            percentage = str(count / int(count_all) * 100)[:4] + '%'
            print('[!] {:>30}{:>21}'.format('- ' + percentage + ' [' + str(count) + '/' + count_all + '] -', time.strftime("%H:%M:%S")))
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
    total_time = str(timedelta(seconds=end_time - start_time))
    print("[+]Running time", total_time[:len(total_time) if total_time.rfind('.') < 0 else -3],
        " End at", time.strftime("%Y-%m-%d %H:%M:%S"))

    print("[+]All finished!!!")

    close_logfile(logdir)

    if not (conf.auto_exit() or auto_exit):
        input("Press enter key exit, you can check the error message before you exit...")

    sys.exit(0)
