# convert_labels

> 思路：将所有的标注文件统一成`json`格式的信息，在将`json`转成相应的标注格式。
>
> `pipline`：
>
> ​	1、在`config.py`中增加自定义配置文件；
>
> ​	2、在`convert_label.py`编写自定义类函数并且实现功能。
>
> ​	

### 修改配置文件

```python
xml2txt_txt, xml2txt, txt2xml = False, False, True

if xml2txt_txt:
    # 针对抠图的配置参数
    total_names = ["glass", "people", "vehicle", "belt", "driving", "phone", "using_phone"]
    target_names = ["glass", "vehicle"]
    cutout_names = ["glass"]
    in_target_names = ["people", "belt", "driving", "phone", "using_phone"]
    org_root = "/home/fb/freework/data/phone_safe"
    dst_target_root = "/home/fb/freework/data/phone_safe_target"
    dst_in_target_root = dst_target_root

if xml2txt:
    org_root = "20"
    dst_root = "20"
    class_names = ["0", "1", "2", "3"]

if txt2xml:
    # 争对单张txt转xml
    org_root = "20"
    dst_root = "20"
    class_names = ["0", "1", "2", "3"]

```

### 实例化并转换

> 支持的数据转换：`xml转txt（抠图与不扣图）、txt转xml`

```python
if xml2txt_txt:
    # 抠图并保存
    convert_xml = Convert_xml_to_txt_txt(total_names, cutout_names, target_names, in_target_names, org_root,dst_target_root,dst_in_target_root)
    convert_xml.main_split_xmls_to_tow_txts()
if xml2txt:
    # 不抠图直接保存
    convert_xml_txt = Convert_xml_to_txt(org_root, class_names)
    convert_xml_txt.main_xmls_to_txts()
if txt2xml:
    # yolo的txt转xml
    convert_txt = Convert_txt_to_xml(org_root, dst_root, class_names)
    convert_txt.main_txts_to_xmls()
```

### `json`格式解析

> 解析成`json`格式如下：针对一张图一个标注文件

```python
annotations = 
    {
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
```

> 解析成`json`格式如下：针对所有的图片对应一个标注文件(`coco`数据格式转通用`json`)

```python
annotations =   
    {
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
```


