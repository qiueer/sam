#-*- encoding:utf-8 -*-
'''
Created on 2014-05-18
@author: 邱景钦
'''
"""
1）支持include引入其他文件
"""

import re, types, os

""" 配置文件类似如下：
system段，system / include必不可少
section段，可以加入类型，例如dict,list类型，当没有指定时，默认为dict
"""
"""
[system]
include=
log=/tmp

[clean_items list]
dir  =  /tmp  ; unit=d  ; count=+3;  standard=access | modify | change |    all; comment=删除/tmp下三天前的问题; test = false
dir  =  /home/ror_bak  ; unit=d  ; count=+3;  standard=access | modify | change |    all; comment=删除/home/ror_bak下三天前的问题; test = false
comment=删除/tmp下三天前的问题
"""

class conf(object):
    conffile = ""
    config = dict()
    def __init__(self, conffile, pattern="="):
        self.conffile = conffile
        self.pattern = pattern
        self.parse_clean_conf(self.conffile)
    
    def parse_clean_conf(self, conffile, isroot=True):
        try:
            fh = open(conffile, "r")
            contents = fh.readlines()
            fh.close()
            section_start = 0
            section_end = 0
            section_id = ""
            section_type = "dict"
            conf = {}
            for line in contents:
                    line = line.strip()
                    if re.match("^$" , line ) or re.match("^#", line):
                            continue
                    
                    if line.startswith("[" ) and line.endswith("]"):
                            section_start = 1
                            section_end = 1
                            tmpstr = line.replace("[", "")
                            tmpstr = tmpstr.replace("]", "").strip()
                            tmpary = re.split("[ |\t]+", tmpstr)
                            if len(tmpary) == 1:
                                section_id = tmpary[0]
                                section_type = "dict"
                            elif len(tmpary) == 2:
                                section_id = tmpary[0]
                                section_type = tmpary[1]
                            if section_type == "dict":
                                conf[section_id] = {}
                            elif section_type == "list":
                                conf[section_id] = list()
                    else:
                            section_end = 0
                            
                    if section_start == 1 and section_end == 0:
                        if section_type == "dict" and str(line).find(";") == -1:
                            tmp_list = re.split(self.pattern, line)
                            if len(tmp_list) < 2:continue #
                            key = str.strip(tmp_list[0])
                            val = str.strip(tmp_list[1])
                            section = dict(conf[section_id])
                            ## 同一key，将其值保存为列表
                            if section.has_key(key) == True:
                                vals = section[key]
                                if type(vals) != types.ListType:
                                    tmplist = list()
                                    tmplist.append(vals)
                                    tmplist.append(val)
                                    section[key] = tmplist
                                else:
                                    vals.append(val)
                            else:
                                section[key] = val
                            conf[section_id] = section
                        
#                         if section_type == "list" and str(line).find(";") != -1:
                        if section_type == "list":
                            itemlist = conf[section_id]
                            tmp_list = re.split(";", line)
                            tmpobj = dict()
                            if len(tmp_list) > 0:
                                for keyval in tmp_list:
                                    keyval = str(keyval).strip().replace(" ", "")
                                    if keyval == "": continue
                                    tmpl = re.split(self.pattern, keyval)
                                    if len(tmpl) > 1:
                                        key = str.strip(tmpl[0])
                                        val = str.strip(tmpl[1])
                                        tmpobj[key] = val
                            if tmpobj:
                                itemlist.append(tmpobj)
                                conf[section_id] = itemlist

            if isroot == True:
                conf["root"] = "true"
            else:
                conf["root"] = "false"
                
            local_config = self.config
            local_config[conffile] = conf
            self.config = local_config

            if dict(conf["system"]).has_key("include") == True and isroot == True: #include
                #print "=======", conf["system"]["include"]
                include = conf["system"]["include"]
                include_ary = str(include).replace(" ", "").split(";")
                if include_ary:
                    for inc in include_ary:
                        if inc == self.conffile:
                            continue
                        if os.path.exists(inc) and os.path.isfile(inc) and str(inc).endswith(".conf") == True:
                            #print "file here"
                            self.parse_clean_conf(inc, isroot=False)
                        elif os.path.exists(inc) and os.path.isdir(inc):
                            #print "dir here"
                            for root,dirs,files in os.walk(inc):
                                for filespath in files:
                                    incfp = os.path.join(root, filespath)
                                    if str(incfp).endswith(".conf") == True:  ##仅处理以.conf结尾的文件
                                    #print "find file here", incfp
                                        self.parse_clean_conf(incfp, isroot=False)
        except Exception,e:
            print "conffile: %s" % (conffile)
            import traceback
            tb = traceback.format_exc()
            print tb
                                    
    def get_config(self):
        return self.config                                
