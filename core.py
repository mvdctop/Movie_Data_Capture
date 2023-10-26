import os.path
import pathlib
import shutil
import sys

from PIL import Image
from io import BytesIO
from datetime import datetime
# from videoprops import get_video_properties

from ADC_function import *
from scraper import get_data_from_json
from number_parser import is_uncensored
from ImageProcessing import cutImage


# from WebCrawler import get_data_from_json

def escape_path(path, escape_literals: str):  # Remove escape literals
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def moveFailedFolder(filepath):
    conf = config.getInstance()
    failed_folder = conf.failed_folder()
    link_mode = conf.link_mode()
    # 模式3或软连接，改为维护一个失败列表，启动扫描时加载用于排除该路径，以免反复处理
    # 原先的创建软连接到失败目录，并不直观，不方便找到失败文件位置，不如直接记录该文件路径
    if conf.main_mode() == 3 or link_mode:
        ftxt = os.path.abspath(os.path.join(failed_folder, 'failed_list.txt'))
        print("[-]Add to Failed List file, see '%s'" % ftxt)
        with open(ftxt, 'a', encoding='utf-8') as flt:
            flt.write(f'{filepath}\n')
    elif conf.failed_move() and not link_mode:
        failed_name = os.path.join(failed_folder, os.path.basename(filepath))
        mtxt = os.path.abspath(os.path.join(failed_folder, 'where_was_i_before_being_moved.txt'))
        print("'[-]Move to Failed output folder, see '%s'" % mtxt)
        with open(mtxt, 'a', encoding='utf-8') as wwibbmt:
            tmstr = datetime.now().strftime("%Y-%m-%d %H:%M")
            wwibbmt.write(f'{tmstr} FROM[{filepath}]TO[{failed_name}]\n')
        try:
            if os.path.exists(failed_name):
                print('[-]File Exists while moving to FailedFolder')
                return
            shutil.move(filepath, failed_name)
        except:
            print('[-]File Moving to FailedFolder unsuccessful!')


def get_info(json_data):  # 返回json里的数据
    title = json_data.get('title')
    studio = json_data.get('studio')
    year = json_data.get('year')
    outline = json_data.get('outline')
    runtime = json_data.get('runtime')
    director = json_data.get('director')
    actor_photo = json_data.get('actor_photo', {})
    release = json_data.get('release')
    number = json_data.get('number')
    cover = json_data.get('cover')
    trailer = json_data.get('trailer')
    website = json_data.get('website')
    series = json_data.get('series')
    label = json_data.get('label', "")
    return title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label


def small_cover_check(path, filename, cover_small, movie_path, json_headers=None):
    full_filepath = Path(path) / filename
    if config.getInstance().download_only_missing_images() and not file_not_exist_or_empty(str(full_filepath)):
        return
    if json_headers != None:
        download_file_with_filename(cover_small, filename, path, movie_path, json_headers['headers'])
    else:
        download_file_with_filename(cover_small, filename, path, movie_path)
    print('[+]Image Downloaded! ' + full_filepath.name)


def create_folder(json_data):  # 创建文件夹
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(
        json_data)
    conf = config.getInstance()
    success_folder = conf.success_folder()
    actor = json_data.get('actor')
    location_rule = eval(conf.location_rule(), json_data)
    if 'actor' in conf.location_rule() and len(actor) > 100:
        print(conf.location_rule())
        location_rule = eval(conf.location_rule().replace("actor", "'多人作品'"), json_data)
    maxlen = conf.max_title_len()
    if 'title' in conf.location_rule() and len(title) > maxlen:
        shorttitle = title[0:maxlen]
        location_rule = location_rule.replace(title, shorttitle)
    # 当演员为空时，location_rule被计算为'/number'绝对路径，导致路径连接忽略第一个路径参数，因此添加./使其始终为相对路径
    path = os.path.join(success_folder, f'./{location_rule.strip()}')
    if not os.path.exists(path):
        path = escape_path(path, conf.escape_literals())
        try:
            os.makedirs(path)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + ')-' + title, "/number")
            path = escape_path(path, conf.escape_literals())
            try:
                os.makedirs(path)
            except:
                print(f"[-]Fatal error! Can not make folder '{path}'")
                os._exit(0)

    return os.path.normpath(path)


# =====================资源下载部分===========================

# path = examle:photo , video.in the Project Folder!
def download_file_with_filename(url, filename, path, filepath, json_headers=None):
    conf = config.getInstance()
    configProxy = conf.proxy()

    for i in range(configProxy.retry):
        try:
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except:
                    print(f"[-]Fatal error! Can not make folder '{path}'")
                    os._exit(0)
            r = get_html(url=url, return_type='content', json_headers=json_headers)
            if r == '':
                print('[-]Movie Download Data not found!')
                return
            with open(os.path.join(path, filename), "wb") as code:
                code.write(r)
            return
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Image Download : Proxy error ' + str(i) + '/' + str(configProxy.retry))
        # except IOError:
        #     print(f"[-]Create Directory '{path}' failed!")
        #     moveFailedFolder(filepath)
        #     return
        except Exception as e:
            print('[-]Image Download :Error', e)
    print('[-]Connect Failed! Please check your Proxy or Network!')
    moveFailedFolder(filepath)
    return


def trailer_download(trailer, leak_word, c_word, hack_word, number, path, filepath):
    if download_file_with_filename(trailer, number + leak_word + c_word + hack_word + '-trailer.mp4', path,
                                   filepath) == 'failed':
        return
    configProxy = config.getInstance().proxy()
    for i in range(configProxy.retry):
        if file_not_exist_or_empty(path + '/' + number + leak_word + c_word + hack_word + '-trailer.mp4'):
            print('[!]Video Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(trailer, number + leak_word + c_word + hack_word + '-trailer.mp4', path,
                                        filepath)
            continue
        else:
            break
    if file_not_exist_or_empty(path + '/' + number + leak_word + c_word + hack_word + '-trailer.mp4'):
        return
    print('[+]Video Downloaded!', path + '/' + number + leak_word + c_word + hack_word + '-trailer.mp4')


def actor_photo_download(actors, save_dir, number):
    if not isinstance(actors, dict) or not len(actors) or not len(save_dir):
        return
    save_dir = Path(save_dir)
    if not save_dir.is_dir():
        return
    conf = config.getInstance()
    actors_dir = save_dir / '.actors'
    download_only_missing_images = conf.download_only_missing_images()
    dn_list = []
    for actor_name, url in actors.items():
        res = re.match(r'^http.*(\.\w+)$', url, re.A)
        if not res:
            continue
        ext = res.group(1)
        pic_fullpath = actors_dir / f'{actor_name}{ext}'
        if download_only_missing_images and not file_not_exist_or_empty(pic_fullpath):
            continue
        dn_list.append((url, pic_fullpath))
    if not len(dn_list):
        return
    parallel = min(len(dn_list), conf.extrafanart_thread_pool_download())
    if parallel > 100:
        print('[!]Warrning: Parallel download thread too large may cause website ban IP!')
    result = parallel_download_files(dn_list, parallel)
    failed = 0
    for i, r in enumerate(result):
        if not r:
            failed += 1
            print(f"[-]Actor photo '{dn_list[i][0]}' to '{dn_list[i][1]}' download failed!")
    if failed:  # 非致命错误，电影不移入失败文件夹，将来可以用模式3补齐
        print(
            f"[-]Failed downloaded {failed}/{len(result)} actor photo for [{number}] to '{actors_dir}', you may retry run mode 3 later.")
    else:
        print(f"[+]Successfully downloaded {len(result)} actor photo.")


# 剧照下载成功，否则移动到failed
def extrafanart_download(data, path, number, filepath, json_data=None):
    if config.getInstance().extrafanart_thread_pool_download():
        return extrafanart_download_threadpool(data, path, number, json_data)
    extrafanart_download_one_by_one(data, path, filepath, json_data)


def extrafanart_download_one_by_one(data, path, filepath, json_data=None):
    tm_start = time.perf_counter()
    j = 1
    conf = config.getInstance()
    path = os.path.join(path, conf.get_extrafanart())
    configProxy = conf.proxy()
    download_only_missing_images = conf.download_only_missing_images()
    for url in data:
        jpg_filename = f'extrafanart-{j}.jpg'
        jpg_fullpath = os.path.join(path, jpg_filename)
        if download_only_missing_images and not file_not_exist_or_empty(jpg_fullpath):
            continue
        if download_file_with_filename(url, jpg_filename, path, filepath, json_data) == 'failed':
            moveFailedFolder(filepath)
            return
        for i in range(configProxy.retry):
            if file_not_exist_or_empty(jpg_fullpath):
                print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
                download_file_with_filename(url, jpg_filename, path, filepath, json_data)
                continue
            else:
                break
        if file_not_exist_or_empty(jpg_fullpath):
            return
        print('[+]Image Downloaded!', Path(jpg_fullpath).name)
        j += 1
    if conf.debug():
        print(f'[!]Extrafanart download one by one mode runtime {time.perf_counter() - tm_start:.3f}s')


def extrafanart_download_threadpool(url_list, save_dir, number, json_data=None):
    tm_start = time.perf_counter()
    conf = config.getInstance()
    extrafanart_dir = Path(save_dir) / conf.get_extrafanart()
    download_only_missing_images = conf.download_only_missing_images()
    dn_list = []
    for i, url in enumerate(url_list, start=1):
        jpg_fullpath = extrafanart_dir / f'extrafanart-{i}.jpg'
        if download_only_missing_images and not file_not_exist_or_empty(jpg_fullpath):
            continue
        dn_list.append((url, jpg_fullpath))
    if not len(dn_list):
        return
    parallel = min(len(dn_list), conf.extrafanart_thread_pool_download())
    if parallel > 100:
        print('[!]Warrning: Parallel download thread too large may cause website ban IP!')
    result = parallel_download_files(dn_list, parallel, json_data)
    failed = 0
    for i, r in enumerate(result, start=1):
        if not r:
            failed += 1
            print(f'[-]Extrafanart {i} for [{number}] download failed!')
    if failed:  # 非致命错误，电影不移入失败文件夹，将来可以用模式3补齐
        print(
            f"[-]Failed downloaded {failed}/{len(result)} extrafanart images for [{number}] to '{extrafanart_dir}', you may retry run mode 3 later.")
    else:
        print(f"[+]Successfully downloaded {len(result)} extrafanarts.")
    if conf.debug():
        print(f'[!]Extrafanart download ThreadPool mode runtime {time.perf_counter() - tm_start:.3f}s')


def image_ext(url):
    try:
        ext = os.path.splitext(url)[-1]
        if ext in {'.jpg', '.jpge', '.bmp', '.png', '.gif'}:
            return ext
        return ".jpg"
    except:
        return ".jpg"


# 封面是否下载成功，否则移动到failed
def image_download(cover, fanart_path, thumb_path, path, filepath, json_headers=None):
    full_filepath = os.path.join(path, thumb_path)
    if config.getInstance().download_only_missing_images() and not file_not_exist_or_empty(full_filepath):
        return
    if json_headers != None:
        if download_file_with_filename(cover, thumb_path, path, filepath, json_headers['headers']) == 'failed':
            moveFailedFolder(filepath)
            return
    else:
        if download_file_with_filename(cover, thumb_path, path, filepath) == 'failed':
            moveFailedFolder(filepath)
            return

    configProxy = config.getInstance().proxy()
    for i in range(configProxy.retry):
        if file_not_exist_or_empty(full_filepath):
            print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
            if json_headers != None:
                download_file_with_filename(cover, thumb_path, path, filepath, json_headers['headers'])
            else:
                download_file_with_filename(cover, thumb_path, path, filepath)
            continue
        else:
            break
    if file_not_exist_or_empty(full_filepath):
        return
    print('[+]Image Downloaded!', Path(full_filepath).name)
    if not config.getInstance().jellyfin():
        shutil.copyfile(full_filepath, os.path.join(path, fanart_path))


def print_files(path, leak_word, c_word, naming_rule, part, cn_sub, json_data, filepath, tag, actor_list, liuchu,
                uncensored, hack, hack_word, _4k, fanart_path, poster_path, thumb_path, iso):
    
    conf = config.getInstance()
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(
        json_data)
    if config.getInstance().main_mode() == 3:  # 模式3下，由于视频文件不做任何改变，.nfo文件必须和视频文件名称除后缀外完全一致，KODI等软件方可支持
        nfo_path = str(Path(filepath).with_suffix('.nfo'))
    else:
        nfo_path = os.path.join(path, f"{number}{part}{leak_word}{c_word}{hack_word}.nfo")
    try:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                print(f"[-]Fatal error! can not make folder '{path}'")
                os._exit(0)

        old_nfo = None
        try:
            if os.path.isfile(nfo_path):
                old_nfo = etree.parse(nfo_path)
        except:
            pass
        # KODI内查看影片信息时找不到number，配置naming_rule=number+'#'+title虽可解决
        # 但使得标题太长，放入时常为空的outline内会更适合，软件给outline留出的显示版面也较大
        if not outline:
            pass
        elif json_data['source'] == 'pissplay':
            outline = f"{outline}"
        else:
            outline = f"{number}#{outline}"
        with open(nfo_path, "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
            print("<movie>", file=code)
            if not config.getInstance().jellyfin():
                print("  <title><![CDATA[" + naming_rule + "]]></title>", file=code)
                print("  <originaltitle><![CDATA[" + json_data['original_naming_rule'] + "]]></originaltitle>",
                      file=code)
                print("  <sorttitle><![CDATA[" + naming_rule + "]]></sorttitle>", file=code)
            else:
                print("  <title>" + naming_rule + "</title>", file=code)
                print("  <originaltitle>" + json_data['original_naming_rule'] + "</originaltitle>", file=code)
                print("  <sorttitle>" + naming_rule + "</sorttitle>", file=code)
            print("  <customrating>JP-18+</customrating>", file=code)
            print("  <mpaa>JP-18+</mpaa>", file=code)
            try:
                print("  <set>" + series + "</set>", file=code)
            except:
                print("  <set></set>", file=code)
            print("  <studio>" + studio + "</studio>", file=code)
            print("  <year>" + year + "</year>", file=code)
            if not config.getInstance().jellyfin():
                print("  <outline><![CDATA[" + outline + "]]></outline>", file=code)
                print("  <plot><![CDATA[" + outline + "]]></plot>", file=code)
            else:
                print("  <outline>" + outline + "</outline>", file=code)
                print("  <plot>" + outline + "</plot>", file=code)
            print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
            
            if False != conf.get_direct(): 
                print("  <director>" + director + "</director>", file=code)
                
            print("  <poster>" + poster_path + "</poster>", file=code)
            print("  <thumb>" + thumb_path + "</thumb>", file=code)
            if not config.getInstance().jellyfin():  # jellyfin 不需要保存fanart
                print("  <fanart>" + fanart_path + "</fanart>", file=code)
            try:
                for key in actor_list:
                    print("  <actor>", file=code)
                    print("    <name>" + key + "</name>", file=code)
                    try:
                        print("    <thumb>" + actor_photo.get(str(key)) + "</thumb>", file=code)
                    except:
                        pass
                    print("  </actor>", file=code)
            except:
                pass
            print("  <maker>" + studio + "</maker>", file=code)
            print("  <label>" + label + "</label>", file=code)

            jellyfin = config.getInstance().jellyfin()
            if not jellyfin:
                if config.getInstance().actor_only_tag():
                    for key in actor_list:
                        try:
                            print("  <tag>" + key + "</tag>", file=code)
                        except:
                            pass
                else:
                    if cn_sub:
                        print("  <tag>中文字幕</tag>", file=code)
                    if liuchu:
                        print("  <tag>流出</tag>", file=code)
                    if uncensored:
                        print("  <tag>无码</tag>", file=code)
                    if hack:
                        print("  <tag>破解</tag>", file=code)
                    if _4k:
                        print("  <tag>4k</tag>", file=code)
                    if iso:
                        print("  <tag>原盘</tag>", file=code)
                    for i in tag:
                        print("  <tag>" + i + "</tag>", file=code)
            if cn_sub:
                print("  <genre>中文字幕</genre>", file=code)
            if liuchu:
                print("  <genre>无码流出</genre>", file=code)
            if uncensored:
                print("  <genre>无码</genre>", file=code)
            if hack:
                print("  <genre>破解</genre>", file=code)
            if _4k:
                print("  <genre>4k</genre>", file=code)
            try:
                for i in tag:
                    print("  <genre>" + i + "</genre>", file=code)
            except:
                pass
            print("  <num>" + number + "</num>", file=code)
            print("  <premiered>" + release + "</premiered>", file=code)
            print("  <releasedate>" + release + "</releasedate>", file=code)
            print("  <release>" + release + "</release>", file=code)
            if old_nfo:
                try:
                    xur = old_nfo.xpath('//userrating/text()')[0]
                    if isinstance(xur, str) and re.match('\d+\.\d+|\d+', xur.strip()):
                        print(f"  <userrating>{xur.strip()}</userrating>", file=code)
                except:
                    pass
            try:
                f_rating = json_data.get('userrating')
                uc = json_data.get('uservotes')
                print(f"""  <rating>{round(f_rating * 2.0, 1)}</rating>
  <criticrating>{round(f_rating * 20.0, 1)}</criticrating>
  <ratings>
    <rating name="javdb" max="5" default="true">
      <value>{f_rating}</value>
      <votes>{uc}</votes>
    </rating>
  </ratings>""", file=code)
            except:
                if old_nfo:
                    try:
                        for rtag in ('rating', 'criticrating'):
                            xur = old_nfo.xpath(f'//{rtag}/text()')[0]
                            if isinstance(xur, str) and re.match('\d+\.\d+|\d+', xur.strip()):
                                print(f"  <{rtag}>{xur.strip()}</{rtag}>", file=code)
                        f_rating = old_nfo.xpath(f"//ratings/rating[@name='javdb']/value/text()")[0]
                        uc = old_nfo.xpath(f"//ratings/rating[@name='javdb']/votes/text()")[0]
                        print(f"""  <ratings>
    <rating name="javdb" max="5" default="true">
      <value>{f_rating}</value>
      <votes>{uc}</votes>
    </rating>
  </ratings>""", file=code)
                    except:
                        pass
            print("  <cover>" + cover + "</cover>", file=code)
            if config.getInstance().is_trailer():
                print("  <trailer>" + trailer + "</trailer>", file=code)
            print("  <website>" + website + "</website>", file=code)
            print("</movie>", file=code)
            print("[+]Wrote!            " + nfo_path)
    except IOError as e:
        print("[-]Write Failed!")
        print("[-]", e)
        moveFailedFolder(filepath)
        return
    except Exception as e1:
        print("[-]Write Failed!")
        print("[-]", e1)
        moveFailedFolder(filepath)
        return


def add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, hack, _4k, iso) -> None:
    """
    add watermark on poster or thumb for describe extra properties 给海报和缩略图加属性水印

    :poster_path 海报位置
    :thumb_path 缩略图位置
    :cn_sub: 中文字幕 可选值：1,"1" 或其他值
    :uncensored 无码 可选值：1,"1" 或其他值
    :hack 破解 可选值：1,"1" 或其他值
    :_4k Bool
    """
    mark_type = ''
    if cn_sub:
        mark_type += ',字幕'
    if leak:
        mark_type += ',无码流出'
    if uncensored:
        mark_type += ',无码'
    if hack:
        mark_type += ',破解'
    if _4k:
        mark_type += ',4k'
    if iso:
        mark_type += ',iso'
    if mark_type == '':
        return
    add_mark_thread(thumb_path, cn_sub, leak, uncensored, hack, _4k, iso)
    add_mark_thread(poster_path, cn_sub, leak, uncensored, hack, _4k, iso)
    print('[+]Add Mark:         ' + mark_type.strip(','))


def add_mark_thread(pic_path, cn_sub, leak, uncensored, hack, _4k, iso):
    size = 9
    img_pic = Image.open(pic_path)
    # 获取自定义位置，取余配合pos达到顺时针添加的效果
    # 左上 0, 右上 1, 右下 2， 左下 3
    count = config.getInstance().watermark_type()
    if cn_sub:
        add_to_pic(pic_path, img_pic, size, count, 1)  # 添加
        count = (count + 1) % 4
    if leak:
        add_to_pic(pic_path, img_pic, size, count, 2)
        count = (count + 1) % 4
    if uncensored:
        add_to_pic(pic_path, img_pic, size, count, 3)
        count = (count + 1) % 4
    if hack:
        add_to_pic(pic_path, img_pic, size, count, 4)
        count = (count + 1) % 4
    if _4k:
        add_to_pic(pic_path, img_pic, size, count, 5)
        count = (count + 1) % 4
    if iso:
        add_to_pic(pic_path, img_pic, size, count, 6)
    img_pic.close()


def add_to_pic(pic_path, img_pic, size, count, mode):
    mark_pic_path = ''
    pngpath = ''
    if mode == 1:
        pngpath = "Img/SUB.png"
    elif mode == 2:
        pngpath = "Img/LEAK.png"
    elif mode == 3:
        pngpath = "Img/UNCENSORED.png"
    elif mode == 4:
        pngpath = "Img/HACK.png"
    elif mode == 5:
        pngpath = "Img/4K.png"
    elif mode == 6:
        pngpath = "Img/ISO.png"
    else:
        print('[-]Error: watermark image param mode invalid!')
        return
    # 先找pyinstaller打包的图片
    if hasattr(sys, '_MEIPASS') and os.path.isfile(os.path.join(getattr(sys, '_MEIPASS'), pngpath)):
        mark_pic_path = os.path.join(getattr(sys, '_MEIPASS'), pngpath)
    # 再找py脚本所在路径的图片
    elif os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), pngpath)):
        mark_pic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), pngpath)
    # 如果没有本地图片才通过网络下载
    else:
        mark_pic_path = BytesIO(
            get_html("https://raw.githubusercontent.com/yoshiko2/AV_Data_Capture/master/" + pngpath,
                     return_type="content"))
    img_subt = Image.open(mark_pic_path)
    scroll_high = int(img_pic.height / size)
    scroll_wide = int(scroll_high * img_subt.width / img_subt.height)
    img_subt = img_subt.resize((scroll_wide, scroll_high), Image.LANCZOS)
    r, g, b, a = img_subt.split()  # 获取颜色通道，保持png的透明性
    # 封面四个角的位置
    pos = [
        {'x': 0, 'y': 0},
        {'x': img_pic.width - scroll_wide, 'y': 0},
        {'x': img_pic.width - scroll_wide, 'y': img_pic.height - scroll_high},
        {'x': 0, 'y': img_pic.height - scroll_high},
    ]
    img_pic.paste(img_subt, (pos[count]['x'], pos[count]['y']), mask=a)
    img_pic.save(pic_path, quality=95)


# ========================结束=================================


def paste_file_to_folder(filepath, path, multi_part, number, part, leak_word, c_word, hack_word):  # 文件路径，番号，后缀，要移动至的位置
    filepath_obj = pathlib.Path(filepath)
    houzhui = filepath_obj.suffix
    try:
        targetpath = os.path.join(path, f"{number}{leak_word}{c_word}{hack_word}{houzhui}")
        # 任何情况下都不要覆盖，以免遭遇数据源或者引擎错误导致所有文件得到同一个number，逐一
        # 同名覆盖致使全部文件损失且不可追回的最坏情况
        if os.path.exists(targetpath):
            raise FileExistsError('File Exists on destination path, we will never overwriting.')
        link_mode = config.getInstance().link_mode()
        # 如果link_mode 1: 建立软链接 2: 硬链接优先、无法建立硬链接再尝试软链接。
        # 移除原先soft_link=2的功能代码，因默认记录日志，已经可追溯文件来源
        create_softlink = False
        if link_mode not in (1, 2):
            shutil.move(filepath, targetpath)
        elif link_mode == 2:
            # 跨卷或跨盘符无法建立硬链接导致异常，回落到建立软链接
            try:
                os.link(filepath, targetpath, follow_symlinks=False)
            except:
                create_softlink = True
        if link_mode == 1 or create_softlink:
            # 先尝试采用相对路径，以便网络访问时能正确打开视频，失败则可能是因为跨盘符等原因无法支持
            # 相对路径径，改用绝对路径方式尝试建立软链接
            try:
                filerelpath = os.path.relpath(filepath, path)
                os.symlink(filerelpath, targetpath)
            except:
                os.symlink(str(filepath_obj.resolve()), targetpath)
        return

    except FileExistsError as fee:
        print(f'[-]FileExistsError: {fee}')
        moveFailedFolder(filepath)
        return
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return
    except OSError as oserr:
        print(f'[-]OS Error errno {oserr.errno}')
        return


def paste_file_to_folder_mode2(filepath, path, multi_part, number, part, leak_word, c_word,
                               hack_word):  # 文件路径，番号，后缀，要移动至的位置
    if multi_part == 1:
        number += part  # 这时number会被附加上CD1后缀
    filepath_obj = pathlib.Path(filepath)
    houzhui = filepath_obj.suffix
    targetpath = os.path.join(path, f"{number}{part}{leak_word}{c_word}{hack_word}{houzhui}")
    if os.path.exists(targetpath):
        raise FileExistsError('File Exists on destination path, we will never overwriting.')
    try:
        link_mode = config.getInstance().link_mode()
        create_softlink = False
        if link_mode not in (1, 2):
            shutil.move(filepath, targetpath)
            print("[!]Move =>          ", path)
            return
        elif link_mode == 2:
            try:
                os.link(filepath, targetpath, follow_symlinks=False)
            except:
                create_softlink = True
        if link_mode == 1 or create_softlink:
            try:
                filerelpath = os.path.relpath(filepath, path)
                os.symlink(filerelpath, targetpath)
            except:
                os.symlink(str(filepath_obj.resolve()), targetpath)
        print("[!]Link =>          ", path)
    except FileExistsError as fee:
        print(f'[-]FileExistsError: {fee}')
    except PermissionError:
        print('[-]Error! Please run as administrator!')
    except OSError as oserr:
        print(f'[-]OS Error errno  {oserr.errno}')


def linkImage(path, number, part, leak_word, c_word, hack_word, ext):
    """
    首先尝试为图片建立符合Jellyfin封面图文件名规则的硬连接以节省磁盘空间
    如果目标目录无法建立硬链接则将图片复制一份成为常规文件
    常规文件日期已经存在时，若修改日期比源文件更旧，则将被新的覆盖，否则忽略
    """
    if not all(len(v) for v in (path, number, part, ext)):
        return
    covers = ("-fanart", "-poster", "-thumb")
    normal_prefix = f"{number}{leak_word}{c_word}{hack_word}"
    multi_prefix = f"{number}{part}{leak_word}{c_word}{hack_word}"
    normal_pathes = (Path(path) / f"{normal_prefix}{c}{ext}" for c in covers)
    multi_pathes = (Path(path) / f"{multi_prefix}{c}{ext}" for c in covers)
    for normal_path, multi_path in zip(normal_pathes, multi_pathes):
        if not normal_path.is_file():
            continue
        mkLink = False
        if not multi_path.exists():
            mkLink = True
        elif multi_path.is_file():
            if multi_path.stat().st_nlink > 1:
                continue
            elif normal_path.stat().st_mtime <= multi_path.stat().st_mtime:
                continue
            mkLink = True
            multi_path.unlink(missing_ok=True)
        if not mkLink:
            continue
        try:
            os.link(str(normal_path), str(multi_path), follow_symlinks=False)
        except:
            shutil.copyfile(str(normal_path), str(multi_path))


def debug_print(data: json):
    try:
        print("[+] ------- DEBUG INFO -------")
        for i, v in data.items():
            if i == 'outline':
                print('[+]  -', "%-19s" % i, ':', len(v), 'characters')
                continue
            if i == 'actor_photo' or i == 'year':
                continue
            if i == 'extrafanart':
                print('[+]  -', "%-19s" % i, ':', len(v), 'links')
                continue
            print(f'[+]  - {i:<{cn_space(i, 19)}} : {v}')

        print("[+] ------- DEBUG INFO -------")
    except:
        pass


def core_main_no_net_op(movie_path, number):
    conf = config.getInstance()
    part = ''
    leak_word = ''
    leak = False
    c_word = ''
    cn_sub = False
    hack = False
    hack_word = ''
    _4k = False
    iso = False
    imagecut = 1
    multi = False
    part = ''
    path = str(Path(movie_path).parent)

    if re.search('[-_]CD\d+', movie_path, re.IGNORECASE):
        part = re.findall('[-_]CD\d+', movie_path, re.IGNORECASE)[0].upper()
        multi = True
    if re.search(r'[-_]C(\.\w+$|-\w+)|\d+ch(\.\w+$|-\w+)', movie_path,
                 re.I) or '中文' in movie_path or '字幕' in movie_path or ".chs" in movie_path or '.cht' in movie_path:
        cn_sub = True
        c_word = '-C'  # 中文字幕影片后缀
    uncensored = True if is_uncensored(number) else 0
    if '流出' in movie_path or 'uncensored' in movie_path.lower():
        leak_word = '-无码流出'  # 无码流出影片后缀
        leak = True

    if 'hack'.upper() in str(movie_path).upper() or '破解' in movie_path:
        hack = True
        hack_word = "-hack"

    if '4k'.upper() in str(movie_path).upper() or '4k' in movie_path:
        _4k = True

    if '.iso'.upper() in str(movie_path).upper() or '.iso' in movie_path:
        iso = True
    # try:

    #     props = get_video_properties(movie_path)  # 判断是否为4K视频
    #     if props['width'] >= 4096 or props['height'] >= 2160:
    #         _4k = True
    # except:
    #     pass
    prestr = f"{number}{leak_word}{c_word}{hack_word}"

    full_nfo = Path(path) / f"{prestr}{part}.nfo"
    if full_nfo.is_file():
        if full_nfo.read_text(encoding='utf-8').find(r'<tag>无码</tag>') >= 0:
            uncensored = True
        try:
            nfo_xml = etree.parse(full_nfo)
            nfo_fanart_path = nfo_xml.xpath('//fanart/text()')[0]
            ext = Path(nfo_fanart_path).suffix
        except:
            return
    else:
        return
    fanart_path = f"fanart{ext}"
    poster_path = f"poster{ext}"
    thumb_path = f"thumb{ext}"
    if config.getInstance().image_naming_with_number():
        fanart_path = f"{prestr}-fanart{ext}"
        poster_path = f"{prestr}-poster{ext}"
        thumb_path = f"{prestr}-thumb{ext}"
    full_fanart_path = os.path.join(path, fanart_path)
    full_poster_path = os.path.join(path, poster_path)
    full_thumb_path = os.path.join(path, thumb_path)

    if not all(os.path.isfile(f) for f in (full_fanart_path, full_thumb_path)):
        return

    cutImage(imagecut, path, fanart_path, poster_path, bool(conf.face_uncensored_only() and not uncensored))
    if conf.is_watermark():
        add_mark(full_poster_path, full_thumb_path, cn_sub, leak, uncensored, hack, _4k, iso)

    if multi and conf.jellyfin_multi_part_fanart():
        linkImage(path, number, part, leak_word, c_word, hack_word, ext)


def move_subtitles(filepath, path, multi_part, number, part, leak_word, c_word, hack_word) -> bool:
    filepath_obj = pathlib.Path(filepath)
    link_mode = config.getInstance().link_mode()
    sub_res = config.getInstance().sub_rule()
    result = False
    for subfile in filepath_obj.parent.glob('**/*'):
        if subfile.is_file() and subfile.suffix.lower() in sub_res:
            if multi_part and part.lower() not in subfile.name.lower():
                continue
            if filepath_obj.stem.split('.')[0].lower() != subfile.stem.split('.')[0].lower():
                continue
            sub_targetpath = Path(path) / f"{number}{leak_word}{c_word}{hack_word}{''.join(subfile.suffixes)}"
            if link_mode not in (1, 2):
                shutil.move(str(subfile), str(sub_targetpath))
                print(f"[+]Sub Moved!        {sub_targetpath.name}")
                result = True
            else:
                shutil.copyfile(str(subfile), str(sub_targetpath))
                print(f"[+]Sub Copied!       {sub_targetpath.name}")
                result = True
            if result:
                break
    return result


def core_main(movie_path, number_th, oCC, specified_source=None, specified_url=None):
    conf = config.getInstance()
    # =======================================================================初始化所需变量
    multi_part = False
    part = ''
    leak_word = ''
    c_word = ''
    cn_sub = False
    liuchu = False
    hack = False
    hack_word = ''
    _4k = False
    iso = False

    # 下面被注释的变量不需要
    # rootpath = os.getcwd
    number = number_th
    json_data = get_data_from_json(number, oCC, specified_source, specified_url)  # 定义番号

    # Return if blank dict returned (data not found)
    if not json_data:
        moveFailedFolder(movie_path)
        return

    if json_data["number"] != number:
        # fix issue #119
        # the root cause is we normalize the search id
        # print_files() will use the normalized id from website,
        # but paste_file_to_folder() still use the input raw search id
        # so the solution is: use the normalized search id
        number = json_data["number"]
    imagecut = json_data.get('imagecut')
    tag = json_data.get('tag')
    # =======================================================================判断-C,-CD后缀
    if re.search('[-_]CD\d+', movie_path, re.IGNORECASE):
        multi_part = True
        part = re.findall('[-_]CD\d+', movie_path, re.IGNORECASE)[0].upper()
    if re.search(r'[-_]C(\.\w+$|-\w+)|\d+ch(\.\w+$|-\w+)', movie_path,
                 re.I) or '中文' in movie_path or '字幕' in movie_path:
        cn_sub = True
        c_word = '-C'  # 中文字幕影片后缀

    if re.search(r'[-_]UC(\.\w+$|-\w+)', movie_path,
                 re.I):
        cn_sub = True
        hack_word = '-UC'  #
        hack = True
        
    if re.search(r'[-_]U(\.\w+$|-\w+)', movie_path,
                 re.I):#
        hack = True
        hack_word = '-U' 
    # 判断是否无码
    unce = json_data.get('无码')
    uncensored = int(unce) if isinstance(unce, bool) else int(is_uncensored(number))

    if '流出' in movie_path or 'uncensored' in movie_path.lower():
        liuchu = '流出'
        leak = True
        leak_word = '-无码流出'  # 流出影片后缀
    else:
        leak = False

    if 'hack'.upper() in str(movie_path).upper() or '破解' in movie_path:
        hack = True
        hack_word = "-hack"

    if '4k'.upper() in str(movie_path).upper() or '4k' in movie_path:
        _4k = True

    if '.iso'.upper() in str(movie_path).upper() or '.iso' in movie_path:
        iso = True

    # 判断是否4k
    if '4K' in tag:
        tag.remove('4K')  # 从tag中移除'4K'

    # 判断是否为无码破解
    if '无码破解' in tag:
        tag.remove('无码破解')  # 从tag中移除'无码破解'

    # try:
    #     props = get_video_properties(movie_path)  # 判断是否为4K视频
    #     if props['width'] >= 4096 or props['height'] >= 2160:
    #         _4k = True
    # except:
    #     pass

    # 调试模式检测
    if conf.debug():
        debug_print(json_data)

    # 创建文件夹
    # path = create_folder(rootpath + '/' + conf.success_folder(),  json_data.get('location_rule'), json_data)

    cover = json_data.get('cover')
    ext = image_ext(cover)

    fanart_path = f"fanart{ext}"
    poster_path = f"poster{ext}"
    thumb_path = f"thumb{ext}"
    if config.getInstance().image_naming_with_number():
        fanart_path = f"{number}{leak_word}{c_word}{hack_word}-fanart{ext}"
        poster_path = f"{number}{leak_word}{c_word}{hack_word}-poster{ext}"
        thumb_path = f"{number}{leak_word}{c_word}{hack_word}-thumb{ext}"

    # main_mode
    #  1: 刮削模式 / Scraping mode
    #  2: 整理模式 / Organizing mode
    #  3：不改变路径刮削
    if conf.main_mode() == 1:
        # 创建文件夹
        path = create_folder(json_data)
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            if 'headers' in json_data:
                small_cover_check(path, poster_path, json_data.get('cover_small'), movie_path, json_data)
            else:
                small_cover_check(path, poster_path, json_data.get('cover_small'), movie_path)

        # creatFolder会返回番号路径
        if 'headers' in json_data:
            image_download(cover, fanart_path, thumb_path, path, movie_path, json_data)
        else:
            image_download(cover, fanart_path, thumb_path, path, movie_path)

        if not multi_part or part.lower() == '-cd1':
            try:
                # 下载预告片
                if conf.is_trailer() and json_data.get('trailer'):
                    trailer_download(json_data.get('trailer'), leak_word, c_word, hack_word, number, path, movie_path)

                # 下载剧照 data, path, filepath
                if conf.is_extrafanart() and json_data.get('extrafanart'):
                    if 'headers' in json_data:
                        extrafanart_download(json_data.get('extrafanart'), path, number, movie_path, json_data)
                    else:
                        extrafanart_download(json_data.get('extrafanart'), path, number, movie_path)

                # 下载演员头像 KODI .actors 目录位置
                if conf.download_actor_photo_for_kodi():
                    actor_photo_download(json_data.get('actor_photo'), path, number)
            except:
                pass

        # 裁剪图
        cutImage(imagecut, path, thumb_path, poster_path, bool(conf.face_uncensored_only() and not uncensored))

        # 兼容Jellyfin封面图文件名规则
        if multi_part and conf.jellyfin_multi_part_fanart():
            linkImage(path, number_th, part, leak_word, c_word, hack_word, ext)

        # 移动电影
        paste_file_to_folder(movie_path, path, multi_part, number, part, leak_word, c_word, hack_word)

        # Move subtitles
        move_status = move_subtitles(movie_path, path, multi_part, number, part, leak_word, c_word, hack_word)
        if move_status:
            cn_sub = True
        # 添加水印
        if conf.is_watermark():
            add_mark(os.path.join(path, poster_path), os.path.join(path, thumb_path), cn_sub, leak, uncensored,
                     hack, _4k, iso)

        # 最后输出.nfo元数据文件，以完成.nfo文件创建作为任务成功标志
        print_files(path, leak_word, c_word, json_data.get('naming_rule'), part, cn_sub, json_data, movie_path, tag,
                    json_data.get('actor_list'), liuchu, uncensored, hack, hack_word
                    , _4k, fanart_path, poster_path, thumb_path, iso)

    elif conf.main_mode() == 2:
        # 创建文件夹
        path = create_folder(json_data)
        # 移动文件
        paste_file_to_folder_mode2(movie_path, path, multi_part, number, part, leak_word, c_word, hack_word)

        # Move subtitles
        move_subtitles(movie_path, path, multi_part, number, part, leak_word, c_word, hack_word)

    elif conf.main_mode() == 3:
        path = str(Path(movie_path).parent)
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            if 'headers' in json_data:
                small_cover_check(path, poster_path, json_data.get('cover_small'), movie_path, json_data)
            else:
                small_cover_check(path, poster_path, json_data.get('cover_small'), movie_path)

        # creatFolder会返回番号路径
        if 'headers' in json_data:
            image_download(cover, fanart_path, thumb_path, path, movie_path, json_data)
        else:
            image_download(cover, fanart_path, thumb_path, path, movie_path)

        if not multi_part or part.lower() == '-cd1':
            try:
                # 下载预告片
                if conf.is_trailer() and json_data.get('trailer'):
                    trailer_download(json_data.get('trailer'), leak_word, c_word, hack_word, number, path, movie_path)

                # 下载剧照 data, path, filepath
                if conf.is_extrafanart() and json_data.get('extrafanart'):
                    if 'headers' in json_data:
                        extrafanart_download(json_data.get('extrafanart'), path, number, movie_path, json_data)
                    else:
                        extrafanart_download(json_data.get('extrafanart'), path, number, movie_path)

                # 下载演员头像 KODI .actors 目录位置
                if conf.download_actor_photo_for_kodi():
                    actor_photo_download(json_data.get('actor_photo'), path, number)
            except:
                pass

        # 裁剪图
        cutImage(imagecut, path, fanart_path, poster_path, bool(conf.face_uncensored_only() and not uncensored))

        # 添加水印
        if conf.is_watermark():
            add_mark(os.path.join(path, poster_path), os.path.join(path, fanart_path), cn_sub, leak, uncensored, hack,
                     _4k, iso)

        # 兼容Jellyfin封面图文件名规则
        if multi_part and conf.jellyfin_multi_part_fanart():
            linkImage(path, number_th, part, leak_word, c_word, hack_word, ext)

        # 最后输出.nfo元数据文件，以完成.nfo文件创建作为任务成功标志
        print_files(path, leak_word, c_word, json_data.get('naming_rule'), part, cn_sub, json_data, movie_path,
                    tag, json_data.get('actor_list'), liuchu, uncensored, hack, hack_word, _4k, fanart_path,
                    poster_path,
                    thumb_path, iso)
