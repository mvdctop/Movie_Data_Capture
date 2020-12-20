import argparse
import os
import sys

from number_parser import get_number
from core import *

def check_update(local_version):
    data = json.loads(get_html("https://api.github.com/repos/yoshiko2/AV_Data_Capture/releases/latest"))

    remote = data["tag_name"]
    local = local_version

    if not local == remote:
        line1 = "* New update " + str(remote) + " *"
        print("[*]" + line1.center(54))
        print("[*]" + "↓ Download ↓".center(54))
        print("[*] https://github.com/yoshiko2/AV_Data_Capture/releases")
        print("[*]======================================================")


def argparse_function(ver: str) -> [str, str, bool]:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", default='', nargs='?', help="Single Movie file path.")
    parser.add_argument("-c", "--config", default='config.ini', nargs='?', help="The config file Path.")
    parser.add_argument("-n", "--number", default='', nargs='?',help="Custom file number")
    parser.add_argument("-a", "--auto-exit", dest='autoexit', action="store_true", help="Auto exit after program complete")
    parser.add_argument("-v", "--version", action="version", version=ver)
    args = parser.parse_args()

    return args.file, args.config, args.number, args.autoexit

def movie_lists(root, escape_folder):
    for folder in escape_folder:
        if folder in root:
            return []
    total = []
    file_type = ['.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.MP4', '.AVI', '.RMVB', '.WMV','.MOV', '.MKV', '.FLV', '.TS', '.WEBM', '.iso','.ISO']
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.isdir(f):
            total += movie_lists(f, escape_folder)
        elif os.path.splitext(f)[1] in file_type:
            total.append(f)
    return total


def create_failed_folder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            sys.exit(0)


def CEF(path):
    try:
        files = os.listdir(path)  # 获取路径下的子文件(夹)列表
        for file in files:
            os.removedirs(path + '/' + file)  # 删除这个空文件夹
            print('[+]Deleting empty folder', path + '/' + file)
    except:
        a = ''


def create_data_and_move(file_path: str, c: config.Config,debug):
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    n_number = get_number(debug,file_path)

    if debug == True:
        print("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
        core_main(file_path, n_number, c)
        print("[*]======================================================")
    else:
        try:
            print("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
            core_main(file_path, n_number, c)
            print("[*]======================================================")
        except Exception as err:
            print("[-] [{}] ERROR:".format(file_path))
            print('[-]', err)

            # 3.7.2 New: Move or not move to failed folder.
            if c.failed_move() == False:
                if c.soft_link():
                    print("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
            elif c.failed_move() == True:
                if c.soft_link():
                    print("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
                else:
                    try:
                        print("[-]Move [{}] to failed folder".format(file_path))
                        shutil.move(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
                    except Exception as err:
                        print('[!]', err)

def create_data_and_move_with_custom_number(file_path: str, c: config.Config, custom_number=None):
    try:
        print("[!]Making Data for [{}], the number is [{}]".format(file_path, custom_number))
        core_main(file_path, custom_number, c)
        print("[*]======================================================")
    except Exception as err:
        print("[-] [{}] ERROR:".format(file_path))
        print('[-]', err)

        if c.soft_link():
            print("[-]Link {} to failed folder".format(file_path))
            os.symlink(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
        else:
            try:
                print("[-]Move [{}] to failed folder".format(file_path))
                shutil.move(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
            except Exception as err:
                print('[!]', err)


if __name__ == '__main__':
    version = '4.2.1'

    # Parse command line args
    single_file_path, config_file, custom_number, auto_exit = argparse_function(version)

    # Read config.ini
    conf = config.Config(path=config_file)

    version_print = 'Version ' + version
    print('[*]================== AV Data Capture ===================')
    print('[*]' + version_print.center(54))
    print('[*]======================================================')

    if conf.update_check():
        check_update(version)

    create_failed_folder(conf.failed_folder())
    os.chdir(os.getcwd())

    # ========== Single File ==========
    if not single_file_path == '':
        print('[+]==================== Single File =====================')
        create_data_and_move_with_custom_number(single_file_path, conf,custom_number)
        CEF(conf.success_folder())
        CEF(conf.failed_folder())
        print("[+]All finished!!!")
        input("[+][+]Press enter key exit, you can check the error messge before you exit.")
        sys.exit(0)
    # ========== Single File ==========

    movie_list = movie_lists(".", re.split("[,，]", conf.escape_folder()))

    count = 0
    count_all = str(len(movie_list))
    print('[+]Find', count_all, 'movies')
    if conf.debug() == True:
        print('[+]'+' DEBUG MODE ON '.center(54, '-'))
    if conf.soft_link():
        print('[!] --- Soft link mode is ENABLE! ----')
    for movie_path in movie_list:  # 遍历电影列表 交给core处理
        count = count + 1
        percentage = str(count / int(count_all) * 100)[:4] + '%'
        print('[!] - ' + percentage + ' [' + str(count) + '/' + count_all + '] -')
        create_data_and_move(movie_path, conf, conf.debug())

    CEF(conf.success_folder())
    CEF(conf.failed_folder())
    print("[+]All finished!!!")
    if conf.auto_exit():
        sys.exit(0)
    if auto_exit:
        sys.exit(0)
    input("Press enter key exit, you can check the error message before you exit...")
    sys.exit(0)
