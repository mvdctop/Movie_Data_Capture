import os
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
            print("[-] Config file not found! Use the default settings")
            self.conf = self._default_config()

    def main_mode(self) -> str:
        try:
            return self.conf.getint("common", "main_mode")
        except ValueError:
            self._exit("common:main_mode")

    def failed_folder(self) -> str:
        return self.conf.get("common", "failed_output_folder")

    def success_folder(self) -> str:
        return self.conf.get("common", "success_output_folder")

    def soft_link(self) -> bool:
        return self.conf.getboolean("common", "soft_link")

    def proxy(self) -> [str, int, int, str]:
        try:
            sec = "proxy"
            proxy = self.conf.get(sec, "proxy")
            timeout = self.conf.getint(sec, "timeout")
            retry = self.conf.getint(sec, "retry")
            proxytype = self.conf.get(sec, "type")
            
            return proxy, timeout, retry, proxytype
        except ValueError:
            self._exit("common")

    def naming_rule(self) -> str:
        return self.conf.get("Name_Rule", "naming_rule")

    def location_rule(self) -> str:
        return self.conf.get("Name_Rule", "location_rule")

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

        sec2 = "proxy"
        conf.add_section(sec2)
        conf.set(sec2, "proxy", "127.0.0.1:1080")
        conf.set(sec2, "timeout", "10")
        conf.set(sec2, "retry", "3")

        sec3 = "Name_Rule"
        conf.add_section(sec3)
        conf.set(sec3, "location_rule", "actor + '/' + number")
        conf.set(sec3, "naming_rule", "number + '-' + title")

        sec4 = "update"
        conf.add_section(sec4)
        conf.set(sec4, "update_check", "1")

        sec5 = "priority"
        conf.add_section(sec5)
        conf.set(sec5, "website", "javbus,javdb,fanza,xcity,mgstage,fc2,avsox,jav321,xcity")

        sec6 = "escape"
        conf.add_section(sec6)
        conf.set(sec6, "literals", "\()/")  # noqa
        conf.set(sec6, "folders", "failed, JAV_output")

        sec7 = "debug_mode"
        conf.add_section(sec7)
        conf.set(sec7, "switch", "0")

        return conf


if __name__ == "__main__":
    config = Config()
    print(config.main_mode())
    print(config.failed_folder())
    print(config.success_folder())
    print(config.soft_link())
    print(config.proxy())
    print(config.naming_rule())
    print(config.location_rule())
    print(config.update_check())
    print(config.sources())
    print(config.escape_literals())
    print(config.escape_folder())
    print(config.debug())
