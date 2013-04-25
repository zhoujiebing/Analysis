#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:  zhoujiebing
@contact: zhoujiebing@maimiaotech.com
@date: 2012-08-25 16:18
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
import os
import re
import urllib2

#卖家名,服务开始日期,服务截止日期,订购软件,店铺,订单类型,金额,阶段,数据来源,软件订单名
ORDER_KEYS = [
        ['nick', str],
        ['start_time', str],
        ['end_time', str],
        ['soft', str],
        ['link', str],
        ['type', str],
        ['money', int],
        ['stage', str],
        ['from', str],
        ['order_name', str]]

class SelfOrder:

    @classmethod
    def get_file_name(self, current_dir, code, date):
        #order_ts-17966062013-03-05.csv
        return current_dir + 'data/order/order_' + str(code) + str(date) + '.csv'

    @classmethod
    def get_store_order(self, code, current_dir, date):
        """获取date 当天的所有订单"""

        order_list = []
        file_name = SelfOrder.get_file_name(current_dir, code, date)
        if os.path.isfile(file_name):
            for line in file(file_name):
                order = SelfOrder.parser_ztc_order(line)
                if not order:
                    continue
                order_list.append(order)
        return order_list

    @classmethod
    def parser_self_order(self, line):
        
        order = {}
        line_data = line.split(',')
        if len(line_data) != len(ORDER_KEYS):
            pass
        for i in range(len(line_data)):
            key_type = ORDER_KEYS[i]
            order[key_type[0]] = key_type[1](line_data[i])

        return order 

       
