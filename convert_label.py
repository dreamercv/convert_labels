# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        标书格式转换的类
        
"""

import os
import json
import shutil
import cv2

import base_function
from config import *


# config
class Convert_xml_to_txt():
    def __init__(self, org_root, total_names):
        '''
        # 不抠图直接保存 sample
        >>> convert_xml_txt = Convert_xml_to_txt(org_root, total_objects)
        >>> convert_xml_txt.main_xmls_to_txts()
        '''
        self.org_root = org_root
        self.total_names = total_names

    def xml_to_txt(self, xml_path):
        annotation = base_function.parse_xml(xml_path)
        img_name = annotation["filename"]
        img_w, img_h = annotation["size"][0], annotation["size"][1]
        objects = []
        for name, point_info in annotation["objects"].items():
            objects.append({name: point_info})
        base_function.save_txt_from_xml(self.org_root, self.org_root, img_name, objects, img_w, img_h, self.total_names)

    def main_xmls_to_txts(self):
        for name in os.listdir(self.org_root):
            if not name.endswith("xml"):
                continue
            self.xml_to_txt(os.path.join(self.org_root, name))


class Convert_xml_to_txt_txt():
    def __init__(self, total_names, cutout_names, target_names, in_target_names, org_root, dst_target_root,
                 dst_in_target_root):
        '''
        # 抠图并保存 sample
        >>>convert_xml = Convert_xml_to_txt_txt(total_names, cutout_names, target_names, in_target_names, org_root,
        >>>                                     dst_target_root,
        >>>                                     dst_in_target_root)
        >>>convert_xml.main_split_xmls_to_tow_txts()
        '''
        self.org_root = org_root  # 源文件地址
        self.dst_target_root = dst_target_root  # 存放目标图片与标注文件路径
        self.dst_in_target_root = dst_in_target_root  # 存放抠图后的图片与标注文件路径
        self.total_names = total_names
        self.cutout_names = cutout_names  # 需要抠图的名称
        self.target_names = target_names  # 检测原图中的目标名称
        self.in_target_names = in_target_names  # 检测抠图内的目标名称

    def split_info_target_and_in(self, objects):
        '''
        将数据分成全图的目标、目标中的信息
        :param objects:
        :return:
        '''
        target_objects = []
        in_target_objects = []
        for key, value in objects.items():
            if key in self.target_names:
                target_objects.append({key: value})
            elif key in self.in_target_names:
                in_target_objects.append({key: value})
            else:
                print("label is no found ! ")
        print(target_objects)
        print(len(in_target_objects))
        return target_objects, in_target_objects

    def object_in_target(self, target_box, in_target_objects, img, name):
        txt_path = name + ".txt"
        txt_info = open(txt_path, "w", encoding="utf-8")
        box_w, box_h = abs(target_box[0] - target_box[2]), abs(target_box[1] - target_box[3])
        objects_in_target = []
        # have_in_target = False
        for in_target_object in in_target_objects:
            object_in_target = {}
            for key, boxs in in_target_object.items():
                for box in boxs:
                    if base_function.get_iou(target_box, box) == 0.0:
                        continue
                    # 保存image与应对的txt
                    have_in_target = True
                    xmin = 0 if target_box[0] > box[0] else abs(target_box[0] - box[0])
                    ymin = 0 if target_box[1] > box[1] else abs(target_box[1] - box[1])
                    xmax = xmin + abs(box[0] - box[2]) if target_box[2] > box[2] else box_w
                    ymax = ymin + abs(box[1] - box[3]) if target_box[3] > box[3] else box_h
                    box_info = {key: [xmin, ymin, xmax, ymax]}
                    txt_box = base_function.coor2txt(box_w, box_h, box_info, self.total_names)
                    txt_info.write(" ".join(map(str, txt_box)) + "\n")
                    print(" ".join(map(str, txt_box)) + "\n")
                    # 保存信息为json格式
                    if key not in object_in_target.keys():
                        object_in_target[key] = [box]
                    else:
                        object_in_target[key].append(box)
            objects_in_target.append(object_in_target)
        # if have_in_target:
        print(target_box)
        rect = list(map(int, target_box))
        print(rect)
        print(img.shape)
        target_img = img[rect[1]:rect[3], rect[0]:rect[2]]
        image_path = name + ".jpg"
        cv2.imwrite(image_path, target_img)
        txt_info.close()

        return objects_in_target

    def classfier_target_and_in(self, target_objects, in_target_objects, img, dst_image_path):
        """
        [{"target":
            {
                points:[x,y,w,h],
                in:[{target_in:[[x,y,w,h]]},
                    {target_in:[[x,y,w,h]]},
                    {target_in:[[x,y,w,h]]}
                    ...]
            }
          }
        ]
        :param target_objects:
        :param in_target_objects:
        :return:
        """
        count = 0
        for target_object in target_objects:
            for key, values in target_object.items():
                if key not in self.cutout_names:
                    continue
                for value in values:
                    count += 1
                    name = dst_image_path.split(".")[0] + f"_{str(count).zfill(2)}"
                    objects_in_target = self.object_in_target(value, in_target_objects, img, name)

    def split_xml_to_tow_txt(self, xml_name, org_root, dst_target_root, dst_in_target_root):
        # 解析xml格式转成标注格式（json）
        annotation = base_function.parse_xml(os.path.join(org_root, xml_name))
        img_name = annotation["filename"]
        img_w, img_h = annotation["size"][0], annotation["size"][1]

        image_path = os.path.join(org_root, img_name)
        img = cv2.imread(image_path)

        target_objects, in_target_objects = self.split_info_target_and_in(annotation["objects"])

        # 保存目标信息
        base_function.save_txt_from_xml(org_root, dst_target_root, img_name, target_objects, img_w, img_h,
                                        self.total_names)

        # 归类：目标与目标内的物体归类
        dst_image_path = os.path.join(dst_in_target_root, img_name)
        self.classfier_target_and_in(target_objects, in_target_objects, img, dst_image_path)

    def main_split_xmls_to_tow_txts(self):
        if self.dst_target_root == self.dst_in_target_root:
            os.system(f"rm -rf {self.dst_target_root} && mkdir {self.dst_target_root}")
        else:
            os.system(f"rm -rf {self.dst_target_root} && rm -rf {self.dst_in_target_root}")
            os.system(f"mkdir {self.dst_target_root} && mkdir {self.dst_in_target_root}")

        for name in os.listdir(org_root):
            if not name.endswith("xml"):
                continue
            self.split_xml_to_tow_txt(name, self.org_root, self.dst_target_root, self.dst_in_target_root)


class Convert_txt_to_xml():
    def __init__(self, org_root, dst_root, class_names):
        self.org_root = org_root
        self.dst_root = dst_root
        self.class_names = class_names

    def txt_to_xml(self, txt_path, img):
        img_h, img_w, depth = img.shape
        annotation = base_function.parse_txt(txt_path, img_w, img_h, depth, txt_path.replace("txt", "jpg"),
                                             self.class_names)
        base_function.save_xml_from_txt(self.org_root, self.dst_root, annotation)

    def main_txts_to_xmls(self):
        if not os.path.exists(self.dst_root):
            os.mkdir(self.dst_root)
        for name in os.listdir(self.org_root):
            if not name.endswith("txt"):
                continue
            txt_path = os.path.join(org_root, name)
            img_path = os.path.join(org_root, name.replace("txt", "jpg"))
            img = cv2.imread(img_path)
            if img is None:
                continue
            self.txt_to_xml(txt_path, img)


if __name__ == '__main__':
    if xml2txt_txt:
        # 抠图并保存
        convert_xml = Convert_xml_to_txt_txt(total_names, cutout_names, target_names, in_target_names, org_root,
                                             dst_target_root,
                                             dst_in_target_root)
        convert_xml.main_split_xmls_to_tow_txts()
    if xml2txt:
        # 不抠图直接保存
        convert_xml_txt = Convert_xml_to_txt(org_root, class_names)
        convert_xml_txt.main_xmls_to_txts()
    if txt2xml:
        # yolo的txt转xml
        convert_txt = Convert_txt_to_xml(org_root, dst_root, class_names)
        convert_txt.main_txts_to_xmls()
