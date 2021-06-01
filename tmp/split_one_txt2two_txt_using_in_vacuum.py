# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        
"""
import os, sys
import shutil
import cv2
import argparse

# 0 1 2 3 4 5 6 7 8 9
# 0 1 2 3 4 5 6 p p c
zero_id = "0"
between_id = "1"
pointer_id = "2"
panel_id = "3"
center_id = "4"

# new_idxs = ["0","1","2","3"]
new_zero = "0"
new_between = "1"
new_pointer = "2"
new_center = "3"


def center2rect(coor_data):
    return [float(coor_data[1]) - float(coor_data[3]) / 2,
            float(coor_data[2]) - float(coor_data[4]) / 2,
            float(coor_data[1]) + float(coor_data[3]) / 2,
            float(coor_data[2]) + float(coor_data[4]) / 2]


def get_iou(box1: list, box2: list):
    in_w = min(box1[2], box2[2]) - max(box1[0], box2[0])
    in_h = min(box1[3], box2[3]) - max(box1[1], box2[1])
    inter = 0 if in_h < 0 or in_w < 0 else in_h * in_w
    union = (box1[2] - box1[0]) * (box1[3] - box1[1]) + (box2[2] - box2[0]) * (box2[3] - box2[1]) - inter
    iou = inter / union
    return iou


def txt2coor(img_w, img_h, txt_data):
    id, txt_x, txt_y, txt_w, txt_h = txt_data
    center_x, center_y, bbox_w, bbox_h = \
        int(float(txt_x) * img_w), int(float(txt_y) * img_h), int(float(txt_w) * img_w), int(float(txt_h) * img_h)
    return [int(id), center_x, center_y, bbox_w, bbox_h]


def coor2txt(img_w, img_h, coor_data):
    id, center_x, center_y, bbox_w, bbox_h = coor_data
    txt_x, txt_y, txt_w, txt_h = \
        round(center_x / img_w, 6), round(center_y / img_h, 6), round(bbox_w / img_w, 6), round(bbox_h / img_h, 6)
    return f"{str(id)} {str(txt_x)} {str(txt_y)} {str(txt_w)} {str(txt_h)}"


def classify_split_panel(root, panels_root, panels_info_root, txt_name: str, img):
    panel_datas = []  # 盘数据
    panel_in_datas = []  # 盘内数据
    img_h, img_w, _ = img.shape
    # 盘与盘内的数据分开
    with open(os.path.join(root, txt_name), "r", encoding="utf-8") as txt_info:
        with open(os.path.join(panels_root, txt_name), "w+", encoding='utf-8') as panel_location:
            txt_datas = txt_info.readlines()
            for txt_data in txt_datas:
                txt_data = txt_data.strip().split()
                if txt_data[0] == panel_id:
                    # 保存盘的坐标信息为 txt
                    shutil.copy(os.path.join(root, txt_name.replace("txt", "jpg")),
                                os.path.join(panels_root, txt_name.replace("txt", "jpg")))

                    panel_location.write(f"0 {txt_data[1]} {txt_data[2]} {txt_data[3]} {txt_data[4]}\n")
                    panel_datas.append(txt_data)
                else:
                    panel_in_datas.append(txt_data)

    # 将数据按照盘归类
    panel_count = 0
    for panel_data in panel_datas:
        rect_panel = center2rect(panel_data)
        panel_count += 1
        new_txt_name = txt_name.split(".")[0] + f"_{str(panel_count).zfill(2)}.txt"
        new_img_name = new_txt_name.replace("txt", "jpg")
        coor_data = txt2coor(img_w, img_h, panel_data)
        x1 = coor_data[1] - coor_data[3] // 2 if (coor_data[1] - coor_data[3] // 2) > 0 else 0
        y1 = coor_data[2] - coor_data[4] // 2 if (coor_data[2] - coor_data[4] // 2) > 0 else 0
        x2 = coor_data[1] + coor_data[3] // 2 if (coor_data[1] + coor_data[3] // 2) < img_w else img_w
        y2 = coor_data[2] + coor_data[4] // 2 if (coor_data[2] + coor_data[4] // 2) < img_h else img_h
        new_img = img[y1:y2, x1:x2]

        cv2.imwrite(os.path.join(panels_info_root, new_img_name), new_img)

        with open(os.path.join(panels_info_root, new_txt_name), "w", encoding="utf-8") as panel_in_info:

            for panel_in_data in panel_in_datas:
                rect_in_panel = center2rect(panel_in_data)
                if get_iou(rect_panel, rect_in_panel) > 0.0:
                    if panel_in_data[0] == zero_id:
                        panel_in_data[0] = new_zero
                    elif panel_in_data[0] == between_id:
                        panel_in_data[0] = new_between
                    elif panel_in_data[0] == pointer_id:
                        panel_in_data[0] = new_pointer
                    elif panel_in_data[0] == center_id:
                        panel_in_data[0] = new_center
                    else:
                        continue
                    in_coor_data = txt2coor(img_w, img_h, panel_in_data)
                    in_coor_data[1], in_coor_data[2] = \
                        in_coor_data[1] - (coor_data[1] - coor_data[3] / 2), \
                        in_coor_data[2] - (coor_data[2] - coor_data[4] / 2)
                    res = coor2txt(coor_data[3], coor_data[4], in_coor_data)

                    panel_in_info.write(res + "\n")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str, default="", help="root")
    parser.add_argument('--panels_root', type=str, default="", help="save_root")
    parser.add_argument('--panels_info_root', type=str, default="", help="repeat")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    root = args.root
    panels_root = args.panels_root
    panels_info_root = args.panels_info_root
    if not os.path.exists(panels_root):
        os.mkdir(panels_root)
    if not os.path.exists(panels_info_root):
        os.mkdir(panels_info_root)
    names = os.listdir(root)
    for name in names:
        if not name.endswith("txt"):
            continue
        img_name = name.replace("txt", "jpg")
        img = cv2.imread(os.path.join(root, img_name))
        classify_split_panel(root, panels_root, panels_info_root, name, img)
