# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        json格式的标签转变成适用于yolo的txt文件同時在圖片的根目錄生成coco.names與classes.txt
        其中对json中的label进行筛选，只选择['0', '1', '2', '3', '4', '5', '6', '指针']标签输出
        
"""
import os
import numpy as np
import json
import cv2
import argparse
import logging
import shutil

# 压力表的类别参数
pointer_scope = 6
need_classes = [str(i) for i in range(pointer_scope + 1)]
need_classes.append("指针")  # classes=['0', '1', '2', '3', '4', '5', '6', '指针']
need_classes.append("仪表盘")
coco_names = ['0', '1', '2', '3', '4', '5', '6', 'pointer', 'panel']


# 抽真空表的类别参数


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", '-r', type=str, default=" ", help="图片、标注文件的根目录")
    parser.add_argument("--coco_root", '-c', type=str, default="", help="coco.names的根目录")
    return parser.parse_args()


def get_josn_info(json_path: str):
    with open(json_path, 'r', encoding='utf-8') as json_info:
        json_data = json.load(json_info)
        imageHeight = json_data["imageHeight"]
        imageWidth = json_data["imageWidth"]
        txt_path = json_path.replace("json", "txt")
        print(f"json_path:    " + json_path)

        # img_path = json_path.replace("json", "jpg")
        # img = cv2.imread(img_path)
        if (len(json_data["shapes"]) > 0):
            with open(txt_path, 'w', encoding='utf-8') as txt_info:
                res = []
                for shape in json_data["shapes"]:
                    label = shape["label"]
                    points = shape["points"]
                    if label not in need_classes:
                        continue
                    points = np.array(points)
                    class_index = need_classes.index(label)
                    top_left_x, top_left_y, bottom_right_x, bottom_right_y = \
                        min(points[:, 0]), min(points[:, 1]), max(points[:, 0]), max(points[:, 1])
                    center_x, center_y, bbox_w, bbox_h = \
                        (top_left_x + bottom_right_x) / 2, \
                        (top_left_y + bottom_right_y) / 2, \
                        abs(top_left_x - bottom_right_x), \
                        abs(top_left_y - bottom_right_y)
                    txt_x, txt_y, txt_w, txt_h = \
                        round(center_x / imageWidth, 6), \
                        round(center_y / imageHeight, 6), \
                        round(bbox_w / imageWidth, 6), \
                        round(bbox_h / imageHeight, 6)

                    res.append([class_index, txt_x, txt_y, txt_w, txt_h])

                res = np.array(res)
                res = res[np.argsort(res[:, 0])]
                for r in res:
                    txt_info.write(
                        str(int(r[0])) + " " + str(r[1]) + " " + str(r[2]) + " " + str(r[3]) + " " + str(r[4]) + "\n")
                    print(
                        "txt_info:    " + str(int(r[0])) + " " + str(r[1]) + " " + str(r[2]) + " " + str(
                            r[3]) + " " + str(
                            r[4]))


def get_one_panel_max_number(root):
    one_panel_all_number = []
    names = os.listdir(root)
    for name in names:
        if not name.endswith("json"):
            continue
        json_path = os.path.join(root, name)
        print(json_path)
        with open(json_path, 'r', encoding='utf-8') as json_info:
            json_data = json.load(json_info)
            shapes = json_data["shapes"]
            for shape in shapes:
                label = shape["label"]
                if label == "仪表盘" or label == "指针" or label == "vacuum_meter" \
                        or label == "central_point" or label == "pointer" :
                    continue
                int_label = float(label)
                one_panel_all_number.append(int_label)
    print((one_panel_all_number))
    return max(one_panel_all_number)


def cvat2txt(root, coco_root):
    names = os.listdir(root)

    # with open(os.path.join(root, "classes.txt"), 'w', encoding='utf-8') as coco_data:
    #     for class_name in need_classes:
    #         coco_data.write(f"{str(class_name)}\n")
    with open(os.path.join(coco_root, "coco.names"), 'w', encoding='utf-8') as coco_data:
        for coco_name in coco_names:
            coco_data.write(f"{str(coco_name)}\n")

    # 存放每个表盘的最大值
    max_numbers = []
    for name in names:
        if (not name.endswith("json")):
            continue
        if (name == "classes.txt"):
            continue
        get_josn_info(os.path.join(root, name))
    print(max_numbers)


def ckeck_images_txt(root):
    names = os.listdir(root)
    txt_names, image_names = [], []
    for name in names:
        if name.endswith("jpg"):
            image_names.append(name)
        elif name.endswith("json"):
            continue
        elif name.endswith("txt"):
            txt_names.append(name)
        else:
            logging.info(name, " is not jpg txt json")

    logging.info(len(image_names))

    for txt_name in txt_names:
        image_name = txt_name.replace("txt", "jpg")
        if image_name not in image_names:
            os.remove(os.path.join(root, image_name))
            logging.info(image_name)

    logging.info(len(image_names))


def get_max_munber_panel(root):
    max_numbers = []
    max_number = get_one_panel_max_number(root)
    max_numbers.append(max_number)
    print(max_numbers)
    set(max_numbers)
    print(max_numbers)


if __name__ == '__main__':
    # args = parse_args()
    # root = args.root
    # coco_root = args.coco_root
    # cvat2txt(root, coco_root)
    # # ckeck_images_txt(root)
    get_max_munber_panel("/home/fb/project/docker/data/DJKT/chouzhenkong")
