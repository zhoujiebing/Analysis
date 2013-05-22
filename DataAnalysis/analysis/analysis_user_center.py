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
from CommonTools.send_tools import send_sms, send_email_with_text
from DataAnalysis.conf.settings import CURRENT_DIR
from user_center.conf.settings import WORKER_DICT
from user_center.services.shop_db_service import ShopDBService
from user_center.services.order_db_service import OrderDBService
from user_center.services.refund_db_service import RefundDBService
from user_center.services.support_db_service import SupportDBService

class UserCenter:

    def __init__(self):
        self.time_now = datetime.datetime.now()
        self.code_name = {'ts-1796606':'省油宝', 'ts-1797607':'选词王', 'ts-1817244':'淘词'}
        self.order_type = {1:'新订', 2:'续订', 3:'升级', 4:'后台赠送', 5:'后台自动续订'}
        self.support_type = {7:'7天初访', 14:'2周回访', 30:'1月回访', 90:'3月回访', \
                180:'半年回访',270:'9月回访',-3:'3天到期续签'}
        self.time_type = {u'1个月':[7,14,-3],\
                u'3个月':[7,30,-3],\
                u'6个月':[7,30,90,-3],\
                u'12个月':[7,30,180,270,-3]}
        logger.info('UserCenter init success')
         
    def collect_online_info(self):
        """获取用户数据中心信息"""
        
        logger.info('start collect_online_info')
        
        #获取所有用户
        all_shop = ShopDBService.get_all_shop_list()
        self.nick_shop = {}        
        for shop in all_shop:
            self.nick_shop[shop['nick']] = shop
        
        logger.info('finish collect shop info')
        
        #获取所有订单
        all_order = OrderDBService.get_all_orders_list()
        logger.info('finish collect order info')
        
        self.user_orders = {}
        for order in all_order:
            key = (order['nick'], order['article_code'])
            if not self.user_orders.has_key(key):    
                self.user_orders[key] = []
            self.user_orders[key].append(order)
        
        logger.info('finish arrange order info')
        
        #获取所有退款
        all_refund = RefundDBService.get_all_refunds_list()
        refund_list = [refund['order_id'] for refund in all_refund]
        
        logger.info('finish collect refund info')
        
        for key in self.user_orders.keys():
            real_orders = []
            orders = self.user_orders[key]
            orders.sort(key=lambda order:order['order_cycle_start'])
            for i in range(len(orders)):
                order = orders[i]
                if int(order['total_pay_fee']) > 500:
                    if i < len(orders) - 1:
                        next_order = orders[i+1]
                        if int(next_order['total_pay_fee']) <= 500 and next_order['biz_type'] == 2:
                            order['order_cycle_end'] = next_order['order_cycle_end']
                    real_orders.append(order)
            self.user_orders[key] = real_orders
        logger.info('finish collect_online_info')

    def analysis_orders_renew(self, start_time, end_time, article_code_list):
        """续费率统计"""
       
        some_days = [-10, -3, 0, 3, 7, 10]
        some_day_count = {}
        success_count = {}
        fail_count = {}
        for key in article_code_list:
            success_count[key] = 0
            fail_count[key] = 0
            for days in some_days:
                some_day_count[(key,days)] = 0 

        for key in self.user_orders.keys():
            orders = self.user_orders[key]
            article_code = key[1]
            if not article_code in article_code_list:
                continue
            for i in range(len(orders)):
                deadline = orders[i]['order_cycle_end']
                if deadline >= start_time and deadline <= end_time:
                    
                    if i < len(orders) - 1:
                        success_count[article_code] += 1
                        delay_days = (orders[i+1]['order_cycle_start'] - deadline).days
                        for days in some_days:
                            if delay_days > days:
                                continue
                            some_day_count[(article_code, days)] += 1

                    else:
                        fail_count[article_code] += 1
                    
                    break
                elif deadline > end_time:
                    break
        
        return_str = ''
        header = '产品,统计开始时间,统计结束时间,过期用户数,截止当下的续费数,续费率\n'
        some_days_str = ','.join([str(day)+'天续费' for day in some_days]) + '\n'
        
        for key in article_code_list:
            fail_num = success_count[key]+fail_count[key]
            success_percent = float(success_count[key]) / fail_num
            report = '%s, %s, %s, %d, %d, %.2f\n' % (self.code_name[key], \
                    str(start_time.date()), str(end_time.date()), fail_num, \
                    success_count[key], success_percent)
            
            report1 = []
            report2 = []
            for i in range(len(some_days)):
                days = some_days[i]
                days_count = some_day_count[(key, days)]
                report2.append('%.2f' % (float(days_count) / fail_num))
                if i > 0:
                    days = some_days[i-1]
                    days_count -= some_day_count[(key, days)]
                report1.append(str(days_count))
            return_str += header
            return_str += report
            return_str += some_days_str
            return_str += ','.join(report1)+'\n'
            return_str += ','.join(report2)+'\n'
        
        return return_str

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

def daily_report_script():
    """日常订单统计报表"""
    
    today = datetime.datetime.combine(datetime.date.today(), datetime.time())
    daily_report_date = today - datetime.timedelta(days=11)
    user_obj = UserCenter()
    user_obj.collect_online_info()
    return_str = user_obj.analysis_orders_renew(daily_report_date, daily_report_date, ['ts-1796606', 'ts-1797607'])
    send_email_with_text('zhangfenfen@maimiaotech.com', return_str, '日常续费统计')
    #send_email_with_text('zhoujiebing@maimiaotech.com', return_str, '日常续费统计')

if __name__ == '__main__':
    daily_report_script()
    #user_obj = UserCenter(['ts-1796606'])
    #user_obj.collect_online_info()
    #user_obj.analysis_orders_statistics()
