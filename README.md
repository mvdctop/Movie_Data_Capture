# AV Data Capture (CLI)

CLI 版本  
<a title="Hits" target="_blank" href="https://github.com/yoshiko2/AV_Data_Capture"><img src="https://hits.b3log.org/yoshiko2/AV_Data_Capture.svg"></a>
![](https://img.shields.io/badge/build-passing-brightgreen.svg?style=flat-square)
![](https://img.shields.io/github/downloads/yoshiko2/av_data_capture/total.svg?style=flat-square)
![](https://img.shields.io/github/license/yoshiko2/av_data_capture.svg?style=flat-square)
![](https://img.shields.io/github/release/yoshiko2/av_data_capture.svg?style=flat-square)
![](https://img.shields.io/badge/Python-3.7-yellow.svg?style=flat-square&logo=python)<br>
[GUI 版本](https://github.com/moyy996/AVDC)  
<a title="Hits" target="_blank" href="https://github.com/moyy996/avdc"><img src="https://hits.b3log.org/moyy996/AVDC.svg"></a>
![](https://img.shields.io/badge/build-passing-brightgreen.svg?style=flat-square)
![](https://img.shields.io/github/downloads/moyy996/avdc/total.svg?style=flat-square)
![](https://img.shields.io/github/license/moyy996/avdc.svg?style=flat-square)
![](https://img.shields.io/github/release/moyy996/avdc.svg?style=flat-square)
![](https://img.shields.io/badge/Python-3.6-yellow.svg?style=flat-square&logo=python)
![](https://img.shields.io/badge/Pyqt-5-blue.svg?style=flat-square)<br>


**日本电影元数据 抓取工具 | 刮削器**，配合本地影片管理软件 Emby, Jellyfin, Kodi 等管理本地影片，该软件起到分类与元数据（metadata）抓取作用，利用元数据信息来分类，供本地影片分类整理使用。  
##### 本地电影刮削与整理一体化解决方案

# 目录
* [声明](#声明)
* [FAQ](#FAQ)
* [故事](#故事)
* [效果图](#效果图)
* [如何使用](#如何使用)
    * [下载](#下载)
    * [简要教程](#简要教程)
* [完整文档](#完整文档)
    * [模块安装](#模块安装)
    * [配置](#配置configini)
    * [多目录影片处理](#多目录影片处理)
    * [多集影片处理](#多集影片处理)
    * [中文字幕处理](#中文字幕处理)
    * [异常处理（重要）](#异常处理重要)
* [写在后面](#写在后面)

# 声明
* 本软件仅供**技术交流，学术交流**使用
* 本软件作者编写出该软件旨在学习 Python ，提高编程水平
* 用户在使用本软件前，请用户自觉遵守当地法律法规，如果本软件使用过程中存在违反当地法律法规的行为，请勿使用该软件
* 用户在使用本软件时，若产生一切违法行为由用户承担
* 严禁用户将本软件使用于商业和个人其他意图
* 本软件作者保留最终决定权和最终解释权

**若用户不同意上述条款任意一条，请勿使用本软件**

# FAQ
### 软件能下片吗？
* 本软件不提供任何影片下载地址，仅供本地影片分类整理使用
### 什么是元数据（metadata）？
* 元数据包括了影片的封面，导演，演员，简介，类型......
### 软件收费吗？
* 本软件永久免费，**除了作者<ruby>钦<rt>yìng</rt></ruby>点以外**
### 软件运行异常怎么办？
* 认真看 [异常处理（重要）](#异常处理重要)
### 为什么软件要单线程运行？
* 多线程爬取可能会触发网站反爬机制，同时也违背了些道德，故单线程运行

# 效果图
**图片来自网络**，图片仅供参考，具体效果请自行联想
![preview_picture_1](https://i.loli.net/2019/07/04/5d1cf9bb1b08b86592.jpg)
![preview_picture_2](https://i.loli.net/2019/07/04/5d1cf9bb2696937880.jpg)

# 如何使用
## 下载
* release的程序可脱离**python环境**运行，可跳过 [模块安装](#模块安装)
### Windows
Release 下载地址(**仅限Windows**):

[![](https://img.shields.io/badge/%E4%B8%8B%E8%BD%BD-windows-blue.svg?style=for-the-badge&logo=windows)](https://github.com/yoshiko2/AV_Data_Capture/releases)

* 若 Windows 用户需要运行源代码版本，请安装 Windows Python 环境:[点击前往](https://www.python.org/downloads/windows/) 选中 executable installer 下载

### MacOS, Linux
* MacOS, Linux 用户请下载源码包运行
* MacOS Python环境：开箱即用，[可选安装最新版本](https://docs.brew.sh/Homebrew-and-Python)
* Linux Python环境：开箱即用，可选安装最新版本，恕 Linux 版本众多请自行搜索

## 简要教程:
1. 把软件拉到和电影的同一目录
2. 设置 config.ini 文件的代理（路由器拥有自动代理功能的可以把 proxy= 后面内容去掉）
3. 运行软件等待完成
4. 把 JAV_output 导入至 Kodi, Emby, Jellyfin 中。

详细请看以下完整文档

# 完整文档

## 模块安装
如果运行**源码**版，运行前请安装**Python环境**和安装以下**模块**  

在终端 cmd/Powershell/Terminal 中输入以下代码来安装模块

```python
pip install requests pyquery lxml Beautifulsoup4 pillow
```

## 配置config.ini
### 运行模式
```
[common]
main_mode=1
```
1为普通模式，  
2为整理模式：仅根据女优把电影命名为番号并分类到女优名称的文件夹下

```
success_output_folder=JAV_outputd
failed_output_folder=failed
```
设置成功输出目录和失败输出目录

---
#### 软链接
方便PT下载完既想刮削又想继续上传的仓鼠党同志
```
[common]
soft_link=0
```
1为开启软链接模式  
0为关闭

---
### 网络设置
```
[proxy]  
proxy=127.0.0.1:1081  
timeout=10  
retry=3
```  
#### 针对某些地区的代理设置
```
proxy=127.0.0.1:1081  
```

打开```config.ini```,在```[proxy]```下的```proxy```行设置本地代理地址和端口，支持Shadowxxxx/X,V2XXX本地代理端口  
素人系列抓取建议使用日本代理  
**路由器拥有自动代理功能的可以把proxy=后面内容去掉**  
**本地代理软件开全局模式的用户同上**  
**如果遇到tineout错误，可以把文件的proxy=后面的地址和端口删除，并开启代理软件全局模式，或者重启电脑，代理软件，网卡**  

---
#### 连接超时重试设置
```
timeout=10  
```
10为超时重试时间 单位：秒

---
#### 连接重试次数设置
```
retry=3  
```
3即为重试次数

---
#### 检查更新开关
```
[update]  
update_check=1  
```
0为关闭，1为开启，不建议关闭

---
### 媒体库选择 
```
[media]
media_warehouse=emby
#emby plex kodi
```
可选择emby, plex, kodi
如果是PLEX，请安装插件：```XBMCnfoMoviesImporter```

---
### 排除指定字符和目录
```
[escape]  
literals=\  
folders=failed,JAV_output
```

```literals=``` 标题指定字符删除，例如```iterals=\()```，则删除标题中```\()```字符  
```folders=``` 指定目录，例如```folders=failed,JAV_output```，多目录刮削时跳过failed,JAV_output  

---
### 调试模式
```
[debug_mode]
switch=1  
```

如要开启调试模式，请手动输入以上代码到```config.ini```中，开启后可在抓取中显示影片元数据

---
### (可选)设置自定义目录和影片重命名规则
```
[Name_Rule]
location_rule=actor+'/'+number
naming_rule=number+'-'+title
```
已有默认配置

---
#### 命名参数
```
title = 片名
actor = 演员
studio = 公司
director = 导演
release = 发售日
year = 发行年份
number = 番号
cover = 封面链接
tag = 类型
outline = 简介
runtime = 时长
```

上面的参数以下都称之为**变量**

#### 例子：
自定义规则方法：有两种元素，变量和字符，无论是任何一种元素之间连接必须要用加号 **+** ，比如：```'naming_rule=['+number+']-'+title```，其中冒号 ' ' 内的文字是字符，没有冒号包含的文字是变量，元素之间连接必须要用加号 **+** 

目录结构规则：默认 ```location_rule=actor+'/'+number```

**不推荐修改时在这里添加 title**，有时 title 过长，因为 Windows API 问题，抓取数据时新建文件夹容易出错。

影片命名规则：默认 ```naming_rule=number+'-'+title```

**在 Emby, Kodi等本地媒体库显示的标题，不影响目录结构下影片文件的命名**，依旧是 番号+后缀。

---

### 更新开关
```
[update]
update_check=1
```

1为开，0为关

## 多目录影片处理
可以在多个有影片目录的父目录下搜索影片后缀，然后剪切到和程序同一目录下  

## 多集影片处理
**建议使用视频合并合并为一个视频文件**
可以把多集电影按照集数后缀命名为类似```ssni-xxx-cd1.mp4m,ssni-xxx-cd2.mp4，abp-xxx-CD1.mp4```的规则，只要含有```-CDn./-cdn.```类似命名规则，即可使用分集功能

## 中文字幕处理

运行 ```AV_Data_capture.py/.exe```

当文件名包含:
中文，字幕，-c., -C., 处理元数据时会加上**中文字幕**标签

## 异常处理（重要）

### 请确保软件是完整地！确保ini文件内容是和下载提供ini文件内容的一致的！
---
### 关于软件打开就闪退
可以打开cmd命令提示符，把 ```AV_Data_capture.py/.exe```拖进cmd窗口回车运行，查看错误，出现的错误信息**依据以下条目解决**

---
### 关于 ```Updata_check``` 和 ```JSON``` 相关的错误
跳转 [网络设置](#网络设置)

---
### 关于字幕文件移动功能
字幕文件前缀必须与影片文件前缀一致，才可以使用该功能

---
### 关于```FileNotFoundError: [WinError 3] 系统找不到指定的路径。: 'JAV_output''``` 
在软件所在文件夹下新建 JAV_output 文件夹，可能是你没有把软件拉到和电影的同一目录

---
### 关于连接拒绝的错误
请设置好[代理](#针对某些地区的代理设置)

---
### 关于Nonetype,xpath报错
同上

---
### 关于番号提取失败或者异常
**目前可以提取元素的影片:JAVBUS上有元数据的电影，素人系列:300Maan,259luxu,siro等,FC2系列**

>下一张图片来自 Pockies 的 blog 原作者已授权

![](https://raw.githubusercontent.com/Pockies/pic/master/741f9461gy1g1cxc31t41j20i804zdgo.jpg)

目前作者已经完善了番号提取机制，功能较为强大，可提取上述文件名的的番号，如果出现提取失败或者异常的情况，请用以下规则命名


```
COSQ-004.mp4
```

条件：文件名中间要有下划线或者减号"_","-"，没有多余的内容只有番号为最佳，可以让软件更好获取元数据
对于多影片重命名，可以用 [ReNamer](http://www.den4b.com/products/renamer) 来批量重命名


---
### 关于PIL/image.py
暂时无解，可能是网络问题或者pillow模块打包问题，你可以用源码运行（要安装好第一步的模块）  

### 拖动法
针对格式比较奇葩的番号  
影片放在和程序同一目录下，拖动至```AV_Data_Capture.exe```，即可完成刮削和整理


### 软件会自动把元数据获取成功的电影移动到 JAV_output 文件夹中，根据演员分类，失败的电影移动到failed文件夹中。

### 把JAV_output文件夹导入到 Emby, Kodi中，等待元数据刷新，完成

### 关于群晖NAS
开启 SMB，并在 Windows 上挂载为网络磁盘即可使用本软件，也适用于其他 NAS

## 写在后面
怎么样，看着自己的日本电影被这样完美地管理，是不是感觉成就感爆棚呢?

**tg官方电报群:[ 点击进群](https://t.me/joinchat/J54y1g3-a7nxJ_-WS4-KFQ)**


