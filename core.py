import re
import requests #need install
from pyquery import PyQuery as pq#need install
from lxml import etree#need install
import os
import os.path
import shutil
from bs4 import BeautifulSoup#need install
from PIL import Image#need install
import time

#=====================爬虫核心部分==========================
def get_html(url):#网页请求核心
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    getweb = requests.get(str(url),proxies={"http": "http://127.0.0.1:2334","https": "https://127.0.0.1:2334"},timeout=5,headers=headers).text
    try:
        return getweb
    except Exception as e:
        print(e)
    except IOError as e1:
        print(e1)

def getTitle(htmlcode):  #获取标题
    doc = pq(htmlcode)
    title=str(doc('div.container h3').text()).replace(' ','-')
    return title
def getStudio(htmlcode): #获取厂商
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[5]/a/text()')).strip(" ['']")
    return result
def getYear(htmlcode):   #获取年份
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    result2 = str(re.search('\d{4}', result).group(0))
    return result2
def getCover(htmlcode):  #获取封面链接
    doc = pq(htmlcode)
    image = doc('a.bigImage')
    return image.attr('href')
    print(image.attr('href'))
def getRelease(htmlcode): #获取出版日期
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    return result
def getRuntime(htmlcode): #获取分钟
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = soup.find(text=re.compile('分鐘'))
    return a
def getActor(htmlcode):   #获取女优
    b=[]
    soup=BeautifulSoup(htmlcode,'lxml')
    a=soup.find_all(attrs={'class':'star-name'})
    for i in a:
        b.append(i.text)
    return ",".join(b)
def getNum(htmlcode):     #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    return result
def getDirector(htmlcode): #获取导演
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/a/text()')).strip(" ['']")
    return result
def getOutline(htmlcode):  #获取演员
    doc = pq(htmlcode)
    result = str(doc('tr td div.mg-b20.lh4 p.mg-b20').text())
    return result
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
        print("[-]Download Failed1!")
        print("[-]Error:"+str(e))
        print("[-]Movie not found in Javbus.com!")
        print("[*]=====================================")
        return "failed"
    except Exception as e1:
        print(e1)
        print("[-]Download Failed2!")
        time.sleep(3)
        os._exit(0)
def PrintFiles(html,html_outline,path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + "/" + getNum(html) + ".nfo", "wt", encoding='UTF-8') as code:
            print("<movie>", file=code)
            print(" <title>" + getTitle(html) + "</title>", file=code)
            print("  <set>", file=code)
            print("  </set>", file=code)
            print("  <studio>" + getStudio(html) + "+</studio>", file=code)
            print("  <year>" + getYear(html) + "</year>", file=code)
            print("  <outline>"+getOutline(html_outline)+"</outline>", file=code)
            print("  <plot>"+getOutline(html_outline)+"</plot>", file=code)
            print("  <runtime>"+str(getRuntime(html)).replace(" ","")+"</runtime>", file=code)
            print("  <director>" + getDirector(html) + "</director>", file=code)
            print("  <poster>" + getNum(html) + ".png</poster>", file=code)
            print("  <thumb>" + getNum(html) + ".png</thumb>", file=code)
            print("  <fanart>"+getNum(html) + '.jpg'+"</fanart>", file=code)
            print("  <actor>", file=code)
            print("    <name>" + getActor(html) + "</name>", file=code)
            print("  </actor>", file=code)
            print("  <maker>" + getStudio(html) + "</maker>", file=code)
            print("  <label>", file=code)
            print("  </label>", file=code)
            print("  <num>" + getNum(html) + "</num>", file=code)
            print("  <release>" + getRelease(html) + "</release>", file=code)
            print("  <cover>"+getCover(html)+"</cover>", file=code)
            print("  <website>" + "https://www.javbus.com/"+getNum(html) + "</website>", file=code)
            print("</movie>", file=code)
            print("[+]Writeed!    "+path + "/" + getNum(html) + ".nfo")
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
    filename = str(os.path.basename(filepath)) #电影文件名
    str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filename))

    print("[!]Making Data for ["+filename+"]")
    try:
        a = str(re.search('\w+-\w+', filename).group())
        return a
    except:
        print('[-]File '+filename+'`s number can not be caught')
        print('[-]Move ' + filename + 'to failed folder')
        if not os.path.exists('failed/'):  # 新建failed文件夹
            os.makedirs('failed/')
            if not os.path.exists('failed/'):
                print("[-]failed!Dirs can not be make (Please run as Administrator)")
                time.sleep(3)
                os._exit(0)
        shutil.move(filepath, str(os.getcwd())+'/'+'failed/')
        os._exit(0)
def get_html_javbus(number):
    return get_html("https://www.javbus.com/" + str(number))
def get_html_dww(number):
    return get_html("https://www.dmm.co.jp/mono/dvd/-/detail/=/cid=" + number.replace("-", ''))
path = '' #设置path为全局变量，后面移动文件要用
def creatFolder(html,number):
    global path
    if not os.path.exists('failed/'): #新建failed文件夹
        os.makedirs('failed/')
        if not os.path.exists('failed/'):
            print("[-]failed!Dirs can not be make (Please run as Administrator)")
            os._exit(0)
    if len(getActor(html)) > 240:    #新建成功输出文件夹
        path = 'JAV_output' + '/' + '超多人' + '/' + number #path为影片+元数据所在目录
    else:
        path = 'JAV_output' + '/' + getActor(html) + '/' + number
    if not os.path.exists(path):
        os.makedirs(path)
    path = str(os.getcwd())+'/'+path
def imageDownload(htmlcode,filepath,number): #封面是否下载成功，否则移动到failed
    if DownloadFileWithFilename(getCover(htmlcode),number + '.jpg', path) == 'failed':
        shutil.move(filepath, 'failed/')
        os._exit(0)
    DownloadFileWithFilename(getCover(htmlcode), number + '.jpg', path)
    print('[+]Downloaded!', path +'/'+number+'.jpg')
def cutImage(number):
    try:
        img = Image.open(path + '/' + number + '.jpg')
        img2 = img.crop((421, 0, 800, 538))
        img2.save(path + '/' + number + '.png')
    except:
        print('[-]Cover cut failed!')
def pasteFileToFolder(filepath, number, path): #文件路径，番号，后缀，要移动至的位置
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|avi|rmvb|wmv|mov|mp4|mkv|flv)$', filepath).group())
    os.rename(filepath, number + houzhui)
    shutil.move(number + houzhui, path)

if __name__ == '__main__':
    filepath=argparse_get_file() #影片的路径
    number=getNumberFromFilename(filepath) #定义番号
    htmlcode=get_html_javbus(number) #获取的HTML代码
    creatFolder(htmlcode,number) #创建文件夹
    imageDownload(htmlcode,filepath,number) #creatFoder会返回番号路径
    cutImage(number) #裁剪图片
    pasteFileToFolder(filepath,number,path) #移动文件
