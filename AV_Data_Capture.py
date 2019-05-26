import glob
import os
import time

#a=glob.glob(os.getcwd()+r"\*.py")
a=glob.glob(os.getcwd()+r"\*\**\*.mp4")
b=glob.glob(os.getcwd()+r"\*.mp4")
for i in b:
    a.append(i)

os.chdir(os.getcwd())
for i in a:
    os.system('python core.py'+' "'+i+'"')
    time.sleep(3)
