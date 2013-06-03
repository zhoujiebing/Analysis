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
from CommonTools.report_tools import Report, MAIN_KEYS 

def analysis_campaign_problem(file_name, campaign_name):
    """分析 某个计划的问题"""

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

    count_keys = ['multi_roi_lower_2', 'avg_cost_lower_10']
    problem_keys = {}
    for key in count_keys:
        problem_keys[key] = 0

    for campaign in campaign_list:
        if campaign['multi_roi'] >= 2:
            continue
        problem_keys['multi_roi_lower_2'] += 1
        if campaign['multi_cost'] / (campaign['count_days']+0.01) < 1000:
            problem_keys['avg_cost_lower_10'] += 1
            #TODO 统计类目 出价
        else:
            #同上
            pass

    content = campaign_name + '问题的分析\n'
   
    return content

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'input arg: file_name, campaign_name'
        exit(0)
    print analysis_campaign_problem(sys.argv[1], sys.argv[2])

