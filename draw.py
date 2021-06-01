# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        
"""
import cv2
import os


def graw_txt_label(root, txt_name, image_name):
    image = cv2.imread(os.path.join(root, image_name))
    h,w,c = image.shape
