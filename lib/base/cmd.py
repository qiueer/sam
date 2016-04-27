#-*- encoding:utf-8 -*-
'''
Created on 2014-05-14

@author: albertqiu
'''
import re, types
import platform


def docmd(command,timeout=300, debug=False, raw=False):
        '''
        功能：
                执行命令
        参数：command，命令以及其参数/选项
                timeout，命令超时时间，单位秒
                debug，是否debug，True输出debug信息，False不输出
                raw，命令输出是否为元素的输出，True是，False会将结果的每一行去除空格、换行符、制表符等，默认False
        返回：
                含有3个元素的元组，前两个元素类型是list，第三个元素类型是int，第一个list存储stdout的输出，第二个list存储stderr的输出，第三int存储命令执行的返回码，其中-1表示命令执行超时
        示例：
                cmd.docmd("ls -alt")
        '''
        import subprocess, datetime, os, time, signal
        start = datetime.datetime.now()
#                 cmd_list = re.split('\|', command)
#                 print cmd_list
#                 cmd_list = [sglcmd.strip() for sglcmd in cmd_list]
#                 cmds = []
#                 for sglcmd in cmd_list:
#                         cmds.extend(re.split(' +' ,  sglcmd))
#                         cmds.append("|")
#                 cmds = cmds[0:-1]
#                 print cmds
# #                 cmds = re.split(' +' ,  command)

        ps = None
        retcode = 0
        if platform.system() == "Linux":
                ps = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
                ps = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        while ps.poll() is None:
                time.sleep(0.2)
                now = datetime.datetime.now()
                if (now - start).seconds > timeout:
                        os.kill(ps.pid, signal.SIGINT)
                        retcode = -1
                        return (None,None,retcode)
        stdo = ps.stdout.readlines()
        stde = ps.stderr.readlines()
        
        if not ps.returncode:
                retcode = ps.returncode
        
        if raw == True:  #去除行末换行符
                stdo = [line.strip("\n") for line in stdo]
                stde = [line.strip("\n") for line in stde]
        
        if raw == False: #去除行末换行符，制表符、空格等
                stdo = [str.strip(line) for line in stdo]
                stde = [str.strip(line) for line in stde]

        
        if debug:
                tmp_list = ["*"] * 20
                tmp_str = "".join(tmp_list)
                
                dbg_info = "".join(["="] * 30)
                print "%s DEBUG BEGIN %s"  % (dbg_info, dbg_info)
                print "\n"
                
                import time
                now = time.strftime("%Y/%m/%d %H:%M:%S ", time.localtime())
                
                print "%s[ time ]%s\n%s\n" % (tmp_str, tmp_str, now)
                print "%s[ cmd ]%s\n%s\n" % (tmp_str, tmp_str, command)
                
                print "%s[ std out ]%s"  %   (tmp_str, tmp_str)
                for line in stdo:
                        print line
                        
                print "%s[ std error ]%s\n"  % (tmp_str, tmp_str)
                for line in stde:
                        print line
                print "\n"
                        
                print "%s[ retcode ]%s\n%s\n"  % (tmp_str, tmp_str, ps.returncode)
                
                print "%s DEBUG END %s" % (dbg_info, dbg_info)
                print "\n\n"
        
        
        return (stdo,stde,retcode)

    
def docmd_ex(command,timeout=300, debug=False, raw=False, pure=True):
        '''
        功能：
                执行命令
        参数：command，命令以及其参数/选项
                timeout，命令超时时间，单位秒
                debug，是否debug，True输出debug信息，False不输出
                raw，命令输出是否为元素的输出，True是，False会将结果的每一行去除空格、换行符、制表符等，默认False
        返回：
                含有3个元素的元组，前两个元素类型是list，第三个元素类型是int，第一个list存储stdout的输出，第二个list存储stderr的输出，第三int存储命令执行的返回码，其中-1表示命令执行超时
        示例：
                cmd.docmd("ls -alt")
        '''
        import subprocess, datetime, os, time, signal
        start = datetime.datetime.now()
        (stdo,stde, retcode) = ([], [], -1)
        ps = None
        if platform.system() == "Linux":
                ps = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
                ps = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        while ps.poll() is None:
                time.sleep(0.2)
                now = datetime.datetime.now()
                if (now - start).seconds > timeout:
                        os.kill(ps.pid, signal.SIGINT)
                        return None,None,-1
                            
        if pure == True:
            stdo = ps.stdout.read()
            stde = ps.stderr.read()
        elif pure == False:
            stdo = ps.stdout.readlines()
            stde = ps.stderr.readlines()
            
        retcode = ps.returncode
        
        if raw == True and pure == False:  #去除行末换行符
                stdo = [line.strip("\n") for line in stdo]
                stde = [line.strip("\n") for line in stde]
        
        if raw == False and pure == False: #去除行末换行符，制表符、空格等
                stdo = [str.strip(line) for line in stdo]
                stde = [str.strip(line) for line in stde]

        
        if debug:
                tmp_list = ["*"] * 20
                tmp_str = "".join(tmp_list)
                
                dbg_info = "".join(["="] * 30)
                print "%s DEBUG BEGIN %s"  % (dbg_info, dbg_info)
                print "\n"
                
                now = time.strftime("%Y/%m/%d %H:%M:%S ", time.localtime())
                
                print "%s[ time ]%s\n%s\n" % (tmp_str, tmp_str, now)
                print "%s[ cmd ]%s\n%s\n" % (tmp_str, tmp_str, command)
                
                print "%s[ std out ]%s"  %   (tmp_str, tmp_str)
                if type(stdo) == types.ListType:
                    for line in stdo:
                            print line
                else:
                    print stdo
                        
                print "%s[ std error ]%s\n"  % (tmp_str, tmp_str)
                if type(stde) == types.ListType:
                    for line in stde:
                            print line
                else:
                    print stde
                print "\n"
                        
                print "%s[ retcode ]%s\n%s\n"  % (tmp_str, tmp_str, ps.returncode)
                
                print "%s DEBUG END %s" % (dbg_info, dbg_info)
                print "\n\n"
        
        return stdo,stde,retcode
 
def docmds(commands,timeout=300, debug=False, raw=False):
        '''
        功能：执行多个命令，每个命令之间用 , 或 ; 号分割
        返回：哈希，key为每个命令，key对应的value为一元组，元组值请参看docmd的说明  
        '''
        cmds = re.split('[,;]+' ,  commands)
        result = {}
        for cmdline in cmds:
                (stdo,stde,retcode) = docmd(cmdline, timeout, debug=debug, raw=raw)
                result[cmdline] = (stdo,stde,retcode)
        return result 
        

        
        
