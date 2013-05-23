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
         
        #要更新的用户
        self.update_shops = []
        #要更新的服务支持
        self.update_supports = []
        #百会导入
        self.add_orders = []

    def collect_online_info(self):
        """获取用户数据中心信息"""
        
        #获取所有用户
        all_shop = ShopDBService.get_all_shop_list()
        self.nick_shop = {}        
        for shop in all_shop:
            self.nick_shop[shop['nick']] = shop
        
        #获取所有退款
        all_refund = RefundDBService.get_all_refunds_list()
        refund_list = [refund['order_id'] for refund in all_refund]
        
        #获取所有订单
        all_order = OrderDBService.get_all_orders_list()
        self.user_order = {}
        
        for order in all_order:
            if not order['article_code'] in self.article_code_list:
                continue
            if order['order_id'] in refund_list:
                continue
            key = order['nick'] + order['article_code']
            old_order = self.user_order.get(key, {'order_cycle_start':datetime.datetime(2011, 1, 1, 0, 0)})
            if order['order_cycle_start'] > old_order['order_cycle_start']:
                self.user_order[key] = order

        #获取所有服务支持
        all_support = SupportDBService.get_all_supports_list()
        self.user_supports = {}
        
        for support in all_support:
            if not support['article_code'] in self.article_code_list:
                continue
            key = support['nick'] + support['article_code']
            if not self.user_supports.has_key(key):
                self.user_supports[key] = []
            self.user_supports[key].append(support)

        #nick_worker存放 需要修改的客户客服关系 后期 取消
        self.nick_worker = {}
        
        for line in file(CURRENT_DIR+'data/worker_nick.csv'):
            line_data = line.split(',')
            worker_id = int(line_data[0])
            nick = (line_data[1].split('\n'))[0].decode('utf-8')
            self.nick_worker[nick] = worker_id
    
    def collect_reset_supports(self):
        """根据所有有效订单,全量更新服务支持"""
        
        support_list = []
        for order in self.user_order.values():
            support_list.extend(self.generate_order_supports(order))
        for support in support_list:
            if support['occur_time'] < self.time_now:
                continue
            self.update_supports.append(support)
    
    def collect_update_worker(self):
        """更新客户客服关系"""

        for nick in self.nick_worker.keys():
            new_worker_id = self.nick_worker[nick]
            shop = self.nick_shop.get(nick, None)
            if not shop:
                #要更新的用户 并不存在
                logger.info('collect_update_worker %s not exist' % nick)
                print 'collect_update_worker %s not exist' % nick
                continue
            if shop['worker_id'] != new_worker_id:
                shop['worker_id'] = new_worker_id
                shop['update_time'] = self.time_now
                self.update_shops.append(shop)
                for article_code in self.code_name.keys():
                    key = nick+article_code
                    order = self.user_order.get(key, None)
                    if order:
                        self.add_orders.append(order)

    
    def collect_useful_orders(self):
        """收集全量有效订单"""
        
        for order in self.user_order.values():
            if order['article_code'] not in self.article_code_list:
                continue
            self.add_orders.append(order)

    def collect_update_info(self):
        """收集更新"""
        
        for shop in self.nick_shop.values():
            worker_id = shop.get('worker_id', None)
            if not worker_id:
                logger.info('%s worker_id 为 none' % (shop['nick']))
                print '%s worker_id 为 none' % (shop['nick'])
                continue
            upset_flag = False
            normal_flag = False
            
            for article_code in self.code_name.keys():
                key = shop['nick'] + article_code
                article_status = article_code + '_status'
                article_order = article_code + '_order_id'
                article_deadline = article_code + '_deadline'
                
                #获取shop中关于该产品的信息
                deadline = shop.get(article_deadline, None)
                order = self.user_order.get(key, None)
                order_id = shop.get(article_order, None)
                supports = self.user_supports.get(key, [])

                if not order and order_id:
                    #新退款用户
                    shop[article_order] = None
                    shop[article_status] = '退款'
                    shop[article_code + '_deadline'] = None
                    upset_flag = True

                if order and order_id != order['order_id']:
                    #新订或续订用户
                    deadline = order['order_cycle_end']
                    shop[article_code + '_deadline'] = deadline
                    shop[article_order] = order['order_id']
                    upset_flag = True
                    #百会导入
                    self.add_orders.append(order)
                
                if not deadline:
                    #压根没购买过
                    continue

                if deadline < self.time_now and shop[article_status] == '使用中':
                    shop[article_status] = '到期'
                    upset_flag = True

                if deadline > self.time_now:
                    #至少有一个产品是有效的
                    normal_flag = True
                
                #以下是服务支持部分
                for support in supports:
                    if support['order_id'] != shop[article_order] and \
                            support['support_status'] == '未处理':
                        support['support_status'] = '无效'
                        self.update_supports.append(support)
                
                if order and order_id != order['order_id']:
                    #新订或续订用户
                    self.update_supports.extend(self.generate_order_supports(order))

            if not normal_flag and shop['flag']:
                #没有一个有效的产品 转变为无效用户
                shop['flag'] = False
                upset_flag = True

            #收集待更新的用户数据
            if upset_flag:
                shop['update_time'] = self.time_now
                self.update_shops.append(shop)
    
    def generate_order_supports(self, order):
        """生成对应订单的服务支持"""

        support_types = self.time_type[order['order_cycle']]
        support_list = []
        for i in range(len(support_types)):
            support = {}
            days = support_types[i]
            support['nick'] = order['nick']
            support['order_id'] = order['order_id']
            support['article_code'] = order['article_code']
            support['support_id'] = order['order_id']*10 + i
            support['support_type'] = self.support_type[days]
            support['support_status'] = '未处理'
            support['occur_time'] = order['order_cycle_start']+datetime.timedelta(days=days)
            priority = '中'
            if days < 0:
                support['occur_time'] = order['order_cycle_end']-datetime.timedelta(days=-days)
                priority = '高'
            support_list.append(support)

        return support_list

    def write_baihui_info(self):
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
            
            shop = self.nick_shop.get(order['nick'], None)
            if not shop or not shop.get('worker_id', None):
                continue
            order['worker_name'] = WORKER_DICT[shop['worker_id']]
            order['seller_name'] = shop.get('seller_name', '')
            order['seller_mobile'] = shop.get('seller_mobile', '')

            file_obj.write('%(nick)s,%(start)s,%(end)s,%(app_name)s,%(order_type)s,%(sale)d,订购使用中,每日更新,%(shangji)s,%(worker_name)s,%(seller_name)s,%(seller_mobile)s\n' % (order))
            #print '%(nick)s,%(start)s,%(end)s,%(app_name)s,%(order_type)s,%(sale)d,订购使用中,每日更新,%(shangji)s' % (order)

            order_time = order['order_cycle']
            support_list = self.time_type[order_time]
            for days in support_list:
                support = self.support_type[days]
                support_time = order['start']+datetime.timedelta(days=days)
                priority = '中'
                if days < 0:
                    support_time = order['end']-datetime.timedelta(days=-days)
                    priority = '高'
                
                if support_time < self.time_now.date():
                    continue
                support_name = order['nick']+'_'+order['app_name']+'_'+support+'_'+str(support_time)
                file_service_support.write('%s,%s,%s,%s,%s,%s,%s,未回访,后台发掘\n' % \
                        (order['nick'], support_name, priority, order['app_name'], support, str(support_time), order['worker_name']))
                
        file_obj.close()
        file_service_support.close()
    
    def update_online(self):
        """更新用户中心"""

        for shop in self.update_shops:
            ShopDBService.upset_shop(shop)
        
        #由于目前用户中心没有独立的服务支持页面 可先不更新
        #for support in self.update_supports:
        #    SupportDBService.upsert_support(support)

    def write_nick_worker(self):
        """将未更新的客服客户关系写回"""

        file_obj = file(CURRENT_DIR+'data/worker_nick.csv', 'w') 
        for worker_nick in self.nick_worker.items():
            if worker_nick[1] != '':
                file_obj.write('%d,%s\n' % (worker_nick[1], worker_nick[0]))
        file_obj.close()

def daily_update_script():
    """更新user_center 并将更新导入到百会CRM"""
    logger.info('user_center update start') 
    try:
        user_obj = UserCenter(['ts-1796606'])
        user_obj.collect_online_info()
        user_obj.collect_update_info()
        user_obj.write_baihui_info()
        user_obj.update_online()
    except Exception,e:
        logger.exception('user_center update error: %s', str(e))
        send_sms('13738141586', 'user_center update error: '+str(e))
    else:
        logger.info('user_center update finish')

def reset_useful_support_script():
    """全量更新服务支持"""

    user_obj = UserCenter(['ts-1796606'])
    user_obj.collect_online_info()
    user_obj.collect_reset_supports()
    user_obj.update_online()

def reset_user_worker_relation():
    """重设部分客户客服关系"""
    
    user_obj = UserCenter(['ts-1796606'])
    user_obj.collect_online_info()
    user_obj.collect_update_worker()
    user_obj.write_baihui_info()
    user_obj.update_online()

def reset_baihui_info():
    """重设百会数据"""

    user_obj = UserCenter(['ts-1796606'])
    user_obj.collect_online_info()
    user_obj.collect_useful_orders()
    user_obj.write_baihui_info()

if __name__ == '__main__':
    daily_update_script()
    #reset_useful_support_script() 
    #reset_user_worker_relation()
    #reset_baihui_info()
