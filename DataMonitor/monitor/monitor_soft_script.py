#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebing
@contact: zhoujiebing@maimiaotech.com
@date: 2013-02-27 15:52
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
import sys
import logging
logger = logging.getLogger()
import datetime
if __name__ == '__main__':
    sys.path.append('/home/zhoujiebing/Analysis/')

import DataMonitor.conf.settings
from CommonTools.send_tools import send_sms
from CommonTools.logger import logger
from DataMonitor.monitor.monitor_marketing_cost import monitor_marketing_cost
from DataMonitor.monitor.monitor_order_add import monitor_order_add
from DataMonitor.monitor.monitor_comment_add import monitor_comment_add

def monitor_soft_script():
    try:
        return_info = monitor_soft() 
    except Exception,e:
        logger.error('monitor_soft error: %s', str(e))
        send_sms('13738141586', 'monitor_soft_script error: '+str(e))
    else:
        logger.info(return_info)

def monitor_soft():
    """软件监测脚本
    1.麦苗科技营销花费 定期监测
    2.省油宝新增订单数 定期监测
    3.省油宝新增评价 定期监测
    4.北斗新增评价 定期监测
    省油宝,ts-1796606
    北斗,ts-1797607
    """
    current_time = datetime.datetime.now()
    rest_hours = range(1,7)
    if current_time.hour in rest_hours:
        return None
     
    marketing_info = monitor_marketing_cost()
    order_info = monitor_order_add('省油宝', 'ts-1796606')
    comment_info = monitor_comment_add('省油宝', 'ts-1796606') + monitor_comment_add('北斗', 'ts-1797607')
    return_info = marketing_info + order_info + comment_info 
    
    if return_info:
        send_sms('13738141586', 'test: ' + return_info)
        return 'monitor_soft: ' + return_info
        #send XJ
        send_sms('18658818166', return_info)
        if comment_info:
            #send LW
            send_sms('15158877255', comment_info)
            #send XK
            send_sms('13646844762', comment_info)

        if marketing_info or order_info:
            #send YB
            send_sms('15858224656', return_info)
        return 'monitor_soft: ' + return_info
    else:
        return 'monitor_soft ok'

if __name__ == '__main__':
    monitor_soft_script()
