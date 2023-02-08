## Bug修正

主.py的参数名common:stop_counter错

```python
略
  set_natural_number_or_none("advenced_sleep:stop_counter", args.cnt)
略
 conf.set_override("advenced_sleep:stop_counter=0;rerun_delay=0s;face:aways_imagecut=1")
```

core.py最后print_files函数参数错误

```python
        print_files(path, leak_word, c_word, json_data.get('naming_rule'), part, cn_sub, json_data, movie_path,
                    tag, json_data.get('actor_list'), liuchu, uncensored, hack, hack_word, _4k, fanart_path, poster_path,
                    thumb_path)
```



## 增加命名规则：_P分集

core.py修改

```python
    if re.search('[-_]CD\d+', movie_path, re.IGNORECASE):
        part = re.findall('[-_]CD\d+', movie_path, re.IGNORECASE)[0].upper()
        multi = True
    if re.search('[-_]P\d+', movie_path, re.IGNORECASE):
        multi = True
        part = re.findall('[-_]P\d+', movie_path, re.IGNORECASE)[0].upper()
略
    if re.search('[-_]CD\d+', movie_path, re.IGNORECASE):
        multi_part = True
        part = re.findall('[-_]CD\d+', movie_path, re.IGNORECASE)[0].upper()
    if re.search('[-_]P\d+', movie_path, re.IGNORECASE):
        multi_part = True
        part = re.findall('[-_]P\d+', movie_path, re.IGNORECASE)[0].upper()
```



## 在cloud drive挂载的网络盘下，创建的nfo元数据没有被存储。

怀疑是不能对文件文本编辑。

改为在程序目录nfo文件夹下编辑好文件nfo_path_edit后，移动到指定路径nfo_path。

core.py修改

```python
def print_files(path, leak_word, c_word, naming_rule, part, cn_sub, json_data, filepath, tag, actor_list, liuchu,
                uncensored, hack_word, _4k, fanart_path, poster_path, thumb_path):
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(
        json_data)
略
    try:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print(f"[-]Fatal error! can not make folder '{path}'")
                os._exit(0)
        nfo_path_edit = os.path.join("./nfo", f"{number}{part}{leak_word}{c_word}{hack_word}.nfo")
        # 用于保留旧nfo评分信息
        old_nfo = None
略
        with open(nfo_path_edit, "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
略
            print("  <website>" + website + "</website>", file=code)
            print("</movie>", file=code)
            code.close()
            print("[+]Wrote!            " + nfo_path_edit)
            shutil.move(nfo_path_edit,nfo_path)
            print("[+]Moved!            " + nfo_path)
    except IOError as e:
略
```

# 新模式3增加判断字幕（srt或-c）,更新现有nfo标签和图片标签

模式3的无网络模式改成不更新图模式：原来是根据文件名（中文字幕后缀、流出后缀、破解后缀）和nfo更新图片水印。改为也更新nfo，但导致联网了，影响了参数-N --no-network-operation。除非不用get_data_from_json，直接写参数 json_data.get('naming_rule'), tag, json_data.get('actor_list')

create_data_and_move_with_custom_number时是用的core_main里的main mode 3，有下载图片

主.py修改

```python
def create_data_and_move(movie_path: str, zero_op: bool, no_net_op: bool, oCC):
略
            if no_net_op:
                core_main_no_net_op(movie_path, n_number, oCC)
略
                if no_net_op:
                    core_main_no_net_op(movie_path, n_number, oCC)
略            
```

core.py修改

```python
def core_main_no_net_op(movie_path, number_th, oCC, specified_source=None, specified_url=None):
略
	liuchu = False
    json_data = get_data_from_json(number, oCC, specified_source, specified_url)  # 定义番号
    # Return if blank dict returned (data not found)
    if not json_data:
        moveFailedFolder(movie_path)
        return
    tag = json_data.get('tag')    
略
        liuchu = True
    if 'hack'.upper() in str(movie_path).upper() or '破解' in movie_path:
        hack = True
        hack_word = "-hack"
    # 判断字幕文件
    # 原逻辑是对文件名加-C，这里逻辑要重写，加字幕检测，改写nfo
    move_status = move_subtitles(movie_path, path, multi_part, number, part, leak_word, c_word, hack_word)
    if move_status:
        cn_sub = True
        
    # try:
    #     props = get_video_properties(movie_path)  # 判断是否为4K视频
略
    # 最后输出.nfo元数据文件，以完成.nfo文件创建作为任务成功标志
    print_files(path, leak_word, c_word, json_data.get('naming_rule'), part, cn_sub, json_data, movie_path, tag,
                json_data.get('actor_list'), liuchu, uncensored, hack, hack_word
                , _4k, fanart_path, poster_path, thumb_path)
略

def core_main(movie_path, number_th, oCC, specified_source=None, specified_url=None):
略
    elif conf.main_mode() == 3:
        path = str(Path(movie_path).parent)
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀
        #判断subtitle文件
        move_status = move_subtitles(movie_path, path, multi_part, number, part, leak_word, c_word, hack_word)
        if move_status:
            cn_sub = True
略         
```

