import logging
import config
import importlib

def face_crop(filename, width, height):
    # 新宽度是高度的2/3
    cropWidthHalf = int(height/3)
    try:
        locations_model = filter(lambda x: x, config.getInstance().face_locations_model().lower().split(','))
        for model in locations_model:
            center = face_center(filename, model)
            # 如果找到就跳出循环
            if center:
                cropLeft = center-cropWidthHalf
                cropRight = center+cropWidthHalf
                # 越界处理
                if cropLeft < 0:
                    cropLeft = 0
                    cropRight = cropWidthHalf*2
                elif cropRight > width:
                    cropLeft = width-cropWidthHalf*2
                    cropRight = width
                return (cropLeft, 0, cropRight, height)
    except:
        print('[-]Not found face!   ' + filename)
    # 默认靠右切
    return (width-cropWidthHalf*2, 0, width, height)


def face_center(filename, model):
    print('[+]Use model         ' + model)
    try:
        mod = importlib.import_module('.' + model,'ImageProcessing')
        return mod.face_center(filename, model)
    except BaseException as e:
        print('[-]Model found face  ' + filename)
        logging.error(e)
        return 0