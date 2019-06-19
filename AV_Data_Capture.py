import glob
import os
import time
import re
import sys

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
    # TS
    h2 = glob.glob(os.getcwd() + r"\*.ts")

    total = a2+b2+c2+d2+e2+f2+g2+h2
    return total

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

if __name__ =='__main__':
    os.chdir(os.getcwd())
    for i in movie_lists(): #遍历电影列表 交给core处理
        if '_' in i:
            os.rename(re.search(r'[^\\/:*?"<>|\r\n]+$', i).group(), rreplace(re.search(r'[^\\/:*?"<>|\r\n]+$', i).group(), '_', '-', 1))
            i = rreplace(re.search(r'[^\\/:*?"<>|\r\n]+$', i).group(), '_', '-', 1)
        os.system('python core.py' + ' "' + i + '"') #选择从py文件启动  （用于源码py）
        #os.system('core.exe' + ' "' + i + '"')      #选择从exe文件启动（用于EXE版程序）
        print("[*]=====================================")

    print("[!]Cleaning empty folders")
    CEF('JAV_output')
    print("[+]All finished!!!")
    input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看错误信息。")