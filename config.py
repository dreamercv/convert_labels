# encoding utf-8
"""
    @author: Binge.Van
    @input:
    #outut:
    @desc:
        
"""
xml2txt_txt, xml2txt, txt2xml = False, False, True

if xml2txt_txt:
    # 针对抠图的配置参数
    '''
        **针对xml--xml、xml**
    total_names ： 参与训练的所有的类别 --> list[str]
    target_names ：不在子图内的所有目标 --> list[str]
    cutout_names  : 需要抠图的目标 --> list[str]
    in_target_names ：在子图内的目标 --> list[str]
    org_root ： 标注数据的源文件 --> str
    dst_target_root 存放原图与目标标注文件的根目录 
    dst_in_target_root 存放子图与目标标注文件的根目录 
    '''
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
