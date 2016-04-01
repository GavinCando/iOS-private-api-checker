#coding=utf-8
'''
Created on 2015年10月27日
一些预处理脚本
@author: hzwangzhiwei
'''
import config
from db import api_dbs
from db import other_dbs
from api import api_utils
from config import sdks_config
from api.api_utils import framework_dump_apis

#重建document api数据库
def rebuild_document_api(sdk, docset):
    #先删除对应的sdk document api数据
    # api_dbs.delete_apis_by_sdk('document_apis', sdk)
    # document_apis = api_utils.document_apis(sdk, docset, "('instp')")
    # print "%s 新增:" % ("document_apis")
    # print api_dbs.insert_apis('document_apis', document_apis)


    for build_type in config.build_type_list:
        if (build_type == "structdata"):
            print "111"
        table_name = "document_apis_type_%s" % (build_type)
        api_dbs.create_document_type_table(table_name)
        api_dbs.delete_apis_by_sdk(table_name, sdk)
        document_apis = api_utils.document_apis(sdk, docset, "('%s')" % (build_type))
        print "%s 新增:" % (table_name)
        print api_dbs.insert_apis(table_name, document_apis)

def rebuild_framework_header_api(sdk, framework_folder):
    api_dbs.delete_apis_by_sdk('framework_header_apis', sdk)
    
    framework_header_apis = api_utils.framework_header_apis(sdk, framework_folder)
    
    return api_dbs.insert_apis('framework_header_apis', framework_header_apis)


def rebuild_dump_framework_api(sdk, framework_folder):
    api_dbs.delete_apis_by_sdk('framework_dump_apis', sdk)
    
    framework_dump_header_apis = api_utils.framework_dump_apis(sdk, framework_folder)
    
    return api_dbs.insert_apis('framework_dump_apis', framework_dump_header_apis)

def rebuild_dump_private_framework_api(sdk, framework_folder):
    api_dbs.delete_apis_by_sdk('private_framework_dump_apis', sdk)
    
    pri_framework_dump_apis = api_utils.private_framework_dump_apis(sdk, framework_folder)
    pri_framework_dump_apis = api_utils.deduplication_api_list(pri_framework_dump_apis)
    #for api in pri_framework_dump_apis:
    #    print api
    
    return api_dbs.insert_apis('private_framework_dump_apis', pri_framework_dump_apis)


def rebuild_sdk_private_api(sdk_version):
    api_dbs.delete_apis_by_sdk('framework_private_apis', sdk_version['sdk'])
    api_dbs.delete_apis_by_sdk('private_apis', sdk_version['sdk'])

    print rebuild_framework_header_api(sdk_version['sdk'], sdk_version['framework'])
    print rebuild_dump_framework_api(sdk_version['sdk'], sdk_version['framework'])
    print rebuild_dump_private_framework_api(sdk_version['sdk'], sdk_version['private_framework'])



    #清理私有api最终结果库
    api_dbs.clean_table('private_apis')

    #通过计算，获得私有api，并保存到数据库汇总
    private_framework_apis = api_dbs.get_private_framework_dump_apis(sdk_version['sdk'])

    #1. private_framework_api 转存到private表中
    print 'One private api. count: ', api_dbs.insert_apis('private_apis', private_framework_apis)

    #2. framework_dump - framework_header
    #3. framework_dump中_开头的api
    framework_dump_private_apis = []
    framework_dump_apis = api_dbs.get_framework_dump_apis(sdk_version['sdk'])

    len_framework_dump_apis = len(framework_dump_apis)
    for count in range(len_framework_dump_apis):
        api = framework_dump_apis[count]
        if api['api_name'] and api['api_name'][0:1] == '_':
            print 'api start with `_`\tclass_name:%s\tapi_name:%s\tsdk version:%s ... %d/%d' % (api['class_name'], api['api_name'], api['sdk'], count, len_framework_dump_apis)
            framework_dump_private_apis.append(api)
            continue
        #对于不以下划线开头的
        r = api_dbs.is_api_exist_in('framework_header_apis', api['api_name'], api['class_name'], api['sdk'])
        if r:
            print 'api is public in public framework\tclass_name:%s\tapi_name:%s\tsdk version:%s ... %d/%d' % (api['class_name'], api['api_name'], api['sdk'], count, len_framework_dump_apis)
            pass
        else:
            print 'api is private in public framework\tclass_name:%s\tapi_name:%s\tsdk version:%s ... %d/%d' % (api['class_name'], api['api_name'], api['sdk'], count, len_framework_dump_apis)
            framework_dump_private_apis.append(api)

    #framework_dump_private_apis = framework_dump_private_apis + list(private_framework_apis)
    print 'count of private apis in Public Framework:', len(framework_dump_private_apis)
    print 'start group by...'
    framework_dump_private_apis = api_utils.deduplication_api_list(framework_dump_private_apis)
    print 'deduplication private api len:', len(framework_dump_private_apis)
    rst = api_dbs.insert_apis('private_apis', framework_dump_private_apis)
    print 'insert into db private_apis, len:', rst
    rst = api_dbs.insert_apis('framework_private_apis', framework_dump_private_apis)
    print 'insert into db framework_private_apis, len:', rst

    #gavin add 最后 将包含在 private_apis 中的 document_apis 里面的 从 private_apis中剔除掉
    # print "check if document apis in private_apis ..."
    # document_apis = api_dbs.get_document_apis(sdk_version['sdk'])
    # lenDocumentApis = len(document_apis)
    # for count_document_api in range(lenDocumentApis):
    #     single_document_api = document_apis[count_document_api]
    #
    #     if (single_document_api["api_name"] == "initWithIndexSet:"):
    #         print  single_document_api
    #         print count_document_api
    #         # exit()
    #     else:
    #         continue
    #
    #     print "check sdk:%s api_name:%s framework:%s class_name:%s ... %d/%d" % (single_document_api["sdk"], single_document_api["api_name"], single_document_api["framework"], single_document_api["class_name"], count_document_api, lenDocumentApis)
    #     import re
    #     if (single_document_api["framework"] == None):
    #         if (single_document_api["header_file"] != None):
    #             if (single_document_api["header_file"] == "/usr/include/objc/NSObject.h"):
    #                 single_document_api["framework"] = "Foundation"
    #             elif (len(re.findall('/usr/include/dispatch/.*.h',single_document_api["header_file"])) > 0):#GCD pass
    #                 continue
    #             elif (single_document_api["header_file"] == "/usr/include/objc/runtime.h"):
    #                 continue
    #             elif (single_document_api["header_file"] == "/usr/include/objc/objc.h"):
    #                 continue
    #             elif (single_document_api["header_file"] == "/usr/include/objc/message.h"):
    #                 continue
    #             elif (single_document_api["header_file"] == "/usr/include/objc/objc-auto.h"):
    #                 continue
    #             else:
    #                 print single_document_api
    #                 exit()
    #         else:
    #             print single_document_api
    #             exit()
    #
    #     r = api_dbs.is_api_exist_in_with_framework("private_apis", single_document_api["api_name"], single_document_api["framework"], single_document_api["sdk"])
    #     if r:#document中的api在private_apis里面
    #         api_dbs.delete_apis_from_private_apis(r["api_name"], r["framework"], r["class_name"], r["sdk"])
    #         print "document api is in private apis api_name:%s class_name:%s sdk:%s" % (single_document_api["api_name"], single_document_api["class_name"], single_document_api["sdk"])
    #         print single_document_api

    
if __name__ == '__main__':
    pass

    # print other_dbs.create_some_table()
    # #重建sdk=9.3的有文档api
    # rebuild_document_api('9.3', '9.3-docSet.dsidx')
    
    for sdk_version in sdks_config:
        rebuild_sdk_private_api(sdk_version)



