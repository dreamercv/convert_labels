# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        生成yolo的txt标签，同时生成json格式的标签，然后用脚本将json格式的转成ocr格式的标签
        
"""
import os
import cv2
import argparse
import shutil
import numpy as np
from lxml import etree
from tqdm import tqdm
import xml.etree.ElementTree as ET
import json

import codecs

json_info = {
    "version": "4.5.6",
}


def str2list(string: str):
    string = string.strip()
    std_points = string.split(";")
    points = []
    for point in std_points:
        point = point.split(",")
        points.append(list(map(float, point)))
    # points = np.array(points)
    print(points)
    return points


def cvat_xml2txt(points, img_w, img_h, classes_id):
    points = np.array(points)
    txt_data = [classes_id]
    top_x, top_y, bottom_x, bottom_y = \
        max(points[:, 0]), max(points[:, 1]), \
        min(points[:, 0]), min(points[:, 1])
    center_x, center_y, w, h = \
        (top_x + bottom_x) / 2, (top_y + bottom_y) / 2, \
        abs(top_x - bottom_x), abs(top_y - bottom_y),
    txt_data += [round(center_x / img_w, 6), round(center_y / img_h, 6), round(w / img_w, 6), round(h / img_h, 6)]
    print(txt_data)
    return txt_data


def parse_anno_file(cvat_xml, save_root, labels: list):
    tree = ET.parse(cvat_xml)
    root = tree.getroot()
    images = root.findall("image")
    for image in images:
        json_info = {
            "version": "4.5.6",
            "shapes": []
        }

        image_head = {}
        for key, value in image.items():
            image_head[key] = value
        image_name = image_head["name"].split(os.sep)[-1]
        print(image_name)

        txt_name = image_name.replace("jpg", "txt")
        img_w, img_h = int(image_head["width"]), int(image_head["height"])
        txt_path = os.path.join(save_root, txt_name)
        txt_info = open(txt_path, 'w', encoding='utf-8')

        json_name = image_name.replace("jpg", "json")
        json_path = os.path.join(save_root, json_name)
        json_info["imagePath"], json_info["imageHeight"], json_info["imageWidth"] = image_name, img_h, img_w

        polygons = image.findall("polygon")
        for polygon in polygons:
            polygon_head = {}
            for p_key, mp_value in polygon.items():
                polygon_head[p_key] = mp_value

            points = str2list(polygon_head["points"])
            if polygon_head["label"] in labels:  # 匹配到铜管的坐标信息,铜管信息转成yolo格式的txt标注文件
                txt_data = cvat_xml2txt(points, img_w, img_h, labels.index(polygon_head["label"]))
                txt_info.write(" ".join(str(data) for data in txt_data) + "\n")
            else:  # 文字类型的数据转成json格式，之后在用另一个脚本转成paddleocr的格式
                one_info = {}
                one_info["label"] = polygon.find("attribute").text
                # slashUStr.decode("unicode-escape")
                one_info["points"] = points
                print(polygon.find("attribute").text)
                json_info["shapes"].append(one_info)
        with open(json_path, 'w', encoding='utf-8') as json_data:
            json.dump(json_info, json_data, indent=4, ensure_ascii=False)
        print(json.dumps(json_info, indent=4, ensure_ascii=False))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", '-x', type=str,
                        default="/home/fb/project/docker/data/dakin_ocr_dataset/DJKT_brass20210312.xml",
                        help="xml路径")
    parser.add_argument("--save", '-s', type=str,
                        default="/home/fb/project/docker/data/dakin_ocr_dataset/brass/DJKT_brass20210312done",
                        help="txt,json与图片保存在一起")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    cvat_xml = args.xml
    save_root = args.save
    labels = ["brass"]
    # cvat_xml = "/home/fb/project/docker/data/dakin_ocr_dataset/DJKT_brass20210312.xml"
    # save_root = "/home/fb/project/docker/data/dakin_ocr_dataset/brass/DJKT_brass20210312done"
    if not os.path.exists(save_root):
        os.mkdir(save_root)
    parse_anno_file(cvat_xml, save_root, labels)

    # anno = parse_anno_file(cvat_xml)
    # points = "2001.80,3450.50;2248.90,3454.00;2477.10,3.80;2221.40,3.40"
    # str2list(points)
