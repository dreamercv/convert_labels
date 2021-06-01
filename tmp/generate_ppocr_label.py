# encoding: utf-8
'''
@author: binge.van
@input: 
@output: 
@desc:
    生成paddleocr类型的标签，包括：检测、识别以及对应的字典,将数据按照1：9分成测试与训练集
'''
import os, sys
import json
import numpy as np
import cv2
import math
import argparse
import shutil


# xxx.jpg  [{"transcription":"1213","points": [[], [], [], []]},
#           {"transcription":"1213","points": [[], [], [], []]}...]
def get_det_label(data_root, detect_label_path):
    with open(detect_label_path, 'w', encoding="utf-8") as out_file:
        for folder_name in os.listdir(data_root):  # DJKT_brass_train_20210107
            print(folder_name)
            folder_path = os.path.join(data_root, folder_name)
            if os.path.isfile(folder_path):
                continue

            print(os.listdir(folder_path))
            for file_name in os.listdir(folder_path):  # DJKT_characters_none_none_phone_train_p_day_20210107_1.jpg
                if not file_name.endswith('json'):
                    continue
                print(file_name)
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, encoding='utf-8') as json_info:
                    data = json.load(json_info)
                    info = []
                    image_name = data["imagePath"]
                    sub_image_path = os.path.join(folder_name, image_name)
                    for shape in data["shapes"]:
                        print(shape["label"])
                        try:
                            if (shape["label"].isalpha() and shape["label"].lower() in img_names) or (
                                    len(shape["points"]) != 4):
                                continue
                            points = shape["points"]
                            npoint = []
                            npoint.append(list(map(int, points[0])))
                            npoint.append(list(map(int, points[3])))
                            npoint.append(list(map(int, points[2])))
                            npoint.append(list(map(int, points[1])))
                            # for point in shape["points"]:
                            #     npoint.append(list(map(int, point)))
                            info.append({"transcription": shape["label"],
                                         "points": npoint})
                        except:
                            pass
                out_file.write(sub_image_path + "\t" + json.dumps(info, ensure_ascii=False) + "\n")


# dekin_ocr_rec/word_000001.jpg 1123
# dekin_ocr_rec/word_000001.jpg 1123
# ...

def degree(p1, p2):
    vector = [p2[0] - p1[0], p2[1] - p1[1]]
    vector_base = [1, 0]
    up = vector[0] * vector_base[0] + vector[1] * vector_base[1]
    bottom1 = np.sqrt(vector[0] ** 2 + vector[1] ** 2)
    bottom2 = np.sqrt(vector_base[0] ** 2 + vector_base[1] ** 2)
    cos = up / (bottom1 * bottom2)
    radian = math.acos(cos)
    degree = radian * 180 / math.pi
    if vector[1] < 0:
        return -degree
    return degree


def affine(cnt, img, angle, ):  ## 必须是array数组的形式
    img_h, img_w = img.shape[:2]
    org_x, org_y = cnt[0][0], cnt[0][1]
    rect = cv2.minAreaRect(np.int0(cnt))  # 获得最小外接矩形的（中心(x,y), (宽,高), 旋转角度）

    (center_x, center_y), _, _ = rect[0], rect[1], rect[2]
    affine_matrix = cv2.getRotationMatrix2D((center_x, center_y), angle, 1)

    rotate_img = cv2.warpAffine(img, affine_matrix, (img_w, img_h))

    affine_point = np.dot(affine_matrix, np.array([[org_x], [org_y], [1]]))
    affine_w = abs(center_x - affine_point[0])
    affine_h = abs(center_y - affine_point[1])
    print(affine_w)
    print(affine_h)
    print(center_x)
    print(center_y)

    word_image = rotate_img[int(center_y - affine_h):int(center_y + affine_h),
                 int(center_x - affine_w):int(center_x + affine_w), :]

    return word_image, rotate_img


def get_rec_label(data_root, rec_root, rec_label_path):
    if not os.path.exists(rec_root):
        os.mkdir(rec_root)
    image_count = 0

    with open(rec_label_path, "w", encoding='utf-8') as out_file:
        for folder_name in os.listdir(data_root):  # DJKT_brass_train_20210107
            folder_path = os.path.join(data_root, folder_name)
            if os.path.isfile(folder_path):
                continue
            for file_name in os.listdir(folder_path):  # DJKT_characters_none_none_phone_train_p_day_20210107_1.jpg

                if not file_name.endswith("json"):
                    continue
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, encoding='utf-8') as json_info:
                    data = json.load(json_info)
                    image_name = data["imagePath"]
                    org_image = cv2.imread(os.path.join(folder_path, image_name))
                    print(org_image)
                    print(image_name)
                    for shape in data["shapes"]:

                        try:
                            if (shape["label"].lower() in img_names) or (len(shape["points"]) != 4):
                                continue
                            image_count += 1
                            points = shape["points"]
                            angle = degree(points[1], points[2])
                            word_image, rotate_img = affine(points, org_image, angle)
                            if word_image.size == 0:
                                continue
                            word_image_name = f"word_{str(image_count).zfill(6)}.jpg"
                            word_image_path = os.path.join(rec_root, word_image_name)
                            cv2.imwrite(word_image_path, word_image)
                            # cv2.imwrite(os.path.join("../../EV/data/dekin_p",word_image_name), rotate_img)
                            label = shape["label"]
                            out_file.write(word_image_name + "\t" + label + "\n")
                        except:
                            pass


def get_dict(data_root, dict_path):
    dict = []

    for folder_name in os.listdir(data_root):  # DJKT_brass_train_20210107
        folder_path = os.path.join(data_root, folder_name)
        if os.path.isfile(folder_path):
            continue
        for file_name in os.listdir(folder_path):  # DJKT_characters_none_none_phone_train_p_day_20210107_1.jpg

            if not file_name.endswith("json"):
                continue
            file_path = os.path.join(folder_path, file_name)
            print(file_path)
            with open(file_path, encoding='utf-8') as json_info:  # gb18030
                data = json.load(json_info)
                for shape in data["shapes"]:
                    label = shape["label"]
                    if label is None:
                        continue
                    for s in label:
                        dict.append(s)
    set_dict = set(dict)

    with open(dict_path, 'w', encoding='utf-8') as out_file:
        for s in set_dict:
            out_file.write(f"{str(s)}\n")


def get_max_len_txt(rec_label_path):
    txt_len = []
    with open(rec_label_path, "r", encoding="utf-8") as rec_label:
        lines = rec_label.readlines()
        for line in lines:
            word = line.split("\t")[-1].strip()
            txt_len.append(len(word))
    # print(max(txt_len))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", '-r', type=str,
                        default="/home/fb/freework/FBlab/images",
                        help="图片根目录")
    # parser.add_argument("--names", '-n', type=list,
    #                     default=["brass"],
    #                     help="txt,json与图片保存在一起")
    return parser.parse_args()


def split_train_val(image_root, names):
    num = 0

    for classes_name in names:
        train_dir = os.path.join(image_root, classes_name) + "_train"
        val_dir = os.path.join(image_root, classes_name) + "_val"

        os.system(f"rm -rf {train_dir}"), os.system(f"rm -rf {val_dir}")
        os.mkdir(train_dir), os.mkdir(val_dir)
        for dir_name in os.listdir(os.path.join(image_root, classes_name)):

            org_dir_path = os.path.join(image_root, classes_name, dir_name)
            for json_name in os.listdir(org_dir_path):
                if json_name.endswith("json"):
                    num += 1
                    json_path = os.path.join(org_dir_path, json_name)
                    json_info = open(json_path, "r", encoding='utf-8')
                    image_name = json.load(json_info)["imagePath"]
                    json_info.close()
                    image_path = os.path.join(org_dir_path, image_name)

                    if num % 10 == 0:
                        if not os.path.exists(os.path.join(val_dir, dir_name)):
                            os.mkdir(os.path.join(val_dir, dir_name))
                        dst_json_path = os.path.join(val_dir, dir_name, json_name)
                        dst_image_path = os.path.join(val_dir, dir_name, image_name)

                    else:
                        if not os.path.exists(os.path.join(train_dir, dir_name)):
                            os.mkdir(os.path.join(train_dir, dir_name))
                        dst_json_path = os.path.join(train_dir, dir_name, json_name)
                        dst_image_path = os.path.join(train_dir, dir_name, image_name)
                    print(json_path)
                    print(dst_json_path)
                    shutil.copyfile(json_path, dst_json_path), shutil.copyfile(image_path, dst_image_path)


if __name__ == '__main__':
    args = parse_args()
    # # names = ["brass","Signalline","insulation"]
    org_names = ["brass"]
    names = ["brass_val", "brass_train"]
    img_names = ["brass", "signalline", "insulation"]
    root = args.root
    split_train_val(root, org_names)
    for name in names:
        detect_images, rec_images = os.path.join(root, name), os.path.join(root, f"{name}_rec")
        detect_txt, rec_txt = os.path.join(root, f"{name}_detect.txt"), os.path.join(root, f"{name}_rec.txt")
        os.system(f"rm -rf {rec_images} && rm -rf {detect_txt} && rm -rf {rec_txt}")

        get_det_label(detect_images, detect_txt)
        get_rec_label(detect_images, rec_images, rec_txt)
    for img_name in org_names:
        detect_images = os.path.join(root, img_name)
        dict_txt = os.path.join(root, f"{img_name}_dict.txt")
        os.system(f"rm -rf {dict_txt}")
        get_dict(detect_images, dict_txt)
