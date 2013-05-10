#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebing
@contact: zhoujiebing@maimiaotech.com
@date: 2013-05-02 10:52
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
import os
import re
import sys
import datetime

if __name__ == '__main__':
    sys.path.append('../../')

from DataAnalysis.conf.settings import CURRENT_DIR
from CommonTools.self_order_tools import SelfOrder
from CommonTools.logger import logger
from CommonTools.send_tools import send_email_with_file, send_sms

def send_add_order_and_support():
    """发送每日新增订单与服务支持"""
    
    merge_order = []
    merge_support = []
    order_head = CURRENT_DIR+'data/order_head.csv'
    support_head = CURRENT_DIR+'data/support_head.csv'
    send_order = CURRENT_DIR+'data/new_order.csv'
    send_support = CURRENT_DIR+'data/new_support.csv'

    merge_order.append(CURRENT_DIR+'data/order.csv')
    merge_support.append(CURRENT_DIR+'data/support.csv')
    os.system('cat %s %s > %s' % (order_head, ' '.join(merge_order), send_order))
    os.system('cat %s %s > %s' % (support_head, ' '.join(merge_support), send_support))

    subject = '昨日新增订单测试版'
    content = '支持专属客服,注意，订单抓取现在使用新脚本且近期订单API抽风的可能性比较大，请事先认真核对下再导入到百会CRM。\n有问题和不明确的请及时反馈'
    send_email_with_file('zhangfenfen@maimiaotech.com', content, subject, [send_order, send_support])
    #send_email_with_file('zhoujiebing@maimiaotech.com', content, subject, [send_order, send_support])


if __name__ == '__main__':
    try: 
        send_add_order_and_support()
    except Exception, e:
        logger.exception('send_add_order_and_support error: %s', str(e))
        send_sms('send_add_order_and_support error:%s' % (str(e)))
