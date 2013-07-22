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

def filter_fun(campaign):
    global campaign_name
    if campaign['campaign'] != campaign_name:
        return False
    
    if campaign['click'] > 0 and campaign['click'] <= 20:
        return True

    return False

def analysis_campaign_problem(file_name):
    """分析 某个计划的问题"""
    
    campaign_list = Report.parse_report_file(file_name, filter_fun)
    print 'nick,multi_cpc,mult_roi,avg_cost'
    for campaign in campaign_list:
        print '%s, %.1f, %.3f, %.1f' % (campaign['nick'], \
                campaign['multi_cpc']/100, campaign['multi_roi'], \
                campaign['cost'] / 100.0)
        
        
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'input arg: file_name, campaign_name'
        exit(0)
    global campaign_name
    campaign_name = sys.argv[2]
    analysis_campaign_problem(sys.argv[1])

