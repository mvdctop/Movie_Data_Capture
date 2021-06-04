import os
import sys
import configparser
import codecs

class Config:
    def __init__(self, path: str = "config.ini"):
        if os.path.exists(path):
            self.conf = configparser.ConfigParser()
            try:
                self.conf.read(path, encoding="utf-8-sig")
            except:
                self.conf.read(path, encoding="utf-8")
        else:
            print("[-]Config file not found!")
            sys.exit(2)
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

    def main_mode(self) -> str:
        try:
            return self.conf.getint("common", "main_mode")
        except ValueError:
            self._exit("common:main_mode")

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
        return self.conf.getboolean("common", "auto_exit")
    def transalte_to_sc(self) -> bool:
        return self.conf.getboolean("common", "transalte_to_sc")
    def multi_threading(self) -> bool:
        return self.conf.getboolean("common", "multi_threading")
    def is_transalte(self) -> bool:
        return self.conf.getboolean("transalte", "switch")
    def is_trailer(self) -> bool:
        return self.conf.getboolean("trailer", "switch")

    def is_watermark(self) -> bool:
        return self.conf.getboolean("watermark", "switch")

    def is_extrafanart(self) -> bool:
        return self.conf.getboolean("extrafanart", "switch")

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
        return self.conf.getboolean("debug_mode", "switch")

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
        conf.set(sec1, "failed_output_folder", "failed")
        conf.set(sec1, "success_output_folder", "JAV_output")
        conf.set(sec1, "soft_link", "0")
        conf.set(sec1, "failed_move", "1")
        conf.set(sec1, "auto_exit", "0")
        conf.set(sec1, "transalte_to_sc", "1")
        # actor_gender value: female or male or both or all(含人妖)
        conf.set(sec1, "actor_gender", "female")

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
        conf.set(sec5, "website", "airav,javbus,javdb,fanza,xcity,mgstage,fc2,avsox,jav321,xcity")

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
    config = Config()
    print(config.main_mode())
    print(config.failed_folder())
    print(config.success_folder())
    print(config.soft_link())
    print(config.failed_move())
    print(config.auto_exit())
    print(config.proxy().enable)
    print(config.proxy().retry)
    print(config.naming_rule())
    print(config.location_rule())
    print(config.update_check())
    print(config.sources())
    print(config.escape_literals())
    print(config.escape_folder())
    print(config.debug())
    print(config.is_transalte())
    print(config.get_transalte_engine())
    # print(config.get_transalte_appId())
    print(config.get_transalte_key())
    print(config.get_transalte_delay())
    print(config.transalte_values())
    print(config.actor_gender())
