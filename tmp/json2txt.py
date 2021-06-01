# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        json格式的标注转yolo的txt：文字识别的三个类别
"""
import json
import os, shutil, sys
import argparse

img_names = ["brass", "signalline", "insulation"]


def json2txt(root, json_name: str):
    json_path = os.path.join(root, json_name)
    txt_path = os.path.join(root, json_name.replace("json", "txt"))
    json_info = open(json_path, 'r', encoding='utf-8')
    txt_info = open(txt_path, "w", encoding='utf-8')

    data = json.load(json_info)
    image_name = data["imagePath"]
    image_width, image_height = data["imageWidth"], data["imageHeight"]
    for shape in data["shapes"]:
        # print(shape["label"])
        label = shape["label"]
        print(label.lower())
        print(shape["label"].isalpha())
        print(shape["label"].lower() in img_names)
        print((len(shape["points"]) == 4))
        try:
            if not shape["label"].isalpha() or shape["label"].lower() not in img_names or (len(shape["points"]) != 2):
                continue
            print(f'----------{shape["label"]}')
            points = shape["points"]
            for i in range(len(points)):
                points[i] = list(map(float, points[i]))
                print(points[i])
            print(points)
            cx, cy, w, h = round((points[0][0] + points[1][0]) / (2*image_width), 6), \
                           round((points[0][1] + points[1][1]) / (2*image_height), 6), \
                           round(abs(points[0][0] - points[1][0]) /image_width , 6), \
                           round(abs(points[0][1] - points[1][1]) /image_height , 6)
            txt_info.write(f"0 {str(cx)} {str(cy)} {str(w)} {str(h)}\n")
            print(f"{txt_path} is sucessful !")
        except:
            pass
    json_info.close()
    txt_info.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", '-r', type=str,
                        default="/home/fb/project/docker/DJKT_brass20210409test_data",
                        help="图片根目录")
    return parser.parse_args()


def main():
    args = parse_args()
    root = args.root
    for name in os.listdir(root):
        if not name.endswith("json"):
            continue
        json2txt(root, name)


if __name__ == '__main__':
    main()
