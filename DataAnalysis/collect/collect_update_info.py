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
        """获取用户信息"""
        
        self.shop_list = ShopDBService.get_all_shop_list()
        all_order = OrderDBService.get_all_orders_list()
        self.user_order = {}
        
        for order in all_order:
            if not order['article_code'] in self.article_code_list:
                continue
            key = order['nick'] + order['article_code']
            if order['order_end'] < self.time_now - datetime.timedelta(days=4):
                continue
            old_order = self.user_order.get(key, {'order_start':datetime.datetime(2011, 1, 1, 0, 0)})
            if order['order_start'] > old_order['order_start']:
                self.user_order[key] = order

    def collect_update_info(self):
        """收集更新"""
        
        self.update_shops = [] 
        self.update_orders = []
        
        for shop in self.shop_list:
            worker_id = shop.get('worker_id', None)
            if not worker_id:
                logger.info('%s worker_id 为 none', shop['nick'])
                continue
            upset_flag = False
            normal_flag = False

            for article_code in self.code_name.keys():
                article_status = article_code + '_status'
                if not shop.has_key(article_status):
                    #没有购买该产品
                    continue
                deadline = shop.get(article_code + '_deadline', None)
                order = self.user_order.get(shop['nick']+article_code, None)
                article_order = article_code + '_order_id'
                order_id = shop.get(article_order, 0)
                
                if order and order_id != order['order_id']:
                    if order['order_type'] == '退订':
                        shop[article_status] = '退款'
                    else:
                        order['worker_name'] = WORKER_DICT[worker_id]
                        order['seller_name'] = shop.get('seller_name', '未找到')
                        order['seller_mobile'] = shop.get('seller_mobile', '')
                        self.update_orders.append(order)
                   
                    if not deadline:
                        logger.info('%s 没有 deadline', shop['nick'])
                        deadline = order['order_end']
                        shop[article_code + '_deadline'] = deadline

                    shop[article_order] = order['order_id']
                    upset_flag = True
                
                if not deadline:
                    continue
                if deadline < self.time_now and shop[article_status] == '使用中':
                    shop[article_order] = '到期'
                    upset_flag = True
                if deadline > self.time_now:
                    normal_flag = True
            
            if not normal_flag and shop['flag']:
                shop['flag'] = False
                upset_flag = True

            if upset_flag:
                shop['update_time'] = self.time_now
                self.update_shops.append(shop)

                
    def write_baihui_orders(self):
        """将需要更新的订单及服务支持写入文件"""

        self.file_obj = file(CURRENT_DIR+'data/order.csv', 'w')
        self.file_service_support = file(CURRENT_DIR+'data/support.csv', 'w')
        for order in self.update_orders:
            order['app_name'] = self.code_name[order['article_code']] 
            order_start = order['order_start']
            order['start'] = datetime.date(order_start.year, order_start.month, order_start.day)
            order_end = order['order_end']
            order['end'] = datetime.date(order_end.year, order_end.month, order_end.day)
            order['shangji'] = order['nick']+'_'+order['app_name']+'_'+str(order['end'])
            
            self.file_obj.write('%(nick)s,%(start)s,%(end)s,%(app_name)s,%(order_type)s,%(sale)d,订购使用中,每日更新,%(shangji)s,%(worker_name)s,%(seller_name)s,%(seller_mobile)s\n' % (order))
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
                self.file_service_support.write('%s,%s,%s,%s,%s,%s,%s,未回访,后台发掘\n' % \
                        (order['nick'], support_name, priority, order['app_name'], support, str(support_time), order['worker_name']))
                
        self.file_obj.close()
        self.file_service_support.close()
    
    def update_shops_online(self):
        """更新用户中心"""

        for shop in self.update_shops:
            ShopDBService.upsert_shop(shop)

def collect_update_info_script():
    """更新user_center 并将更新导入到百会CRM"""
    
    user_obj = UserCenter(['ts-1796606'])
    user_obj.collect_online_info()
    user_obj.collect_update_info()
    user_obj.write_baihui_orders()
    user_obj.update_shops_online()

if __name__ == '__main__':
    collect_update_info_script()

