# encoding: utf-8
'''
@author: binge.van
@input: 
@output: 
@desc:

    =======================================
        txt中的坐标是中点坐标与长宽
        单个xml文件转成单个txt文件
'''
import os
import xml.etree.ElementTree as ET
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_root", type=str, default="", help="")
    parser.add_argument("--coco_names", type=str, default="", help="")
    return parser.parse_args()


def coor_xml2txt(image_width, image_height, box):
    W, H = image_width, image_height
    xmin, ymin, xmax, ymax = box
    xmid, ymid = (xmin + xmax) / 2, (ymin + ymax) / 2
    w, h = xmax - xmin, ymax - ymin
    return xmid / W, ymid / H, w / W, h / H


# 标签从xml操txt转换
def xml2txt(file_root, class_names_path):
    class_names = []

    file_names = os.listdir(file_root)
    for name in file_names:
        if not name.endswith("xml"):
            continue

        xml_path = os.path.join(file_root, name)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        size = root.find("size")
        image_width, image_height, image_depth = \
            float(size.find("width").text), \
            float(size.find("height").text), \
            float(size.find("depth").text)

        txt_path = xml_path.replace("xml", "txt")
        print(f"----xml_path---{xml_path}-----")

        with open(txt_path, 'w', encoding='utf-8') as txt_info:
            for obj in root.findall("object"):
                class_name = obj.find("name").text
                if class_name not in class_names:
                    class_names.append(class_name)
                bnd_box = obj.find("bndbox")
                bbox = [float(bnd_box.find(coor).text) for coor in ["xmin", "ymin", "xmax", "ymax"]]
                x_txt, y_txt, w_txt, h_txt = coor_xml2txt(image_width, image_height, bbox)
                class_index = class_names.index(class_name)
                print(
                    f"-----{name}------{str(class_index)} {str(x_txt)} {str(y_txt)} {str(w_txt)} {str(h_txt)}-----------")
                txt_info.write(f"{str(class_index)} {str(x_txt)} {str(y_txt)} {str(w_txt)} {str(h_txt)} \n")

    print(class_names)
    with open(class_names_path, 'w', encoding='utf-8') as names_info:
        for name in class_names:
            names_info.write(f"{name}\n")

import PIL
from PIL import Image
import image_to_numpy
def read_save_img(image_root,dir_names):
    '''
    读取图片同时保存，防止出现ios相机中的自动旋转
    :param image_root:
    :param dir_name:
    :return:
    '''
    for dir_name in dir_names:
        dir_path = os.path.join(image_root,dir_name)
        save_root = os.path.join(image_root,dir_name)+"_dat"
        if  os.path.exists(save_root):
            os.system(f"rm -rf {save_root}")
        os.mkdir(save_root)
        for name in os.listdir(dir_path):
            if name.endswith("xml"):
                continue
            print(name)
            img_path = os.path.join(dir_path,name)

            img = Image.open(img_path)
            # img = PIL.ImageOps.exif_transpose(img)
            img.save(os.path.join(save_root,name))

if __name__ == '__main__':
    # args = parse_args()
    # read_save_img("/home/fb/freework/data/safebelt", ["THbelt20210422done"])
    xml2txt("/home/fb/freework/data/safebelt/THbelt20210422done_dat", "/home/fb/freework/data/safebelt/coco.names")
