import face_recognition


def face_center(filename, model):
    image = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(image, 1, model)
    print('[+]Found person      [' + str(len(face_locations)) + ']      By model hog')
    maxRight = 0
    maxTop = 0
    for face_location in face_locations:
        top, right, bottom, left = face_location
        # 中心点
        x = int((right+left)/2)
        if x > maxRight:
            maxRight = x
            maxTop = top
    return maxRight,maxTop
