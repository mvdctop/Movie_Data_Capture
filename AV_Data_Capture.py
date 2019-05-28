import glob
import os
import time

def movie_lists():
    #MP4
    a2 = glob.glob(os.getcwd() + r"\*.mp4")
    # AVI
    b2 = glob.glob(os.getcwd() + r"\*.avi")
    # RMVB
    c2 = glob.glob(os.getcwd() + r"\*.rmvb")
    # WMV
    d2 = glob.glob(os.getcwd() + r"\*.wmv")
    # MOV
    e2 = glob.glob(os.getcwd() + r"\*.mov")
    # MKV
    f2 = glob.glob(os.getcwd() + r"\*.mkv")
    # FLV
    g2 = glob.glob(os.getcwd() + r"\*.flv")

    total = a2+b2+c2+d2+e2+f2+g2
    return total

def lists_from_test(custom_nuber):
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

if __name__ =='__main__':
    os.chdir(os.getcwd())
    for i in movie_lists():
        os.system('python core.py' + ' "' + i + '"')
    print("[!]Cleaning empty folders")
    CEF('JAV_output')
    print("[+]All finished!!!")
    time.sleep(3)
