#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2013-05-23 11:12
@version: 1.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
if __name__ == '__main__':
    import sys
    sys.path.append('../../')

import datetime
import random
from DataAnalysis.conf.settings import CURRENT_DIR
from CommonTools.report_tools import Report, MAIN_KEYS 

def collect_all_shop(file_name, campaign_name):
    """收集所有店铺"""

    campaign_list = []
    for line in file(file_name):
        campaign = Report.parser_report(line)
        if not campaign:
            continue
        if campaign['campaign'] == '账户整体情况':
            shop = campaign
            continue
        if campaign['campaign'].find(campaign_name) != -1:
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

    return campaign_list

def sample_script():
    """随机抽样脚本"""

    report_date = datetime.date.today() - datetime.timedelta(days=1)
    campaign_name = '省油宝加力计划'
    file_name = CURRENT_DIR+'data/report_data/syb_report'+str(report_date)+'.csv'
    campaign_list = collect_all_shop(file_name, campaign_name)
    campaign_list.sort(key=lambda campaign:campaign['multi_pay_count'] / (campaign['count_days']+0.01), \
            reverse=True)
    select = campaign_list[0]
    for key in select.keys():
        print key+' : '+str(select[key])

if __name__ == '__main__':
    sample_script()

