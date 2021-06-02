# convert_labels

解析成json格式如下：---针对一张图一个标注文件

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

解析标注文件格式如下：--针对所有的图片对应一个标注文件(coco数据格式)

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



dealing labels of dataset such as xml/json/coco/txt  ...
