import os
import re
import sys
import configparser
import time
import typing
from pathlib import Path

G_conf_override = {
    # index 0 save Config() first instance for quick access by using getInstance()
    0: None,
    # register override config items
    # no need anymore
}


def getInstance():
    if isinstance(G_conf_override[0], Config):
        return G_conf_override[0]
    return Config()


class Config:
    def __init__(self, path: str = "config.ini"):
        path_search_order = (
            Path(path),
            Path.cwd() / "config.ini",
            Path.home() / "mdc.ini",
            Path.home() / ".mdc.ini",
            Path.home() / ".mdc/config.ini",
            Path.home() / ".config/mdc/config.ini"
        )
        ini_path = None
        for p in path_search_order:
            if p.is_file():
                ini_path = p.resolve()
                break
        if ini_path:
            self.conf = configparser.ConfigParser()
            self.ini_path = ini_path
            try:
                if self.conf.read(ini_path, encoding="utf-8-sig"):
                    if G_conf_override[0] is None:
                        G_conf_override[0] = self
            except UnicodeDecodeError:
                if self.conf.read(ini_path, encoding="utf-8"):
                    if G_conf_override[0] is None:
                        G_conf_override[0] = self
            except Exception as e:
                print("ERROR: Config file can not read!")
                print("读取配置文件出错！")
                print('=================================')
                print(e)
                print("======= Auto exit in 60s ======== ")
                time.sleep(60)
                os._exit(-1)
        else:
            print("ERROR: Config file not found!")
            print("Please put config file into one of the following path:")
            print('\n'.join([str(p.resolve()) for p in path_search_order[2:]]))
            # 对于找不到配置文件的情况，还是在打包时附上对应版本的默认配置文件，有需要时为其在搜索路径中生成，
            # 要比用户乱找一个版本不对应的配置文件会可靠些。这样一来，单个执行文件就是功能完整的了，放在任何
            # 执行路径下都可以放心使用。
            res_path = None
            # pyinstaller打包的在打包中找config.ini
            if hasattr(sys, '_MEIPASS') and (Path(getattr(sys, '_MEIPASS')) / 'config.ini').is_file():
                res_path = Path(getattr(sys, '_MEIPASS')) / 'config.ini'
            # 脚本运行的所在位置找
            elif (Path(__file__).resolve().parent / 'config.ini').is_file():
                res_path = Path(__file__).resolve().parent / 'config.ini'
            if res_path is None:
                os._exit(2)
            ins = input("Or, Do you want me create a config file for you? (Yes/No)[Y]:")
            if re.search('n', ins, re.I):
                os._exit(2)
            # 用户目录才确定具有写权限，因此选择 ~/mdc.ini 作为配置文件生成路径，而不是有可能并没有写权限的
            # 当前目录。目前版本也不再鼓励使用当前路径放置配置文件了，只是作为多配置文件的切换技巧保留。
            write_path = path_search_order[2]  # Path.home() / "mdc.ini"
            write_path.write_text(res_path.read_text(encoding='utf-8'), encoding='utf-8')
            print("Config file '{}' created.".format(write_path.resolve()))
            input("Press Enter key exit...")
            os._exit(0)
            # self.conf = self._default_config()
            # try:
            #     self.conf = configparser.ConfigParser()
            #     try: # From single crawler debug use only
            #         self.conf.read('../' + path, encoding="utf-8-sig")
            #     except:
            #         self.conf.read('../' + path, encoding="utf-8")
            # except Exception as e:
            #     print("[-]Config file not found! Use the default settings")
            #     print("[-]",e)
            #     os._exit(3)
            #     #self.conf = self._default_config()

    def set_override(self, option_cmd: str):
        """
        通用的参数覆盖选项 -C 配置覆盖串
        配置覆盖串语法：小节名:键名=值[;[小节名:]键名=值][;[小节名:]键名+=值]  多个键用分号分隔 名称可省略部分尾部字符
        或 小节名:键名+=值[;[小节名:]键名=值][;[小节名:]键名+=值]  在已有值的末尾追加内容，多个键的=和+=可以交叉出现
        例子: face:aspect_ratio=2;aways_imagecut=1;priority:website=javdb
        小节名必须出现在开头至少一次，分号后可只出现键名=值，不再出现小节名，如果后续全部键名都属于同一个小节
        例如配置文件存在两个小节[proxy][priority]，那么pro可指代proxy，pri可指代priority
        [face]  ;face小节下方有4个键名locations_model= uncensored_only= aways_imagecut= aspect_ratio=
        l,lo,loc,loca,locat,locati...直到locations_model完整名称都可以用来指代locations_model=键名
        u,un,unc...直到uncensored_only完整名称都可以用来指代uncensored_only=键名
        aw,awa...直到aways_imagecut完整名称都可以用来指代aways_imagecut=键名
        as,asp...aspect_ratio完整名称都可以用来指代aspect_ratio=键名
        a则因为二义性，不是合法的省略键名
        """
        def err_exit(str):
            print(str)
            os._exit(2)

        sections = self.conf.sections()
        sec_name = None
        for cmd in option_cmd.split(';'):
            syntax_err = True
            rex = re.findall(r'^(.*?):(.*?)(=|\+=)(.*)$', cmd, re.U)
            if len(rex) and len(rex[0]) == 4:
                (sec, key, assign, val) = rex[0]
                sec_lo = sec.lower().strip()
                key_lo = key.lower().strip()
                syntax_err = False
            elif sec_name:  # 已经出现过一次小节名，属于同一个小节的后续键名可以省略小节名
                rex = re.findall(r'^(.*?)(=|\+=)(.*)$', cmd, re.U)
                if len(rex) and len(rex[0]) == 3:
                    (key, assign, val) = rex[0]
                    sec_lo = sec_name.lower()
                    key_lo = key.lower().strip()
                    syntax_err = False
            if syntax_err:
                err_exit(f"[-]Config override syntax incorrect. example: 'd:s=1' or 'debug_mode:switch=1'. cmd='{cmd}' all='{option_cmd}'")
            if not len(sec_lo):
                err_exit(f"[-]Config override Section name '{sec}' is empty! cmd='{cmd}'")
            if not len(key_lo):
                err_exit(f"[-]Config override Key name '{key}' is empty! cmd='{cmd}'")
            if not len(val.strip()):
                print(f"[!]Conig overide value '{val}' is empty! cmd='{cmd}'")
            sec_name = None
            for s in sections:
                if not s.lower().startswith(sec_lo):
                    continue
                if sec_name:
                    err_exit(f"[-]Conig overide Section short name '{sec_lo}' is not unique! dup1='{sec_name}' dup2='{s}' cmd='{cmd}'")
                sec_name = s
            if sec_name is None:
                err_exit(f"[-]Conig overide Section name '{sec}' not found! cmd='{cmd}'")
            key_name = None
            keys = self.conf[sec_name]
            for k in keys:
                if not k.lower().startswith(key_lo):
                    continue
                if key_name:
                    err_exit(f"[-]Conig overide Key short name '{key_lo}' is not unique! dup1='{key_name}' dup2='{k}' cmd='{cmd}'")
                key_name = k
            if key_name is None:
                err_exit(f"[-]Conig overide Key name '{key}' not found! cmd='{cmd}'")
            if assign == "+=":
                val = keys[key_name] + val
            if self.debug():
                print(f"[!]Set config override [{sec_name}]{key_name}={val}  by cmd='{cmd}'")
            self.conf.set(sec_name, key_name, val)

    def main_mode(self) -> int:
        try:
            return self.conf.getint("common", "main_mode")
        except ValueError:
            self._exit("common:main_mode")

    def source_folder(self) -> str:
        return self.conf.get("common", "source_folder").replace("\\\\", "/").replace("\\", "/")

    def failed_folder(self) -> str:
        return self.conf.get("common", "failed_output_folder").replace("\\\\", "/").replace("\\", "/")

    def success_folder(self) -> str:
        return self.conf.get("common", "success_output_folder").replace("\\\\", "/").replace("\\", "/")

    def actor_gender(self) -> str:
        return self.conf.get("common", "actor_gender")

    def link_mode(self) -> int:
        return self.conf.getint("common", "link_mode")

    def scan_hardlink(self) -> bool:
        return self.conf.getboolean("common", "scan_hardlink", fallback=False)#未找到配置选项,默认不刮削

    def failed_move(self) -> bool:
        return self.conf.getboolean("common", "failed_move")

    def auto_exit(self) -> bool:
        return self.conf.getboolean("common", "auto_exit")

    def translate_to_sc(self) -> bool:
        return self.conf.getboolean("common", "translate_to_sc")

    def multi_threading(self) -> bool:
        return self.conf.getboolean("common", "multi_threading")

    def del_empty_folder(self) -> bool:
        return self.conf.getboolean("common", "del_empty_folder")

    def nfo_skip_days(self) -> int:
        return self.conf.getint("common", "nfo_skip_days", fallback=30)

    def ignore_failed_list(self) -> bool:
        return self.conf.getboolean("common", "ignore_failed_list")

    def download_only_missing_images(self) -> bool:
        return self.conf.getboolean("common", "download_only_missing_images")

    def mapping_table_validity(self) -> int:
        return self.conf.getint("common", "mapping_table_validity")

    def jellyfin(self) -> int:
        return self.conf.getint("common", "jellyfin")

    def actor_only_tag(self) -> bool:
        return self.conf.getboolean("common", "actor_only_tag")

    def sleep(self) -> int:
        return self.conf.getint("common", "sleep")

    def anonymous_fill(self) -> bool:
        return self.conf.getint("common", "anonymous_fill")

    def stop_counter(self) -> int:
        return self.conf.getint("advenced_sleep", "stop_counter", fallback=0)

    def rerun_delay(self) -> int:
        value = self.conf.get("advenced_sleep", "rerun_delay")
        if not (isinstance(value, str) and re.match(r'^[\dsmh]+$', value, re.I)):
            return 0  # not match '1h30m45s' or '30' or '1s2m1h4s5m'
        if value.isnumeric() and int(value) >= 0:
            return int(value)
        sec = 0
        sec += sum(int(v)  for v in re.findall(r'(\d+)s', value, re.I))
        sec += sum(int(v)  for v in re.findall(r'(\d+)m', value, re.I)) * 60
        sec += sum(int(v)  for v in re.findall(r'(\d+)h', value, re.I)) * 3600
        return sec

    def is_translate(self) -> bool:
        return self.conf.getboolean("translate", "switch")

    def is_trailer(self) -> bool:
        return self.conf.getboolean("trailer", "switch")

    def is_watermark(self) -> bool:
        return self.conf.getboolean("watermark", "switch")

    def is_extrafanart(self) -> bool:
        return self.conf.getboolean("extrafanart", "switch")

    def extrafanart_thread_pool_download(self) -> int:
        try:
            v = self.conf.getint("extrafanart", "parallel_download")
            return v if v >= 0 else 5
        except:
            return 5

    def watermark_type(self) -> int:
        return int(self.conf.get("watermark", "water"))

    def get_uncensored(self):
        try:
            sec = "uncensored"
            uncensored_prefix = self.conf.get(sec, "uncensored_prefix")
            # uncensored_poster = self.conf.get(sec, "uncensored_poster")
            return uncensored_prefix

        except ValueError:
            self._exit("uncensored")

    def get_extrafanart(self):
        try:
            extrafanart_download = self.conf.get("extrafanart", "extrafanart_folder")
            return extrafanart_download
        except ValueError:
            self._exit("extrafanart_folder")

    def get_translate_engine(self) -> str:
        return self.conf.get("translate", "engine")

    def get_target_language(self) -> str:
        return self.conf.get("translate", "target_language")

    # def get_translate_appId(self) ->str:
    #     return self.conf.get("translate","appid")

    def get_translate_key(self) -> str:
        return self.conf.get("translate", "key")

    def get_translate_delay(self) -> int:
        return self.conf.getint("translate", "delay")

    def translate_values(self) -> str:
        return self.conf.get("translate", "values")

    def get_translate_service_site(self) -> str:
        return self.conf.get("translate", "service_site")

    def proxy(self):
        try:
            sec = "proxy"
            switch = self.conf.get(sec, "switch")
            proxy = self.conf.get(sec, "proxy")
            timeout = self.conf.getint(sec, "timeout")
            retry = self.conf.getint(sec, "retry")
            proxytype = self.conf.get(sec, "type")
            iniProxy = IniProxy(switch, proxy, timeout, retry, proxytype)
            return iniProxy
        except ValueError:
            self._exit("common")

    def cacert_file(self) -> str:
        return self.conf.get('proxy', 'cacert_file')

    def media_type(self) -> str:
        return self.conf.get('media', 'media_type')

    def sub_rule(self) -> typing.Set[str]:
        return set(self.conf.get('media', 'sub_type').lower().split(','))

    def naming_rule(self) -> str:
        return self.conf.get("Name_Rule", "naming_rule")

    def location_rule(self) -> str:
        return self.conf.get("Name_Rule", "location_rule")

    def max_title_len(self) -> int:
        """
        Maximum title length
        """
        try:
            return self.conf.getint("Name_Rule", "max_title_len")
        except:
            return 50

    def image_naming_with_number(self) -> bool:
        try:
            return self.conf.getboolean("Name_Rule", "image_naming_with_number")
        except:
            return False

    def number_uppercase(self) -> bool:
        try:
            return self.conf.getboolean("Name_Rule", "number_uppercase")
        except:
            return False
        
    def number_regexs(self) -> str:
        try:
            return self.conf.get("Name_Rule", "number_regexs")
        except:
            return ""

    def update_check(self) -> bool:
        try:
            return self.conf.getboolean("update", "update_check")
        except ValueError:
            self._exit("update:update_check")

    def sources(self) -> str:
        return self.conf.get("priority", "website")

    def escape_literals(self) -> str:
        return self.conf.get("escape", "literals")

    def escape_folder(self) -> str:
        return self.conf.get("escape", "folders")

    def debug(self) -> bool:
        return self.conf.getboolean("debug_mode", "switch")

    def get_direct(self) -> bool:
        return self.conf.getboolean("direct", "switch")
    
    def is_storyline(self) -> bool:
        try:
            return self.conf.getboolean("storyline", "switch")
        except:
            return True

    def storyline_site(self) -> str:
        try:
            return self.conf.get("storyline", "site")
        except:
            return "1:avno1,4:airavwiki"

    def storyline_censored_site(self) -> str:
        try:
            return self.conf.get("storyline", "censored_site")
        except:
            return "2:airav,5:xcity,6:amazon"

    def storyline_uncensored_site(self) -> str:
        try:
            return self.conf.get("storyline", "uncensored_site")
        except:
            return "3:58avgo"

    def storyline_show(self) -> int:
        v = self.conf.getint("storyline", "show_result", fallback=0)
        return v if v in (0, 1, 2) else 2 if v > 2 else 0

    def storyline_mode(self) -> int:
        return 1 if self.conf.getint("storyline", "run_mode", fallback=1) > 0 else 0

    def cc_convert_mode(self) -> int:
        v = self.conf.getint("cc_convert", "mode", fallback=1)
        return v if v in (0, 1, 2) else 2 if v > 2 else 0

    def cc_convert_vars(self) -> str:
        return self.conf.get("cc_convert", "vars",
            fallback="actor,director,label,outline,series,studio,tag,title")

    def javdb_sites(self) -> str:
        return self.conf.get("javdb", "sites", fallback="38,39")

    def face_locations_model(self) -> str:
        return self.conf.get("face", "locations_model", fallback="hog")

    def face_uncensored_only(self) -> bool:
        return self.conf.getboolean("face", "uncensored_only", fallback=True)

    def face_aways_imagecut(self) -> bool:
        return self.conf.getboolean("face", "aways_imagecut", fallback=False)

    def face_aspect_ratio(self) -> float:
        return self.conf.getfloat("face", "aspect_ratio", fallback=2.12)

    def jellyfin_multi_part_fanart(self) -> bool:
        return self.conf.getboolean("jellyfin", "multi_part_fanart", fallback=False)

    def download_actor_photo_for_kodi(self) -> bool:
        return self.conf.getboolean("actor_photo", "download_for_kodi", fallback=False)

    @staticmethod
    def _exit(sec: str) -> None:
        print("[-] Read config error! Please check the {} section in config.ini", sec)
        input("[-] Press ENTER key to exit.")
        exit()

    @staticmethod
    def _default_config() -> configparser.ConfigParser:
        conf = configparser.ConfigParser()

        sec1 = "common"
        conf.add_section(sec1)
        conf.set(sec1, "main_mode", "1")
        conf.set(sec1, "source_folder", "./")
        conf.set(sec1, "failed_output_folder", "failed")
        conf.set(sec1, "success_output_folder", "JAV_output")
        conf.set(sec1, "link_mode", "0")
        conf.set(sec1, "scan_hardlink", "0")
        conf.set(sec1, "failed_move", "1")
        conf.set(sec1, "auto_exit", "0")
        conf.set(sec1, "translate_to_sc", "1")
        # actor_gender value: female or male or both or all(含人妖)
        conf.set(sec1, "actor_gender", "female")
        conf.set(sec1, "del_empty_folder", "1")
        conf.set(sec1, "nfo_skip_days", "30")
        conf.set(sec1, "ignore_failed_list", "0")
        conf.set(sec1, "download_only_missing_images", "1")
        conf.set(sec1, "mapping_table_validity", "7")
        conf.set(sec1, "jellyfin", "0")
        conf.set(sec1, "actor_only_tag", "0")
        conf.set(sec1, "sleep", "3")
        conf.set(sec1, "anonymous_fill", "0")

        sec2 = "advenced_sleep"
        conf.add_section(sec2)
        conf.set(sec2, "stop_counter", "0")
        conf.set(sec2, "rerun_delay", "0")

        sec3 = "proxy"
        conf.add_section(sec3)
        conf.set(sec3, "proxy", "")
        conf.set(sec3, "timeout", "5")
        conf.set(sec3, "retry", "3")
        conf.set(sec3, "type", "socks5")
        conf.set(sec3, "cacert_file", "")

        sec4 = "Name_Rule"
        conf.add_section(sec4)
        conf.set(sec4, "location_rule", "actor + '/' + number")
        conf.set(sec4, "naming_rule", "number + '-' + title")
        conf.set(sec4, "max_title_len", "50")
        conf.set(sec4, "image_naming_with_number", "0")
        conf.set(sec4, "number_uppercase", "0")
        conf.set(sec4, "number_regexs", "")

        sec5 = "update"
        conf.add_section(sec5)
        conf.set(sec5, "update_check", "1")

        sec6 = "priority"
        conf.add_section(sec6)
        conf.set(sec6, "website", "airav,javbus,javdb,fanza,xcity,mgstage,fc2,fc2club,avsox,jav321,xcity")

        sec7 = "escape"
        conf.add_section(sec7)
        conf.set(sec7, "literals", "\()/")  # noqa
        conf.set(sec7, "folders", "failed, JAV_output")

        sec8 = "debug_mode"
        conf.add_section(sec8)
        conf.set(sec8, "switch", "0")

        sec9 = "translate"
        conf.add_section(sec9)
        conf.set(sec9, "switch", "0")
        conf.set(sec9, "engine", "google-free")
        conf.set(sec9, "target_language", "zh_cn")
        # conf.set(sec8, "appid", "")
        conf.set(sec9, "key", "")
        conf.set(sec9, "delay", "1")
        conf.set(sec9, "values", "title,outline")
        conf.set(sec9, "service_site", "translate.google.cn")

        sec10 = "trailer"
        conf.add_section(sec10)
        conf.set(sec10, "switch", "0")

        sec11 = "uncensored"
        conf.add_section(sec11)
        conf.set(sec11, "uncensored_prefix", "S2M,BT,LAF,SMD")

        sec12 = "media"
        conf.add_section(sec12)
        conf.set(sec12, "media_type",
                 ".mp4,.avi,.rmvb,.wmv,.mov,.mkv,.flv,.ts,.webm,iso")
        conf.set(sec12, "sub_type",
                 ".smi,.srt,.idx,.sub,.sup,.psb,.ssa,.ass,.usf,.xss,.ssf,.rt,.lrc,.sbv,.vtt,.ttml")

        sec13 = "watermark"
        conf.add_section(sec13)
        conf.set(sec13, "switch", "1")
        conf.set(sec13, "water", "2")

        sec14 = "extrafanart"
        conf.add_section(sec14)
        conf.set(sec14, "switch", "1")
        conf.set(sec14, "extrafanart_folder", "extrafanart")
        conf.set(sec14, "parallel_download", "1")

        sec15 = "storyline"
        conf.add_section(sec15)
        conf.set(sec15, "switch", "1")
        conf.set(sec15, "site", "1:avno1,4:airavwiki")
        conf.set(sec15, "censored_site", "2:airav,5:xcity,6:amazon")
        conf.set(sec15, "uncensored_site", "3:58avgo")
        conf.set(sec15, "show_result", "0")
        conf.set(sec15, "run_mode", "1")
        conf.set(sec15, "cc_convert", "1")

        sec16 = "cc_convert"
        conf.add_section(sec16)
        conf.set(sec16, "mode", "1")
        conf.set(sec16, "vars", "actor,director,label,outline,series,studio,tag,title")

        sec17 = "javdb"
        conf.add_section(sec17)
        conf.set(sec17, "sites", "33,34")

        sec18 = "face"
        conf.add_section(sec18)
        conf.set(sec18, "locations_model", "hog")
        conf.set(sec18, "uncensored_only", "1")
        conf.set(sec18, "aways_imagecut", "0")
        conf.set(sec18, "aspect_ratio", "2.12")

        sec19 = "jellyfin"
        conf.add_section(sec19)
        conf.set(sec19, "multi_part_fanart", "0")

        sec20 = "actor_photo"
        conf.add_section(sec20)
        conf.set(sec20, "download_for_kodi", "0")

        return conf


class IniProxy():
    """ Proxy Config from .ini
    """
    SUPPORT_PROXY_TYPE = ("http", "socks5", "socks5h")

    enable = False
    address = ""
    timeout = 5
    retry = 3
    proxytype = "socks5"

    def __init__(self, switch, address, timeout, retry, proxytype) -> None:
        """ Initial Proxy from .ini
        """
        if switch == '1' or switch == 1:
            self.enable = True
        self.address = address
        self.timeout = timeout
        self.retry = retry
        self.proxytype = proxytype

    def proxies(self):
        """
        获得代理参数，默认http代理
        get proxy params, use http proxy for default
        """
        if self.address:
            if self.proxytype in self.SUPPORT_PROXY_TYPE:
                proxies = {"http": self.proxytype + "://" + self.address,
                           "https": self.proxytype + "://" + self.address}
            else:
                proxies = {"http": "http://" + self.address, "https": "https://" + self.address}
        else:
            proxies = {}

        return proxies


if __name__ == "__main__":
    def evprint(evstr):
        code = compile(evstr, "<string>", "eval")
        print('{}: "{}"'.format(evstr, eval(code)))


    config = Config()
    mfilter = {'conf', 'proxy', '_exit', '_default_config', 'ini_path', 'set_override'}
    for _m in [m for m in dir(config) if not m.startswith('__') and m not in mfilter]:
        evprint(f'config.{_m}()')
    pfilter = {'proxies', 'SUPPORT_PROXY_TYPE'}
    # test getInstance()
    assert (getInstance() == config)
    for _p in [p for p in dir(getInstance().proxy()) if not p.startswith('__') and p not in pfilter]:
        evprint(f'getInstance().proxy().{_p}')

    # Create new instance
    conf2 = Config()
    assert getInstance() != conf2
    assert getInstance() == config

    conf2.set_override("d:s=1;face:asp=2;f:aw=0;pri:w=javdb;f:l=")
    assert conf2.face_aspect_ratio() == 2
    assert conf2.face_aways_imagecut() == False
    assert conf2.sources() == "javdb"
    print(f"Load Config file '{conf2.ini_path}'.")
