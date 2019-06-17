<h1 style="text-align:center">日本AV元数据抓取工具</h1>

## 关于本软件 （~路star谢谢）


目前，我下的AV越来越多，也意味着AV要集中地管理，形成媒体库。现在有两款主流的AV元数据获取器，"EverAver"和"Javhelper"。前者的优点是元数据获取比较全，缺点是不能批量处理；后者优点是可以批量处理，但是元数据不够全。

为此，综合上述软件特点，我写出了本软件，为了方便的管理本地AV，和更好的手冲体验。没女朋友怎么办ʅ(‾◡◝)ʃ 

**tg官方电报群:https://t.me/AV_Data_Capture_Official**

**推荐用法:按照说明使用该软件后，对于不能正常获取元数据的电影可以用[Everaver](http://everaver.blogspot.com/)来补救**

### **请认真阅读下面使用说明再使用** * [如何使用](#如何使用)

![](https://i.loli.net/2019/06/02/5cf2b5d0bbecf69019.png)


## 软件流程图
![](https://i.loli.net/2019/06/02/5cf2bb9a9e2d997635.png)

# 如何使用
---------------
release的程序可脱离python环境运行，可跳过第一步

下载地址(Windows):https://github.com/wenead99/AV_Data_Capture/releases

## 1. 请安装requests,pyquery,lxml,Beautifulsoup4,pillow模块,在 CMD/终端 逐条输入以下命令安装
```python
pip install requests
```
###
```python
pip install pyquery
   ```
###
```python
pip install lxml
```
###
```python
pip install Beautifulsoup4
```
###
```python
pip install pillow
```

## 2. 设置proxy.ini
#### 1.针对网络审查国家或地区

打开```proxy.ini```,在```[proxy]```下的```proxy```行设置本地代理地址和端口，支持Shadowsocks/R,V2RAY本地代理端口:
```proxy=127.0.0.1:1080```

#### 2.设置自定义目录和影片重命名规则

**目前可以提取元素的影片:JAVBUS上有元数据的电影，素人系列:300Maan,326scp,326urf,259luxu,siro系列,FC2系列(不推荐)**
>**命名参数**
>title = 片名
>actor = 演员
>studio = 公司
>director = 导演
>release = 发售日
>year = 发行年份
>number = 番号
>cover = 封面链接
>tag = 类型
>outline = 简介
>runtime = 时长
>**例子**:
>目录结构：'JAV_output/'+actor+'/'+actor+' '+' ['+year+']'+title+' ['+number+']'

## 3. 关于番号提取失败或者异常
>下一张图片来自Pockies的blog:https://pockies.github.io/2019/03/25/everaver-emby-kodi/ 原作者已授权

![](https://raw.githubusercontent.com/Pockies/pic/master/741f9461gy1g1cxc31t41j20i804zdgo.jpg)


**目前作者已经完善了番号提取机制，功能较为强大，可提取上述文件名的的番号，如果出现提取失败或者异常的情况，请用以下规则命名**

```
COSQ-004.mp4
```

>文件名中间要有下划线或者减号"_","-"，没有多余的内容只有番号为最佳，可以让软件更好获取元数据
>对于多影片重命名，可以用ReNamer来批量重命名
>软件官网:http://www.den4b.com/products/renamer


## 4. 把软件拷贝和AV的统一目录下

## 5. 运行 ```AV_Data_capture.py/.exe```
>**你也可以把单个影片拖动到core程序**

![](https://i.loli.net/2019/06/02/5cf2b5d03640e73201.gif)

## 6. 软件会自动把元数据获取成功的电影移动到JAV_output文件夹中，根据女优分类，失败的电影移动到failed文件夹中。

## 7. 把JAV_output文件夹导入到EMBY,KODI中，根据封面选片子，享受手冲乐趣

## 8.输出的文件如下
![](https://i.loli.net/2019/06/02/5cf2b5cfd1b0226763.png)
![](https://i.loli.net/2019/06/02/5cf2b5cfd1b0246492.png)
![](https://i.loli.net/2019/06/02/5cf2b5d009e4930666.png)



