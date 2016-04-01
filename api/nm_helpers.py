#coding=utf-8
'''
Created on 2015年10月27日

@author: hzwangzhiwei
'''
import re


def get_apis_of_file(filepath):
    """
    get the methods of file
    Args:
        header file path(absolute)
    Returns:
        methods list
    """
    apis = []
    fp = open(filepath)
    text = fp.readlines()
    fp.close()
    for line in text:
        tmpResult = extract(line)
        if (len(tmpResult) > 0):
            for tmpApi in tmpResult:
                apis.append(tmpApi)
    return apis

def remove_comments(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return ""
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def get_objc_func(text):
    """ get objective-c style fucntions
    Args:
        header file content
    Returns:
        function list
        [{'UIAlertView': ['textFieldAtIndex:',...], 'type': 'interface'} ]
    """
    methods = []

    #gavincui change 只匹配以冒号结尾的api信息
    # reResult = re.findall('.*[+|-]\[(.*) (.*)\].*', text)
    reResult = re.findall('.*[+|-]\[(.*) (.*:)\].*', text)

    if (len(reResult) >0):
        for row in reResult:
            class_name = row[0]
            api_name = row[1]

            ifHasCategory = re.findall('(.*)\(.*\)', class_name)
            if (len(ifHasCategory) > 0):
                class_name = ifHasCategory[0]

            tmpObj = {"class":class_name, "methods":[api_name], "type":"C/C++"}
            methods.append(tmpObj)

    return methods


def extract(text):
    no_comment_text = remove_comments(text)
    methods = []
    methods += get_objc_func(no_comment_text)
    return methods



if __name__ == '__main__':
#     pri = extract_pri('E:/Eclipse_WS/iOS-private-api-checker/tmp/Frameworks/UIKit.framework/Headers/UIToolbar.h')

#     print list(pri)

    pub = get_apis_of_file('E:/Eclipse_WS/iOS-private-api-checker/tmp/Frameworks/UIKit.framework/Headers/UIToolbar.h')
    print pub[0]['methods']