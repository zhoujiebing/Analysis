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
from user_center.services.refund_db_service import RefundDBService
from user_center.services.support_db_service import SupportDBService

class UserCenter:

    def __init__(self, article_code_list=['ts-1796606', 'ts-1797607', 'ts-1817244']):
        self.time_now = datetime.datetime.now()
        self.article_code_list = article_code_list
        self.code_name = {'ts-1796606':'省油宝', 'ts-1797607':'选词王', 'ts-1817244':'淘词'}
        self.order_type = {1:'新订', 2:'续订', 3:'升级', 4:'后台赠送', 5:'后台自动续订'}
        self.support_type = {7:'7天初访', 14:'2周回访', 30:'1月回访', 90:'3月回访', \
                180:'半年回访',270:'9月回访',-3:'3天到期续签'}
        self.time_type = {u'1个月':[7,14,-3],\
                u'3个月':[7,30,-3],\
                u'6个月':[7,30,90,-3],\
                u'12个月':[7,30,180,270,-3]}
         
    def collect_online_info(self):
        """获取用户数据中心信息"""
        
        #获取所有用户
        all_shop = ShopDBService.get_all_shop_list()
        self.nick_shop = {}        
        
        #获取所有订单
        all_order = OrderDBService.get_all_orders_list()
        self.user_orders = {}
        
        #获取所有退款
        all_refund = RefundDBService.get_all_refunds_list()
        refund_list = [refund['order_id'] for refund in all_refund]
        
        for shop in all_shop:
            self.nick_shop[shop['nick']] = shop

        for order in all_order:
            if not order['article_code'] in self.article_code_list:
                continue
            key = (order['nick'], order['article_code'])
            if not self.user_orders.has_key(key):    
                self.user_orders[key] = []
            self.user_orders[key].append(order)
        
        for key in self.user_orders.keys():
            self.user_orders[key].sort(key=lambda order:order['order_cycle_start'])

    def analysis_orders(self, start_time, end_time):
        """收集更新"""
       
        days = 3
        seven_day_count = {}
        success_count = {}
        fail_count = {}
        for key in self.article_code_list:
            success_count[key] = 0
            fail_count[key] = 0
            seven_day_count[key] = 0

        for key in self.user_orders.keys():
            orders = self.user_orders[key]
            article_code = key[1]
            for i in range(len(orders)):
                deadline = orders[i]['order_cycle_end']
                if deadline >= start_time and deadline <= end_time:
                    if i < len(orders) - 1:
                        success_count[article_code] += 1
                        if (orders[i+1]['order_cycle_start'] - deadline).days <= days:
                            seven_day_count[article_code] += 1
                    else:
                        fail_count[article_code] += 1

        print '产品,统计开始时间,统计结束时间,过期用户数,截止当下的续约率,到期后%d天内续约率' % days
        for key in self.article_code_list:
            fail_num = success_count[key]+fail_count[key]
            success_percent = float(success_count[key]) / fail_num
            seven_day_percent = float(seven_day_count[key]) / fail_num
            print '%s, %s, %s, %d, %.2f, %.2f' % (self.code_name[key], \
                    str(start_time.date()), str(end_time.date()), \
                    fail_num, success_percent, seven_day_percent)
    
    def write_baihui_orders(self):
        """将需要更新的订单及服务支持写入文件"""

        file_obj = file(CURRENT_DIR+'data/order.csv', 'w')
        file_service_support = file(CURRENT_DIR+'data/support.csv', 'w')
        for order in self.add_orders: 
            order['app_name'] = self.code_name[order['article_code']] 
            order_start = order['order_cycle_start']
            order['start'] = datetime.date(order_start.year, order_start.month, order_start.day)
            order_end = order['order_cycle_end']
            order['end'] = datetime.date(order_end.year, order_end.month, order_end.day)
            order['shangji'] = order['nick']+'_'+order['app_name']+'_'+str(order['end'])
            order['order_type'] = self.order_type[order['biz_type']]
            order['sale'] = int(order['total_pay_fee']) / 100
            
            shop = self.nick_shop[order['nick']]
            order['worker_name'] = WORKER_DICT[shop['worker_id']]
            order['seller_name'] = shop.get('seller_name', '')
            order['seller_mobile'] = shop.get('seller_mobile', '')

            file_obj.write('%(nick)s,%(start)s,%(end)s,%(app_name)s,%(order_type)s,%(sale)d,订购使用中,每日更新,%(shangji)s,%(worker_name)s,%(seller_name)s,%(seller_mobile)s\n' % (order))
            #print '%(nick)s,%(start)s,%(end)s,%(app_name)s,%(order_type)s,%(sale)d,订购使用中,每日更新,%(shangji)s' % (order)

            order_time = order['order_cycle']
            support_list = self.time_type[order_time]
            for days in support_list:
                support = self.support_type[days]
                support_time = order_start+datetime.timedelta(days=days)
                priority = '中'
                if days < 0:
                    support_time = order_end-datetime.timedelta(days=-days)
                    priority = '高'
                
                if support_time < self.time_now:
                    continue
                support_name = order['app_name']+'_'+support+'_'+str(support_time)
                file_service_support.write('%s,%s,%s,%s,%s,%s,%s,未回访,后台发掘\n' % \
                        (order['nick'], support_name, priority, order['app_name'], support, str(support_time), order['worker_name']))
                
        file_obj.close()
        file_service_support.close()
    
def daily_update_script():
    """更新user_center 并将更新导入到百会CRM"""
    
    user_obj = UserCenter(['ts-1796606', 'ts-1797607'])
    user_obj.collect_online_info()
    user_obj.analysis_orders(datetime.datetime(2013, 2, 1), datetime.datetime(2013, 2, 28))
    user_obj.analysis_orders(datetime.datetime(2013, 3, 1), datetime.datetime(2013, 3, 31))
    user_obj.analysis_orders(datetime.datetime(2013, 4, 1), datetime.datetime(2013, 4, 30))
    user_obj.analysis_orders(datetime.datetime(2013, 5, 1), datetime.datetime(2013, 5, 10))

if __name__ == '__main__':
    daily_update_script()
