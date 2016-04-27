# -*- encoding=utf-8 -*-
'''
漫道 SMS
@author: qiueer
'''

import socket
import struct
import json
import types


class MD(object):

    def __init__(self, bid=19, sub_id=2, port=2110, server="127.0.0.1"):
        """
        开发环境：
            server: 10.0.5.51
            bid: 19
            sub_id: 1
        正式环境：
            server: 127.0.0.1
            bid: 19
            sub_id: 2
        """
        self.bid = bid if bid else 19
        self.sub_id = sub_id if sub_id else 2
        self.port = port if port else 2110
        self.server = server if server else "10.0.1.86"
        

    def send(self, msg, telephone):
        """
        telephone: str or array
            12341322523,12328343125
            or ["12341322523","12328343125"]
        """
        try:
            if type(telephone) == types.ListType:
                telephone = ",".join(telephone)
            msg = u"告警：%s"  % (msg)
            jsondict = {
                "business_id": self.bid,
                "business_sub_id": self.sub_id,
                "city": 0,
                "control_bits": 0,
                "priority": 1,
                "send_at": "0",
                "sms_content": msg,
                "target_number":  telephone
            }
            jsonstr =  json.dumps(jsondict)
            size = struct.calcsize("%ds"%(len(jsonstr)))+1
            formatstr = ">iB%ds" % (len(jsonstr))  #java网络流是大端，big-endian
            vals = (size, 1, jsonstr)
            bytes_stream =  struct.pack(formatstr, *vals)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.server, self.port)
            sock.connect(server_address)
            sock.sendall(bytes_stream)
            
            ret_size_str = sock.recv(4)  ## 前面四个字节，是int类型，表明返回内容的长度
            ret_size_tpl = struct.unpack(">i", ret_size_str)   #java网络流是大端，big-endian
            result = None
            if ret_size_tpl:
                
                ret_size = ret_size_tpl[0]
            
                ret_content_str = sock.recv(ret_size)
                fstr = "%ds" % (ret_size)
                content_tpl = struct.unpack(fstr, ret_content_str)
                content = content_tpl[0]
                result =  content
            sock.close()
            return result
        except Exception as expt:
            import traceback
            print traceback.format_exc()
        
if __name__ == "__main__":
    #dev env
    MD(server="10.0.5.51", bid=19, sub_id=1).send("hahaha", "12345678901")
