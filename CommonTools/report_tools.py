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
REPORT_KEYS = [
        ['nick', str], 
        ['campaign', str],
        ['roi', float], 
        ['cost', float],
        ['pay', float], 
        ['click', int],
        ['cpc', float],
        ['pay_count', float],
        ['fav_count', int],
        ['conversion', float],
        ['multi_roi', float],
        ['multi_cost', float],
        ['multi_pay', float],
        ['multi_fav', int],
        ['count_days', int],
        ['sid', str]]

class Report:
    
    @classmethod
    def parser_report(self, _line):
        """用于解析 report 数据"""

        report_dict = {}
        data = _line.split(',')
        if len(REPORT_KEYS) != len(data):
            print _line
            return None
        for i in range(len(data)):
            key_type = REPORT_KEYS[i]
            report_dict[key_type[0]] = key_type[1](data[i])
        return report_dict
        
    @classmethod
    def add_shop(self, report_dict, shop):
        """增加店铺 report 数据"""

        report_dict['shop_cost'] = shop['cost']
        report_dict['shop_multi_cost'] = shop['multi_cost']
        report_dict['shop_pay'] = shop['pay']
        report_dict['shop_multi_pay'] = shop['multi_pay']

        report_dict['multi_cost_percent'] = report_dict['multi_cost'] / (shop['multi_cost'] + 0.000001)
        report_dict['multi_pay_percent'] = report_dict['multi_pay'] / (shop['multi_pay'] + 0.000001)
    
    @classmethod
    def to_string(self, report):
        """与parser_report搭配使用效果更佳"""

        report['roi'] = report['pay'] / (report['cost'] + 0.01)
        report['multi_roi'] = report['multi_pay'] / (report['multi_cost'] + 0.01)
        report['conversion'] = report['pay_count'] / (report['click'] + 0.01)
        report_str = []
        for key_type in REPORT_KEYS:
            key = key_type[0]
            report_str.append(str(report[key]))
        return ','.join(report_str) + '\n'

        #月光下的湖,省油宝长尾计划,0.0,5725,0,44,130.0,0,0,0.0,0.4,44188,16000,9,21,33426264
        #report_str = '%(nick)s,%(name)s,%(roi).1f,%(cost)d,%(pay)d,%(click)d,%(cpc).1f,%(pay_count)d,%(fav_count)d,%(conversion).1f,%(multi_roi).1f,%(multi_cost)d,%(multi_pay)d,%(multi_fav_count)d,%(multi_days)d,%(sid)d\n' % (report)
        #return report_str

    @classmethod
    def merge_report(self, one_day_report, multi_day_report, shop, campaign=None):
        """聚合单天和多天报表"""
        
        if one_day_report['base'].has_key('failed_msg') or multi_day_report['base'].has_key('failed_msg'):
            return None
        if one_day_report['effect'].has_key('failed_msg') or multi_day_report['effect'].has_key('failed_msg'):
            return None
        report = {}
        report['nick'] = shop['nick']
        report['sid'] = shop['sid']
        report['click'] = one_day_report['base']['click']
        report['pv'] = one_day_report['base']['impressions']
        report['cpc'] = one_day_report['base']['cpc']
        report['cost'] = one_day_report['base']['cost']
        report['multi_click'] = multi_day_report['base']['click'] 
        report['multi_pv'] = multi_day_report['base']['impressions']
        report['multi_cpc'] = multi_day_report['base']['cpc']
        report['multi_cost'] = multi_day_report['base']['cost']

        report['fav_count'] = one_day_report['effect']['favshopcount'] + one_day_report['effect']['favitemcount']
        
        report['pay_count'] = one_day_report['effect']['indirectpaycount'] + one_day_report['effect']['directpaycount']
        
        report['pay'] = one_day_report['effect']['indirectpay'] + one_day_report['effect']['directpay']
        
        report['multi_fav'] = multi_day_report['effect']['favshopcount'] + multi_day_report['effect']['favitemcount']
        
        #report['multi_pay_count'] = multi_day_report['effect']['indirectpaycount'] + multi_day_report['effect']['directpaycount']
        
        report['multi_pay'] = multi_day_report['effect']['indirectpay'] + multi_day_report['effect']['directpay']
        
        report['count_days'] = shop['days']
        report['campaign'] = '账户整体情况'
        if campaign:
            report['campaign'] = shop.get(campaign['campaign_id'], campaign['title'])
            report['campaign'] = report['campaign'].replace(',', '逗号')
        return report 

