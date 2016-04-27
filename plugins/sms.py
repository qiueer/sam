# -*- encoding=utf-8 -*-
'''
Created on 2015年6月27日

@author: qiujingqin
'''

import time
import urllib2
import httplib
import urllib
import types
import sys, os
import platform


class SMS(object):

    def __init__(self, apikey=None, host=None, port=None, version=None):
        self.apikey = apikey if apikey else "ea02074a60233f861a14ff1f7a57fe4a"
        self.host = host if host else "yunpian.com"  #服务地址
        self.port = port if port else 80 #端口号
        self.version = version if version else "v1"  #版本号
    
    def get_user_info(self):
        """
        取账户信息
        """
        user_get_uri = "/" + self.version + "/user/get.json"  #查账户信息的URI
        conn = httplib.HTTPConnection(self.host, port=self.port)
        conn.request('GET', user_get_uri + "?apikey=" + self.apikey)
        response = conn.getresponse()
        response_str = response.read()
        conn.close()
        return response_str

    def tpl_send_sms(self, tpl_id, tpl_value, mobile, timeout=60):
        """
        模板接口发短信
        短信内容超过70个字符的，按每67字一条计
        """
        if type(mobile) == types.ListType:
            mobile = ",".join(mobile)
        sms_tpl_send_uri = "/" + self.version + "/sms/tpl_send.json" #模板短信接口的URI
        params = urllib.urlencode({'apikey': self.apikey, 'tpl_id': tpl_id, 'tpl_value': tpl_value, 'mobile': mobile})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = httplib.HTTPConnection(self.host, port=self.port, timeout=timeout)
        conn.request("POST", sms_tpl_send_uri, params, headers)
        response = conn.getresponse()
        response_str = response.read()
        conn.close()
        return response_str
    
    def alert(self, alertstr,  mobile, timeout=60):
        tpl_id = 585591
        tpl_value = u"#text#=%s&#company#=丘尔" % (alertstr)
        return self.tpl_send_sms(tpl_id, tpl_value, mobile, timeout=timeout)
    
    def mutil_alert(self, alertstr, mobile_list, timeout=60):
        result = dict()
        for mobile in mobile_list:
            respstr = self.alert(alertstr, mobile, timeout=timeout)
            result[mobile] = respstr
        return result
