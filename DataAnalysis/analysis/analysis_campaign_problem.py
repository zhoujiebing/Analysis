#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2013-06-03 11:12
@version: 1.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
if __name__ == '__main__':
    import sys
    sys.path.append('../../')
import datetime
import DataAnalysis.conf.settings
from CommonTools.report_tools import Report, MAIN_KEYS 
from diagnose.services.get_hy_rank import get_shop_hy_list 
from DataAnalysis.db_model.shop_db import Shop
Date = datetime.datetime(2013,3,28,0,0)

def analysis_campaign_problem(file_name, campaign_name):
    """分析 某个计划的问题"""
    
    shop_status_list = Shop.get_all_normal_shop_status(2)
    shop_dict = {}
    for shop in shop_status_list:
        shop_dict[shop['nick']] = shop

    campaign_list = []
    for line in file(file_name):
        campaign = Report.parser_report(line)
        if not campaign:
            continue
        if campaign['campaign'] == '账户整体情况':
            shop = campaign
            continue
        if campaign['campaign'] == campaign_name:
            if campaign['nick'] != shop['nick']:
                print '出现不一致:',shop['nick']
            Report.add_shop(campaign, shop)
            #排除非正常 数据
            if campaign['count_days'] <= 0:
                continue
            if campaign['multi_cost'] > campaign['shop_multi_cost'] or \
                    campaign['multi_pay'] > campaign['shop_multi_pay']:
                continue
            campaign_list.append(campaign)

    print 'nick,multi_cpc,mult_roi,avg_cost,cpc_max'
    for campaign in campaign_list:
        if campaign['pv'] > 0 and campaign['cost'] < 1000:
                
            #cid_list = get_shop_hy_list(str(campaign['nick']), Date)
            #if len(cid_list) <= 0:
            #    continue
            #cid_str = '|'.join([str(cid) for cid in cid_list])
            shop = shop_dict.get(campaign['nick'], None)
            if not shop or not shop.has_key('key_campaign_settings'):
                continue
            print '%s, %.1f, %.3f, %.1f, %.1f' % (campaign['nick'], \
                    campaign['multi_cpc']/100, campaign['multi_roi'], \
                    campaign['cost'] / 100.0, shop['key_campaign_settings']['cpc_max'] / 100.0)
        
        
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'input arg: file_name, campaign_name'
        exit(0)
    analysis_campaign_problem(sys.argv[1], sys.argv[2])

