#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:xieguanfu 
@contact: xieguanfu@maimiaotech.com
@date: 2013-07-17 11:55
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
from CommonTools.send_tools import send_sms, send_email_with_text, DIRECTOR
from CommonTools.wangwang_tools import parse_wangwang_talk_record
from DataAnalysis.conf.settings import CURRENT_DIR
from user_center.conf.settings import WORKER_DICT, FULL_NUM
from user_center.services.shop_db_service import ShopDBService
from user_center.services.order_db_service import OrderDBService
from user_center.services.refund_db_service import RefundDBService
from user_center.services.support_db_service import SupportDBService
from DataAnalysis.analysis.analysis_campaign_complex import analysis_campaign_complex

class YearlyMember:

    @classmethod     
    def collect_member_info(cls,article_code):
        """获取用户数据中心信息"""
        #获取所有订单
        all_order = OrderDBService.get_all_orders_list()
        order_time_dict={}
        for order in all_order:
            if article_code is not None and article_code !=order["article_code"]:
                continue
            nick=order["nick"] 
            if nick not in  order_time_dict:
                order_time_dict[nick]={"order_count":0,"pay":0,"free_order_count":0,"days":0}
            days=(order["order_cycle_end"]-order["order_cycle_start"]).days
            order_time_dict[nick]["order_count"]+=1
            order_time_dict[nick]["pay"]+=int(order["total_pay_fee"])
            order_time_dict[nick]["days"]+=days
            if int(order["total_pay_fee"])<=500:
                order_time_dict[nick]["free_order_count"]+=1
        return order_time_dict

    @classmethod
    def collect_year_member_info(cls,article_code):
        """年度会员统计"""
        f=open(CURRENT_DIR+"/data/year_member.csv","w")
        f.write("nick,订购天数,订单数,免费订单数\n")
        order_dict=cls.collect_member_info(article_code)
        return_list=[]
        for key,info in order_dict.iteritems():
            if info["days"]>=365:
                info["nick"]=key
                return_list.append(info)
                message="%s,%s,%s,%s\n" %(key,info["days"],info["order_count"],info["free_order_count"])
                f.write(message)
        f.close()
        return return_list

        
if __name__=="__main__":
    syb="ts-1796606"
    YearlyMember.collect_year_member_info(syb)
