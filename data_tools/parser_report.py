#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2013-04-16 11:12
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
from Analysis.settings import REPORT_KEYS

def parser_report(_line):
    """用于解析 report 数据"""

    report_dict = {}
    data = _line.split(',')
    if len(REPORT_KEYS) != len(data):
        pass
    for i in range(len(data)):
        key_type = REPORT_KEYS[i]
        report_dict[key_type[0]] = key_type[1](data[i])
    
    return report_dict
    
def add_shop(report_dict, shop):
    """增加店铺 report 数据"""

    report_dict['shop_cost'] = shop['cost']
    report_dict['shop_multi_cost'] = shop['multi_cost']
    report_dict['shop_pay'] = shop['pay']
    report_dict['shop_multi_pay'] = shop['multi_pay']

    report_dict['multi_cost_percent'] = report_dict['multi_cost'] / (shop['multi_cost'] + 0.000001)
    report_dict['multi_pay_percent'] = report_dict['multi_pay'] / (shop['multi_pay'] + 0.000001)
