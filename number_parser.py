import os
import re
from core import *



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
                filepath = filepath.replace("_", "-")
                filepath.strip('22-sht.me').strip('-HD').strip('-hd')
                filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filepath))  # 去除文件名中时间
                if 'FC2' or 'fc2' in filename:
                    filename = filename.replace('PPV', '').replace('ppv', '').replace('--', '-').replace('_', '-')
                file_number = re.search(r'\w+-\w+', filename, re.A).group()
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
            filepath = filepath.replace("_", "-")
            filepath.strip('22-sht.me').strip('-HD').strip('-hd')
            filename = str(re.sub("\[\d{4}-\d{1,2}-\d{1,2}\] - ", "", filepath))  # 去除文件名中时间
            if 'FC2' or 'fc2' in filename:
                filename = filename.replace('PPV', '').replace('ppv', '').replace('--', '-').replace('_', '-')
            file_number = re.search(r'\w+-\w+', filename, re.A).group()
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
