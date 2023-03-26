import sys
sys.path.append('../')

from ImageProcessing.hog import face_center as hog_face_center


def face_center(filename, model):
    return hog_face_center(filename, model)
