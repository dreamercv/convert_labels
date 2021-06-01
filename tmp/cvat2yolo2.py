# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        找出json文件中保温棉与铜管的字段，并将其转换成yolo格式的txt文件，用于训练目标检测
        
"""
import os
import numpy as np
import json
import cv2
import argparse
import logging
import shutil


# 压力表的类别参数


# 抽真空表的类别参数


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", '-r', type=str, default=" ", help="图片、标注文件的根目录")
    parser.add_argument("--coco_root", '-c', type=str, default="", help="coco.names的根目录")
    return parser.parse_args()


def coor2txt(img_w, img_h, coor_data):
    coor_data = np.asarray(coor_data)
    top_left_x, top_left_y, bottom_right_x, bottom_right_y = \
        min(coor_data[:, 0]), min(coor_data[:, 1]), max(coor_data[:, 0]), max(coor_data[:, 1])
    center_x, center_y, bbox_w, bbox_h = \
        (top_left_x + bottom_right_x) / 2, \
        (top_left_y + bottom_right_y) / 2, \
        abs(top_left_x - bottom_right_x), \
        abs(top_left_y - bottom_right_y)
    txt_x, txt_y, txt_w, txt_h = \
        round(center_x / img_w, 6), \
        round(center_y / img_h, 6), \
        round(bbox_w / img_w, 6), \
        round(bbox_h / img_h, 6)
    return [txt_x, txt_y, txt_w, txt_h]

def from_json_get_txt(json_info, class_names):
    txt_data = []
    json_data = json.load(json_info)
    imageHeight = json_data["imageHeight"]
    imageWidth = json_data["imageWidth"]
    shapes = json_data["shapes"]
    if (len(shapes) > 0):
        for shape in shapes:
            label = shape["label"]
            points = shape["points"]
            if label not in class_names:
                continue
            txt_points = coor2txt(imageWidth, imageHeight, points)
            txt_data.append(txt_points)
    return imageWidth, imageHeight, txt_data


def main():
    class_names = ["brass", "insulation"]
    image_root = "/home/fb/project/docker/data/dakin_ocr_dataset"
    image_file_names = ["brass_train/DJKT_brass20210409done",
                        "insulation_train/DJKT_insulation20210409done",
                        "insulation_test/DJKT_insulation20210409done"]

    for image_file in image_file_names:

        image_file_path = os.path.join(image_root, image_file)
        os.system(f"rm -rf {image_file_path}/*.txt")
        names = os.listdir(image_file_path)
        for name in names:
            print(name)
            if not name.endswith("json"):
                continue
            path = os.path.join(image_file_path, name)
            json_info = open(path, 'r', encoding="utf-8")
            img_w, img_h, txt_data = from_json_get_txt(json_info, class_names)
            if len(txt_data) > 0:
                txt_path = path.replace("json", "txt")
                txt_info = open(txt_path, "w", encoding="utf-8")
                for txt in txt_data:
                    info = list(map(str, txt))
                    print(txt)
                    print("0 " + " ".join(info))
                    txt_info.write("0 " + " ".join(info) + "\n")
                txt_info.close()
            json_info.close()


if __name__ == '__main__':
    main()
