import os
import re
import sys
import configparser
import time
from pathlib import Path


G_conf_override = {
    # index 0 save Config() first instance for quick access by using getInstance()
    0 : None,
    # register override config items
    "common:main_mode" : None,
    "common:source_folder" : None,
    "common:auto_exit" : None,
    "common:nfo_skip_days" : None,
    "common:stop_counter" : None,
    "common:ignore_failed_list" : None,
    "debug_mode:switch" : None
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
                sys.exit(2)
            ins = input("Or, Do you want me create a config file for you? (Yes/No)[Y]:")
            if re.search('n', ins, re.I):
                sys.exit(2)
            # 用户目录才确定具有写权限，因此选择 ~/mdc.ini 作为配置文件生成路径，而不是有可能并没有写权限的
            # 当前目录。目前版本也不再鼓励使用当前路径放置配置文件了，只是作为多配置文件的切换技巧保留。
            write_path = path_search_order[2]   # Path.home() / "mdc.ini"
            write_path.write_text(res_path.read_text(encoding='utf-8'), encoding='utf-8')
            print("Config file '{}' created.".format(write_path.resolve()))
            input("Press Enter key exit...")
            sys.exit(0)
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
            #     sys.exit(3)
            #     #self.conf = self._default_config()
    def getboolean_override(self, section, item) -> bool:
        return self.conf.getboolean(section, item) if G_conf_override[f"{section}:{item}"] is None else bool(G_conf_override[f"{section}:{item}"])

    def getint_override(self, section, item) -> int:
        return self.conf.getint(section, item) if G_conf_override[f"{section}:{item}"] is None else int(G_conf_override[f"{section}:{item}"])

    def get_override(self, section, item) -> str:
        return self.conf.get(section, item) if G_conf_override[f"{section}:{item}"] is None else str(G_conf_override[f"{section}:{item}"])

    def main_mode(self) -> int:
        try:
            return self.getint_override("common", "main_mode")
        except ValueError:
            self._exit("common:main_mode")

    def source_folder(self) -> str:
        return self.get_override("common", "source_folder")

    def failed_folder(self) -> str:
        return self.conf.get("common", "failed_output_folder")

    def success_folder(self) -> str:
        return self.conf.get("common", "success_output_folder")

    def actor_gender(self) -> str:
        return self.conf.get("common", "actor_gender")

    def soft_link(self) -> bool:
        return self.conf.getboolean("common", "soft_link")
    def failed_move(self) -> bool:
        return self.conf.getboolean("common", "failed_move")
    def auto_exit(self) -> bool:
        return self.getboolean_override("common", "auto_exit")
    def transalte_to_sc(self) -> bool:
        return self.conf.getboolean("common", "transalte_to_sc")
    def multi_threading(self) -> bool:
        return self.conf.getboolean("common", "multi_threading")
    def del_empty_folder(self) -> bool:
        return self.conf.getboolean("common", "del_empty_folder")
    def nfo_skip_days(self) -> int:
        try:
            return self.getint_override("common", "nfo_skip_days")
        except:
            return 30
    def stop_counter(self) -> int:
        try:
            return self.getint_override("common", "stop_counter")
        except:
            return 0
    def ignore_failed_list(self) -> bool:
        return self.getboolean_override("common", "ignore_failed_list")
    def download_only_missing_images(self) -> bool:
        return self.conf.getboolean("common", "download_only_missing_images")
    def mapping_table_validity(self) -> int:
        return self.conf.getint("common", "mapping_table_validity")
    def is_transalte(self) -> bool:
        return self.conf.getboolean("transalte", "switch")
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
    def get_transalte_engine(self) -> str:
        return self.conf.get("transalte","engine")
    # def get_transalte_appId(self) ->str:
    #     return self.conf.get("transalte","appid")
    def get_transalte_key(self) -> str:
        return self.conf.get("transalte","key")
    def get_transalte_delay(self) -> int:
        return self.conf.getint("transalte","delay")
    def transalte_values(self) -> str:
        return self.conf.get("transalte", "values")
    def get_translate_service_site(self) -> str:
        return self.conf.get("transalte", "service_site")
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

    def sub_rule(self):
        return self.conf.get('media', 'sub_type').split(',')

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
        return self.getboolean_override("debug_mode", "switch")

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
        try:
            v = self.conf.getint("storyline", "show_result")
            return v if v in (0,1,2) else 2 if v > 2 else 0
        except:
            return 0

    def storyline_mode(self) -> int:
        try:
            v = self.conf.getint("storyline", "run_mode")
            return v if v in (0,1,2) else 2 if v > 2 else 0
        except:
            return 1

    def cc_convert_mode(self) -> int:
        try:
            v = self.conf.getint("cc_convert", "mode")
            return v if v in (0,1,2) else 2 if v > 2 else 0
        except:
            return 1

    def cc_convert_vars(self) -> str:
        try:
            return self.conf.get("cc_convert", "vars")
        except:
            return "actor,director,label,outline,series,studio,tag,title"

    def javdb_sites(self) -> str:
        try:
            return self.conf.get("javdb", "sites")
        except:
            return "33,34"

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
        conf.set(sec1, "soft_link", "0")
        conf.set(sec1, "failed_move", "1")
        conf.set(sec1, "auto_exit", "0")
        conf.set(sec1, "transalte_to_sc", "1")
        # actor_gender value: female or male or both or all(含人妖)
        conf.set(sec1, "actor_gender", "female")
        conf.set(sec1, "del_empty_folder", "1")
        conf.set(sec1, "nfo_skip_days", 30)
        conf.set(sec1, "stop_counter", 0)
        conf.set(sec1, "ignore_failed_list", 0)
        conf.set(sec1, "download_only_missing_images", 1)
        conf.set(sec1, "mapping_table_validity", 7)

        sec2 = "proxy"
        conf.add_section(sec2)
        conf.set(sec2, "proxy", "")
        conf.set(sec2, "timeout", "5")
        conf.set(sec2, "retry", "3")
        conf.set(sec2, "type", "socks5")
        conf.set(sec2, "cacert_file", "")


        sec3 = "Name_Rule"
        conf.add_section(sec3)
        conf.set(sec3, "location_rule", "actor + '/' + number")
        conf.set(sec3, "naming_rule", "number + '-' + title")
        conf.set(sec3, "max_title_len", "50")

        sec4 = "update"
        conf.add_section(sec4)
        conf.set(sec4, "update_check", "1")

        sec5 = "priority"
        conf.add_section(sec5)
        conf.set(sec5, "website", "airav,javbus,javdb,fanza,xcity,mgstage,fc2,fc2club,avsox,jav321,xcity")

        sec6 = "escape"
        conf.add_section(sec6)
        conf.set(sec6, "literals", "\()/")  # noqa
        conf.set(sec6, "folders", "failed, JAV_output")

        sec7 = "debug_mode"
        conf.add_section(sec7)
        conf.set(sec7, "switch", "0")

        sec8 = "transalte"
        conf.add_section(sec8)
        conf.set(sec8, "switch", "0")
        conf.set(sec8, "engine", "google-free")
        # conf.set(sec8, "appid", "")
        conf.set(sec8, "key", "")
        conf.set(sec8, "delay", "1")
        conf.set(sec8, "values", "title,outline")
        conf.set(sec8, "service_site", "translate.google.cn")

        sec9 = "trailer"
        conf.add_section(sec9)
        conf.set(sec9, "switch", "0")

        sec10 = "uncensored"
        conf.add_section(sec10)
        conf.set(sec10, "uncensored_prefix", "S2M,BT,LAF,SMD")

        sec11 = "media"
        conf.add_section(sec11)
        conf.set(sec11, "media_type", ".mp4,.avi,.rmvb,.wmv,.mov,.mkv,.flv,.ts,.webm,.MP4,.AVI,.RMVB,.WMV,.MOV,.MKV,.FLV,.TS,.WEBM,iso,ISO")
        conf.set(sec11, "sub_type", ".smi,.srt,.idx,.sub,.sup,.psb,.ssa,.ass,.txt,.usf,.xss,.ssf,.rt,.lrc,.sbv,.vtt,.ttml")

        sec12 = "watermark"
        conf.add_section(sec12)
        conf.set(sec12, "switch", 1)
        conf.set(sec12, "water", 2)

        sec13 = "extrafanart"
        conf.add_section(sec13)
        conf.set(sec13, "switch", 1)
        conf.set(sec13, "extrafanart_folder", "extrafanart")
        conf.set(sec13, "parallel_download", 1)

        sec14 = "storyline"
        conf.add_section(sec14)
        conf.set(sec14, "switch", 1)
        conf.set(sec14, "site", "1:avno1,4:airavwiki")
        conf.set(sec14, "censored_site", "2:airav,5:xcity,6:amazon")
        conf.set(sec14, "uncensored_site", "3:58avgo")
        conf.set(sec14, "show_result", 0)
        conf.set(sec14, "run_mode", 1)
        conf.set(sec14, "cc_convert", 1)

        sec15 = "cc_convert"
        conf.add_section(sec15)
        conf.set(sec15, "mode", 1)
        conf.set(sec15, "vars", "actor,director,label,outline,series,studio,tag,title")

        sec16 = "javdb"
        conf.add_section(sec16)
        conf.set(sec15, "sites", "33,34")

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
        ''' 获得代理参数，默认http代理
        '''
        if self.address:
            if self.proxytype in self.SUPPORT_PROXY_TYPE:
                proxies = {"http": self.proxytype + "://" + self.address, "https": self.proxytype + "://" + self.address}
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
    mfilter = {'conf', 'proxy', '_exit', '_default_config', 'getboolean_override', 'getint_override', 'get_override', 'ini_path'}
    for _m in [m for m in dir(config) if not m.startswith('__') and m not in mfilter]:
        evprint(f'config.{_m}()')
    pfilter = {'proxies', 'SUPPORT_PROXY_TYPE'}
    # test getInstance()
    assert(getInstance() == config)
    for _p in [p for p in dir(getInstance().proxy()) if not p.startswith('__') and p not in pfilter]:
        evprint(f'getInstance().proxy().{_p}')

    # Override Test
    G_conf_override["common:nfo_skip_days"] = 4321
    G_conf_override["common:stop_counter"] = 1234
    assert config.nfo_skip_days() == 4321
    assert getInstance().stop_counter() == 1234
    # remove override
    G_conf_override["common:stop_counter"] = None
    G_conf_override["common:nfo_skip_days"] = None
    assert config.nfo_skip_days() != 4321
    assert config.stop_counter() != 1234
    # Create new instance
    conf2 = Config()
    assert getInstance() != conf2
    assert getInstance() == config
    G_conf_override["common:main_mode"] = 9
    G_conf_override["common:source_folder"] = "A:/b/c"
    # Override effect to all instances
    assert config.main_mode() == 9
    assert conf2.main_mode() == 9
    assert getInstance().main_mode() == 9
    assert conf2.source_folder() == "A:/b/c"
    print("### Override Test ###".center(36))
    evprint('getInstance().main_mode()')
    evprint('config.source_folder()')
    G_conf_override["common:main_mode"] = None
    evprint('conf2.main_mode()')
    evprint('config.main_mode()')
    # unregister key acess will raise except
    try:
        print(G_conf_override["common:actor_gender"])
    except KeyError as ke:
        print(f'Catched KeyError: {ke} is not a register key of G_conf_override dict.', file=sys.stderr)
    print(f"Load Config file '{conf2.ini_path}'.")
