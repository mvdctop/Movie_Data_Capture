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
from ADC_function import *
from configparser import ConfigParser

#初始化全局变量
title=''
studio=''
year=''
outline=''
runtime=''
director=''
actor_list=[]
actor=''
release=''
number=''
cover=''
imagecut=''
tag=[]
naming_rule  =''#eval(config['Name_Rule']['naming_rule'])
location_rule=''#eval(config['Name_Rule']['location_rule'])
#=====================本地文件处理===========================
def argparse_get_file():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Write the file path on here")
    args = parser.parse_args()
    return args.file
def CreatFailedFolder():
    if not os.path.exists('failed/'):  # 新建failed文件夹
        try:
            os.makedirs('failed/')
        except:
            print("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            os._exit(0)
def getNumberFromFilename(filepath):
    global title
    global studio
    global year
    global outline
    global runtime
    global director
    global actor_list
    global actor
    global release
    global number
    global cover
    global imagecut
    global tag

    global naming_rule
    global location_rule

#================================================获取文件番号================================================
    try:    #试图提取番号
    # ====番号获取主程序====
        try:  # 普通提取番号 主要处理包含减号-的番号
            filepath.strip('22-sht.me').strip('-HD').strip('-hd')
            filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filepath))  # 去除文件名中文件名
            file_number = re.search('\w+-\d+', filename).group()
        except:  # 提取不含减号-的番号
            try:  # 提取东京热番号格式 n1087
                filename1 = str(re.sub("h26\d", "", filepath)).strip('Tokyo-hot').strip('tokyo-hot')
                filename0 = str(re.sub(".*?\.com-\d+", "", filename1)).strip('_')
                file_number = str(re.search('n\d{4}', filename0).group(0))
            except:  # 提取无减号番号
                filename1 = str(re.sub("h26\d", "", filepath))  # 去除h264/265
                filename0 = str(re.sub(".*?\.com-\d+", "", filename1))
                file_number2 = str(re.match('\w+', filename0).group())
                file_number = str(file_number2.replace(re.match("^[A-Za-z]+", file_number2).group(),re.match("^[A-Za-z]+", file_number2).group() + '-'))
                if not re.search('\w-', file_number).group() == 'None':
                    file_number = re.search('\w+-\w+', filename).group()
                #上面是插入减号-到番号中
        print("[!]Making Data for   [" + filename + "],the number is [" + file_number + "]")
    # ====番号获取主程序=结束===
    except Exception as e: #番号提取异常
        print('[-]'+str(os.path.basename(filepath))+' Cannot catch the number :')
        print('[-]' + str(os.path.basename(filepath)) + ' :', e)
        print('[-]Move ' + os.path.basename(filepath) + ' to failed folder')
        shutil.move(filepath, str(os.getcwd()) + '/' + 'failed/')
        os._exit(0)
    except IOError as e2:
        print('[-]' + str(os.path.basename(filepath)) + ' Cannot catch the number :')
        print('[-]' + str(os.path.basename(filepath)) + ' :',e2)
        print('[-]Move ' + os.path.basename(filepath) + ' to failed folder')
        shutil.move(filepath, str(os.getcwd()) + '/' + 'failed/')
        os._exit(0)
    try:




# ================================================网站规则添加开始================================================

        try:  #添加 需要 正则表达式的规则
            #=======================javbus.py=======================
            if re.search('^\d{5,}', file_number).group() in filename:
                json_data = json.loads(javbus.main_uncensored(file_number))
        except: #添加 无需 正则表达式的规则
            # ====================fc2fans_club.py===================
            if 'fc2' in filename:
                json_data = json.loads(fc2fans_club.main(file_number.strip('fc2_').strip('fc2-')))
            elif 'FC2' in filename:
                json_data = json.loads(fc2fans_club.main(file_number.strip('FC2_').strip('FC2-')))

            #========================siro.py========================
            elif 'siro' in filename:
                json_data = json.loads(siro.main(file_number))
            elif 'SIRO' in filename:
                json_data = json.loads(siro.main(file_number))
            elif '259luxu' in filename:
                json_data = json.loads(siro.main(file_number))
            elif '259LUXU' in filename:
                json_data = json.loads(siro.main(file_number))
            elif '300MAAN' in filename:
                json_data = json.loads(siro.main(file_number))
            elif '300maan' in filename:
                json_data = json.loads(siro.main(file_number))
            elif '326SCP' in filename:
                json_data = json.loads(siro.main(file_number))
            elif '326scp' in filename:
                json_data = json.loads(siro.main(file_number))
            elif '326URF' in filename:
                json_data = json.loads(siro.main(file_number))
            elif '326urf' in filename:
                json_data = json.loads(siro.main(file_number))

            #=======================javbus.py=======================
            else:
                json_data = json.loads(javbus.main(file_number))



#================================================网站规则添加结束================================================




        title     = json_data['title']
        studio    = json_data['studio']
        year      = json_data['year']
        outline   = json_data['outline']
        runtime   = json_data['runtime']
        director  = json_data['director']
        actor_list= str(json_data['actor']).strip("[ ]").replace("'",'').replace(" ",'').split(',') #字符串转列表
        release   = json_data['release']
        number    = json_data['number']
        cover     = json_data['cover']
        imagecut  = json_data['imagecut']
        tag       = str(json_data['tag']).strip("[ ]").replace("'",'').replace(" ",'').split(',')   #字符串转列表
        actor = str(actor_list).strip("[ ]").replace("'",'').replace(" ",'')

        naming_rule  = eval(config['Name_Rule']['naming_rule'])
        location_rule =eval(config['Name_Rule']['location_rule'])
    except IOError as e:
        print('[-]'+str(e))
        print('[-]Move ' + filename + ' to failed folder')
        shutil.move(filepath, str(os.getcwd())+'/'+'failed/')
        os._exit(0)

    except Exception as e:
        print('[-]'+str(e))
        print('[-]Move ' + filename + ' to failed folder')
        shutil.move(filepath, str(os.getcwd())+'/'+'failed/')
        os._exit(0)
path = '' #设置path为全局变量，后面移动文件要用
def creatFolder():
    global path
    if len(actor) > 240:                    #新建成功输出文件夹
        path = location_rule.replace("'actor'","'超多人'",3).replace("actor","'超多人'",3) #path为影片+元数据所在目录
        #print(path)
    else:
        path = location_rule
        #print(path)
    if not os.path.exists(path):
        os.makedirs(path)
#=====================资源下载部分===========================
def DownloadFileWithFilename(url,filename,path): #path = examle:photo , video.in the Project Folder!
    config = ConfigParser()
    config.read('proxy.ini', encoding='UTF-8')
    proxy = str(config['proxy']['proxy'])
    if not str(config['proxy']['proxy']) == '':
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            r = requests.get(url, headers=headers,proxies={"http": "http://" + str(proxy), "https": "https://" + str(proxy)})
            with open(str(path) + "/" + filename, "wb") as code:
                code.write(r.content)
                # print(bytes(r),file=code)
        except IOError as e:
            print("[-]Movie not found in All website!")
            print("[-]" + filename, e)
            # print("[*]=====================================")
            return "failed"
        except Exception as e1:
            print(e1)
            print("[-]Download Failed2!")
            time.sleep(3)
            os._exit(0)
    else:
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            r = requests.get(url, headers=headers)
            with open(str(path) + "/" + filename, "wb") as code:
                code.write(r.content)
                # print(bytes(r),file=code)
        except IOError as e:
            print("[-]Movie not found in All website!")
            print("[-]" + filename, e)
            # print("[*]=====================================")
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
        with open(path + "/" + naming_rule + ".nfo", "wt", encoding='UTF-8') as code:
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
            print("  <poster>" + naming_rule + ".png</poster>", file=code)
            print("  <thumb>" + naming_rule + ".png</thumb>", file=code)
            print("  <fanart>"+naming_rule + '.jpg'+"</fanart>", file=code)
            try:
                for u in actor_list:
                    print("  <actor>", file=code)
                    print("   <name>" + u + "</name>", file=code)
                    print("  </actor>", file=code)
            except:
                aaaa=''
            print("  <maker>" + studio + "</maker>", file=code)
            print("  <label>", file=code)
            print("  </label>", file=code)
            try:
                for i in tag:
                    print("  <tag>" + i + "</tag>", file=code)
            except:
                aaaaa=''
            try:
                for i in tag:
                    print("  <genre>" + i + "</genre>", file=code)
            except:
                aaaaaaaa=''
            print("  <num>" + number + "</num>", file=code)
            print("  <release>" + release + "</release>", file=code)
            print("  <cover>"+cover+"</cover>", file=code)
            print("  <website>" + "https://www.javbus.com/"+number + "</website>", file=code)
            print("</movie>", file=code)
            print("[+]Writeed!          "+path + "/" + naming_rule + ".nfo")
    except IOError as e:
        print("[-]Write Failed!")
        print(e)
    except Exception as e1:
        print(e1)
        print("[-]Write Failed!")
def imageDownload(filepath): #封面是否下载成功，否则移动到failed
    if DownloadFileWithFilename(cover,naming_rule+ '.jpg', path) == 'failed':
        shutil.move(filepath, 'failed/')
        os._exit(0)
    DownloadFileWithFilename(cover, naming_rule + '.jpg', path)
    print('[+]Image Downloaded!', path +'/'+naming_rule+'.jpg')
def cutImage():
    if imagecut == 1:
        try:
            img = Image.open(path + '/' + naming_rule + '.jpg')
            imgSize = img.size
            w = img.width
            h = img.height
            img2 = img.crop((w / 1.9, 0, w, h))
            img2.save(path + '/' + naming_rule + '.png')
        except:
            print('[-]Cover cut failed!')
    else:
        img = Image.open(path + '/' + naming_rule + '.jpg')
        w = img.width
        h = img.height
        img.save(path + '/' + naming_rule + '.png')
def pasteFileToFolder(filepath, path): #文件路径，番号，后缀，要移动至的位置
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|avi|rmvb|wmv|mov|mp4|mkv|flv|ts)$', filepath).group())
    os.rename(filepath, naming_rule + houzhui)
    shutil.move(naming_rule + houzhui, path)

if __name__ == '__main__':
    filepath=argparse_get_file() #影片的路径
    CreatFailedFolder()
    getNumberFromFilename(filepath) #定义番号
    creatFolder() #创建文件夹
    imageDownload(filepath) #creatFoder会返回番号路径
    PrintFiles(path)#打印文件
    cutImage() #裁剪图
    pasteFileToFolder(filepath,path) #移动文件
