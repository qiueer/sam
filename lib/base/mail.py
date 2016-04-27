# -*- encoding=utf-8 -*-
'''
@author: Qiueer
'''
import types
import time
import smtplib
from email.mime.text import MIMEText

from lib.base.sdate import sdate
from lib.base.slog import slog

class mail(object):
    
    def __init__(self, username, password, smtp_server, port=25, **kwargs):
        kwargs = dict(kwargs)
        logpath =  kwargs.get("logpath", None)
        debug=kwargs.get("debug", False)
        self._app = kwargs.get("app" ,"")
        self._username = username
        self._password = password
        self._smtp_server = smtp_server
        self._port = port if port else 25
        self._is_login = False
        self._smtp = None
        self._login()
        
        self._logger = None
        if logpath:
            self._logger = slog(logpath, debug=debug)

    def _login(self):
        smtp=smtplib.SMTP()
        smtp.connect(self._smtp_server, port=self._port)  #smtp server,
        smtp.ehlo()
        smtp.starttls()
        (code, msg) = smtp.login(self._username , self._password)
        if code == 235:
            self._is_login = True
            self._smtp = smtp
    
    def __del__(self):
        self._smtp.quit()

    def send_mail(self, tolist, title, content, fmt="plain"):
            assert type(tolist) == types.ListType
            self._login()
            try:
                    appstr = self._app+", " if self._app else ""
                    m_content = "\
                    %s \
                    \n\n\
                    -------------------------------------------------------------------------\n\
                    %sAuto Send @%s, Please Do Not Reply! \n\
                    "  % (content, appstr, sdate().datetime())
                    
                    if fmt == "html":
                            m_content = m_content.replace("\n", "<br />")
                    m_charset = "utf-8"
                    msg=MIMEText(m_content, _subtype=fmt, _charset=m_charset)
                    msg['Subject']= title   #email title
                    msg['From']= self._username   #sender
                    msg['To']=','.join(tolist)  #recipient
                    msg['date']=time.strftime('%a, %d %b %Y %H:%M:%S %z')  #define send datetime
                    res = self._smtp.sendmail(self._username , tolist , msg.as_string())

                    if self._logger:
                        logobj = {}
                        logobj['Topic']= "SEND MAIL"
                        logobj['Subject']= title   #email title
                        logobj['From']= self._username   #sender
                        logobj['To']=','.join(tolist)  #recipient
                        logobj['date']=time.strftime('%a, %d %b %Y %H:%M:%S %z')  #define send datetime
                        logobj['result'] = res
                        logobj['orders']= ["Topic", "Subject", "From", "To", "res", "date"]
                        self._logger.dictlog("info", width=8, **logobj)
                    if not res: ## 返回空字典，说明都发送成功
                        return True
            except Exception,data:
                    import traceback
                    tb = traceback.format_exc()
                    if self._logger:
                        logobj = {}
                        logobj['traceback']= tb   #email title
                        self._logger.dictlog("warn", width=10, **logobj)
            return False
                    
    def send_html_mail(self, m_to_list, m_title, m_content):
        return self.send_mail(m_to_list, m_title, m_content, fmt="html")