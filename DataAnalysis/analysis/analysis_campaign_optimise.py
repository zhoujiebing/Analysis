#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2013-07-04 10:01
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""

if __name__ == '__main__':
    import sys
    sys.path.append('../../')
import datetime
from DataAnalysis.db_model.shop_db import Shop 
from CommonTools.send_tools import send_email_with_text, send_sms, DIRECTOR
from CommonTools.logger import logger

def analysis_campaign_optimise():
    try:
        analysis_campaign_status()
    except Exception,e:
        logger.exception('analysis_campaign_optimise error: %s' % (str(e)))
        send_sms(DIRECTOR['PHONE'], 'analysis_campaign_optimise error: %s' % (str(e)))
    else:
        logger.info('analysis_campaign_optimise ok')
        
def analysis_campaign_status():
    """分析省油宝用户的 各种状态"""
    
    key_campaign_optimize = {}
    auto_campaign_optimize = {}

    shop_status_list = Shop.get_all_normal_shop_status(2)
    for shop_status in shop_status_list:
        #加力计划
        campaign_ids = shop_status.get('key_campaign_ids', [])
        for campaign_id in campaign_ids:
            campaign_setting = shop_status[str(campaign_id)]
            optimize_time = campaign_setting.get('key_campaign_optimize_time', None)
            if not campaign_setting.get('key_campaign_cancel_status', False) and optimize_time:
                optimize_date = optimize_time.date()
                if not key_campaign_optimize.has_key(optimize_date):
                    key_campaign_optimize[optimize_date] = 0
                key_campaign_optimize[optimize_date] += 1
        
        #长尾计划
        campaign_ids = shop_status.get('auto_campaign_ids', [])
        for campaign_id in campaign_ids:
            campaign_setting = shop_status[str(campaign_id)]
            optimize_time = campaign_setting.get('auto_campaign_optimize_time', None)
            if not campaign_setting.get('auto_campaign_cancel_status', False) and optimize_time:
                optimize_date = optimize_time.date()
                if not auto_campaign_optimize.has_key(optimize_date):
                    auto_campaign_optimize[optimize_date] = 0
                auto_campaign_optimize[optimize_date] += 1
     
    date_list = []
    edate = datetime.date.today()
    sdate = edate - datetime.timedelta(days=7)
    while sdate <= edate:
        date_list.append(sdate)
        sdate += datetime.timedelta(days=1)
    
    for date in date_list:
        if not key_campaign_optimize.has_key(date):
            key_campaign_optimize[date] = 0
        if not auto_campaign_optimize.has_key(date):
            auto_campaign_optimize[date] = 0
    
    content = ''
    sum_campaign = sum(key_campaign_optimize.values())
    content += '省油宝加力计划总数:%d\n' % (sum_campaign)
    for date in date_list:
        content += '%s: %d, %.2f\n' % (str(date), \
             key_campaign_optimize[date], key_campaign_optimize[date] / float(sum_campaign))

    sum_campaign = sum(auto_campaign_optimize.values())
    content += '\n省油宝长尾计划总数:%d\n' % (sum_campaign)
    for date in date_list:
        content += '%s: %d, %.2f\n' % (str(date), \
             auto_campaign_optimize[date], auto_campaign_optimize[date] / float(sum_campaign))

    send_email_with_text(DIRECTOR['EMAIL'], content, '省油宝优化频率分析')
    send_email_with_text('chenke@maimiaotech.com', content, '省油宝优化频率分析')
    send_email_with_text('luoyan@maimiaotech.com', content, '省油宝优化频率分析')

if __name__ == '__main__':
    analysis_campaign_status()
