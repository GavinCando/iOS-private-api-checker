#coding=utf-8
'''
Created on 2015年10月27日
class-dump操作类
@author: hzwangzhiwei
'''
import subprocess
import os
from utils import utils
class_dump_path = utils.get_clas_dump_path()

dump_cmd = class_dump_path + " -H %s -o %s" # dump cmd模板字符串

def dump_framework(frame_path, out_path):
    '''
    info:使用class-dump来解开framework中的api
    '''
    cmd = dump_cmd % (frame_path, out_path)
    ret = subprocess.call(cmd.split())
    if ret != 0:
        return frame_path
    return ""
    
def dump_app(app_path):
    '''
    get all private variables, properties, and interface name
    '''
    class_dump = class_dump_path + " %s" % app_path


    cur_dir = os.getcwd()
    class_dump_file_name = os.path.join(cur_dir, "tmp/classDumpResult.txt")
    cmd = "%s > %s" % (class_dump, class_dump_file_name)

    os.system(cmd)

    fp = open(class_dump_file_name)
    out = fp.readlines()
    fp.close()
    os.remove(class_dump_file_name)

    totalLine = ""
    for line in out:
        totalLine += line

    return totalLine