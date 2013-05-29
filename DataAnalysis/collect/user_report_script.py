#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2013-05-24 11:12
@version: 1.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
if __name__ == '__main__':
    import sys
    sys.path.append('../../')
import datetime
from DataAnalysis.conf.settings import logger, CURRENT_DIR
from CommonTools.send_tools import send_email_with_file
from CommonTools.report_tools import Report, MAIN_KEYS 
from user_center.services.order_db_service import OrderDBService

def write_renew_report(file_name, nick_list):
    """收集nick_list的报表"""
    
    print_keys = ['nick', 'campaign', 'multi_cost', 'multi_cpc', 'multi_roi', \
            'multi_cvr', 'multi_ctr', 'count_days']
    header_keys = ['店铺昵称', '计划名称', '多天花费', '多天cpc', '多天roi', '多天转化率',\
            '多天点击率', '统计天数']
    write_obj = file(CURRENT_DIR+'data/renew_report.csv', 'w')
    write_obj.write(','.join(header_keys)+'\n')

    for line in file(file_name):
        campaign = Report.parser_report(line)
        if not campaign:
            continue

        if campaign['nick'] in nick_list:
            report_str = []
            for key in print_keys:
                if key in ['multi_cost', 'multi_cpc']:
                    campaign[key] /= 100.0
                elif key in ['multi_cvr', 'multi_ctr', 'multi_roi']:
                    campaign[key] = '%.3f' % campaign[key]
                report_str.append(str(campaign[key]))
            write_obj.write(','.join(report_str)+'\n')
    
    write_obj.close()

def collect_renew_nicks(start_time, end_time, article_code_list=['ts-1796606', 'ts-1797607', 'ts-1817244']):
    """收集所有某时间段内过期但未续费的用户"""

    user_orders = {}
    article_nicks = {}
    for article_code in article_code_list:
        article_nicks[article_code] = []

    all_order = OrderDBService.get_all_orders_list()
    for order in all_order:
        if order['article_code'] not in article_code_list:
            continue
        key = (order['nick'], order['article_code'])
        if not user_orders.has_key(key):
            user_orders[key] = []
        user_orders[key].append(order)
        
    for key in user_orders.keys():
        orders = user_orders[key]
        orders.sort(key=lambda order:order['order_cycle_start'])
        
        for i in range(len(orders)):
            order = orders[i]
            deadline = order['order_cycle_end']
            if deadline >= start_time and deadline <= end_time:
                if i == len(orders) - 1:
                    article_nicks[order['article_code']].append(order['nick'])
                    break
            elif deadline > end_time:
                break
    
    return article_nicks

def renew_account_script(_days = 4):
    """电话续费"""
    
    article_code_list = ['ts-1796606']
    today = datetime.date.today()
    renew_date = today - datetime.timedelta(days=_days)
    report_date = today - datetime.timedelta(days=_days+1)
    renew_time = datetime.datetime.combine(renew_date, datetime.time())
    article_nicks = collect_renew_nicks(renew_time, renew_time, article_code_list)
    for article_code in article_code_list:
        nick_list = article_nicks[article_code]
        file_name = CURRENT_DIR+'data/report_data/syb_report'+str(report_date)+'.csv'
        write_renew_report(file_name, nick_list)
        send_file = CURRENT_DIR+'data/renew_report.csv' 
        text = '需电话营销的用户报表测试版'
        #send_email_with_file('zhoujiebing@maimiaotech.com', text, str(renew_date)+'电话营销的用户报表', [send_file])
        send_email_with_file('zhangfenfen@maimiaotech.com', text, str(renew_date)+'电话营销的用户报表', [send_file])

if __name__ == '__main__':
    renew_account_script()
