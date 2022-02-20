import argparse
import json
import os
import re
import sys
import shutil
import typing
import urllib3
import signal
import platform
from opencc import OpenCC

import ADC_function
import config
from datetime import datetime, timedelta
import time
from pathlib import Path
from ADC_function import  file_modification_days, get_html, parallel_download_files
from number_parser import get_number
from core import core_main, moveFailedFolder


def check_update(local_version):
    htmlcode = ""
    try:
        htmlcode = get_html("https://api.github.com/repos/yoshiko2/Movie_Data_Capture/releases/latest")
    except:
        print("===== Failed to connect to github =====")
        print("========== AUTO EXIT IN 60s ===========")
        time.sleep(60)
        os._exit(-1)
    data = json.loads(htmlcode)
    remote = int(data["tag_name"].replace(".",""))
    local_version = int(local_version.replace(".", ""))
    if local_version < remote:
        print("[*]" + ("* New update " + str(data["tag_name"]) + " *").center(54))
        print("[*]" + "↓ Download ↓".center(54))
        print("[*]https://github.com/yoshiko2/Movie_Data_Capture/releases")
        print("[*]======================================================")


def argparse_function(ver: str) -> typing.Tuple[str, str, str, str, bool]:
    conf = config.getInstance()
    parser = argparse.ArgumentParser(epilog=f"Load Config file '{conf.ini_path}'.")
    parser.add_argument("file", default='', nargs='?', help="Single Movie file path.")
    parser.add_argument("-p","--path",default='',nargs='?',help="Analysis folder path.")
    parser.add_argument("-m","--main-mode",default='',nargs='?',help="Main mode. 1:Scraping 2:Organizing 3:Scraping in analysis folder")
    parser.add_argument("-n", "--number", default='', nargs='?', help="Custom file number of single movie file.")
    # parser.add_argument("-C", "--config", default='config.ini', nargs='?', help="The config file Path.")
    default_logdir = str(Path.home() / '.mlogs')
    parser.add_argument("-o","--log-dir",dest='logdir',default=default_logdir,nargs='?',
        help=f"""Duplicate stdout and stderr to logfiles in logging folder, default on.
        default folder for current user: '{default_logdir}'. Change default folder to an empty file,
        or use --log-dir= to turn log off.""")
    parser.add_argument("-q","--regex-query",dest='regexstr',default='',nargs='?',help="python re module regex filepath filtering.")
    parser.add_argument("-d","--nfo-skip-days",dest='days',default='',nargs='?', help="Override nfo_skip_days value in config.")
    parser.add_argument("-c","--stop-counter",dest='cnt',default='',nargs='?', help="Override stop_counter value in config.")
    parser.add_argument("-i", "--ignore-failed-list", action="store_true", help="Ignore failed list '{}'".format(
                         os.path.join(os.path.abspath(conf.failed_folder()), 'failed_list.txt')))
    parser.add_argument("-a", "--auto-exit", action="store_true",
                        help="Auto exit after program complete")
    parser.add_argument("-g","--debug", action="store_true",
                        help="Turn on debug mode to generate diagnostic log for issue report.")
    parser.add_argument("-z","--zero-operation",dest='zero_op', action="store_true",
                        help="""Only show job list of files and numbers, and **NO** actual operation
is performed. It may help you correct wrong numbers before real job.""")
    parser.add_argument("-v", "--version", action="version", version=ver)

    args = parser.parse_args()
    def get_natural_number_or_none(value):
        return int(value) if isinstance(value, str) and value.isnumeric() and int(value)>=0 else None
    def get_str_or_none(value):
        return value if isinstance(value, str) and len(value) else None
    def get_bool_or_none(value):
        return True if isinstance(value, bool) and value else None
    config.G_conf_override["common:main_mode"] = get_natural_number_or_none(args.main_mode)
    config.G_conf_override["common:source_folder"] = get_str_or_none(args.path)
    config.G_conf_override["common:auto_exit"] = get_bool_or_none(args.auto_exit)
    config.G_conf_override["common:nfo_skip_days"] = get_natural_number_or_none(args.days)
    config.G_conf_override["common:stop_counter"] = get_natural_number_or_none(args.cnt)
    config.G_conf_override["common:ignore_failed_list"] = get_bool_or_none(args.ignore_failed_list)
    config.G_conf_override["debug_mode:switch"] = get_bool_or_none(args.debug)

    return args.file, args.number, args.logdir, args.regexstr, args.zero_op

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
        try:
            self.term.flush()
            self.log.flush()
            os.fsync(self.log.fileno())
            return True
        except Exception as ex:
            print("flush error,please handle me in future")
            return False
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
    logfile = abslog_dir / f'mdc_{log_tmstr}.txt'
    errlog = abslog_dir / f'mdc_{log_tmstr}_err.txt'

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
    # 合并日志 只检测日志目录内的文本日志，忽略子目录。三天前的日志，按日合并为单个日志，三个月前的日志，
    # 按月合并为单个月志，去年及以前的月志，今年4月以后将之按年合并为年志
    # 测试步骤：
    """
    LOGDIR=/tmp/mlog
    mkdir -p $LOGDIR
    for f in {2016..2020}{01..12}{01..28};do;echo $f>$LOGDIR/mdc_${f}T235959.txt;done
    for f in {01..09}{01..28};do;echo 2021$f>$LOGDIR/mdc_2021${f}T235959.txt;done
    for f in {00..23};do;echo 20211001T$f>$LOGDIR/mdc_20211001T${f}5959.txt;done
    echo "$(ls -1 $LOGDIR|wc -l) files in $LOGDIR"
    # 1932 files in /tmp/mlog
    mdc -zgic1 -d0 -m3 -o $LOGDIR
    # python3 ./Movie_Data_Capture.py -zgic1 -o $LOGDIR
    ls $LOGDIR
    # rm -rf $LOGDIR
    """
    today = datetime.today()
    # 第一步，合并到日。3天前的日志，文件名是同一天的合并为一份日志
    for i in range(1):
        txts = [f for f in log_dir.glob(r'*.txt') if re.match(r'^mdc_\d{8}T\d{6}$', f.stem, re.A)]
        if not txts or not len(txts):
            break
        e = [f for f in txts if '_err' in f.stem]
        txts.sort()
        tmstr_3_days_ago = (today.replace(hour=0) - timedelta(days=3)).strftime("%Y%m%dT99")
        deadline_day = f'mdc_{tmstr_3_days_ago}'
        day_merge = [f for f in txts if f.stem < deadline_day]
        if not day_merge or not len(day_merge):
            break
        cutday = len('T235959.txt')  # cut length mdc_20201201|T235959.txt
        for f in day_merge:
            try:
                day_file_name = str(f)[:-cutday] + '.txt' # mdc_20201201.txt
                with open(day_file_name, 'a', encoding='utf-8') as m:
                    m.write(f.read_text(encoding='utf-8'))
                f.unlink(missing_ok=True)
            except:
                pass
    # 第二步，合并到月
    for i in range(1):  # 利用1次循环的break跳到第二步，避免大块if缩进或者使用goto语法
        txts = [f for f in log_dir.glob(r'*.txt') if re.match(r'^mdc_\d{8}$', f.stem, re.A)]
        if not txts or not len(txts):
            break
        txts.sort()
        tmstr_3_month_ago = (today.replace(day=1) - timedelta(days=3*30)).strftime("%Y%m32")
        deadline_month = f'mdc_{tmstr_3_month_ago}'
        month_merge = [f for f in txts if f.stem < deadline_month]
        if not month_merge or not len(month_merge):
            break
        tomonth = len('01.txt')  # cut length mdc_202012|01.txt
        for f in month_merge:
            try:
                month_file_name = str(f)[:-tomonth] + '.txt' # mdc_202012.txt
                with open(month_file_name, 'a', encoding='utf-8') as m:
                    m.write(f.read_text(encoding='utf-8'))
                f.unlink(missing_ok=True)
            except:
                pass
    # 第三步，月合并到年
    if today.month < 4:
        return
    mons = [f for f in log_dir.glob(r'*.txt') if re.match(r'^mdc_\d{6}$', f.stem, re.A)]
    if not mons or not len(mons):
        return
    mons.sort()
    deadline_year = f'mdc_{today.year-1}13'
    year_merge = [f for f in mons if f.stem < deadline_year]
    if not year_merge or not len(year_merge):
        return
    toyear = len('12.txt')   # cut length mdc_2020|12.txt
    for f in year_merge:
        try:
            year_file_name = str(f)[:-toyear] + '.txt' # mdc_2020.txt
            with open(year_file_name, 'a', encoding='utf-8') as y:
                y.write(f.read_text(encoding='utf-8'))
            f.unlink(missing_ok=True)
        except:
            pass
    # 第四步，压缩年志 如果有压缩需求，请自行手工压缩，或者使用外部脚本来定时完成。推荐nongnu的lzip，对于
    # 这种粒度的文本日志，压缩比是目前最好的。lzip -9的运行参数下，日志压缩比要高于xz -9，而且内存占用更少，
    # 多核利用率更高(plzip多线程版本)，解压速度更快。压缩后的大小差不多是未压缩时的2.4%到3.7%左右，
    # 100MB的日志文件能缩小到3.7MB。


def signal_handler(*args):
    print('[!]Ctrl+C detected, Exit.')
    sys.exit(9)

def sigdebug_handler(*args):
    config.G_conf_override["debug_mode:switch"] = not config.G_conf_override["debug_mode:switch"]
    print('[!]Debug {}'.format('On' if config.getInstance().debug() else 'oFF'))


# 新增失败文件列表跳过处理，及.nfo修改天数跳过处理，提示跳过视频总数，调试模式(-g)下详细被跳过文件，跳过小广告
def movie_lists(source_folder, regexstr):
    conf = config.getInstance()
    main_mode = conf.main_mode()
    debug = conf.debug()
    nfo_skip_days = conf.nfo_skip_days()
    soft_link = conf.soft_link()
    file_type = conf.media_type().lower().split(",")
    trailerRE = re.compile(r'-trailer\.', re.IGNORECASE)
    cliRE = None
    if isinstance(regexstr, str) and len(regexstr):
        try:
            cliRE = re.compile(regexstr, re.IGNORECASE)
        except:
            pass
    failed_list_txt_path = Path(conf.failed_folder()).resolve() / 'failed_list.txt'
    failed_set = set()
    if (main_mode == 3 or soft_link) and not conf.ignore_failed_list():
        try:
            flist = failed_list_txt_path.read_text(encoding='utf-8').splitlines()
            failed_set = set(flist)
            if len(flist) != len(failed_set): # 检查去重并写回，但是不改变failed_list.txt内条目的先后次序，重复的只保留最后的
                fset = failed_set.copy()
                for i in range(len(flist)-1, -1, -1):
                    fset.remove(flist[i]) if flist[i] in fset else flist.pop(i)
                failed_list_txt_path.write_text('\n'.join(flist) + '\n', encoding='utf-8')
                assert len(fset) == 0 and len(flist) == len(failed_set)
        except:
            pass
    if not Path(source_folder).is_dir():
        print('[-]Source folder not found!')
        return []
    total = []
    source = Path(source_folder).resolve()
    skip_failed_cnt, skip_nfo_days_cnt = 0, 0
    escape_folder_set = set(re.split("[,，]", conf.escape_folder()))
    for full_name in source.glob(r'**/*'):
        if main_mode != 3 and set(full_name.parent.parts) & escape_folder_set:
            continue
        if not full_name.suffix.lower() in file_type:
            continue
        absf = str(full_name)
        if absf in failed_set:
            skip_failed_cnt += 1
            if debug:
                print('[!]Skip failed movie:', absf)
            continue
        is_sym = full_name.is_symlink()
        if main_mode != 3 and (is_sym or full_name.stat().st_nlink > 1):  # 短路布尔 符号链接不取stat()，因为符号链接可能指向不存在目标
            continue # file is symlink or hardlink(Linux/NTFS/Darwin)
        # 调试用0字节样本允许通过，去除小于120MB的广告'苍老师强力推荐.mp4'(102.2MB)'黑道总裁.mp4'(98.4MB)'有趣的妹子激情表演.MP4'(95MB)'有趣的臺灣妹妹直播.mp4'(15.1MB)
        movie_size = 0 if is_sym else full_name.stat().st_size  # 同上 符号链接不取stat()及st_size，直接赋0跳过小视频检测
        if movie_size > 0 and movie_size < 125829120:  # 1024*1024*120=125829120
            continue
        if cliRE and not cliRE.search(absf) or trailerRE.search(full_name.name):
            continue
        if main_mode == 3 and nfo_skip_days > 0 and file_modification_days(full_name.with_suffix('.nfo')) <= nfo_skip_days:
            skip_nfo_days_cnt += 1
            if debug:
                print(f"[!]Skip movie by it's .nfo which modified within {nfo_skip_days} days: '{absf}'")
            continue
        total.append(absf)

    if skip_failed_cnt:
        print(f"[!]Skip {skip_failed_cnt} movies in failed list '{failed_list_txt_path}'.")
    if skip_nfo_days_cnt:
        print(f"[!]Skip {skip_nfo_days_cnt} movies in source folder '{source}' who's .nfo modified within {nfo_skip_days} days.")
    if nfo_skip_days <= 0 or not soft_link or main_mode == 3:
        return total
    # 软连接方式，已经成功削刮的也需要从成功目录中检查.nfo更新天数，跳过N天内更新过的
    skip_numbers = set()
    success_folder = Path(conf.success_folder()).resolve()
    for f in success_folder.glob(r'**/*'):
        if not re.match(r'\.nfo', f.suffix, re.IGNORECASE):
            continue
        if file_modification_days(f) > nfo_skip_days:
            continue
        number = get_number(False, f.stem)
        if not number:
            continue
        skip_numbers.add(number.lower())

    rm_list = []
    for f in total:
        n_number = get_number(False, os.path.basename(f))
        if n_number and n_number.lower() in skip_numbers:
            rm_list.append(f)
    for f in rm_list:
        total.remove(f)
        if debug:
            print(f"[!]Skip file successfully processed within {nfo_skip_days} days: '{f}'")
    if len(rm_list):
        print(f"[!]Skip {len(rm_list)} movies in success folder '{success_folder}' who's .nfo modified within {nfo_skip_days} days.")

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


def create_data_and_move(file_path: str, zero_op, oCC):
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    debug = config.getInstance().debug()
    n_number = get_number(debug, os.path.basename(file_path))
    file_path = os.path.abspath(file_path)

    if debug == True:
        print(f"[!] [{n_number}] As Number making data for '{file_path}'")
        if zero_op:
            return
        if n_number:
            core_main(file_path, n_number, oCC)
        else:
            print("[-] number empty ERROR")
            moveFailedFolder(file_path)
        print("[*]======================================================")
    else:
        try:
            print(f"[!] [{n_number}] As Number making data for '{file_path}'")
            if zero_op:
                return
            if n_number:
                core_main(file_path, n_number, oCC)
            else:
                raise ValueError("number empty")
            print("[*]======================================================")
        except Exception as err:
            print(f"[-] [{file_path}] ERROR:")
            print('[-]', err)

            try:
                moveFailedFolder(file_path)
            except Exception as err:
                print('[!]', err)


def create_data_and_move_with_custom_number(file_path: str, custom_number, oCC):
    conf = config.getInstance()
    file_name = os.path.basename(file_path)
    try:
        print("[!] [{1}] As Number making data for '{0}'".format(file_path, custom_number))
        if custom_number:
            core_main(file_path, custom_number, oCC)
        else:
            print("[-] number empty ERROR")
        print("[*]======================================================")
    except Exception as err:
        print("[-] [{}] ERROR:".format(file_path))
        print('[-]', err)

        if conf.soft_link():
            print("[-]Link {} to failed folder".format(file_path))
            os.symlink(file_path, os.path.join(conf.failed_folder(), file_name))
        else:
            try:
                print("[-]Move [{}] to failed folder".format(file_path))
                shutil.move(file_path, os.path.join(conf.failed_folder(), file_name))
            except Exception as err:
                print('[!]', err)


def main():
    version = '6.0.2'
    urllib3.disable_warnings() #Ignore http proxy warning

    # Read config.ini first, in argparse_function() need conf.failed_folder()
    conf = config.Config("config.ini")

    # Parse command line args
    single_file_path, custom_number, logdir, regexstr, zero_op = argparse_function(version)



    main_mode = conf.main_mode()
    folder_path = ""
    if not main_mode in (1, 2, 3):
        print(f"[-]Main mode must be 1 or 2 or 3! You can run '{os.path.basename(sys.argv[0])} --help' for more help.")
        sys.exit(4)

    signal.signal(signal.SIGINT, signal_handler)
    if sys.platform == 'win32':
        signal.signal(signal.SIGBREAK, sigdebug_handler)
    else:
        signal.signal(signal.SIGWINCH, sigdebug_handler)
    dupe_stdout_to_logfile(logdir)

    platform_total = str(' - ' + platform.platform() + ' \n[*] - ' + platform.machine() + ' - Python-' + platform.python_version())

    print('[*]================= Movie Data Capture =================')
    print('[*]' + version.center(54))
    print('[*]======================================================')
    print('[*]' + platform_total)
    print('[*]======================================================')
    print('[*] - 严禁在墙内宣传本项目 - ')
    print('[*]======================================================')

    start_time = time.time()
    print('[+]Start at', time.strftime("%Y-%m-%d %H:%M:%S"))

    print(f"[+]Load Config file '{conf.ini_path}'.")
    if conf.debug():
        print('[+]Enable debug')
    if conf.soft_link():
        print('[!]Enable soft link')
    if len(sys.argv)>1:
        print('[!]CmdLine:'," ".join(sys.argv[1:]))
    print('[+]Main Working mode ## {}: {} ## {}{}{}'
        .format(*(main_mode, ['Scraping', 'Organizing', 'Scraping in analysis folder'][main_mode-1],
        "" if not conf.multi_threading() else ", multi_threading on",
        "" if conf.nfo_skip_days() == 0 else f", nfo_skip_days={conf.nfo_skip_days()}",
        "" if conf.stop_counter() == 0 else f", stop_counter={conf.stop_counter()}"
        ) if not single_file_path else ('-','Single File', '','',''))
    )

    if conf.update_check():
        check_update(version)

    create_failed_folder(conf.failed_folder())

    # Download Mapping Table, parallel version
    def fmd(f):
        return ('https://raw.githubusercontent.com/yoshiko2/Movie_Data_Capture/master/MappingTable/' + f,
                Path.home() / '.local' / 'share' / 'mdc' / f)
    map_tab = (fmd('mapping_actor.xml'), fmd('mapping_info.xml'), fmd('c_number.json'))
    for k,v in map_tab:
        if v.exists():
            if file_modification_days(str(v)) >= conf.mapping_table_validity():
                print("[+]Mapping Table Out of date! Remove", str(v))
                os.remove(str(v))
    res = parallel_download_files(((k, v) for k, v in map_tab if not v.exists()))
    for i, fp in enumerate(res, start=1):
        if fp and len(fp):
            print(f"[+] [{i}/{len(res)}] Mapping Table Downloaded to {fp}")
        else:
            print(f"[-] [{i}/{len(res)}] Mapping Table Download failed")
            print("[-] --- AUTO EXIT AFTER 30s !!! --- ")
            time.sleep(30)
            os._exit(-1)

    # create OpenCC converter
    ccm = conf.cc_convert_mode()
    try:
        oCC = None if ccm == 0 else OpenCC('t2s.json' if ccm == 1 else 's2t.json')
    except:
        # some OS no OpennCC cpython, try opencc-python-reimplemented.
        # pip uninstall opencc && pip install opencc-python-reimplemented
        oCC = None if ccm == 0 else OpenCC('t2s' if ccm == 1 else 's2t')

    if not single_file_path == '': #Single File
        print('[+]==================== Single File =====================')
        if custom_number == '':
            create_data_and_move_with_custom_number(single_file_path, get_number(conf.debug(), os.path.basename(single_file_path)), oCC)
        else:
            create_data_and_move_with_custom_number(single_file_path, custom_number, oCC)
    else:
        folder_path = conf.source_folder()
        if not isinstance(folder_path, str) or folder_path == '':
            folder_path = os.path.abspath(".")

        movie_list = movie_lists(folder_path, regexstr)

        count = 0
        count_all = str(len(movie_list))
        print('[+]Find', count_all, 'movies.')
        print('[*]======================================================')
        stop_count = conf.stop_counter()
        if stop_count<1:
            stop_count = 999999
        else:
            count_all = str(min(len(movie_list), stop_count))

        for movie_path in movie_list:  # 遍历电影列表 交给core处理
            count = count + 1
            percentage = str(count / int(count_all) * 100)[:4] + '%'
            print('[!] {:>30}{:>21}'.format('- ' + percentage + ' [' + str(count) + '/' + count_all + '] -', time.strftime("%H:%M:%S")))
            create_data_and_move(movie_path, zero_op, oCC)
            if count >= stop_count:
                print("[!]Stop counter triggered!")
                break

    if conf.del_empty_folder() and not zero_op:
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

    if not conf.auto_exit():
        input("Press enter key exit, you can check the error message before you exit...")

    sys.exit(0)

import multiprocessing
if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
