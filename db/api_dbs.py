#coding=utf-8
'''
Created on 2015年10月27日

@author: hzwangzhiwei
'''
from db.sqlite_utils import SqliteHandler
import config

def clean_table(table_name):
    sql = "delete from %s" % (table_name)
    return SqliteHandler().exec_sql(sql)

#批量插入有文档的api
def insert_apis(table_name, datas):
    sql = "insert into " + table_name + "(api_name, class_name, type, header_file, sdk, framework) values(:api_name, :class_name, :type, :header_file, :sdk, :framework)"
    return SqliteHandler().exec_insert_many(sql, datas)


def create_document_type_table(table_name):
    sql = "CREATE TABLE IF NOT EXISTS %s (\
              api_name varchar,\
              class_name varchar,\
              type varchar,\
              header_file varchar,\
              sdk varchar,\
              framework varchar)" % (table_name)
    SqliteHandler().exec_sql(sql)

def delete_apis_by_sdk(table_name, sdk):
    sql = "delete from " + table_name + " where sdk = ?;"
    return SqliteHandler().exec_update(sql, (sdk, ))


def get_private_api_list():
    sql = "select * from private_apis group by api_name;"
    params = ()
    return SqliteHandler().exec_select(sql, params)


def get_document_apis(sdk = config.sdks_config[0]["sdk"]):
    sql = "select * from document_apis where sdk = ?"
    params = (sdk, )
    return SqliteHandler().exec_select(sql, params)

def get_document_apis_type(type_name, sdk = config.sdks_config[0]["sdk"]):
    sql = "select * from document_apis_type_%s where sdk = ?" % (type_name)
    params = (sdk, )
    return SqliteHandler().exec_select(sql, params)

def delete_apis_from_private_apis(api_name, framework, class_name, sdk):
    sql = "delete from private_apis where api_name = '%s' and class_name = '%s' and framework = '%s' and sdk = '%s'" % (api_name, class_name, framework,  sdk)
    return SqliteHandler().exec_update(sql)

#获得所有的私有框架dump出来的api
def get_private_framework_dump_apis(sdk):
    sql = "select * from private_framework_dump_apis where sdk = ?"
    params = (sdk, )
    return SqliteHandler().exec_select(sql, params)

#获得所有的共有框架dump出来的api
def get_framework_dump_apis(sdk):
    sql = "select * from framework_dump_apis where sdk = ?"
    params = (sdk, )
    return SqliteHandler().exec_select(sql, params)

def get_private_apis(private=None, public=None):
    where_content = ""
    if (private != None and len(private) > 0):
        for single_private in private:
            if (single_private.endswith(".framework") == False):
                single_private = "%s.framework" % (single_private)
            where_content += "'%s'," % (single_private)

    if (public != None and len(public) > 0):
        for single_public in public:
            if (single_public.endswith(".framework") == False):
                single_public = "%s.framework" % (single_public)
            where_content += "'%s'," % (single_public)

    if (len(where_content) > 0):
        where_content = "(%s)" % (where_content[0:-1])
        sql = "select * from private_apis where framework in %s group by api_name;" % (where_content)
    else:
        sql = "select * from private_apis group by api_name;"
    params = ()
    return SqliteHandler().exec_select(sql, params)

def get_framework_private_apis():
    sql = "select * from framework_private_apis group by api_name;"
    params = ()
    return SqliteHandler().exec_select(sql, params)

def is_api_exist_in_with_framework(table_name, api_name, framework, sdk):
    sql = "select * from " + table_name + " where api_name = ? and framework = ? and sdk = ?;"

    if (framework.endswith(".framework") == False):
        framework = "%s.framework" % (framework)

    params = (api_name, framework, sdk)
    return SqliteHandler().exec_select_one(sql, params)

def is_api_exist_in(table_name, api_name, api_class, sdk):
    sql = "select * from " + table_name + " where api_name = ? and class_name = ? and sdk = ?;"
    params = (api_name, api_class, sdk)
    return SqliteHandler().exec_select_one(sql, params)

def is_api_exist_in_private_apis(api_name):
    sql = "select * from private_apis where api_name = '%s'" %(api_name)
    return SqliteHandler().exec_select_one(sql)