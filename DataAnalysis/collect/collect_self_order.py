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
from tao_models.conf.settings import set_taobao_client
set_taobao_client('12685542', '6599a8ba3455d0b2a043ecab96dfa6f9')
from tao_models.vas_order_search import VasOrderSearch

class UserOrder:

    def __init__(self, article_code):
        self.article_code = article_code
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

        self.order_list = VasOrderSearch.search_vas_order(self.article_code, start_created, end_created)

    def get_yesterday_order(self):
        """获取昨天的订单"""

        self.order_list = VasOrderSearch.search_vas_order_yesterday(self.article_code)

    def write_order(self, date, lost_flag=False):
        """写入文件"""

        self.file_obj = file(CURRENT_DIR+'data/order/order_'+self.article_code+str(date)+'.csv', 'w')
        #服务支持没有必要存历史的记录
        if not lost_flag:
            self.file_service_support = file(CURRENT_DIR+'data/support_'+self.article_code+'.csv', 'w')
        else:
            self.file_service_support = file(CURRENT_DIR+'data/lost_support_'+self.article_code+'.csv', 'a')
        app_name = self.code_name[self.article_code] 
        for order in self.order_list:
            nick = order.nick
            order_start = order.order_cycle_start
            order_start = datetime.date(order_start.year, order_start.month, order_start.day)
            order_end = order.order_cycle_end
            order_end = datetime.date(order_end.year, order_end.month, order_end.day)
            shop_search = 'http://shopsearch.taobao.com/search?q=' + nick
            biz_type = order.biz_type
            sale = int(order.total_pay_fee) / 100
            shangji = nick+'_'+app_name+'_'+str(order_end)
            self.file_obj.write('%s,%s,%s,%s,%s,%s,%d,订购使用中,每日更新,%s\n' % (nick, str(order_start),\
                    str(order_end), app_name, shop_search, self.order_type[biz_type], sale, shangji))
            rand = hash(str(nick)) % 20
            order_time = order.order_cycle
            support_list = self.time_type[order_time]
            for days in support_list:
                support = self.support_type[days]
                support_time = order_start+datetime.timedelta(days=days)
                priority = '中'
                if days < 0:
                    support_time = order_end-datetime.timedelta(days=-days)
                    priority = '高'
                support_name = app_name+'_'+support+'_'+str(support_time)+'_'+str(rand)
                self.file_service_support.write('%s,%s,%s,%s,%s,%s,%d,未回访,后台发掘\n' % \
                        (nick, support_name, priority, app_name, support, str(support_time), rand))
                
        self.file_obj.close()
        self.file_service_support.close()

def collect_lost_order(start_date, end_date):
    """收集遗漏的订单"""

    while start_date < end_date:
        start_created = datetime.datetime.combine(start_date, datetime.time())
        syb = UserOrder('ts-1796606')
        syb.get_lost_order(start_created, start_created+datetime.timedelta(days=1))
        syb.write_order(start_date, True)
        xcw = UserOrder('ts-1797607')
        xcw.get_lost_order(start_created, start_created+datetime.timedelta(days=1))
        xcw.write_order(start_date, True)
        print '抓取 ' + str(start_date) + '的订单成功'
        start_date += datetime.timedelta(days=1)
        time.sleep(20)


def collect_self_order_script():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    syb = UserOrder('ts-1796606')
    syb.get_yesterday_order()
    syb.write_order(yesterday)
    xcw = UserOrder('ts-1797607')
    xcw.get_yesterday_order()
    xcw.write_order(yesterday)

if __name__ == '__main__':
    #collect_lost_order(datetime.date(2013,4,28), datetime.date(2013,5,2))
    collect_self_order_script()
