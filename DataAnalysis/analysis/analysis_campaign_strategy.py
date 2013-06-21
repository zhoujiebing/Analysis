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
import numpy
import datetime
import DataAnalysis.conf.settings
from CommonTools.report_tools import Report, BASE_KEYS 

def filter_campaign_before(campaign):
    """过滤函数,过滤出要使用新策略的计划"""
    
    if campaign['campaign'] != '省油宝加力计划':
        return False
    if campaign['click'] <= 20 and campaign['pv'] > 0:
        return True

    return False

def analysis_campaign_problem(file_name_before, file_name_after):
    """对比分析 计划在策略前后 的 效果"""
    
    campaign_list = parse_report_file(file_name_before, filter_campaign_before)
    campaign_dict = {}
    for campaign in campaign_list:
        campaign_dict[campaign['nick']] = campaign
    
    for campaign in parse_report_file(filter_campaign_after):
        if campaign['campaign'] != '省油宝加力计划':
            continue
        account = campaign_dict.get(campaign['nick'], None)
        if account:
            Report.add_compare(account, campaign)
    compare_list = []
    for nick in campaign_dict:
        compare_delta = campaign_dict[nick].get('compare_delta', False)
        if compare_delta
            compare_list.append(compare_delta)
    compare_list = numpy.array(compare_list)
    print 'campaign_list: ',len(compare_list)
    for i in range(len(BASE_KEYS)):
        key = BASE_KEYS[i]
        key_average = numpy.average(compare_list, axis=i)
        print 'avg_%s_diff: %.2f' % (key, key_average)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'input arg: file_name_before, file_name_after'
        exit(0)
    analysis_campaign_problem(sys.argv[1], sys.argv[2])

