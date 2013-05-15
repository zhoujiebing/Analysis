#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2012-10-15 11:12
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
if __name__ == '__main__':
    import sys
    sys.path.append('../../')
from CommonTools.report_tools import Report

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
    sum_multi_roi = 0
    sum_multi_pay = 0
    sum_shop_multi_pay = 0
    sum_multi_cost = 0
    sum_shop_multi_cost = 0
    sum_multi_cost_percent = 0
    sum_multi_pay_percent = 0
    multi_cost_percent_bigger_9 = 0
    multi_cost_percent_bigger_5 = 0
    for syb in campaign_list:
        if syb['multi_cost'] <= 0:
            zero_cost += 1
            continue
        sum_multi_cost += syb['multi_cost']
        sum_shop_multi_cost += syb['shop_multi_cost']
        sum_multi_pay += syb['multi_pay']
        sum_shop_multi_pay += syb['shop_multi_pay']
        sum_multi_cost_percent += syb['multi_cost_percent']
        sum_multi_pay_percent += syb['multi_pay_percent']
        if syb['multi_cost_percent'] >= 0.9:
            multi_cost_percent_bigger_9 += 1
        if syb['multi_cost_percent'] >= 0.5:
            multi_cost_percent_bigger_5 += 1

        if syb['multi_roi'] <= 0:
            multi_roi_zero += 1
        else:
            multi_roi_unzero += 1
            sum_multi_roi += syb['multi_roi']
            if syb['multi_roi'] >= 2:
                multi_roi_bigger_2 += 1

    unzero_cost = len(campaign_list) - zero_cost
    content = campaign_name + '的单独分析\n'
    content += '用户数：%d,(计划多天) 花费为0数：%d，花费不为0数：%d\n' % (len(campaign_list), zero_cost, unzero_cost)
    content += '(计划多天) ROI大于0数：%d,占比：%.1f，ROI大于2数：%d，占比：%.1f\n' %(multi_roi_unzero,\
            float(multi_roi_unzero) / unzero_cost, multi_roi_bigger_2, float(multi_roi_bigger_2) / unzero_cost)
    content += '计划多天花费不为0的用户中\n'
    content += '(计划多天花费占全店多天花费比例)的平均值：%.2f,(计划多天成交占全店多天成交比例)的平均值：%.2f\n' %(sum_multi_cost_percent / unzero_cost, sum_multi_pay_percent / unzero_cost)
    content += '其中多天花费占比 不小于0.9的 比例：%.2f, 不小于0.5的 比例：%.2f\n' % (\
            float(multi_cost_percent_bigger_9)/unzero_cost , float(multi_cost_percent_bigger_5)/unzero_cost)
    content += '所有计划多天花费占所有全店多天花费的比例：%.2f,所有计划多天成交占所有全店多天成交的比例：%.2f\n\n' %(sum_multi_cost / sum_shop_multi_cost, sum_multi_pay / sum_shop_multi_pay)
    #content += '多天ROI大于0的用户的平均多天ROI：%.1f\n' % (sum_multi_roi / multi_roi_unzero)
    return content

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'input arg: file_name, campaign_name'
        exit(0)
    print analysis_campaign_complex(sys.argv[1], sys.argv[2])

