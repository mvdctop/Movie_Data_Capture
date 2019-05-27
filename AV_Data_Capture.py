import glob
import os
import time

def movie_lists():
    #MP4
    a1 = glob.glob(os.getcwd() + r"\*\**\*.mp4")
    a2 = glob.glob(os.getcwd() + r"\*.mp4")
    # AVI
    b1 = glob.glob(os.getcwd() + r"\*\**\*.avi")
    b2 = glob.glob(os.getcwd() + r"\*.avi")
    # RMVB
    c1 = glob.glob(os.getcwd() + r"\*\**\*.rmvb")
    c2 = glob.glob(os.getcwd() + r"\*.rmvb")
    # WMV
    d1 = glob.glob(os.getcwd() + r"\*\**\*.wmv")
    d2 = glob.glob(os.getcwd() + r"\*.wmv")
    # MOV
    e1 = glob.glob(os.getcwd() + r"\*\**\*.mov")
    e2 = glob.glob(os.getcwd() + r"\*.mov")
    # MKV
    f1 = glob.glob(os.getcwd() + r"\*\**\*.mkv")
    f2 = glob.glob(os.getcwd() + r"\*.mkv")
    # FLV
    g1 = glob.glob(os.getcwd() + r"\*\**\*.flv")
    g2 = glob.glob(os.getcwd() + r"\*.flv")

    total = a1+a2+b1+b2+c1+c2+d1+d2+e1+e2+f1+f2+g1+g2
    return total

def lists_from_test(custom_nuber):
    a=[]
    a.append(custom_nuber)
    return a

os.chdir(os.getcwd())
for i in movie_lists():
    os.system('python core.py'+' "'+i+'"')
print("[+]All finished!!!")
