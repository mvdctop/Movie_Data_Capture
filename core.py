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

def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
    getweb = requests.get(str(url),proxies={"http": "http://127.0.0.1:2334","https": "https://127.0.0.1:2334"},timeout=5,headers=headers).text
    try:
        return getweb
    except Exception as e:
        print(e)
    except IOError as e1:
        print(e1)
#================================================
def getTitle(htmlcode):
    doc = pq(htmlcode)
    title=str(doc('div.container h3').text()).replace(' ','-')
    return title
def getStudio(htmlcode):
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[5]/a/text()')).strip(" ['']")
    return result
def getYear(htmlcode):
    html = etree.fromstring(htmlcode,etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    result2 = str(re.search('\d{4}', result).group(0))
    return result2
def getCover(htmlcode):
    doc = pq(htmlcode)
    image = doc('a.bigImage')
    return image.attr('href')
    print(image.attr('href'))
def getRelease(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[2]/text()')).strip(" ['']")
    return result
def getRuntime(htmlcode):
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = soup.find(text=re.compile('分鐘'))
    return a
def getActor(htmlcode):
    b=[]
    soup=BeautifulSoup(htmlcode,'lxml')
    a=soup.find_all(attrs={'class':'star-name'})
    for i in a:
        b.append(i.text)
    return ",".join(b)
def getNum(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    return result
def getDirector(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[4]/a/text()')).strip(" ['']")
    return result
def getOutline(htmlcode):
    doc = pq(htmlcode)
    result = str(doc('tr td div.mg-b20.lh4 p.mg-b20').text())
    return result
#================================================
def DownloadFileWithFilename(url,filename,path): #path = examle:photo , video.in the Project Folder!
    import requests
    import re
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        r = requests.get(url)
        with open(str(path) + "/"+str(filename), "wb") as code:
            code.write(r.content)
            # print('[+]Downloaded!',str(path) + "/"+str(filename))
    except IOError as e:
        print("[-]Download Failed1!")
        print("[-]Movie not found in Javbus.com!")
        print("[*]=====================================")
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
#================================================
if __name__ == '__main__':
    #命令行处理
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Write the file path on here")
    args = parser.parse_args()
    filename=str(os.path.basename(args.file)) #\[\d{4}(\-|\/|.)\d{1,2}\1\d{1,2}\]
    #去除文件名中日期
    #print(filename)
    deldate=str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ","",filename))
    #print(deldate)
    number=str(re.search('\w+-\w+',deldate).group())
    #print(number)
    #获取网页信息
    html = get_html("https://www.javbus.com/"+str(number))
    html_outline=get_html("https://www.dmm.co.jp/mono/dvd/-/detail/=/cid="+number.replace("-",''))
    #处理超长文件夹名称
    if len(getActor(html)) > 240:
        path = 'JAV_output' + '/' + '超多人' + '/' + getNum(html)
    else:
        path = 'JAV_output' + '/' + getActor(html) + '/' + getNum(html)
    if not os.path.exists(path):
        os.makedirs(path)
    #文件路径处理
    #print(str(args))
    filepath = str(args).replace("Namespace(file='",'').replace("')",'').replace('\\\\', '\\')
    #print(filepath)
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|avi|rmvb|wmv|mov|mp4|mkv|flv)$',filepath).group())
    print("[!]Making Data for ["+number+houzhui+"]")
    #下载元数据


    if not os.path.exists('failed/'):
        os.makedirs('failed/')
        if not os.path.exists('failed/'):
            print("[-]failed!Dirs can not be make (Please run as Administrator)")
            os._exit(0)
        if DownloadFileWithFilename(getCover(html), getNum(html) + '.jpg', path) == 'failed':
            shutil.move(filepath, 'failed/')
            time.sleep(3)
            os._exit(0)
    else:
        if DownloadFileWithFilename(getCover(html), getNum(html) + '.jpg', path) == 'failed':
            shutil.move(filepath, 'failed/')
            os._exit(0)
        DownloadFileWithFilename(getCover(html), getNum(html) + '.jpg', path)
        print('[+]Downloaded!', path +'/'+getNum(html)+'.jpg')
    #切割图片做封面
    try:
        img = Image.open(path + '/' + getNum(html) + '.jpg')
        img2 = img.crop((421, 0, 800, 538))
        img2.save(path + '/' + getNum(html) + '.png')
    except:
        print('[-]Cover cut failed!')
    # 电源文件位置处理
    os.rename(filepath, number + houzhui)
    shutil.move(number + houzhui, path)
    #处理元数据
    PrintFiles(path)
    print('[!]Finished!')
    time.sleep(3)