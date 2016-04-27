#-*- encoding:utf-8 -*-
'''
Created on 2015-03-06
@author: albertqiu
to statistics http request information
'''
import pycurl
import urllib
import StringIO

class HStat():
    
    '''
    INPUT
    '''
    _url = ""  #string
    _timeout = 60 #int
    _is_gzip = True # boolean
    _postdata = None #dict
    
    '''
    OUTPUT
    '''
    _body = ""   #string
    _status = 0   #int
    _size = 0  #int , unit: bytes
    _request_time = 0.0  # float
    _time_st = None  # dict
    
    def __init__(self, url, timeout=60, postdata=None, is_gzip=True):
        try:
            self._url = url
            self._timeout = timeout ## 单位：s
            self._postdata = postdata
            self._is_gzip = is_gzip
            self._time_st = {}
            self.__get_info__()
        except Exception as expt:
            print expt
        
    def __get_info__(self, url=None, timeout=None, postdata=None, is_gzip=None):
        try:
            input_url = url if url else self._url
            timeout = timeout if timeout else self._timeout
            postdata = postdata if postdata else self._postdata
            is_gzip = is_gzip if is_gzip else self._is_gzip
            
            c = pycurl.Curl()
            b = StringIO.StringIO()
            c.setopt(pycurl.WRITEFUNCTION, b.write) ## 将输出交由StringIO处理
    
            c.setopt(pycurl.URL,input_url)
            c.setopt(pycurl.TIMEOUT, timeout)
            
            #避免libcurl crash
            c.setopt(pycurl.NOSIGNAL, 1)
            
            if is_gzip == True:
                c.setopt(pycurl.ENCODING, 'gzip')
                
            if postdata:
                # Option -d/--data HTTP POST data
                c.setopt(c.POSTFIELDS, urllib.urlencode(postdata))
    
            c.perform()
            
            t_dns = c.getinfo(pycurl.NAMELOOKUP_TIME)
            t_redirect = c.getinfo(pycurl.REDIRECT_TIME)
            t_conn =  c.getinfo(pycurl.CONNECT_TIME)
            t_pre_tran =  c.getinfo(pycurl.PRETRANSFER_TIME)
            t_start_tran =  c.getinfo(pycurl.STARTTRANSFER_TIME)
            t_total = c.getinfo(pycurl.TOTAL_TIME)
            time_st = {
                       "dns_time": t_dns,
                       "redirect_time": t_redirect,
                       "connect_time": t_conn,
                       "pre_tran_time": t_pre_tran,
                       "start_tran_time": t_start_tran,
                       "total_time": t_total,
            }
            
            self._time_st = time_st
            self._status = c.getinfo(pycurl.HTTP_CODE)
            self._size = c.getinfo(pycurl.SIZE_DOWNLOAD)
            self._body = b.getvalue()
            self._request_time = t_total
            c.close()
            b.close()
        except pycurl.error as expt:
            import traceback
            tb = traceback.format_exc()
            self._body = tb
            self._size = -1
            self._request_time = 0
            self._status = 10000
            self._time_st = {}
            

        
    def new(self, url=None, timeout=120, postdata=None, is_gzip=True):
        self.__get_info__(url=url, timeout=timeout, postdata=postdata, is_gzip=is_gzip)
        
    def get_url(self):
        return self._url
        
    def get_status(self):
        return self._status
    
    def get_size(self):
        return self._size
    
    def get_request_time(self):
        return self._request_time
    
    def get_body_raw(self):
        return self._body
    
    def get_body_object(self):
        from json import JSONDecoder
        result = False
        try:
                result = JSONDecoder().decode(self._body)
        except :
                print"[!!!! exception !!!!]\ndecode json error, json  string is: %s \n" % (self._body)
        return result
    
    def get_time_st(self):
        return self._time_st
