import os
import re
from core import *


G_spat = re.compile(
    "(^22-sht\.me|-fhd|_fhd|^fhd_|^fhd-|-hd|_hd|^hd_|^hd-|-sd|_sd|-1080p|_1080p|-720p|_720p)",
    re.IGNORECASE)


def get_number(debug,filepath: str) -> str:
    # """
    # >>> from number_parser import get_number
    # >>> get_number("/Users/Guest/AV_Data_Capture/snis-829.mp4")
    # 'snis-829'
    # >>> get_number("/Users/Guest/AV_Data_Capture/snis-829-C.mp4")
    # 'snis-829'
    # >>> get_number("C:¥Users¥Guest¥snis-829.mp4")
    # 'snis-829'
    # >>> get_number("C:¥Users¥Guest¥snis-829-C.mp4")
    # 'snis-829'
    # >>> get_number("./snis-829.mp4")
    # 'snis-829'
    # >>> get_number("./snis-829-C.mp4")
    # 'snis-829'
    # >>> get_number(".¥snis-829.mp4")
    # 'snis-829'
    # >>> get_number(".¥snis-829-C.mp4")
    # 'snis-829'
    # >>> get_number("snis-829.mp4")
    # 'snis-829'
    # >>> get_number("snis-829-C.mp4")
    # 'snis-829'
    # """
    filepath = os.path.basename(filepath)

    if debug == False:
        try:
            if '-' in filepath or '_' in filepath:  # 普通提取番号 主要处理包含减号-和_的番号
                #filepath = filepath.replace("_", "-")
                filepath = G_spat.sub("", filepath)
                filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filepath))  # 去除文件名中时间
                lower_check = filename.lower()
                if 'fc2' in lower_check:
                    filename = lower_check.replace('ppv', '').replace('--', '-').replace('_', '-').upper()
                file_number = re.search(r'\w+(-|_)\w+', filename, re.A).group()
                if "tokyo" in lower_check and "hot" in lower_check:
                    file_number = re.search(r'(cz|gedo|k|n|red-|se)\d{2,4}', lower_check, re.A).group()
                elif "carib" in lower_check:
                    file_number = str(re.search(r'\d{6}(-|_)\d{3}', lower_check, re.A).group()).replace('_', '-')
                elif "1pon" in lower_check or "paco" in lower_check:
                    file_number = str(re.search(r'\d{6}(-|_)\d{3}', lower_check, re.A).group()).replace('-', '_')
                elif "10mu" in lower_check:
                    file_number = str(re.search(r'\d{6}(-|_)\d{2}', lower_check, re.A).group()).replace('-', '_')
                return file_number
            else:  # 提取不含减号-的番号，FANZA CID
                # 欧美番号匹配规则
                oumei = re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', filepath)
                if oumei:
                    return oumei.group()

                try:
                    return str(
                        re.findall(r'(.+?)\.',
                                   str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filepath).group()))).strip(
                        "['']").replace('_', '-')
                except:
                    return re.search(r'(.+?)\.', filepath)[0]
        except Exception as e:
            print('[-]' + str(e))
            return
    elif debug == True:
        if '-' in filepath or '_' in filepath:  # 普通提取番号 主要处理包含减号-和_的番号
            #filepath = filepath.replace("_", "-")
            filepath = G_spat.sub("", filepath)
            filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filepath))  # 去除文件名中时间
            lower_check = filename.lower()
            if 'fc2' in lower_check:
                filename = lower_check.replace('ppv', '').replace('--', '-').replace('_', '-').upper()
            file_number = re.search(r'\w+(-|_)\w+', filename, re.A).group()
            if "tokyo" in lower_check and "hot" in lower_check:
                file_number = re.search(r'(cz|gedo|k|n|red-|se)\d{2,4}', lower_check, re.A).group()
            elif "carib" in lower_check:
                file_number = str(re.search(r'\d{6}(-|_)\d{3}', lower_check, re.A).group()).replace('_', '-')
            elif "1pon" in lower_check or "paco" in lower_check:
                file_number = str(re.search(r'\d{6}(-|_)\d{3}', lower_check, re.A).group()).replace('-', '_')
            elif "10mu" in lower_check:
                file_number = str(re.search(r'\d{6}(-|_)\d{2}', lower_check, re.A).group()).replace('-', '_')
            return file_number
        else:  # 提取不含减号-的番号，FANZA CID
            # 欧美番号匹配规则
            oumei = re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', filepath)
            if oumei:
                return oumei.group()

            try:
                return str(
                    re.findall(r'(.+?)\.',
                               str(re.search('([^<>/\\\\|:""\\*\\?]+)\\.\\w+$', filepath).group()))).strip(
                    "['']").replace('_', '-')
            except:
                return re.search(r'(.+?)\.', filepath)[0]


# if __name__ == "__main__":
#     import doctest
#     doctest.testmod(raise_on_error=True)
