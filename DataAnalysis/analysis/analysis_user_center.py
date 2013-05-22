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

    def analysis_orders_renew(self, start_time, end_time):
        """分析续订"""
       
        seven_day_count = {}
        two_week_count = {}
        one_month_count = {}
        success_count = {}
        fail_count = {}
        for key in self.article_code_list:
            success_count[key] = 0
            fail_count[key] = 0
            seven_day_count[key] = 0
            two_week_count[key] = 0
            one_month_count[key] = 0

        for key in self.user_orders.keys():
            orders = self.user_orders[key]
            article_code = key[1]
            for i in range(len(orders)):
                deadline = orders[i]['order_cycle_end']
                if deadline >= start_time and deadline <= end_time:
                    while i < len(orders) - 1:
                        if int(orders[i+1]['total_pay_fee']) > 500:
                            break
                        else:
                            i += 1

                    if i < len(orders) - 1:
                        success_count[article_code] += 1
                        delay_days = (orders[i+1]['order_cycle_start'] - deadline).days
                        if delay_days <= 7:
                            seven_day_count[article_code] += 1
                        if delay_days <= 14:
                            two_week_count[article_code] += 1
                        if delay_days <= 30:
                            one_month_count[article_code] += 1
                    else:
                        fail_count[article_code] += 1

        print '产品,统计开始时间,统计结束时间,过期用户数,截止当下的续约率,7天内续约率,14天内续约率,30天内续约率'
        for key in self.article_code_list:
            fail_num = success_count[key]+fail_count[key]
            success_percent = float(success_count[key]) / fail_num
            seven_day_percent = float(seven_day_count[key]) / fail_num
            two_week_percent = float(two_week_count[key]) / fail_num
            one_month_percent = float(one_month_count[key]) / fail_num

            print '%s, %s, %s, %d, %.2f, %.2f, %.2f, %.2f' % (self.code_name[key], \
                    str(start_time.date()), str(end_time.date()), \
                    fail_num, success_percent, seven_day_percent, two_week_percent, one_month_percent)
    
    def analysis_orders_statistics(self):
        """统计订单类型"""
        
        price_type = [0 for i in range(8)]
        first_type = {}
        second_type = {}
        more_type = [0 for i in range(6)]
        
        cycle_type = [u"1个月", u"12个月", u"6个月", u"3个月", u"0个月" ]
        for key in cycle_type:
            first_type[key] = 0
            second_type[key] = 0
            
        order_count = 0
        for key in self.user_orders.keys():
            orders = self.user_orders[key]
            for i in range(len(orders)):
                order = orders[i]
                if i == 0:
                    first_type[order['order_cycle']] += 1
                    fee = int(order['total_pay_fee']) / 100
                    price_type[fee / 100] += 1
                    order_count += 1

                elif i == 1:
                    second_type[order['order_cycle']] += 1

                more_type[i] += 1
            
            if order_count > 10000:
                break
        print '首次订购价格'
        price_sum = sum(price_type)
        for i in range(len(price_type)):
            print '%d~%d: %d, %.4f' % (i*100, i*100+100, price_type[i], float(price_type[i])/price_sum)
        print '合计:', price_sum

        print '第一次订购周期'
        cycle_sum = sum(first_type.values())
        for key in cycle_type:
            print '%s, %d, %.3f' % (key, first_type[key], float(first_type[key])/cycle_sum)
        print '合计:', cycle_sum

        print '第二次订购周期'
        cycle_sum = sum(second_type.values())
        for key in cycle_type:
            print '%s, %d, %.3f' % (key, second_type[key], float(second_type[key])/cycle_sum)
        print '合计:',cycle_sum

        print '重复订购情况'
        more_sum = sum(more_type)
        for i in range(len(more_type)):
            print '订购%d次, %d, %.3f' % (i+1, more_type[i], float(more_type[i])/more_sum)
        print '合计:',more_sum 

def daily_update_script():
    """更新user_center 并将更新导入到百会CRM"""
    
    user_obj = UserCenter(['ts-1796606', 'ts-1797607'])
    user_obj.collect_online_info()
    user_obj.analysis_orders_renew(datetime.datetime(2013, 2, 1), datetime.datetime(2013, 2, 28))
    user_obj.analysis_orders_renew(datetime.datetime(2013, 3, 1), datetime.datetime(2013, 3, 31))
    user_obj.analysis_orders_renew(datetime.datetime(2013, 4, 1), datetime.datetime(2013, 4, 30))
    user_obj.analysis_orders_renew(datetime.datetime(2013, 5, 1), datetime.datetime(2013, 5, 20))


if __name__ == '__main__':
    daily_update_script()
    #user_obj = UserCenter(['ts-1796606'])
    #user_obj.collect_online_info()
    #user_obj.analysis_orders_statistics()
