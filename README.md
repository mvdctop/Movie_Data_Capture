# 日本AV元数据抓取工具  （刮削器）

## 关于本软件 （~路star谢谢）

**#0.5重大更新：新增对FC2,259LUXU,SIRO,300MAAN系列影片抓取支持,优化对无码视频抓取**

目前，我下的AV越来越多，也意味着AV要集中地管理，形成媒体库。现在有两款主流的AV元数据获取器，"EverAver"和"Javhelper"。前者的优点是元数据获取比较全，缺点是不能批量处理；后者优点是可以批量处理，但是元数据不够全。

为此，综合上述软件特点，我写出了本软件，为了方便的管理本地AV，和更好的手冲体验。没女朋友怎么办ʅ(‾◡◝)ʃ 

**预计本周末适配DS Video，暂时只支持Kodi,EMBY**

**tg官方电报群:https://t.me/AV_Data_Capture_Official**

### **请认真阅读下面使用说明再使用** * [如何使用](#如何使用)

![](https://i.loli.net/2019/06/02/5cf2b5d0bbecf69019.png)


## 软件流程图
![](https://i.loli.net/2019/06/02/5cf2bb9a9e2d997635.png)

## 如何使用
### **请认真阅读下面使用说明**
  **release的程序可脱离python环境运行，可跳过第一步（仅限windows平台)**
  **下载地址(Windows):https://github.com/wenead99/AV_Data_Capture/releases**
1. 请安装requests,pyquery,lxml,Beautifulsoup4,pillow模块,可在CMD逐条输入以下命令安装
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

## 2. 设置本地代理（针对网络审查国家或地区）**Beta8新特性**
打开proxy.ini,在proxy行设置本地代理地址和端口，支持Shadowsocks/R,V2RAY本地代理端口


3. 你的AV在被软件管理前最好命名为番号:

```
COSQ-004.mp4
```

或者

```
COSQ_004.mp4
```

文件名中间要有下划线或者减号"_","-"，没有多余的内容只有番号为最佳，可以让软件更好获取元数据
对于多影片重命名，可以用ReNamer来批量重命名
软件官网:http://www.den4b.com/products/renamer

![](https://i.loli.net/2019/06/02/5cf2b5cfbfe1070559.png)


4. 把软件拷贝到AV的所在目录下，运行程序（中国大陆用户必须挂VPN，Shsadowsocks开全局代理）
5. 运行AV_Data_capture.py
6. **你也可以把单个影片拖动到core程序**

![](https://i.loli.net/2019/06/02/5cf2b5d03640e73201.gif)

7. 软件会自动把元数据获取成功的电影移动到JAV_output文件夹中，根据女优分类，失败的电影移动到failed文件夹中。

8. 把JAV_output文件夹导入到EMBY,KODI中，根据封面选片子，享受手冲乐趣

![](https://i.loli.net/2019/06/02/5cf2b5cfd1b0226763.png)
![](https://i.loli.net/2019/06/02/5cf2b5cfd1b0246492.png)
![](https://i.loli.net/2019/06/02/5cf2b5d009e4930666.png)



