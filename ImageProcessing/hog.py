import face_recognition

def face_center(filename, model):
    image = face_recognition.load_image_file(filename)
    face_locations = face_recognition.face_locations(image, 0, model)
    if face_locations:
        top, right, bottom, left = face_locations[0]
        # 中心点
        return int((right+left)/2)
    return 0