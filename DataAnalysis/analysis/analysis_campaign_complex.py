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
from CommonTools.report_tools import Report, MAIN_KEYS 

def analysis_campaign_complex(file_name, campaign_name):
    """详细分析 某个计划"""

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

    zero_cost = 0
    multi_roi_zero = 0
    multi_roi_unzero = 0
    multi_roi_bigger_2 = 0
    
    sum_key_dict = {}
    main_keys = []
    daily_keys = ['multi_pv', 'multi_click', 'multi_cost', 'multi_pay', 'multi_pay_count']
    for key in MAIN_KEYS:
        main_keys.append(key)
        main_keys.append('shop_'+key)

    main_keys.extend(['multi_cost_percent', 'multi_pay_percent'])
    for key in main_keys:
        sum_key_dict[key] = 0
    for key in daily_keys:
        sum_key_dict['daily_'+key] = 0

    multi_cost_percent_bigger_9 = 0
    multi_cost_percent_bigger_5 = 0
    
    for campaign in campaign_list:
        if campaign['multi_cost'] <= 0:
            zero_cost += 1
            continue
                       
        for key in main_keys:
            sum_key_dict[key] += campaign[key]
        for key in daily_keys:
            sum_key_dict['daily_'+key] += campaign[key] / campaign['count_days']
        
        if campaign['multi_cost_percent'] >= 0.9:
            multi_cost_percent_bigger_9 += 1
        if campaign['multi_cost_percent'] >= 0.5:
            multi_cost_percent_bigger_5 += 1

        if campaign['multi_roi'] <= 0:
            multi_roi_zero += 1
        else:
            multi_roi_unzero += 1
            if campaign['multi_roi'] >= 2:
                multi_roi_bigger_2 += 1

    unzero_cost = len(campaign_list) - zero_cost
    
    content = campaign_name + '的分析\n'
    content += '用户数：%d, 花费为0数：%d，花费不为0数：%d, 如下统计针对多天花费不为0的用户\n' % (len(campaign_list), zero_cost, unzero_cost)
    content += '单天报表分析:\n'
    content += '昨日 平均花费：%.1f, 平均成交额：%.1f, 平均ROI：%.1f, 平均CPC：%.1f\n' % (\
            sum_key_dict['cost'] / unzero_cost / 100, sum_key_dict['pay'] / unzero_cost / 100, \
            sum_key_dict['pay'] / sum_key_dict['cost'], sum_key_dict['cost'] / sum_key_dict['click'] / 100)

    content += '昨日 平均展现：%d, 平均点击：%d, 平均点击率：%.3f, 平均转化率：%.3f\n' % (\
            sum_key_dict['pv'] / unzero_cost, sum_key_dict['click'] / unzero_cost, \
            sum_key_dict['click'] / (sum_key_dict['pv']+0.01), \
            sum_key_dict['pay_count'] / (sum_key_dict['click']+0.01))
    
    content += '多天报表分析:\n'
    content += '日均花费：%.1f, 日均成交额：%.1f, 日均ROI：%.1f, 日均CPC：%.1f\n' % (\
            sum_key_dict['daily_multi_cost'] / unzero_cost / 100, \
            sum_key_dict['daily_multi_pay'] / unzero_cost / 100, \
            sum_key_dict['daily_multi_pay'] / sum_key_dict['daily_multi_cost'],\
            sum_key_dict['daily_multi_cost'] / sum_key_dict['daily_multi_click'] / 100)

    content += '日均展现：%d, 日均点击：%d, 日均点击率：%.3f, 日均转化率：%.3f\n' % (\
            sum_key_dict['daily_multi_pv'] / unzero_cost, \
            sum_key_dict['daily_multi_click'] / unzero_cost, \
            sum_key_dict['daily_multi_click'] / (sum_key_dict['daily_multi_pv']+0.01),\
            sum_key_dict['daily_multi_pay_count'] / (sum_key_dict['daily_multi_click']+0.01))
    
    content += '多天ROI大于0数：%d,占比：%.1f，多天ROI大于2数：%d，占比：%.1f\n' %(multi_roi_unzero,\
            float(multi_roi_unzero) / unzero_cost, multi_roi_bigger_2, float(multi_roi_bigger_2) / unzero_cost)
    content += '其中该计划多天花费占全店花费比 不小于0.9的 比例：%.2f, 不小于0.5的 比例：%.2f\n' % (\
            float(multi_cost_percent_bigger_9)/unzero_cost , float(multi_cost_percent_bigger_5)/unzero_cost)
    content += '所有计划多天花费占所有全店多天 花费的比例：%.2f,所有计划多天成交占所有全店多天成交的比例：%.2f\n\n' %(sum_key_dict['multi_cost'] / sum_key_dict['shop_multi_cost'], sum_key_dict['multi_pay'] / sum_key_dict['shop_multi_pay'])
   
    return content

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'input arg: file_name, campaign_name'
        exit(0)
    print analysis_campaign_complex(sys.argv[1], sys.argv[2])

