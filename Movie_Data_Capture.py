import argparse
import json
import os
import random
import re
import sys
import time
import shutil
import typing
import urllib3
import signal
import platform
import config

from datetime import datetime, timedelta
from lxml import etree
from pathlib import Path
from opencc import OpenCC

from scraper import get_data_from_json
from ADC_function import file_modification_days, get_html, parallel_download_files
from number_parser import get_number
from core import core_main, core_main_no_net_op, moveFailedFolder, debug_print


def check_update(local_version):
    htmlcode = get_html("https://api.github.com/repos/yoshiko2/Movie_Data_Capture/releases/latest")
    data = json.loads(htmlcode)
    remote = int(data["tag_name"].replace(".", ""))
    local_version = int(local_version.replace(".", ""))
    if local_version < remote:
        print("[*]" + ("* New update " + str(data["tag_name"]) + " *").center(54))
        print("[*]" + "↓ Download ↓".center(54))
        print("[*]https://github.com/yoshiko2/Movie_Data_Capture/releases")
        print("[*]======================================================")


def argparse_function(ver: str) -> typing.Tuple[str, str, str, str, bool, bool, str, str]:
    conf = config.getInstance()
    parser = argparse.ArgumentParser(epilog=f"Load Config file '{conf.ini_path}'.")
    parser.add_argument("file", default='', nargs='?', help="Single Movie file path.")
    parser.add_argument("-p", "--path", default='', nargs='?', help="Analysis folder path.")
    parser.add_argument("-m", "--main-mode", default='', nargs='?',
                        help="Main mode. 1:Scraping 2:Organizing 3:Scraping in analysis folder")
    parser.add_argument("-n", "--number", default='', nargs='?', help="Custom file number of single movie file.")
    # parser.add_argument("-C", "--config", default='config.ini', nargs='?', help="The config file Path.")
    parser.add_argument("-L", "--link-mode", default='', nargs='?',
                        help="Create movie file link. 0:moving movie file, do not create link 1:soft link 2:try hard link first")
    default_logdir = str(Path.home() / '.mlogs')
    parser.add_argument("-o", "--log-dir", dest='logdir', default=default_logdir, nargs='?',
                        help=f"""Duplicate stdout and stderr to logfiles in logging folder, default on.
        default folder for current user: '{default_logdir}'. Change default folder to an empty file,
        or use --log-dir= to turn log off.""")
    parser.add_argument("-q", "--regex-query", dest='regexstr', default='', nargs='?',
                        help="python re module regex filepath filtering.")
    parser.add_argument("-d", "--nfo-skip-days", dest='days', default='', nargs='?',
                        help="Override nfo_skip_days value in config.")
    parser.add_argument("-c", "--stop-counter", dest='cnt', default='', nargs='?',
                        help="Override stop_counter value in config.")
    parser.add_argument("-R", "--rerun-delay", dest='delaytm', default='', nargs='?',
                        help="Delay (eg. 1h10m30s or 60 (second)) time and rerun, until all movies proceed. Note: stop_counter value in config or -c must none zero.")
    parser.add_argument("-i", "--ignore-failed-list", action="store_true", help="Ignore failed list '{}'".format(
        os.path.join(os.path.abspath(conf.failed_folder()), 'failed_list.txt')))
    parser.add_argument("-a", "--auto-exit", action="store_true",
                        help="Auto exit after program complete")
    parser.add_argument("-g", "--debug", action="store_true",
                        help="Turn on debug mode to generate diagnostic log for issue report.")
    parser.add_argument("-N", "--no-network-operation", action="store_true",
                        help="No network query, do not get metadata, for cover cropping purposes, only takes effect when main mode is 3.")
    parser.add_argument("-w", "--website", dest='site', default='', nargs='?',
                        help="Override [priority]website= in config.")
    parser.add_argument("-D", "--download-images", dest='dnimg', action="store_true",
                        help="Override [common]download_only_missing_images=0 force invoke image downloading.")
    parser.add_argument("-C", "--config-override", dest='cfgcmd', action='append', nargs=1,
                        help="Common use config override. Grammar: section:key=value[;[section:]key=value] eg. 'de:s=1' or 'debug_mode:switch=1' override[debug_mode]switch=1 Note:this parameters can be used multiple times")
    parser.add_argument("-z", "--zero-operation", dest='zero_op', action="store_true",
                        help="""Only show job list of files and numbers, and **NO** actual operation
is performed. It may help you correct wrong numbers before real job.""")
    parser.add_argument("-v", "--version", action="version", version=ver)
    parser.add_argument("-s", "--search", default='', nargs='?', help="Search number")
    parser.add_argument("-ss", "--specified-source", default='', nargs='?', help="specified Source.")
    parser.add_argument("-su", "--specified-url", default='', nargs='?', help="specified Url.")

    args = parser.parse_args()

    def set_natural_number_or_none(sk, value):
        if isinstance(value, str) and value.isnumeric() and int(value) >= 0:
            conf.set_override(f'{sk}={value}')

    def set_str_or_none(sk, value):
        if isinstance(value, str) and len(value):
            conf.set_override(f'{sk}={value}')

    def set_bool_or_none(sk, value):
        if isinstance(value, bool) and value:
            conf.set_override(f'{sk}=1')

    set_natural_number_or_none("common:main_mode", args.main_mode)
    set_natural_number_or_none("common:link_mode", args.link_mode)
    set_str_or_none("common:source_folder", args.path)
    set_bool_or_none("common:auto_exit", args.auto_exit)
    set_natural_number_or_none("common:nfo_skip_days", args.days)
    set_natural_number_or_none("advenced_sleep:stop_counter", args.cnt)
    set_bool_or_none("common:ignore_failed_list", args.ignore_failed_list)
    set_str_or_none("advenced_sleep:rerun_delay", args.delaytm)
    set_str_or_none("priority:website", args.site)
    if isinstance(args.dnimg, bool) and args.dnimg:
        conf.set_override("common:download_only_missing_images=0")
    set_bool_or_none("debug_mode:switch", args.debug)
    if isinstance(args.cfgcmd, list):
        for cmd in args.cfgcmd:
            conf.set_override(cmd[0])

    no_net_op = False
    if conf.main_mode() == 3:
        no_net_op = args.no_network_operation
        if no_net_op:
            conf.set_override("advenced_sleep:stop_counter=0;advenced_sleep:rerun_delay=0s;face:aways_imagecut=1")

    return args.file, args.number, args.logdir, args.regexstr, args.zero_op, no_net_op, args.search, args.specified_source, args.specified_url


class OutLogger(object):
    def __init__(self, logfile) -> None:
        self.term = sys.stdout
        self.log = open(logfile, "w", encoding='utf-8', buffering=1)
        self.filepath = logfile

    def __del__(self):
        self.close()

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.close()

    def write(self, msg):
        self.term.write(msg)
        self.log.write(msg)

    def flush(self):
        if 'flush' in dir(self.term):
            self.term.flush()
        if 'flush' in dir(self.log):
            self.log.flush()
        if 'fileno' in dir(self.log):
            os.fsync(self.log.fileno())

    def close(self):
        if self.term is not None:
            sys.stdout = self.term
            self.term = None
        if self.log is not None:
            self.log.close()
            self.log = None


class ErrLogger(OutLogger):

    def __init__(self, logfile) -> None:
        self.term = sys.stderr
        self.log = open(logfile, "w", encoding='utf-8', buffering=1)
        self.filepath = logfile

    def close(self):
        if self.term is not None:
            sys.stderr = self.term
            self.term = None

        if self.log is not None:
            self.log.close()
            self.log = None


def dupe_stdout_to_logfile(logdir: str):
    if not isinstance(logdir, str) or len(logdir) == 0:
        return
    log_dir = Path(logdir)
    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
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
    # 日志关闭前保存日志路径
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
        assert (filepath.parent.samefile(log_dir))
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
                day_file_name = str(f)[:-cutday] + '.txt'  # mdc_20201201.txt
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
        tmstr_3_month_ago = (today.replace(day=1) - timedelta(days=3 * 30)).strftime("%Y%m32")
        deadline_month = f'mdc_{tmstr_3_month_ago}'
        month_merge = [f for f in txts if f.stem < deadline_month]
        if not month_merge or not len(month_merge):
            break
        tomonth = len('01.txt')  # cut length mdc_202012|01.txt
        for f in month_merge:
            try:
                month_file_name = str(f)[:-tomonth] + '.txt'  # mdc_202012.txt
                with open(month_file_name, 'a', encoding='utf-8') as m:
                    m.write(f.read_text(encoding='utf-8'))
                f.unlink(missing_ok=True)
            except:
                pass
    # 第三步，月合并到年
    for i in range(1):
        if today.month < 4:
            break
        mons = [f for f in log_dir.glob(r'*.txt') if re.match(r'^mdc_\d{6}$', f.stem, re.A)]
        if not mons or not len(mons):
            break
        mons.sort()
        deadline_year = f'mdc_{today.year - 1}13'
        year_merge = [f for f in mons if f.stem < deadline_year]
        if not year_merge or not len(year_merge):
            break
        toyear = len('12.txt')  # cut length mdc_2020|12.txt
        for f in year_merge:
            try:
                year_file_name = str(f)[:-toyear] + '.txt'  # mdc_2020.txt
                with open(year_file_name, 'a', encoding='utf-8') as y:
                    y.write(f.read_text(encoding='utf-8'))
                f.unlink(missing_ok=True)
            except:
                pass
    # 第四步，压缩年志 如果有压缩需求，请自行手工压缩，或者使用外部脚本来定时完成。推荐nongnu的lzip，对于
    # 这种粒度的文本日志，压缩比是目前最好的。lzip -9的运行参数下，日志压缩比要高于xz -9，而且内存占用更少，
    # 多核利用率更高(plzip多线程版本)，解压速度更快。压缩后的大小差不多是未压缩时的2.4%到3.7%左右，
    # 100MB的日志文件能缩小到3.7MB。
    return filepath


def signal_handler(*args):
    print('[!]Ctrl+C detected, Exit.')
    os._exit(9)


def sigdebug_handler(*args):
    conf = config.getInstance()
    conf.set_override(f"debug_mode:switch={int(not conf.debug())}")
    print(f"[!]Debug {('oFF', 'On')[int(conf.debug())]}")


# 新增失败文件列表跳过处理，及.nfo修改天数跳过处理，提示跳过视频总数，调试模式(-g)下详细被跳过文件，跳过小广告
def movie_lists(source_folder, regexstr: str) -> typing.List[str]:
    conf = config.getInstance()
    main_mode = conf.main_mode()
    debug = conf.debug()
    nfo_skip_days = conf.nfo_skip_days()
    link_mode = conf.link_mode()
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
    if (main_mode == 3 or link_mode) and not conf.ignore_failed_list():
        try:
            flist = failed_list_txt_path.read_text(encoding='utf-8').splitlines()
            failed_set = set(flist)
            if len(flist) != len(failed_set):  # 检查去重并写回，但是不改变failed_list.txt内条目的先后次序，重复的只保留最后的
                fset = failed_set.copy()
                for i in range(len(flist) - 1, -1, -1):
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
        if not full_name.is_file():
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
        if main_mode != 3 and (is_sym or (full_name.stat().st_nlink > 1 and not conf.scan_hardlink())):  # 短路布尔 符号链接不取stat()，因为符号链接可能指向不存在目标
            continue  # 模式不等于3下跳过软连接和未配置硬链接刮削
        # 调试用0字节样本允许通过，去除小于120MB的广告'苍老师强力推荐.mp4'(102.2MB)'黑道总裁.mp4'(98.4MB)'有趣的妹子激情表演.MP4'(95MB)'有趣的臺灣妹妹直播.mp4'(15.1MB)
        movie_size = 0 if is_sym else full_name.stat().st_size  # 同上 符号链接不取stat()及st_size，直接赋0跳过小视频检测
        # if 0 < movie_size < 125829120:  # 1024*1024*120=125829120
        #     continue
        if cliRE and not cliRE.search(absf) or trailerRE.search(full_name.name):
            continue
        if main_mode == 3:
            nfo = full_name.with_suffix('.nfo')
            if not nfo.is_file():
                if debug:
                    print(f"[!]Metadata {nfo.name} not found for '{absf}'")
            elif nfo_skip_days > 0 and file_modification_days(nfo) <= nfo_skip_days:
                skip_nfo_days_cnt += 1
                if debug:
                    print(f"[!]Skip movie by it's .nfo which modified within {nfo_skip_days} days: '{absf}'")
                continue
        total.append(absf)

    if skip_failed_cnt:
        print(f"[!]Skip {skip_failed_cnt} movies in failed list '{failed_list_txt_path}'.")
    if skip_nfo_days_cnt:
        print(
            f"[!]Skip {skip_nfo_days_cnt} movies in source folder '{source}' who's .nfo modified within {nfo_skip_days} days.")
    if nfo_skip_days <= 0 or not link_mode or main_mode == 3:
        return total
    # 软连接方式，已经成功削刮的也需要从成功目录中检查.nfo更新天数，跳过N天内更新过的
    skip_numbers = set()
    success_folder = Path(conf.success_folder()).resolve()
    for f in success_folder.glob(r'**/*'):
        if not re.match(r'\.nfo$', f.suffix, re.IGNORECASE):
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
        print(
            f"[!]Skip {len(rm_list)} movies in success folder '{success_folder}' who's .nfo modified within {nfo_skip_days} days.")

    return total


def create_failed_folder(failed_folder: str):
    """
    新建failed文件夹
    """
    if not os.path.exists(failed_folder):
        try:
            os.makedirs(failed_folder)
        except:
            print(f"[-]Fatal error! Can not make folder '{failed_folder}'")
            os._exit(0)


def rm_empty_folder(path):
    abspath = os.path.abspath(path)
    deleted = set()
    for current_dir, subdirs, files in os.walk(abspath, topdown=False):
        try:
            still_has_subdirs = any(_ for subdir in subdirs if os.path.join(current_dir, subdir) not in deleted)
            if not any(files) and not still_has_subdirs and not os.path.samefile(path, current_dir):
                os.rmdir(current_dir)
                deleted.add(current_dir)
                print('[+]Deleting empty folder', current_dir)
        except:
            pass


def create_data_and_move(movie_path: str, zero_op: bool, no_net_op: bool, oCC):
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    debug = config.getInstance().debug()
    n_number = get_number(debug, os.path.basename(movie_path))
    movie_path = os.path.abspath(movie_path)

    if debug is True:
        print(f"[!] [{n_number}] As Number Processing for '{movie_path}'")
        if zero_op:
            return
        if n_number:
            if no_net_op:
                core_main_no_net_op(movie_path, n_number)
            else:
                core_main(movie_path, n_number, oCC)
        else:
            print("[-] number empty ERROR")
            moveFailedFolder(movie_path)
        print("[*]======================================================")
    else:
        try:
            print(f"[!] [{n_number}] As Number Processing for '{movie_path}'")
            if zero_op:
                return
            if n_number:
                if no_net_op:
                    core_main_no_net_op(movie_path, n_number)
                else:
                    core_main(movie_path, n_number, oCC)
            else:
                raise ValueError("number empty")
            print("[*]======================================================")
        except Exception as err:
            print(f"[-] [{movie_path}] ERROR:")
            print('[-]', err)

            try:
                moveFailedFolder(movie_path)
            except Exception as err:
                print('[!]', err)


def create_data_and_move_with_custom_number(file_path: str, custom_number, oCC, specified_source, specified_url):
    conf = config.getInstance()
    file_name = os.path.basename(file_path)
    try:
        print("[!] [{1}] As Number Processing for '{0}'".format(file_path, custom_number))
        if custom_number:
            core_main(file_path, custom_number, oCC, specified_source, specified_url)
        else:
            print("[-] number empty ERROR")
        print("[*]======================================================")
    except Exception as err:
        print("[-] [{}] ERROR:".format(file_path))
        print('[-]', err)

        if conf.link_mode():
            print("[-]Link {} to failed folder".format(file_path))
            os.symlink(file_path, os.path.join(conf.failed_folder(), file_name))
        else:
            try:
                print("[-]Move [{}] to failed folder".format(file_path))
                shutil.move(file_path, os.path.join(conf.failed_folder(), file_name))
            except Exception as err:
                print('[!]', err)


def main(args: tuple) -> Path:
    (single_file_path, custom_number, logdir, regexstr, zero_op, no_net_op, search, specified_source,
     specified_url) = args
    conf = config.getInstance()
    main_mode = conf.main_mode()
    folder_path = ""
    if main_mode not in (1, 2, 3):
        print(f"[-]Main mode must be 1 or 2 or 3! You can run '{os.path.basename(sys.argv[0])} --help' for more help.")
        os._exit(4)

    signal.signal(signal.SIGINT, signal_handler)
    if sys.platform == 'win32':
        signal.signal(signal.SIGBREAK, sigdebug_handler)
    else:
        signal.signal(signal.SIGWINCH, sigdebug_handler)
    dupe_stdout_to_logfile(logdir)

    platform_total = str(
        ' - ' + platform.platform() + ' \n[*] - ' + platform.machine() + ' - Python-' + platform.python_version())

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
    if conf.link_mode() in (1, 2):
        print('[!]Enable {} link'.format(('soft', 'hard')[conf.link_mode() - 1]))
    if len(sys.argv) > 1:
        print('[!]CmdLine:', " ".join(sys.argv[1:]))
    print('[+]Main Working mode ## {}: {} ## {}{}{}'
          .format(*(main_mode, ['Scraping', 'Organizing', 'Scraping in analysis folder'][main_mode - 1],
                    "" if not conf.multi_threading() else ", multi_threading on",
                    "" if conf.nfo_skip_days() == 0 else f", nfo_skip_days={conf.nfo_skip_days()}",
                    "" if conf.stop_counter() == 0 else f", stop_counter={conf.stop_counter()}"
                    ) if not single_file_path else ('-', 'Single File', '', '', ''))
          )

    if conf.update_check():
        try:
            check_update(version)
            # Download Mapping Table, parallel version
            def fmd(f) -> typing.Tuple[str, Path]:
                return ('https://raw.githubusercontent.com/yoshiko2/Movie_Data_Capture/master/MappingTable/' + f,
                        Path.home() / '.local' / 'share' / 'mdc' / f)

            map_tab = (fmd('mapping_actor.xml'), fmd('mapping_info.xml'), fmd('c_number.json'))
            for k, v in map_tab:
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
        except:
            print("[!]" + " WARNING ".center(54, "="))
            print('[!]' + '-- GITHUB CONNECTION FAILED --'.center(54))
            print('[!]' + 'Failed to check for updates'.center(54))
            print('[!]' + '& update the mapping table'.center(54))
            print("[!]" + "".center(54, "="))
            try:
                etree.parse(str(Path.home() / '.local' / 'share' / 'mdc' / 'mapping_actor.xml'))
            except:
                print('[!]' + "Failed to load mapping table".center(54))
                print('[!]' + "".center(54, "="))

    create_failed_folder(conf.failed_folder())

    # create OpenCC converter
    ccm = conf.cc_convert_mode()
    try:
        oCC = None if ccm == 0 else OpenCC('t2s.json' if ccm == 1 else 's2t.json')
    except:
        # some OS no OpenCC cpython, try opencc-python-reimplemented.
        # pip uninstall opencc && pip install opencc-python-reimplemented
        oCC = None if ccm == 0 else OpenCC('t2s' if ccm == 1 else 's2t')

    if not search == '':
        search_list = search.split(",")
        for i in search_list:
            json_data = get_data_from_json(i, oCC, None, None)
            debug_print(json_data)
            time.sleep(int(config.getInstance().sleep()))
        os._exit(0)

    if not single_file_path == '':  # Single File
        print('[+]==================== Single File =====================')
        if custom_number == '':
            create_data_and_move_with_custom_number(single_file_path,
                                                    get_number(conf.debug(), os.path.basename(single_file_path)), oCC,
                                                    specified_source, specified_url)
        else:
            create_data_and_move_with_custom_number(single_file_path, custom_number, oCC,
                                                    specified_source, specified_url)
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
        if stop_count < 1:
            stop_count = 999999
        else:
            count_all = str(min(len(movie_list), stop_count))

        for movie_path in movie_list:  # 遍历电影列表 交给core处理
            count = count + 1
            percentage = str(count / int(count_all) * 100)[:4] + '%'
            print('[!] {:>30}{:>21}'.format('- ' + percentage + ' [' + str(count) + '/' + count_all + '] -',
                                            time.strftime("%H:%M:%S")))
            create_data_and_move(movie_path, zero_op, no_net_op, oCC)
            if count >= stop_count:
                print("[!]Stop counter triggered!")
                break
            sleep_seconds = random.randint(conf.sleep(), conf.sleep() + 2)
            time.sleep(sleep_seconds)

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

    return close_logfile(logdir)


def 分析日志文件(logfile):
    try:
        if not (isinstance(logfile, Path) and logfile.is_file()):
            raise FileNotFoundError('log file not found')
        logtxt = logfile.read_text(encoding='utf-8')
        扫描电影数 = int(re.findall(r'\[\+]Find (.*) movies\.', logtxt)[0])
        已处理 = int(re.findall(r'\[1/(.*?)] -', logtxt)[0])
        完成数 = logtxt.count(r'[+]Wrote!')
        return 扫描电影数, 已处理, 完成数
    except:
        return None, None, None


def period(delta, pattern):
    d = {'d': delta.days}
    d['h'], rem = divmod(delta.seconds, 3600)
    d['m'], d['s'] = divmod(rem, 60)
    return pattern.format(**d)


if __name__ == '__main__':
    version = '6.6.7'
    urllib3.disable_warnings()  # Ignore http proxy warning
    app_start = time.time()

    # Read config.ini first, in argparse_function() need conf.failed_folder()
    conf = config.getInstance()

    # Parse command line args
    args = tuple(argparse_function(version))

    再运行延迟 = conf.rerun_delay()
    if 再运行延迟 > 0 and conf.stop_counter() > 0:
        while True:
            try:
                logfile = main(args)
                (扫描电影数, 已处理, 完成数) = 分析结果元组 = tuple(分析日志文件(logfile))
                if all(isinstance(v, int) for v in 分析结果元组):
                    剩余个数 = 扫描电影数 - 已处理
                    总用时 = timedelta(seconds = time.time() - app_start)
                    print(f'All movies:{扫描电影数}  processed:{已处理}  successes:{完成数}  remain:{剩余个数}' +
                        '  Elapsed time {}'.format(
                        period(总用时, "{d} day {h}:{m:02}:{s:02}") if 总用时.days == 1
                            else period(总用时, "{d} days {h}:{m:02}:{s:02}") if 总用时.days > 1
                            else period(总用时, "{h}:{m:02}:{s:02}")))
                    if 剩余个数 == 0:
                        break
                    下次运行 = datetime.now() + timedelta(seconds=再运行延迟)
                    print(f'Next run time: {下次运行.strftime("%H:%M:%S")}, rerun_delay={再运行延迟}, press Ctrl+C stop run.')
                    time.sleep(再运行延迟)
                else:
                    break
            except:
                break
    else:
        main(args)

    if not conf.auto_exit():
        if sys.platform == 'win32':
            input("Press enter key exit, you can check the error message before you exit...")
