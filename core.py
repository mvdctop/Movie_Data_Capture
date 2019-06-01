import re
import os
import os.path
import shutil
from PIL import Image
import time
import javbus
import json
import fc2fans_club
import siro

#初始化全局变量
title=''
studio=''
year=''
outline=''
runtime=''
director=''
actor=''
release=''
number=''
cover=''
imagecut=''

#=====================资源下载部分===========================
def DownloadFileWithFilename(url,filename,path): #path = examle:photo , video.in the Project Folder!
    import requests
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        r = requests.get(url)
        with open(str(path) + "/"+str(filename), "wb") as code:
            code.write(r.content)
    except IOError as e:
        print("[-]Movie not found in All website!")
        #print("[*]=====================================")
        return "failed"
    except Exception as e1:
        print(e1)
        print("[-]Download Failed2!")
        time.sleep(3)
        os._exit(0)
def PrintFiles(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + "/" + number + ".nfo", "wt", encoding='UTF-8') as code:
            print("<movie>", file=code)
            print(" <title>" + title + "</title>", file=code)
            print("  <set>", file=code)
            print("  </set>", file=code)
            print("  <studio>" + studio + "+</studio>", file=code)
            print("  <year>" + year + "</year>", file=code)
            print("  <outline>"+outline+"</outline>", file=code)
            print("  <plot>"+outline+"</plot>", file=code)
            print("  <runtime>"+str(runtime).replace(" ","")+"</runtime>", file=code)
            print("  <director>" + director + "</director>", file=code)
            print("  <poster>" + number + ".png</poster>", file=code)
            print("  <thumb>" + number + ".png</thumb>", file=code)
            print("  <fanart>"+number + '.jpg'+"</fanart>", file=code)
            print("  <actor>", file=code)
            print("    <name>" + actor + "</name>", file=code)
            print("  </actor>", file=code)
            print("  <maker>" + studio + "</maker>", file=code)
            print("  <label>", file=code)
            print("  </label>", file=code)
            print("  <num>" + number + "</num>", file=code)
            print("  <release>" + release + "</release>", file=code)
            print("  <cover>"+cover+"</cover>", file=code)
            print("  <website>" + "https://www.javbus.com/"+number + "</website>", file=code)
            print("</movie>", file=code)
            print("[+]Writeed!    "+path + "/" + number + ".nfo")
    except IOError as e:
        print("[-]Write Failed!")
        print(e)
    except Exception as e1:
        print(e1)
        print("[-]Write Failed!")

#=====================本地文件处理===========================
def argparse_get_file():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Write the file path on here")
    args = parser.parse_args()
    return args.file
def getNumberFromFilename(filepath):
    global title
    global studio
    global year
    global outline
    global runtime
    global director
    global actor
    global release
    global number
    global cover
    global imagecut

    filename = str(os.path.basename(filepath)) #电影文件名
    str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filename))
    print("[!]Making Data for ["+filename+"]")
    a = str(re.search('\w+-\w+', filename).group())
    #print(a)

    # =======================网站规则添加==============================
    try:
        try:
            if re.search('^\d{5,}', a).group() in filename:
                json_data = json.loads(javbus.main_uncensored(a.replace("-", "_")))
        except:
            if 'fc2' in filename:
                json_data = json.loads(fc2fans_club.main(a))
            elif 'FC2' in filename:
                json_data = json.loads(fc2fans_club.main(a))
            elif 'siro' in filename:
                json_data = json.loads(siro.main(a))
            elif 'SIRO' in filename:
                json_data = json.loads(siro.main(a))
            elif '259luxu' in filename:
                json_data = json.loads(siro.main(a))
            elif '259LUXU' in filename:
                json_data = json.loads(siro.main(a))
            else:
                json_data = json.loads(javbus.main(a))
        # ====================网站规则添加结束==============================

        title = json_data['title']
        studio = json_data['studio']
        year = json_data['year']
        outline = json_data['outline']
        runtime = json_data['runtime']
        director = json_data['director']
        actor = json_data['actor']
        release = json_data['release']
        number = json_data['number']
        cover = json_data['cover']
        imagecut = json_data['imagecut']
    except:
        print('[-]File '+filename+'`s number can not be caught')
        print('[-]Move ' + filename + ' to failed folder')
        if not os.path.exists('failed/'):  # 新建failed文件夹
            os.makedirs('failed/')
            if not os.path.exists('failed/'):
                print("[-]failed!Dirs can not be make (Please run as Administrator)")
                time.sleep(3)
                os._exit(0)
        shutil.move(filepath, str(os.getcwd())+'/'+'failed/')
        os._exit(0)

path = '' #设置path为全局变量，后面移动文件要用

def creatFolder():
    global path
    if not os.path.exists('failed/'): #新建failed文件夹
        os.makedirs('failed/')
        if not os.path.exists('failed/'):
            print("[-]failed!Dirs can not be make (Please run as Administrator)")
            os._exit(0)
    if len(actor) > 240:    #新建成功输出文件夹
        path = 'JAV_output' + '/' + '超多人' + '/' + number #path为影片+元数据所在目录
    else:
        path = 'JAV_output' + '/' + str(actor) + '/' + str(number)
    if not os.path.exists(path):
        os.makedirs(path)
    path = str(os.getcwd())+'/'+path
def imageDownload(filepath): #封面是否下载成功，否则移动到failed
    if DownloadFileWithFilename(cover,str(number) + '.jpg', path) == 'failed':
        shutil.move(filepath, 'failed/')
        os._exit(0)
    DownloadFileWithFilename(cover, number + '.jpg', path)
    print('[+]Image Downloaded!', path +'/'+number+'.jpg')
def cutImage():
    if imagecut == 1:
        try:
            img = Image.open(path + '/' + number + '.jpg')
            imgSize = img.size
            w = img.width
            h = img.height
            img2 = img.crop((w / 1.9, 0, w, h))
            img2.save(path + '/' + number + '.png')
        except:
            print('[-]Cover cut failed!')
    else:
        img = Image.open(path + '/' + number + '.jpg')
        w = img.width
        h = img.height
        img.save(path + '/' + number + '.png')

def pasteFileToFolder(filepath, path): #文件路径，番号，后缀，要移动至的位置
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|avi|rmvb|wmv|mov|mp4|mkv|flv)$', filepath).group())
    os.rename(filepath, number + houzhui)
    shutil.move(number + houzhui, path)

if __name__ == '__main__':
    filepath=argparse_get_file() #影片的路径
    getNumberFromFilename(filepath) #定义番号
    creatFolder() #创建文件夹
    imageDownload(filepath) #creatFoder会返回番号路径
    PrintFiles(path)#打印文件
    cutImage() #裁剪图
    pasteFileToFolder(filepath,path) #移动文件
