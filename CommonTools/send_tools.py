#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2012-12-10 17:13
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
import sys
import json
import time
import smtplib
import urllib,urllib2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from CommonTools.logger import logger

SEND_COMMAND = 'MT_REQUEST' 
SPID = '5208'
SP_PASSWORD = 'mm5208'
DC = '15'
SEND_MSG_URL = 'http://esms.etonenet.com/sms/mt'

def send_email_with_text(msgTo, text, subject):
    """发送文本email"""

    msg = MIMEMultipart()
    msg.attach(MIMEText(text, _charset='utf-8'))
    msg['Subject'] = subject
    msg['From'] = 'zhoujiebing@maimiaotech.com'
    msg['To'] = msgTo
    try:
        smtp = smtplib.SMTP()
        smtp.connect('smtp.ym.163.com', 25) 
        smtp.login(msg['From'], 'zhoujb.19890211')                                                                       
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
    except Exception,e:
        logger.error('send_email: %s' % (str(e)))

def send_email_with_html(msgTo, html, subject):
    """发送html email"""

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = 'zhoujiebing@maimiaotech.com'
    msg['To'] = msgTo
    html_att = MIMEText(html, 'html', 'utf-8')
    msg.attach(html_att)
    try:
        smtp = smtplib.SMTP()
        smtp.connect('smtp.ym.163.com', 25) 
        smtp.login(msg['From'], 'zhoujb.19890211')                                                                       
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
    except Exception,e:
        logger.error('send_email: %s' % (str(e)))

def _toHex(str,charset):
    s = str.encode(charset)
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    return reduce(lambda x,y:x+y, lst)
def _toHex(str,charset):
    s = str.encode(charset)
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    return reduce(lambda x,y:x+y, lst)

def _parse_sms_response(message):
    dict = {}
    response_list = message.split('&')
    for info in response_list:
        key_value = info.split('=')
        dict[key_value[0]] = key_value[1]   
    return dict

def send_sms(cellphone, text, retry_times=3):
    """发送短信"""

    retry_times -= 1
    if retry_times < 0:
        logger.error('send message to %s unsuccessfully'%(cellphone,))
        return
    dict = {}
    dict['command'] = SEND_COMMAND
    dict['spid'] = SPID
    dict['sppassword'] = SP_PASSWORD
    dict['da'] = '86'+cellphone
    dict['dc'] = DC 
    dict['sm']  = _toHex(text,'gbk')
    url_params = urllib.urlencode(dict)
    try:
        response = urllib2.urlopen(SEND_MSG_URL,url_params)
        dict = _parse_sms_response(response.read())
        if dict.get('mterrcode',None) != '000':
            logger.error('send message to %s unsuccessfully:response error'%(cellphone,))
            send_sms(cellphone,text,retry_times)
    except urllib2.HTTPError,e:
        logger.error('send message to %s unsuccessfully:url connect error'%(cellphone,))
        send_sms(cellphone,text,retry_times)
    except Exception,e:
        logger.error('send message to %s unsuccessfully:server error'%(cellphone,))
        send_sms(cellphone,text,retry_times)

