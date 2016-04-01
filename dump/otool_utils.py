#coding=utf-8
'''
Created on 2015年10月29日

@author: hzwangzhiwei
'''

import subprocess
import re
import os

otool_path = "otool" #otool所在的位置

otool_cmd = otool_path + " -L %s" # otool cmd模板字符串

def otool_app(app_path):
    """
    Get framework included in app
    Args:
        Mach-o path
    Returns:
        two sets, one is public framework, one is private framework
    """
    cmd = otool_cmd % app_path

    cur_dir = os.getcwd()
    otool_file_name = os.path.join(cur_dir, "result/otoolResult")
    cmd = "%s > %s" % (cmd, otool_file_name)

    os.system(cmd)

    fp = open(otool_file_name)
    out = fp.readlines()
    fp.close()
    # os.remove(otool_file_name)

    pattern = re.compile("PrivateFrameworks\/(\w*)\.framework")
    pub_pattern = re.compile("Frameworks\/([\.\w]*)")
    
    private = set()
    public = set()
    for outLine in out:
        outLine = outLine.replace("\n","")
        for r in re.finditer(pattern, outLine):
            private.add(r.group(1))
        
        for r in re.finditer(pub_pattern, outLine):
            public.add(r.group(1))

    print "="*50
    print "使用private Framework %d 个" % (len(private))
    print "*"*50
    for singel_private_framework in private:
        print singel_private_framework
    print "*"*50

    print "="*50
    print "使用Public Framework %d 个" % (len(public))
    print "*"*50
    for singel_public_framework in public:
        print singel_public_framework
    print "*"*50
    return private, public