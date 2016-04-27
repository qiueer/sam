# -*- encoding=utf-8 -*-
#version: 1.2
# 使用场景： 业务进程、端口监控 + 业务可用性监控（web）
#
    
import sys
import os
import time
import traceback
from optparse import OptionParser

from lib.base import cmd
from lib.base.hstat import HStat as HAcc
from plugins.md_sms import MD as SMS
from lib.base.slog import slog
from lib.base import common
from lib.base.stask import tqueue
from lib.base.daemon import daemon
from lib.base.mail import mail

from lib.helpers.confex import conf
from lib.helpers import html


reload(sys)
sys.setdefaultencoding('utf8')

def get_realpath():
    return os.path.split(os.path.realpath(__file__))[0]

def get_binname():
    return os.path.split(os.path.realpath(__file__))[1]

def signal_handler(signal, frame):
    pid = os.getpid();
    print ""
    print "Kill These Pids: ",pid
    os.system("kill -9 %d" % pid)
    sys.exit(0)
    

class Monitor(object):
    
    def __init__(self, monitor_conf, conffile, name=None, logpath="/tmp/service_available_monitor.log", debug=True):
        self._logger = slog(logpath, debug=debug)
        self._monitor_conf = monitor_conf
        self._conffile = conffile
        self._name = name

    def check_port(self, srv_port):
        """
        检查业务进程端口
        """
        ## check process here
        cmdstr = "netstat -nlpt | grep ':%s' | wc -l" % (srv_port)
        (stdo, stde, retcode) = cmd.docmd_ex(cmdstr, timeout=10, pure=True)
        flag = False
        if retcode == 0 and len(stdo)>0:
            if int(str(stdo).strip()) > 0:
                flag = True
        
        logdict = {
            "event": "Check Process Port" ,
            "service port": srv_port, 
            "cmdstr": cmdstr,
            "stdo": str(stdo).strip(),
            "stde": str(stde).strip(),
            "retcode": retcode,
            "check result": flag,
            "orders": ["event","service port", "cmdstr", "stdo", "stde", "retcode"],
        }
        if flag == True:
            self._logger.dictlog(level="info", width=14, **logdict)
        else:
            self._logger.dictlog(level="warn", width=14, **logdict)
        return flag

    
    def check_proccess(self, srv_binname):
        """
        检查业务进程
        """
        ## check process here
        ps_cmdstr = "ps -ef | grep '%s' | grep -v grep | wc -l" % (srv_binname)
        (stdo, stde, retcode) = cmd.docmd_ex(ps_cmdstr, timeout=10, pure=True)
        flag = False
        if retcode == 0 and len(stdo)>0:
            if int(str(stdo).strip()) > 0:
                flag = True
        
        logdict = {
            "event": "Check Process" ,
            "service name": srv_binname, 
            "cmdstr": ps_cmdstr,
            "stdo": str(stdo).strip(),
            "stde": str(stde).strip(),
            "retcode": retcode,
            "check result": flag,
            "orders": ["event","service name", "cmdstr", "stdo", "stde", "retcode"],
        }
        if flag == True:
            self._logger.dictlog(level="info", width=14, **logdict)
        else:
            self._logger.dictlog(level="warn", width=14, **logdict)
        return flag
    
    def check_available(self, url, postdata, keyword=None):
        hac = HAcc(url, postdata=postdata)
        status = hac.get_status()
        content = hac.get_body_raw()
        max_len = 200
        clen = len(content)
        max_len = max_len if clen>=max_len else clen
        part_content = content[0:max_len]
        
        status_flag = True
        if status not in [200, 301, 302]:
            status_flag = False

        kw_flag = True
        if keyword:
            if content.find(keyword) != -1:
                kw_flag = False
                
        flag = (status_flag and kw_flag)
                
        logobj = {
            "url": url,
            "post": postdata,
            "status": status,
            "keyword": keyword,
            "part_content": part_content,
        }
        if flag == False:
            self._logger.dictlog(level="warn", **logobj)
        else:
            self._logger.dictlog(level="info", **logobj)
            
        return flag

    def restart_business(self, srv_start_cmd, srv_cwd=None):
        try:
            cmdstr = srv_start_cmd
            if srv_cwd:
                cmdstr = "cd %s &&  %s"  % (srv_cwd, srv_start_cmd)
            (rst_stdo, rst_stde, rst_retcode) = cmd.docmd_ex(cmdstr, timeout=10, pure=True)
            logdict = {
                "event": "Restart Service" ,
                "cmdstr": cmdstr, 
                "stdo": rst_stdo,
                "stde": rst_stde,
                "retcode": rst_retcode,
                "orders": ["event", "cmdstr", "retcode", "stdo","stde"]
            }
            if rst_retcode == 0:
                self._logger.dictlog(level="info", width=12, **logdict)
            else:
                self._logger.dictlog(level="warn", width=12, **logdict)
            return (rst_retcode, cmdstr)
        except Exception, expt:
            self._logger.dictlog(level="warn", width=12, **{"traceback": traceback.format_exc()})
        
    def check(self):
        monitor_conf = self._monitor_conf
        monitor_conf = dict(monitor_conf)
        is_pause = monitor_conf.get("is_pause", "true")
        url = monitor_conf.get("url", None)
        keyword = monitor_conf.get("keyword", None)
        post = monitor_conf.get("post", None)
        srv_name = monitor_conf.get("name", None)
        srv_start_cmd = monitor_conf.get("start_cmd", None)
        srv_binname = monitor_conf.get("binname", None)
        srv_port = monitor_conf.get("port", None)
        sms_receivers = monitor_conf.get("sms_receivers", None)
        email_receivers = monitor_conf.get("email_receivers", None)
        
        if is_pause == "true":
            self._logger.dictlog(level="warn", width=12, **{"event": "Ignore"})
            return
        
        pc_flag = True
        if srv_binname:
            pc_flag = self.check_proccess(srv_binname)
            
        pt_flag = True
        if srv_port:
            pt_flag = self.check_port(srv_port)
            
        web_flag = True
        if url:
            web_flag = self.check_available(url, post, keyword)

        logobj = {"event": "Check Item", "item": self._name, "result": (pc_flag and pt_flag and web_flag), "orders": ["event", "item", "result"]}
        self._logger.dictlog(level="info", **logobj)
                
        if (pc_flag and pt_flag and web_flag) == False:
            self.restart_business(srv_start_cmd, None)
            
            ip = common.get_local_ip()
            if email_receivers:
                m_title = u"服务监控告警：%s，【%s】" % (srv_binname, ip)
#                 dict_data = {
#                              u"服务": srv_binname, 
#                              u"启动命令": srv_start_cmd,
#                 }
#                 m_content = html.get_box_html(u"详情", html.dict2table(dict_data))
                (username, password, server, port) = (None, None, None, None)
                insc = conf(self._conffile, pattern="=")
                configs = insc.get_config()
                for (path, confs) in dict(configs).iteritems():
                    for (key, item) in confs.iteritems():
                        if str(key).lower().strip() != "mail": continue
                        username = item.get("username", None)
                        password = item.get("password", None)
                        server = item.get("server", None)
                        port = item.get("port", 25)
                               
                m_content = html.get_box_html(u"详情", html.dict2table(self._monitor_conf, order_keys=["binname", "start_cmd"]))
                email_receivers_list = str(email_receivers).replace(" ", "").split(";")
                mail(username, password, server, port=int(port)).send_html_mail(email_receivers_list, m_title, m_content)
                logobj = {"event": "Send Alert Email", "title": m_title, "content": m_content, "receivers": email_receivers_list, "orders": ["event", "receivers", "title", "content"]}
                self._logger.dictlog(level="info", **logobj)
            
            if sms_receivers:
                msg = u"服务监控告警：%s，【%s】" % (srv_binname, ip)
                sms_receivers_list = str(sms_receivers).replace(" ", "").split(";")
                SMS(server="127.0.0.1", bid=10, sub_id=901).send(msg, sms_receivers_list)
                logobj = {"event": "Send Alert Sms", "message": msg, "receivers": sms_receivers_list, "orders": ["event", "message","receivers"]}
                self._logger.dictlog(level="info", **logobj)

def doit(item, conffile, name):
    try:
        m = Monitor(item, conffile, name=name, debug=False)
        m.check()
    except Exception , expt:
        print expt
        
        
def main(conffile, global_conf_file):
#     ip = common.get_ip()
#     hostname = common.get_hostname()
#     binpath = get_realpath()
#     binname = get_binname()

    try:
        tq = tqueue(workers=20)
        default_keys = ["system", "root"]
        while True:
            insc = conf(conffile, pattern="=>")
            configs = insc.get_config()
            for (path, confs) in dict(configs).iteritems():
                for (key, item) in confs.iteritems():
                    if key in default_keys: continue
                    tq.add_task(doit, item, global_conf_file, key)
            time.sleep(60)
    except Exception as expt:
        print traceback.format_exc()

if __name__ == "__main__":
    confpath = None
    pidfile = "/tmp/service_available.pid"
    try:
        parser = OptionParser()
        parser.add_option("-f", "--file",  
                          action="store", dest="conffile", default=None,  
                          help="path of config file,must", metavar="FILE")
        parser.add_option("-a", "--action",  
                          action="store", dest="action", default=None,  
                          help="Action, start, stop, restart", metavar="ACTION")

        (options, args) = parser.parse_args()
        
        if not options.action:
            parser.print_help()
            sys.exit()
            
        if options.action and str(options.action).lower() == "stop":
            daemon(pidfile).stop()
            sys.exit(0)

        #check if file exist
        conffile = options.conffile
        if not conffile:
            conffile = get_realpath()+"/etc/sam.conf"

        if os.path.exists(os.path.abspath(conffile)) == False:
            sys.stdout.write("%s Not Exist!" %(conffile))
            sys.exit(1)

        confpath = None
        confpath = os.path.abspath(conffile)
    except Exception, expt:
        print traceback.format_exc()

    if options.action and str(options.action).lower() == "restart":
        daemon(pidfile).restart(main, confpath, get_realpath()+"/etc/config.ini")
    if options.action and str(options.action).lower() == "start":        
        daemon(pidfile).start(main, confpath, get_realpath()+"/etc/config.ini")
    
