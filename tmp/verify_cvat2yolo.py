# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        对转换后的标注可视化，验证修改的脚本是否正确,可视化txt文件
        
"""

import cv2
import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=str,
                        default="/home/fb/freework/data/demo",
                        help="root")
    parser.add_argument('--save_root', type=str,
                        default="/home/fb/freework/data/ver",
                        help="save_root")
    parser.add_argument('--repeat', type=int, default=100, help="repeat")
    return parser.parse_args()


def txt2coor(root, save_root, txt_name: str):
    image_name = txt_name.replace("txt", "jpg")
    image_path = os.path.join(root, image_name)
    img = cv2.imread(image_path)
    img_h, img_w, _ = img.shape
    print(f"image_name: {image_name}")
    print(f"img_w: {img_w}  img_h: {img_h}")

    with open(os.path.join(root, txt_name), 'r', encoding='utf-8') as txt_info:
        for line in txt_info.readlines():
            line = line.strip().strip("\n")
            print(f"    line: {line}")
            line_list = line.split(" ")
            cx, cy, w, h = \
                int(float(line_list[1]) * img_w), \
                int(float(line_list[2]) * img_h), \
                int(float(line_list[3]) * img_w), \
                int(float(line_list[4]) * img_h)
            cv2.rectangle(img, (cx - (w // 2), cy - (h // 2)), (cx + (w // 2), cy + (h // 2)), (0, 0, 255), 2)
            cv2.putText(img, line_list[0], (cx - (w // 2), cy - (h // 2)), cv2.FONT_HERSHEY_SIMPLEX, 4,
                        (0, 255, 0), 2, cv2.LINE_8, 0)

        cv2.imwrite(os.path.join(save_root, image_name), img)


if __name__ == '__main__':
    import logging

    args = parse_args()
    root = args.root
    save_root = args.save_root
    repeat = args.repeat

    if not os.path.exists(save_root):
        os.mkdir(save_root)

    names = os.listdir(root)
    count = 0
    for name in names:
        if not name.endswith("txt"):
            continue
        print(name)
        try:
            if count > repeat:
                break
            txt2coor(root, save_root, name)
            count += 1

        except:
            pass
    '''
    python verify_cvat2yolo.py \
    --root /home/fb/project/docker/data/dakin_ocr_dataset/insulation_test/DJKT_insulation20210409done \
    --save_root /home/fb/project/docker/data/dakin_ocr_dataset/res/detect_others_add_head_verify \
    --repeat 100
    '''
