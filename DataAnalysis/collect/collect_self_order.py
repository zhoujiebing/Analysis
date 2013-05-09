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
import os
import sys
import time
if __name__ == '__main__':
    sys.path.append('../../')

import datetime
from CommonTools.logger import logger
from CommonTools.send_tools import send_sms
from DataAnalysis.conf.settings import CURRENT_DIR
from user_center.conf.settings import WORKER_DICT
from user_center.services.shop_db_service import ShopDBService
from user_center.services.order_db_service import OrderDBService
class UserOrder:

    def __init__(self):
        self.code_name = {'ts-1796606':'省油宝', 'ts-1797607':'选词王', 'ts-1817244':'淘词'}
        
        self.order_type = {1:'新订', 2:'续订', 3:'升级', 4:'后台赠送', 5:'后台自动续订'}
        self.support_type = {7:'7天初访', 14:'2周回访', 30:'1月回访', 90:'3月回访', \
                180:'半年回访',270:'9月回访',-3:'3天到期续签'}
        self.time_type = {u'1个月':[7,14,-3],\
                u'3个月':[7,30,-3],\
                u'6个月':[7,30,90,-3],\
                u'12个月':[7,30,180,270,-3]}

    def get_lost_order(self, start_created, end_created):
        """获取某段时间的订单
        date 是datetime.datetime(2013,2,18,0,0,0) 这种类型"""
        self.order_list = OrderDBService.get_orders_between_time(start_created, end_created)
    
    def get_yesterday_order(self):
        """获取昨天的订单"""
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday = datetime.datetime.combine(yesterday, datetime.time())
        self.order_list = OrderDBService.get_orders_between_time(yesterday, yesterday) 

    def write_order(self, lost_flag=False):
        """写入文件"""

        if not lost_flag:
            self.file_obj = file(CURRENT_DIR+'data/order.csv', 'w')
            self.file_service_support = file(CURRENT_DIR+'data/support.csv', 'w')
        else:
            self.file_obj = file(CURRENT_DIR+'data/lost_order.csv', 'a')
            self.file_service_support = file(CURRENT_DIR+'data/lost_support.csv', 'a')

        for order in self.order_list:
            order['app_name'] = self.code_name[order['article_code']] 
            order_start = order['order_start']
            order['start'] = datetime.date(order_start.year, order_start.month, order_start.day)
            order_end = order['order_end']
            order['end'] = datetime.date(order_end.year, order_end.month, order_end.day)
            order['shangji'] = order['nick']+'_'+order['app_name']+'_'+str(order['end'])
            self.file_obj.write('%(nick)s,%(start)s,%(end)s,%(app_name)s,%(order_type)s,%(sale)d,订购使用中,每日更新,%(shangji)s\n' % (order))
            #print '%(nick)s,%(start)s,%(end)s,%(app_name)s,%(order_type)s,%(sale)d,订购使用中,每日更新,%(shangji)s' % (order)
            
            #获取专属客服id
            shop = ShopDBService.get_shop_by_nick(order['nick'])
            worker_id = shop['worker_id']
            worker_name = WORKER_DICT[worker_id]

            order_time = order['order_cycle']
            support_list = self.time_type[order_time]
            for days in support_list:
                support = self.support_type[days]
                support_time = order_start+datetime.timedelta(days=days)
                priority = '中'
                if days < 0:
                    support_time = order_end-datetime.timedelta(days=-days)
                    priority = '高'
                support_name = order['app_name']+'_'+support+'_'+str(support_time)+'_'+worker_name
                self.file_service_support.write('%s,%s,%s,%s,%s,%s,%s,未回访,后台发掘\n' % \
                        (order['nick'], support_name, priority, order['app_name'], support, str(support_time), worker_name))
                
        self.file_obj.close()
        self.file_service_support.close()

def collect_lost_order(start_date, end_date):
    """收集遗漏的订单"""

    while start_date < end_date:
        start_created = datetime.datetime.combine(start_date, datetime.time())
        order_obj = UserOrder()
        order_obj.get_lost_order(start_created, start_created+datetime.timedelta(days=1))
        order_obj.write_order(True)
        print '抓取 ' + str(start_date) + '的订单成功'
        start_date += datetime.timedelta(days=1)
        time.sleep(20)


def collect_self_order_script():
    order_obj = UserOrder()
    order_obj.get_yesterday_order()
    order_obj.write_order()

if __name__ == '__main__':
    #collect_lost_order(datetime.date(2013,4,28), datetime.date(2013,5,2))
    collect_self_order_script()
