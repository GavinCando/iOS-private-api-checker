#coding=utf-8
'''
Created on 2015年10月27日
iOS private api检查入口
@author: hzwangzhiwei
'''
import os
from dump import otool_utils
from api import app_utils, api_utils
from db import api_dbs

def check(ipa_path):
    if not os.path.exists(ipa_path):
        #不存在，返回检查结果为空值
        print "被测应用不存在... exit()"
        return [], [], []

    #创建结果存放文件夹
    cur_dir = os.getcwd()
    dest = os.path.join(cur_dir, 'result')
    if (os.path.exists(dest) == True):
        os.system("rm -rf %s" % (dest))
    os.mkdir(dest)

    app_path = app_utils.unzip_ipa(ipa_path, dest) #解压ipa，获得xxx.app目录路径
    
    app = app_utils.get_executable_file(app_path)

    strings = app_utils.get_app_strings(app) #一般是app中的一些可打印文本

    #app中的私有库和公有库 .framework
    private, public = otool_utils.otool_app(app)

    #使用class-dump 获得ipa 中函数信息
    app_varibles = app_utils.get_app_variables(app)

    left_without_document_apis = strings - app_varibles #去除一些关键字，剩余app中的一些关键词


    #2)去除app中的 config.build_type 信息
    import config
    for build_type in config.build_type_list:
        print "="*50
        print "document 匹配 %s:" % (build_type)
        print "*"*50
        document_set_type_apis = api_dbs.get_document_apis_type(build_type)
        left_without_document_apis = api_utils.not_intersection_api(left_without_document_apis, document_set_type_apis, build_type)
        print "*"*50

    # app中的api和数据库中的私有api取交集，获得app中的私有api关键字数据
    # api_set = api_dbs.get_framework_private_apis() #数据库中的私有api


    # gavincui change 2016-03-31 在获得私有库中的内容时, 根据ipa所使用的系统库做一个筛选
    api_set = api_dbs.get_private_apis() #数据库中的私有api
    # api_set = api_dbs.get_private_apis(private, public) #数据库中的私有api
    #gavincui change end

    inter_api = api_utils.intersection_list_and_api(left_without_document_apis, api_set)
    
    app_methods = app_utils.get_app_methods(app) #app中的方法名
    app_apis = []
    for m in app_methods:
        class_name = m["class"] if m["class"] != "ctype" else 'cur_app'
        method_list = m["methods"]
        m_type = m["type"]
        for m in method_list:
            tmp_api = {}
            tmp_api['api_name'] = m
            tmp_api['class_name'] = class_name
            tmp_api['type'] = m_type
            app_apis.append(tmp_api)
    
    
    methods_in_app = api_utils.intersection_api(app_apis, api_set) #app中的私有方法
    methods_not_in_app = inter_api# inter_method - methods_in_app # 不在app中的私有方法
    
    return methods_in_app, methods_not_in_app, private


if __name__ == '__main__':
    nowPath = os.getcwd()
    ipa_path = "%s/target/3.7-release-QQSportsV3.ipa" % (nowPath)
    # ipa_path = "%s/target/TencentSports_reject.ipa" % (nowPath)
    # ipa_path = "%s/target/QQNews_248.ipa" % (nowPath)
    # ipa_path = "%s/target/TencentSports 2016-03-09 13-10-08.ipa" % (nowPath)
    # ipa_path = "/Users/cuiyuan/Downloads/tencentvideo_4.8.0.11810_iphone_r117646_fa_bu_sign.ipa"

    a, b, c = check(ipa_path)

    #将strings内容输出到文件中
    private_1 = open("result/private_1.txt", "w")
    private_2 = open("result/private_2.txt", "w")

    print "=" * 50
    print len(a), "Private Methods in App:"
    print "*" * 50
    for aa in a:
        print aa
        print >>private_1, aa

    print "=" * 50
    print len(b), "Private Methods not in App, May in Framework Used:"
    print "*" * 50
    for bb in b:
        print >>private_2, bb["api_name"]
        # print "%s\t%s\t%s" % (bb["class_name"],bb["api_name"],bb["framework"])

    print "=" * 50
    print len(c), "Private Framework in App:"
    print "*" * 50
    for cc in c:
       print cc
