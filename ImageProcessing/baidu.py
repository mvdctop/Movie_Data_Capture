from aip import AipBodyAnalysis
import config


def face_center(filename, model):
    app_id = config.getInstance().conf.get("face", "appid")
    api_key = config.getInstance().conf.get("face", "key")
    app_secret = config.getInstance().conf.get("face", "secret")
    client = AipBodyAnalysis(app_id, api_key, app_secret)
    with open(filename, 'rb') as fp:
        img = fp.read()
    result = client.bodyAnalysis(img)
    if 'error_code' in result:
        raise ValueError(result['error_msg'])
    print('[+]Found person      ' + str(result['person_num']))
    # 中心点取鼻子x坐标
    maxRight = 0
    maxTop = 0
    for person_info in result["person_info"]:
        x = int(person_info['body_parts']['nose']['x'])
        top = int(person_info['location']['top'])
        if x > maxRight:
            maxRight = x
            maxTop = top
    return maxRight,maxTop
