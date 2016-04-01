#coding=utf-8
'''
Created on 2015年10月29日

@author: hzwangzhiwei
'''
import re
import os
import subprocess
from api import api_helpers
from dump import class_dump_utils
import zipfile

def unzip_ipa(ipa_path, dest_path):
    '''
    unzip a ipa, and return the zip folder
    '''
    file_zip = zipfile.ZipFile(ipa_path, 'r')
    for f in file_zip.namelist():
        file_zip.extract(f, dest_path)
    file_zip.close()
    return os.path.join(dest_path, 'Payload')

def get_executable_file(path):
    '''
    info:从ipa中解压出Payload目录中的xxx.app，扫描其中的文件，寻找 Mach-O 文件的路径
    '''
    for f in os.listdir(path):
        #TODO
        if f != '.DS_Store':
            path = os.path.join(path, f)
            break

    regex = re.compile(".*?Mach-O.*")
    targetResultPath  = os.path.join(path, "checkResult.txt")
    for f in os.listdir(path):
        cmd = "file -b %s > %s" % (os.path.join(path,f), targetResultPath)

        os.system(cmd)
        fp = open(targetResultPath)
        out = fp.readlines()[0]
        fp.close()
        os.remove(targetResultPath)

        if regex.search(out):
            return os.path.join(path, f)
    return None

def get_app_strings(app_path):
    """
    Args:
        app : the full path of the Mach-O file in app
    Returns:
        outfile : the result file of the strings app
        
    info:strings - 显示文件中的可打印字符
    strings 的主要用途是确定非文本文件的包含的文本内容。
    """
    #创建结果存放文件
    cur_dir = os.getcwd() 
    strings_file_name  = 'strings_' + os.path.basename(app_path) or 'strings'
    strings_file_name = os.path.join(cur_dir, "result/" + strings_file_name)

    #使用strings获得ipa字符信息
    cmd = "/usr/bin/strings %s > %s" % (app_path, strings_file_name)
    os.system(cmd)

    fp = open(strings_file_name)
    output = fp.readlines()
    fp.close()
    # os.remove(strings_file_name)

    tmpList = []
    for outputLine in output:
        outputLine = outputLine.replace("\n","")
        for splitTmp in outputLine.split():
            if (len(splitTmp) > 2):#2个以上字符才算 我也不知道为什么 先这么搞吧
                tmpList.append(splitTmp)

    rtValue = set(tmpList)

    return rtValue

def get_app_variables(app):
    "get all variables, properties, and interface name"
    dump_result = class_dump_utils.dump_app(app)
    
    interface = re.compile("^@interface (\w*).*")
    protocol = re.compile("@protocoli (\w*)")
    private = re.compile("^\s*[\w <>]* [*]?(\w*)[\[\]\d]*;")
    prop = re.compile("@property\([\w, ]*\) (?:\w+ )*[*]?(\w+); // @synthesize \w*(?:=([\w]*))?;")
    res = set()
    lines = dump_result.split("\n")
    wait_end = False 
    for line in lines:
        l = line.strip()
        if l.startswith("}"):
            wait_end = False
            continue
        if wait_end:
            r = private.search(l)
            if r:
                res.add(r.groups()[0])
            continue
        r = interface.search(l)
        if r:
            res.add(r.groups()[0])
            wait_end = True
            continue
        r = protocol.search(l)
        if r:
            res.add(r.groups()[0])
            wait_end = True
            continue
        r = prop.search(l)
        if r:
            m = r.groups()
            res.add(m[0])
            res.add("set" + m[0].title() + ":")
            # print "set" + m[0].title() + ":"
            if m[1] != None:
                # res.add("V"+m[1])
                res.add(m[1])

    return res


def get_app_methods(app):
    '''
    info:获得app中的方法
    '''
    dump_result = class_dump_utils.dump_app(app)
    methods_file_name  = 'method_' + os.path.basename(app) or 'app_methods'
    cur_dir = os.getcwd()
    methods_file_name = os.path.join(cur_dir, "result/" + methods_file_name)
    
    strings = open(methods_file_name, "w")

    print >>strings, dump_result 
    #ret_methods = set()
    methods = api_helpers.extract(dump_result)
    #for m in methods:
    #    ret_methods = ret_methods.union(set(m["methods"]))
    #保留class_name信息
    return methods