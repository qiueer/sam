# -*- encoding=utf-8 -*-
'''
Created on 2013-12-28
Update on 2015-06-28 by qiujingqin
@author: albertqiu
'''
import platform, os, types 
import cmd

def get_os_type():
        '''
        return: Windows  or  Linux
        '''
        os_vers = platform.system()
        return os_vers;


def get_local_ip():
        try:
                ip = ""
                if platform.system() == "Linux":
                        (res, error, retcode)= cmd.docmd("/sbin/ifconfig | grep -E 'eth0|em2|bond0' -A3 | grep -v eth1 | grep 'inet addr' | awk '{print $2;}' | cut -d: -f2")
                        ip = res[0]
                elif platform.system() == "Windows":
                        (res, error, retcode)  = cmd.docmd("ipconfig|grep 'IP Address'|awk -F: '{print \$2}'|sed \"s/ //g\"|grep -E '^172|^10|^192\.168'")
                        ip = res[0]
        except Exception,data:
                print data
        return ip


def get_cur_info():
        """Return the frame object for the caller's stack frame."""
        """ 获取文件名和方法名和行号"""
        try:
                raise Exception 
        except:
                import sys
                f = sys.exc_info()[2].tb_frame.f_back
                return (f.f_code.co_filename, f.f_code.co_name, f.f_lineno)
        

def fjson_out(json):
        from json import JSONDecoder
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        deconder = JSONDecoder()
        result = deconder.decode(json)
        pp.pprint(result)
        

def is_normal_env(iplist=""):
        '''
        iplist是ip列表或以分号分割的字符串，默认为空。当采用默认值时，ip为10.12.16.119或os为window
        '''
        ip_test_env = ["10.12.16.119"]
        
        if type(iplist) is types.StringType:
                res = iplist.split(";")
                ip_test_env.extend(res)
        elif type(iplist) is types.ListType:
                ip_test_env.extend(iplist)
                
        os_vers = platform.system()
        if  os_vers == "Windows":
                return False
        elif os_vers == "Linux" :
                ip = os.popen("/sbin/ifconfig eth1|grep 'inet addr'|awk -F: '{print $2}'|awk '{print $1}'").readlines()
                ip = str.strip(ip[0]);
                
                if ip in ip_test_env:
                        return False
                return True

def get_ip():
    import socket
    import traceback
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    except Exception as expt:
        tb = traceback.format_exc()
        print tb
        
    return '127.0.0.1'


def get_hostname():
    import socket
    import traceback
    try:
        hostname = socket.gethostname()
        return hostname
    except Exception as expt:
        tb = traceback.format_exc()
        print tb
    return 'localhost'
                        
        