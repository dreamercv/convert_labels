# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        获取标注文件中的标注信息：
            xml、txt、json后缀文件：()
            后缀文件：
            后缀文件：

            最终解析成json格式如下：---针对一张图一个标注文件
                annotations = {
                                "filename": "Sbelt_phone20200630_1.jpg",
                                "size": [
                                    4096.0,    float
                                    2288.0,
                                    3.0
                                ],
                                "objects": {
                                    "people": [
                                        [
                                            3146.7373046875,  float
                                            644.619140625,
                                            3361.5679931640625,
                                            819.6577301025391
                                        ],
                                        ...
                                    ]
                                }
                            }

            最终解析的标注文件格式如下：--针对所有的图片对应一个标注文件(coco数据格式)
            annotations =   {
                             "fn1.jpg":[
                                        {"height":1000, "width":1000, "bbox":[100.00, 200.00, 10.00, 10.00], "category_id": 1, "category_name": "people1" },
                                        {"height":1000, "width":1000, "bbox":[130.00, 260.00, 10.00, 10.00], "category_id": 2, "category_name": "people2"},
                                        {"height":1000, "width":1000, "bbox":[140.00, 777.00, 10.00, 10.00], "category_id": 3, "category_name": "people3"},
                                    ]，
                            "fn3.jpg":[
                                        {"height":1000, "width":1000, "bbox":[100.00, 200.00, 10.00, 10.00], "category_id": 1, "category_name": "people1"},
                                        {"height":1000, "width":1000, "bbox":[130.00, 260.00, 10.00, 10.00], "category_id": 22,"category_name": "people22"},
                                        {"height":1000, "width":1000, "bbox":[140.00, 777.00, 10.00, 10.00], "category_id": 5, "category_name": "people5"},
                                    ]，
                             ...
                            }
"""
import os, shutil
import json
import xml.etree.ElementTree as ET
from lxml import etree

post_name = ["jpg", "png"]


def read_names(name_path):
    names = []
    name_info = open(name_path, "r", encoding="utf-8")
    for name in name_info.readlines():
        name = name.strip().split()[0]
        names.append(name)
    return names


def split_train_val_test(root, val_ratio=0.2, test_ratio=0.4):
    dirs = []
    result = []
    for dir in dirs:
        dir_path = os.path.join(dir)
        for name in os.listdir(dir_path):
            if not name.split(".")[-1].lower() in post_name:
                continue
            file_path = os.path.join(dir_path, name)
            result.append(file_path)
    from random import shuffle, choice, seed

    num = len(result)
    len_val = int(num * val_ratio)
    len_test = int(num * test_ratio)
    seed(2021)
    shuffle(result)
    return result[:len_val], result[len_val:len_val + len_test], result[len_val + len_test:]


def save_txt(save_path, datas):
    txt_info = open(save_path, "w", encoding="utf-8")
    for data in datas:
        txt_info.write(str(data) + "\n")


def xywh2xyxy(box):
    x, y, w, h = box
    return [x, y, round(x + w, 3), round(y + h, 3)]


def get_iou(box1: list, box2: list):
    in_w = min(box1[2], box2[2]) - max(box1[0], box2[0])
    in_h = min(box1[3], box2[3]) - max(box1[1], box2[1])
    inter = 0 if in_h < 0 or in_w < 0 else in_h * in_w
    union = (box1[2] - box1[0]) * (box1[3] - box1[1]) + (box2[2] - box2[0]) * (box2[3] - box2[1]) - inter
    iou = inter / union
    return iou


def coor2txt(img_w, img_h, box_info, class_names):  # id,x,y,x,y
    '''

    :param img_w:
    :param img_h:
    :param box: {"name":[x,y,x,y]}
    :return: [id,cx,cy,w,h]--int,float
    '''
    print(box_info.keys())
    name = list(box_info.keys())[0]
    box = box_info[name]
    idx = class_names.index(name)
    xmin, ymin, xmax, ymax = box

    txt_box = [idx, (xmin + xmax) / (2 * img_w),
               (ymin + ymax) / (2 * img_h),
               abs(xmin - xmax) / img_w,
               abs(ymin - ymax) / img_h]

    for i in range(1, len(txt_box)):
        txt_box[i] = round(txt_box[i], 6)
    return txt_box


def txt2coor(img_w, img_h, box, class_names):
    '''
    yolo的坐标转成真实像素坐标
    :param img_w:
    :param img_h:
    :param box: [0 cx cy w h]
    :return: [name xmin ymin xmax ymax]
    '''
    name = class_names[int(box[0])]
    tbox = list(map(float, box[1:]))
    cx, cy, w, h = tbox
    bbox = [(cx - w / 2) * img_w, (cy - h / 2) * img_h, (cx + w / 2) * img_w, (cy + h / 2) * img_h]
    bbox.insert(0, name)
    return bbox


def save_txt_from_xml(org_root, dst_root, img_name, target_objects, img_w, img_h, class_names):
    '''
    :param org_root:
    :param dst_root:
    :param img_name:
    :param target_objects: [{k1:[[],[],[]...]}, {k2:[[],[],[]...]}, ...]
    :param img_w:
    :param img_h:
    :param class_names:
    :return:
    '''
    org_image_path = os.path.join(org_root, img_name)
    dst_image_path = os.path.join(dst_root, img_name)
    dst_txt_path = os.path.join(dst_root, img_name.split(".")[0] + ".txt")
    txt_info = open(dst_txt_path, "w", encoding="utf-8")
    for target_object in target_objects:
        for key, values in target_object.items():
            print("11111111111111")
            print(values)
            for value in values:
                txt_box = coor2txt(img_w, img_h, {key: value}, class_names)
                txt_info.write(" ".join(list(map(str, txt_box))) + "\n")
    if dst_root != org_root:
        shutil.copy(org_image_path, dst_image_path)
    txt_info.close()


def save_xml_from_txt(org_root, dst_root, annotation: dict):
    image_name = annotation["filename"]
    width, height, depth = annotation["size"]
    objects = annotation["objects"]
    org_image_path = os.path.join(org_root, image_name)
    dst_image_path = os.path.join(dst_root, image_name)
    dst_xml_path = os.path.join(dst_root, image_name.split(".")[0] + ".xml")
    xml_info = open(dst_xml_path, "w", encoding="utf-8")

    root = etree.Element("annotation")

    folder = etree.Element("folder")
    folder.text = "Unknow"

    filename = etree.Element("filename")
    filename.text = image_name

    source = etree.Element("source")
    database = etree.SubElement(source, "database")
    database.text = "Unknow"
    annotation = etree.SubElement(source, "annotation")
    annotation.text = "Unknow"
    image = etree.SubElement(source, "image")
    image.text = "Unknow"

    size = etree.Element("size")
    img_width = etree.SubElement(size, "width")
    img_width.text = str(width)
    img_height = etree.SubElement(size, "height")
    img_height.text = str(height)
    img_depth = etree.SubElement(size, "depth")
    img_depth.text = str(depth)

    segmented = etree.Element("segmented")
    segmented.text = "0"

    root.append(folder), root.append(filename), \
    root.append(source), root.append(size), root.append(segmented)

    for key, values in objects.items():
        for value in values:
            object = etree.Element("object")
            name = etree.SubElement(object, "name")
            name.text = key
            occluded = etree.SubElement(object, "occluded")
            occluded.text = "0"
            bndbox = etree.SubElement(object, "bndbox")
            xmin = etree.SubElement(bndbox, "xmin")
            xmin.text = str(value[0])
            ymin = etree.SubElement(bndbox, "ymin")
            ymin.text = str(value[1])
            xmax = etree.SubElement(bndbox, "xmax")
            xmax.text = str(value[2])
            ymax = etree.SubElement(bndbox, "ymax")
            ymax.text = str(value[3])

            root.append(object)

    xml = etree.tostring(root, pretty_print=True, encoding="utf-8")
    xml_info.write(xml.decode("utf-8"))
    xml_info.close()

    if org_image_path != dst_image_path:
        shutil.copy(org_image_path, dst_image_path)


def parse_xml(xml_path):
    '''
    读取xml文件，将信息封装成json格式
    :param xml_path: xml的路径
    :return:
    '''
    annotation = {}
    tree = ET.parse(xml_path)
    root = tree.getroot()

    annotation["filename"] = root.find("filename").text

    size = root.find("size")
    annotation["size"] = list(
        map(float, [(size.find("width").text), (size.find("height").text), (size.find("depth").text)]))
    objects = {}
    for obj in root.findall("object"):
        name = obj.find("name").text
        bnd_box = obj.find("bndbox")
        bbox = [float(bnd_box.find(coor).text) for coor in ["xmin", "ymin", "xmax", "ymax"]]
        if name not in objects.keys():
            objects[name] = [bbox]
        else:
            objects[name].append(bbox)
    annotation["objects"] = objects
    # json.load(annotation)
    print(json.dumps(annotation, indent=4))
    return annotation


def parse_txt(txt_path, img_w, img_h, depth, image_name, class_names):
    annotation = dict()
    annotation["filename"] = image_name
    annotation["size"] = [img_w, img_h, depth]
    annotation["objects"] = []

    txt_info = open(txt_path, "r", encoding='utf-8')
    objects = {}
    for line in txt_info.readlines():
        line_info = line.strip().split()
        box_info = txt2coor(img_w, img_h, line_info, class_names)
        name, bbox = box_info[0], box_info[1:]
        if name not in objects.keys():
            objects[name] = [bbox]
        else:
            objects[name].append(bbox)
    annotation["objects"] = objects
    print(json.dumps(annotation, indent=4))
    return annotation


def parse_coco(coco_path):
    json_info = open(coco_path, "r", encoding='utf-8')
    json_data = json.load(json_info)
    images = json_data["images"]
    annotations = json_data["annotations"]
    categories = json_data["categories"]

    images_info = dict()
    for image in images:
        image_idx = image["id"]
        images_info[image_idx] = image

    categories_info = dict()
    for category in categories:
        category_idx = category["id"]
        categories_info[category_idx] = category

    annotations_info = dict()
    for annotation in annotations:
        image_info = images_info[annotation["image_id"]]
        class_info = categories_info[annotation["category_id"]]
        image_name = image_info["file_name"]
        label_info = {"height": image_info["height"], "width": image_info["width"],
                      'bbox': xywh2xyxy(annotation["bbox"]),
                      "category_id": annotation["category_id"], "category_name": class_info["name"]}
        if image_name in annotations_info.keys():
            annotations_info[image_name].append(label_info)
        else:
            annotations_info[image_name] = [label_info]
    print(json.dumps(annotations_info, indent=4))
    return annotations_info


if __name__ == '__main__':
    # get_xml("/home/fb/freework/data/test518/Sbelt_phone20200630_1.xml")
    # bb = coor2txt(13, 12, {"people": (11, 12, 52, 65)})
    # print(bb)
    # box = txt2coor(13, 12, ["1", "2.423077", "3.208333", "4.153846", "4.416667"])
    # print(box)

    # parse_txt(
    #     "/home/fb/freework/data/lifevest/NJSK_lifevest_20210415done/NJSK_lifevest_none_none_none_train_none_day_20210415_1.txt",
    #     3840, 2160, 3, "NJSK_lifevest_none_none_none_train_none_day_20210415_1.jpg")

    parse_coco("/home/fb/project/docker/data/coco_data/annotations/instances_val2017.json")
