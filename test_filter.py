from db.sqlite_utils import SqliteHandler

fp = open("/Users/gavin/Documents/03-my_develop/01-code/pythonWorkspace/iOS-private-api-checker/result/private_2.txt")
content = fp.readlines()
fp.close()


for line in content:
    line = str(line.replace("\n",""))
    sql = "select * from ZTOKEN  WHERE  ZTOKENNAME like '%s' and ZLANGUAGE in (1,2)" % (line)
    rt = SqliteHandler(db="9.3-docSet.dsidx").exec_select(sql)
    if rt:
        print sql