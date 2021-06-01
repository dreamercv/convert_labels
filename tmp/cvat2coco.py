# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        converting the labels from cvat to coco for keupoints
        
"""
import json, os
import numpy as np
import shutil

num_points = 9
pointer_scope = 6
nums = [str(i) for i in range(pointer_scope + 1)]
pointer = "指针"
is_show_image = False

coco_anno = {
    "info": {
        "version": "1.0",
        "description": "baoya Dataset",
        "year": 2021,
        "contributor": "",
        "url": "",
        "date_created": "2021/03/08"
    },
    "licenses": [
        {
            "id": 1,
            "name": "Attribution-NonCommercial-ShareAlike License",
            "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
        },
        {
            "id": 2,
            "name": "Attribution-NonCommercial License",
            "url": "http://creativecommons.org/licenses/by-nc/2.0/"
        }
    ],
    "categories": [
        {
            "skeleton": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 0],
                         [0, 7], [1, 7], [2, 7], [3, 7], [4, 7], [5, 7], [6, 7],
                         [7, 8]],
            "name": "yibiao",  # 子类（具体类别）
            "supercategory": "yibiao",  # 主类
            "id": 1,  # class id
            "keypoints": ["num_0", "num_1", "num_2", "num_3", "num_4", "num_5", "num_6",
                          "num_center", "num_head"]
        }
    ]

}


def get_center(points):
    x1, y1 = points[0][0], points[0][1]
    x2, y2 = points[2][0], points[2][1]
    return int((x1 + x2) / 2), int((y1 + y2) / 2)


def get_dist(point1, point2):
    point1 = np.array(point1)
    point2 = np.array(point2)
    return np.linalg.norm(point1 - point2)


def get_json_info(json_path):
    """
    :param json_path:
    :return:
        annotations : num_keypoints,keypoints
        images      : image_height,image_weight,image_name
    """
    keypoints = [0] * (3 * num_points)
    is_instrument = 0
    instrument_center = [0, 0]
    is_pointer = 0
    pointer_points = [[0, 0], [0, 0]]
    num_instrument = 0
    with open(json_path, "r", encoding='utf-8') as json_info:
        json_data = json.load(json_info)
        image_name = json_data["imagePath"]
        image_height, image_weight = json_data["imageHeight"], json_data["imageWidth"]
        num_keypoints = 0
        for shape in json_data["shapes"]:
            label, points = shape["label"], shape["points"]
            if label in nums:
                x, y = get_center(points)
                num_index = nums.index(label)
                keypoints[num_index * 3], keypoints[num_index * 3 + 1], keypoints[num_index * 3 + 2] = x, y, 2
                num_keypoints += 1
            elif label == pointer:
                is_pointer = 1
                num_keypoints += 2
                pointer_points[0][0], pointer_points[0][1], pointer_points[1][0], pointer_points[1][1] = points[0][0], \
                                                                                                         points[0][1], \
                                                                                                         points[1][0], \
                                                                                                         points[1][1]
            elif label == "仪表盘":
                is_instrument = 1
                num_instrument += 1
                instrument_center[0], instrument_center[1] = get_center(points)
                print(f"labels is not useful such as {label}")
        if is_instrument == 1 and is_pointer == 1:
            dist1 = get_dist(instrument_center, pointer_points[0])
            dist2 = get_dist(instrument_center, pointer_points[1])
            print(dist2, dist1)
            if dist1 > dist2:
                keypoints[7 * 3], keypoints[7 * 3 + 1], keypoints[7 * 3 + 2] = \
                    int(pointer_points[1][0]), int(pointer_points[1][1]), 2
                keypoints[8 * 3], keypoints[8 * 3 + 1], keypoints[8 * 3 + 2] = \
                    int(pointer_points[0][0]), int(pointer_points[0][1]), 2
            else:
                keypoints[7 * 3], keypoints[7 * 3 + 1], keypoints[7 * 3 + 2] = \
                    int(pointer_points[0][0]), int(pointer_points[0][1]), 2
                keypoints[8 * 3], keypoints[8 * 3 + 1], keypoints[8 * 3 + 2] = \
                    int(pointer_points[1][0]), int(pointer_points[1][1]), 2

    return image_height, image_weight, image_name, num_keypoints, keypoints, is_instrument, num_instrument


def generate_coco_anno(save_anno_path, jsons_root, save_image_root):
    """
    :param save_anno_path:
    :param jsons_root:
    :return:
        annotations:    "iscrowd":          0,
                        "bbox":             [],
                        "segmentation":     [],
                        "category_id":      1，
                        "area"：            200
                        "image_id":         image_id,
                        "num_keypoints":    num_keypoints,
                        "id":               image_id,
                        "keypoints":        keypoints

        images：        "id":            image_id，
                        "height":       image_height
                        "width"：       image_weight
                        "file_name":   image_name
    """
    if not os.path.exists(save_image_root):
        os.mkdir(save_image_root)

    json_list = os.listdir(jsons_root)
    image_id = 1
    annotations, images = [], []
    for json_name in json_list:
        if not json_name.endswith("json"):
            continue
        json_path = os.path.join(jsons_root, json_name)
        print(f"-------------json_path-------------{json_path}---------------")

        image_height, image_weight, image_name, num_keypoints, keypoints, is_instrument, num_instrument = \
            get_json_info(json_path)
        print(f"-------------num_keypoints-------------{num_keypoints}---------------")
        if is_instrument == 1 and num_instrument == 1 and num_keypoints <= 9:
            org_image_name = image_name
            dist_image_name = str(image_id).zfill(6) + ".jpg"
            shutil.copy(os.path.join(jsons_root, org_image_name), os.path.join(save_image_root, dist_image_name))

            if is_show_image:
                import cv2
                img = cv2.imread(os.path.join(jsons_root, org_image_name))
                print(keypoints)
                for i in range(num_points):
                    cv2.circle(img, (int(keypoints[i * 3]), int(keypoints[i * 3 + 1])), 5, (0, 255, 0), 2)
                    cv2.putText(img, str(i), (int(keypoints[i * 3]), int(keypoints[i * 3 + 1])),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
                cv2.imwrite(os.path.join(save_image_root, dist_image_name), img)

            annotation = {"iscrowd": 0,
                          "bbox": [200, 200, 400, 400],
                          "segmentation": [
                              [1713.1481481481478, 1025.9259259259259], [1865.0, 1122.2222222222222],
                              [1976.1111111111109, 1251.8518518518517], [2061.296296296296, 1407.4074074074074],
                              [2127.9629629629626, 1700.0], [2102.037037037037, 1877.7777777777776],
                              [2020.5555555555552, 2144.4444444444443],
                              [1909.4444444444443, 2281.4814814814813], [1709.4444444444443, 2437.037037037037],
                              [1550.1851851851848, 2511.111111111111], [1298.333333333333, 2551.8518518518517],
                              [1009.4444444444443, 2533.333333333333], [827.9629629629626, 2362.9629629629626],
                              [679.8148148148148, 2255.555555555555], [572.4074074074074, 2051.8518518518517],
                              [513.1481481481478, 1911.111111111111],
                              [479.8148148148148, 1770.3703703703702], [505.74074074074065, 1607.4074074074074],
                              [583.5185185185182, 1448.148148148148], [642.7777777777778, 1307.4074074074074],
                              [750.1851851851852, 1166.6666666666665], [894.6296296296296, 1103.7037037037037],
                              [1013.1481481481478, 1040.7407407407406], [1168.7037037037035, 1014.8148148148148],
                              [1350.1851851851852, 977.7777777777777],
                              [1539.074074074074, 974.074074074074], [1672.4074074074074, 1007.4074074074074]],
                          "category_id": 1,
                          "area": 2000,
                          "image_id": image_id,
                          "num_keypoints": num_keypoints,
                          "id": image_id,
                          "keypoints": keypoints
                          }
            image = {"id": image_id,
                     "height": image_height,
                     "width": image_weight,
                     "file_name": dist_image_name}
            image_id += 1
            annotations.append(annotation)
            images.append(image)
    coco_anno["annotations"] = annotations
    coco_anno["images"] = images

    with open(save_anno_path, 'w', encoding='utf-8') as coco:
        json.dump(coco_anno, coco, indent=4)
    res = json.dumps(coco_anno, indent=4)
    # print(res)
    return coco_anno


if __name__ == '__main__':
    generate_coco_anno("/home/fb/project/docker/data/DJKT/train.json",
                       "/home/fb/project/docker/data/DJKT/baoya",
                       "/home/fb/project/docker/data/DJKT/train")
