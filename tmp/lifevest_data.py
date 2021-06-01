# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:

    直接生成人与救生衣的数据集----get_person_lifevest_txt
    生成人的数据集，然后对人数据集抠图生成救生衣的数据集
        
"""
import os, sys
import xml.etree.ElementTree as ET
import shutil
import cv2

class_names = ["lifevest", "person"]


def coor_xml2txt(image_width, image_height, box):
    W, H = image_width, image_height
    xmin, ymin, xmax, ymax = box
    xmid, ymid = (xmin + xmax) / 2, (ymin + ymax) / 2
    w, h = xmax - xmin, ymax - ymin
    return round(xmid / W, 6), round(ymid / H, 6), round(w / W, 6), round(h / H, 6)


def point_in_rect(bbox1, bbox2):
    xmin, ymin, xmax, ymax = bbox1
    center_x, center_y = (bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2
    if center_x >= xmin and center_x <= xmax and center_y >= ymin and center_y <= ymax:
        return True
    else:
        return False


def fintune_rec(box1, box2):
    w, h = box1[2] - box1[0], box1[3] - box1[1]
    x1 = box2[0] - box1[0] if box2[0] > box1[0] else 0
    y1 = box2[1] - box1[1] if box2[1] > box1[1] else 0
    x2 = box2[2] - box2[0] + x1 if box2[2] < box1[2] else w
    y2 = box2[3] - box2[1] + y1 if box2[3] < box1[3] else h
    print(f"w {w} h {h} x1 {x1} y1 {y1} x2 {x2} y2 {y2}")
    print(box2)
    print("----------")
    return w, h, [x1, y1, x2, y2]


def get_rect_img(img, box):
    box = list(map(int, box))
    out = img[box[1]:box[3], box[0]:box[2]]
    return out


def get_person_lifevest_txt(xml_name, img_root, person_root):
    xml_path = os.path.join(img_root, xml_name)
    img_txt_path = xml_path.replace("xml", "txt")
    name = xml_name.split(".")[0]

    img_path = os.path.join(img_root, name + ".jpg")
    # img = cv2.imread(img_path)

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # 中点在人内部就代表是救生圈存在
    persons_data, lifevests_data = [], []

    size = root.find("size")
    imgw, imgh = float(size.find("width").text), float(size.find("height").text)

    for obj in root.findall("object"):
        name = obj.find("name").text
        bndbox = obj.find("bndbox")
        bbox = [float(bndbox.find(coor).text) for coor in ["xmin", "ymin", "xmax", "ymax"]]
        if name == "lifevest_person" or name == "no_lifevest_person":
            persons_data.append(bbox)
        elif name == "lifevest":
            lifevests_data.append(bbox)
    # 匹配人与救生圈的位置
    lifevests_idx = []
    for lifevest_data in lifevests_data:
        for i in range(len(persons_data)):
            if point_in_rect(persons_data[i], lifevest_data):
                lifevests_idx.append(i)
                break

    image_info = open(img_txt_path, "w", encoding="utf-8")

    for person_data in persons_data:
        person_txt_data = coor_xml2txt(imgw, imgh, person_data)
        image_info.write("0 " + " ".join(list(map(str, person_txt_data))) + "\n")

    for lifevest_data in lifevests_data:
        lifevest_txt_data = coor_xml2txt(imgw, imgh, lifevest_data)
        image_info.write("1 " + " ".join(list(map(str, lifevest_txt_data))) + "\n")

    image_info.close()


def get_person_then_lifevest_txt(xml_name, img_root, person_root):
    """"
    @xml_mane：josn的标签名称
    @img_root：原始图片的根目录
    @person_root：保存抠图的根目录
    """
    # 结果保存在个文件：原始图片中人的标签，抠图后的人的图片，以及人图片中救生衣的标签
    name = xml_name.split(".")[0]
    xml_path = os.path.join(img_root, xml_name)
    img_path = os.path.join(img_root, name + ".jpg")

    """
    读取json中的信息
    """
    # 保存人与救生圈的坐标信息
    persons_data, lifevests_data = [], []

    tree = ET.parse(xml_path)
    root = tree.getroot()
    # 图片的宽高
    size = root.find("size")
    imgw, imgh = float(size.find("width").text), float(size.find("height").text)
    # 每个目标的标签信息与位置信息
    for obj in root.findall("object"):
        class_name = obj.find("name").text
        bndbox = obj.find("bndbox")
        bbox = [float(bndbox.find(coor).text) for coor in ["xmin", "ymin", "xmax", "ymax"]]
        if class_name == "lifevest_person" or class_name == "no_lifevest_person":
            persons_data.append(bbox)
        elif class_name == "lifevest":
            lifevests_data.append(bbox)

    """
    输出人的标签信息txt
    """
    lifevest_idxs = []
    person_txt_path = os.path.join(img_root, name + ".txt")
    person_txt_info = open(person_txt_path, "w", encoding="utf-8")
    for j in range(len(persons_data)):
        person_txt_data = coor_xml2txt(imgw, imgh, persons_data[j])  # 坐标转换 真实坐标转换成归一化后的坐标
        person_txt_info.write("0 " + " ".join(list(map(str, person_txt_data))) + "\n")
        for i in range(len(lifevests_data)):
            if point_in_rect(persons_data[j], lifevests_data[i]):
                lifevest_idxs.append([j, i])

    person_txt_info.close()

    """
    输出救生衣的信息txt，已知人的坐标，救生衣坐标，以及人与救生衣间的映射关系：persons_data lifevests_data lifevest_idxs
    """
    org_img = cv2.imread(img_path)  # 原始图像

    for i in range(len(lifevest_idxs)):
        # 保存图片的信息
        person_name = name + f"_{str(i).zfill(2)}"
        person_img_path = os.path.join(person_root, person_name + ".jpg")
        lifevests_txt_path = os.path.join(person_root, person_name + ".txt")
        lifevest_txt_info = open(lifevests_txt_path, 'w', encoding="utf-8")

        person_data = persons_data[lifevest_idxs[i][0]]  # 人坐标信息
        lifevest_data = lifevests_data[lifevest_idxs[i][1]]  # 与人对应的救生衣坐标信息

        person_img = get_rect_img(org_img, person_data)  # 抠图

        cv2.imwrite(person_img_path, person_img)  # 保存图片信息
        w, h, box = fintune_rec(person_data, lifevest_data)
        lifevests_txt_data = coor_xml2txt(w, h, box)
        lifevest_txt_info.write("1 " + " ".join(list(map(str, lifevests_txt_data))) + "\n")
        lifevest_txt_info.close()


def main_get_person_lifevest_txt():
    # xml_name, img_root, person_root
    img_root = "/home/fb/freework/data/NJSK_lifevest_20210415done"
    person_root = "/home/fb/freework/data/person"
    if not os.path.exists(person_root):
        os.mkdir(person_root)
    for file_name in os.listdir(img_root):
        if not file_name.endswith("xml"):
            continue
        get_person_lifevest_txt(file_name, img_root, person_root)


def main_get_person_then_lifevest_txt():
    # xml_name, img_root, person_root
    img_root = "/home/fb/freework/data/NJSK_lifevest_20210415done"
    person_root = "/home/fb/freework/data/person"
    if not os.path.exists(person_root):
        os.mkdir(person_root)
    for file_name in os.listdir(img_root):
        if not file_name.endswith("xml"):
            continue
        get_person_then_lifevest_txt(file_name, img_root, person_root)


if __name__ == '__main__':
    main_get_person_then_lifevest_txt()
