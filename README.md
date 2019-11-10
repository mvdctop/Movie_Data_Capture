# AV Data Capture


<a title="Hits" target="_blank" href="https://github.com/yoshiko2/AV_Data_Capture"><img src="https://hits.b3log.org/yoshiko2/AV_Data_Capture.svg"></a>
![](https://img.shields.io/badge/build-passing-brightgreen.svg?style=flat-square)
![](https://img.shields.io/github/downloads/yoshiko2/av_data_capture/total.svg?style=flat-square)<br>
![](https://img.shields.io/github/license/yoshiko2/av_data_capture.svg?style=flat-square)
![](https://img.shields.io/github/release/yoshiko2/av_data_capture.svg?style=flat-square)
![](https://img.shields.io/badge/Python-3.7-yellow.svg?style=flat-square&logo=python)<br>
[![HitCount](http://hits.dwyl.io/yoshiko2/av_data_capture.svg)](http://hits.dwyl.io/yoshiko2/av_data_capture)


**日本电影元数据 抓取工具 | 刮削器**，配合本地影片管理软件EMBY,KODI等管理本地影片，该软件起到分类与元数据抓取作用，利用元数据信息来分类，供本地影片分类整理使用。

# 目录
* [声明](#声明)
* [FAQ](#FAQ)
* [故事](#故事)
* [效果图](#效果图)
* [如何使用](#如何使用)
* [下载](#下载)
* [简明教程](#简要教程)
* [模块安装](#1模块安装)
* [配置](#2配置configini)
* [多目录影片处理](#4多目录影片处理)
* [多集影片处理](#多集影片处理)
* [(可选)设置自定义目录和影片重命名规则](#3可选设置自定义目录和影片重命名规则)
* [运行软件](#5运行-av_data_capturepyexe)
* [影片原路径处理](#4建议把软件拷贝和电影的统一目录下)
* [异常处理（重要）](#51异常处理重要)
* [导入至媒体库](#7把jav_output文件夹导入到embykodi中等待元数据刷新完成)
* [关于群晖NAS](#8关于群晖NAS)
* [写在后面](#9写在后面)

# 声明
* 本软件仅供**技术交流，学术交流**使用<br>
* 本软件作者编写出该软件旨在学习Python3，提高编程水平<br>
* 用户在使用该软件前，请用户自觉遵守当地法律法规，如果该软件使用过程中存在违反当地法律法规的行为，请勿使用该软件<br>
* 用户使用该软件时，若产生一切违法行为由用户承担<br>
* 严禁用户使用于商业和个人其他意图<br>
* 本软件作者保留最终决定权和最终解释权<br>

**若用户不同意上述条款任意一条，请勿使用该软件**<br>

# FAQ
### 这软件能下片吗？
* 该软件不提供任何影片下载地址，仅供本地影片分类整理使用。
### 什么是元数据？
* 元数据包括了影片的：封面，导演，演员，简介，类型......
### 软件收费吗？
* 软件永久免费。**除了作者钦点以外**
### 软件运行异常怎么办？
* 认真看 [异常处理（重要）](#5异常处理重要)

# 故事
[点击跳转至作者博客文章](https://yoshiko2.github.io/2019/10/18/AVDC/)

# 效果图
**图片来自网络**，由于相关法律法规，具体效果请自行联想
![](https://i.loli.net/2019/07/04/5d1cf9bb1b08b86592.jpg)
![](https://i.loli.net/2019/07/04/5d1cf9bb2696937880.jpg)<br>

# 如何使用
### 下载
* release的程序可脱离**python环境**运行，可跳过 [模块安装](#1请安装模块在cmd终端逐条输入以下命令安装)<br>Release 下载地址(**仅限Windows**):<br>[![](https://img.shields.io/badge/%E4%B8%8B%E8%BD%BD-windows-blue.svg?style=for-the-badge&logo=windows)](https://github.com/yoshiko2/AV_Data_Capture/releases)<br>
* Linux,MacOS请下载源码包运行

* Windows Python环境:[点击前往](https://www.python.org/downloads/windows/) 选中executable installer下载
* MacOS Python环境：[点击前往](https://www.python.org/downloads/mac-osx/)
* Linux Python环境：Linux用户懂的吧，不解释下载地址
### 简要教程:<br>
**1.把软件拉到和电影的同一目录<br>2.设置ini文件的代理（路由器拥有自动代理功能的可以把proxy=后面内容去掉）<br>3.运行软件等待完成<br>4.把JAV_output导入至KODI,EMBY中。<br>详细请看以下教程**<br>

## 1.模块安装
如果运行**源码**版，运行前请安装**Python环境**和安装以下**模块**  
在终端/cmd/Powershell中输入以下代码来安装模块
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
###

## 2.配置config.ini
#### 运行模式
>[common]<br>
>main_mode=1<br>

1为普通模式<br>
2为整理模式：仅根据女优把电影命名为番号并分类到女优名称的文件夹下

>failed_output_folder=failed<br>
>success_output_folder=JAV_outputd<br>

设置成功输出目录和失败输出目录

---
### 网络设置
>[proxy]  
>proxy=127.0.0.1:1081  
>timeout=10  
>retry=3  
#### 针对某些地区的代理设置
>proxy=127.0.0.1:1081  

打开```config.ini```,在```[proxy]```下的```proxy```行设置本地代理地址和端口，支持Shadowxxxx/X,V2XXX本地代理端口  
素人系列抓取建议使用日本代理  
**路由器拥有自动代理功能的可以把proxy=后面内容去掉**  
**本地代理软件开全局模式的用户同上**  
**如果遇到tineout错误，可以把文件的proxy=后面的地址和端口删除，并开启代理软件全局模式，或者重启电脑，代理软件，网卡**  

---
#### 连接超时重试设置
>timeout=10  

10为超时重试时间 单位：秒

---
#### 连接重试次数设置
>retry=3  

3即为重试次数

---
#### 检查更新开关
>[update]  
>update_check=1  

0为关闭，1为开启，不建议关闭

---
### 媒体库选择 
>[media]<br>
>media_warehouse=emby<br>
>#emby plex kodi<br>

可选择emby, plex, kodi<br>
如果是PLEX，请安装插件：```XBMCnfoMoviesImporter```

---
### 抓取目录
>[escape]  
>literals=\  

```literals=``` 标题指定字符删除，例如```iterals=\()```，删除标题中```\()```字符

---
### 抓取目录选择
>[movie_location]<br>
>path=<br>

如果directory后面为空，则抓取和程序同一目录下的影片

---
### 调试模式
>[debug_mode]<br>switch=1  

如要开启调试模式，请手动输入以上代码到```config.ini```中，开启后可在抓取中显示影片元数据

---
### 3.(可选)设置自定义目录和影片重命名规则
>[Name_Rule]<br>
>location_rule=actor+'/'+number<br>
>naming_rule=number+'-'+title<br>

已有默认配置

---
#### 命名参数
>title = 片名<br>
>actor = 演员<br>
>studio = 公司<br>
>director = 导演<br>
>release = 发售日<br>
>year = 发行年份<br>
>number = 番号<br>
>cover = 封面链接<br>
>tag = 类型<br>
>outline = 简介<br>
>runtime = 时长<br>

上面的参数以下都称之为**变量**

#### 例子：
自定义规则方法：有两种元素，变量和字符，无论是任何一种元素之间连接必须要用加号 **+** ，比如：```'naming_rule=['+number+']-'+title```，其中冒号 ' ' 内的文字是字符，没有冒号包含的文字是变量，元素之间连接必须要用加号 **+** <br>
目录结构规则：默认 ```location_rule=actor+'/'+number```<br> **不推荐修改时在这里添加title**，有时title过长，因为Windows API问题，抓取数据时新建文件夹容易出错。<br>
影片命名规则：默认 ```naming_rule=number+'-'+title```<br> **在EMBY,KODI等本地媒体库显示的标题，不影响目录结构下影片文件的命名**，依旧是 番号+后缀。

---

### 更新开关
>[update]<br>update_check=1<br>

1为开，0为关

## 4.多目录影片处理
可以在多个有影片目录的父目录下搜索影片后缀，然后剪切到和程序同一目录下  

## 多集影片处理
可以把多集电影按照集数后缀命名为类似```ssni-xxx-cd1.mp4m,ssni-xxx-cd2.mp4，abp-xxx-CD1.mp4```的规则，只要含有```-CDn./-cdn.```类似命名规则，即可使用分集功能

## 5.运行 ```AV_Data_capture.py/.exe```
当文件名包含:<br>
中文，字幕，-c., -C., 处理元数据时会加上**中文字幕**标签
## 5.1 异常处理（重要）
### 请确保软件是完整地！确保ini文件内容是和下载提供ini文件内容的一致的！
---
### 关于软件打开就闪退
可以打开cmd命令提示符，把 ```AV_Data_capture.py/.exe```拖进cmd窗口回车运行，查看错误，出现的错误信息**依据以下条目解决**

---
### 关于 ```Updata_check``` 和 ```JSON``` 相关的错误
跳转 [网络设置](#网络设置)

---
### 关于```FileNotFoundError: [WinError 3] 系统找不到指定的路径。: 'JAV_output''``` 
在软件所在文件夹下新建 JAV_output 文件夹，可能是你没有把软件拉到和电影的同一目录

---
### 关于连接拒绝的错误
请设置好[代理](#针对某些地区的代理设置)<br>

---
### 关于Nonetype,xpath报错
同上<br>

---
### 关于番号提取失败或者异常
**目前可以提取元素的影片:JAVBUS上有元数据的电影，素人系列:300Maan,259luxu,siro等,FC2系列**<br>
>下一张图片来自Pockies的blog 原作者已授权<br>

![](https://raw.githubusercontent.com/Pockies/pic/master/741f9461gy1g1cxc31t41j20i804zdgo.jpg)

目前作者已经完善了番号提取机制，功能较为强大，可提取上述文件名的的番号，如果出现提取失败或者异常的情况，请用以下规则命名<br>
**妈蛋不要喂软件那么多野鸡片子，不让软件好好活了，操**
```
COSQ-004.mp4
```

针对 **野鸡番号** ，你需要把文件名命名为与抓取网站提供的番号一致（文件拓展名除外），然后把文件拖拽至core.exe/.py<br>
**野鸡番号**:比如 ```XXX-XXX-1```,  ```1301XX-MINA_YUKA``` 这种**野鸡**番号，在javbus等资料库存在的作品。<br>**重要**：除了 **影片文件名**  ```XXXX-XXX-C```，后面这种-C的是指电影有中文字幕！<br>
条件：文件名中间要有下划线或者减号"_","-"，没有多余的内容只有番号为最佳，可以让软件更好获取元数据
对于多影片重命名，可以用[ReNamer](http://www.den4b.com/products/renamer)来批量重命名<br>

---
### 关于PIL/image.py
暂时无解，可能是网络问题或者pillow模块打包问题，你可以用源码运行（要安装好第一步的模块）


## 6.软件会自动把元数据获取成功的电影移动到JAV_output文件夹中，根据演员分类，失败的电影移动到failed文件夹中。
## 7.把JAV_output文件夹导入到EMBY,KODI中，等待元数据刷新，完成
## 8.关于群晖NAS
开启SMB在Windows上挂载为网络磁盘即可使用本软件，也适用于其他NAS
## 9.写在后面
怎么样，看着自己的日本电影被这样完美地管理，是不是感觉成就感爆棚呢?<br>
**tg官方电报群:[ 点击进群](https://t.me/joinchat/J54y1g3-a7nxJ_-WS4-KFQ)**<br>


