#-*- encoding:utf-8 -*-
'''
Created on 2013-12-24
@author: 邱景钦
'''
from json import JSONDecoder


def dict2ul(dict_data, width=12, contain_id="tmp1234", **kwargs):
        """
        kwargs: 
            ignore_key = ""; 
            value=[] / ();
        """
        kwargs = dict(kwargs)
        
        ignore_keys = kwargs["ignore_keys"] if kwargs.has_key("ignore_keys") else []
        if kwargs.has_key("ignore_keys"): del(kwargs["ignore_keys"])
        
        order_keys = kwargs["order_keys"] if kwargs.has_key("order_keys") else []
        if kwargs.has_key("order_keys"): del(kwargs["order_keys"])
        
        ul = u"<ul class='ul_split'>"
        if order_keys:
            for key in order_keys:
                if not dict_data.has_key(key): continue
                val = dict_data[key]
                li = u"<li><font class='textinfo'>%s:</font>&nbsp;%s</li>" % (str(key).decode("utf-8").rjust(width).replace(" ", "&nbsp;"), str(val))
                ul = u"%s%s" % ( ul, li)
            
        for (key, value) in dict_data.iteritems():
            if key not in ignore_keys and key not in order_keys:
                li = u"<li><font class='textinfo'>%s:</font>&nbsp;%s</li>" % (str(key).decode("utf-8").rjust(width).replace(" ", "&nbsp;"), str(value))
                ul = u"%s%s" % ( ul, li)
        ul = u"%s</ul>" % (ul)

        return ul



def ds2list(dataset, contain_id="tmp1234", **kwargs):
        """
        kwargs: 
            ignore_key = ""; 
            value=[] / ();
        """
        kwargs = dict(kwargs)
        html = u"<div id='%s' class='%s' border='1px'>"  % (contain_id, contain_id)
        table_html = u"<table class='nest_table'><tr>"
        for item in dataset:
            item = dict(item)
            
            if kwargs and kwargs.has_key("ignore_key") and kwargs.has_key("value") :
                ignore_key = kwargs.get("ignore_key","")
                if item[ignore_key] in kwargs.get("value"):
                    continue
            
            ul = u"<ul class='ul_split'>"
            for (key, value) in item.iteritems():
                li = u"<li><font class='textinfo'>%s:</font>&nbsp;%s</li>" % (key, value)
                ul = u"%s%s" % ( ul, li)
            ul = u"%s</ul>" % (ul)
            td = u"<td class='simple_td'>%s <div class='split'></div></td>" % (ul)
            
            
            table_html = u"%s%s</table>" % (table_html, td)
        html = u"%s%s</div>"    % (html, table_html)
        return html
    
def dict2table(dictdata, table_id="result_table", **kwargs):
        """
        kwargs: 
            ignore_key = ""; 
            value=[] / ();
        """
        kwargs = dict(kwargs)
        
        ignore_keys = kwargs["ignore_keys"] if kwargs.has_key("ignore_keys") else []
        if kwargs.has_key("ignore_keys"): del(kwargs["ignore_keys"])
        
        order_keys = kwargs["order_keys"] if kwargs.has_key("order_keys") else []
        if kwargs.has_key("order_keys"): del(kwargs["order_keys"])
        
        html = u"<table id='%s'>" % (table_id)
        if order_keys:
            for key in order_keys:
                if not dictdata.has_key(key): continue
                val = dictdata[key]
                tmp_html = u"<tr><td style=' text-align:right'>%s</td><td style='font-weight: bolder'>%s</td></tr>" % (str(key).decode("utf-8"), str(val))
                html = u"%s%s" % ( html, tmp_html)
            
        for (key, value) in dictdata.iteritems():
            if key not in ignore_keys and key not in order_keys:
                tmp_html = u"<tr><td style=' text-align:right'>%s</td><td style='font-weight: bolder'>%s</td></tr>" %  (str(key).decode("utf-8"), str(value))
                html = u"%s%s" % ( html, tmp_html)
                
        html = u"%s</table>" % (html)

        return html
    
    
def ds2table(salt_dataset, table_id="result_table"):
        deconder = JSONDecoder()
        html = u"<table id='%s' class='result_table' border='1px'>"  % (table_id)
        for item in salt_dataset:
            item = dict(item)
            row = u"<tr>"
            for minion in item.keys():
                res = item[minion]
#                 res = res.replace(" ", "&nbsp;")
#                 res = str(res).replace("\n", "<br />")
                res = res.replace("'","\"")
                res = deconder.decode(res)
                res = ds2list(res)
                
                row = u"%s\
                    <td class='tb_td' style='padding:4px'>%s</td>\
                    <td class='tb_td' style='padding:4px'>%s</td>\
                " % (row, minion, res)
            row = u"%s</tr>" % (row)
            html = u"%s%s"    % (html, row)

        html = u"%s</table>"    % (html)
        return html

def get_box_html(title, content):
    config = {"title": title, "content": content}
    html = u"<div style='margin: 8px 0'>\
                        <div class='header' style='color:red; background-color:#afafaf; padding: 4px 2px;'>%(title)s</div>\
                        <div class='content' style='border: 1px solid #afafaf; padding: 8px;'>\
                            %(content)s\
                        </div>\
                    </div>" % config
    return html

def list2html(dictitem, sep_line="<br />"):
    """
    dictitem  = {
        "stdo": [],
        "stde": [],
        "retcode": 0 
    }
    sep_line  行分隔符
    """
    import types
    dictitem = dict(dictitem)
    html = u""
    for (key, value)  in dictitem.iteritems():
        ht1 = u"<font style='color: black; font-weight: bold;'>[ %s ]</font><br />" % (key)
        ht2 = u""
        if types.ListType == type(value):
            ht2 = str(sep_line).join(value)
#         elif type(value) in (types.DictType, types.ObjectType):
#             value = dict(value)
#             ht2 = list2html(value)
        else:
            ht2 = str(value)
        html = u"%s%s%s<br />" % (html, ht1, ht2)
    return html


def list2table(input_list):
    table_html = "<table>"
    for line in input_list:
        table_html = "%s<tr><td style='word-wrap:break-word;border:1px solid #aaaaaa;border-spacing: 0;border-collapse:collapse;padding:3px;'>%s</td></tr>" % (table_html, line)
    table_html = "%s</table>" % (table_html)
    return table_html