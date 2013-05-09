#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2012-12-10 17:13
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
import os
import sys
import datetime
if __name__ == '__main__':
    sys.path.append('../../')

from DataAnalysis.conf.settings import logger, CURRENT_DIR
from DBModel.shop_db import Shop 
from DBModel.campaign_db import Campaign
from CommonTools.send_tools import send_sms
from CommonTools.report_tools import Report
from CommonTools.string_tools import parser_string_to_date
from report_db.services.rpt_sum_search_service import RptSumSearchService
from tao_models.common.exceptions import InvalidAccessTokenException

class CollectReport:
    
    def __init__(self, date):
        self.today = datetime.date.today()
        self.end_time = self.today - datetime.timedelta(days=1)
        header = u'账户,计划,当天ROI,当天花费,成交额,当天点击,平均点击花费,成交笔数,收藏,当天转化率,多天ROI,多天花费,多天成交额,多天收藏,天数,店铺id\n'
        self.header = header.encode('utf-8')
        self.syb_user = self._load_syb_user()
        
        self.end_date = date - datetime.timedelta(days=1)
        self.soft_code = None
        self.shop_list = self.get_shop_list()
        self.report_list = []

    def get_shop_list(self):
        """此方法必须被继承
        shop 信息 应包含 sid nick access_token subway_token 特殊计划id 等"""

        return []

    def _load_syb_user(self):
        syb_user = {}
        file_data = file('/home/zhoujiebing/SYB/Webpage/longtail/report/data/syb_user.csv').read().split('\n')
        for line in file_data:
            order = line.split(',')
            if len(order) < 2:
                continue
            nick = order[0]
            order_start = parser_string_to_date(order[1])
            days_delta = (self.today - order_start).days
            if days_delta > 1:
                syb_user[nick] = min(days_delta, 15)
            #提前续订的
            elif days_delta < 0:
                syb_user[nick] = 15
        return syb_user

    def collect_report(self):
        """搜集报表数据"""

        start_date = self.end_date - datetime.timedelta(days=1)
        end_date = self.end_date
        logger.info('start collect report')
        for shop in self.shop_list:
            logger.info('正在抓取帐号 %s 的报表信息' % shop['nick'])
            try:
                shop_report = RptSumSearchService.cust_rpt_sum_search(shop['nick'], shop['sid'], start_date, end_date,\
                        {'base':True, 'effect':True}, True, shop)
                multi_shop_report = RptSumSearchService.cust_rpt_sum_search(shop['nick'], shop['sid'], \
                        end_date - datetime.timedelta(days=shop['days']), end_date,\
                        {'base':True, 'effect':True}, True, shop)

                campaign_list = Campaign.get_shop_campaigns(self.soft_code, shop['access_token'], shop['nick'], shop['sid'])
                campaigns_id = [campaign['campaign_id'] for campaign in campaign_list]
                campaigns_report = RptSumSearchService.camp_rpt_sum_search(campaigns_id, shop['nick'], \
                        shop['sid'], start_date, end_date, {'base':True, 'effect':True}, True, shop)
                multi_campaigns_report = RptSumSearchService.camp_rpt_sum_search(campaigns_id, shop['nick'], \
                        shop['sid'], end_date - datetime.timedelta(days=shop['days']), end_date, \
                        {'base':True, 'effect':True}, True, shop)
            except InvalidAccessTokenException,e:
                logger.error('%s : InvalidAccessTokenException' % (shop['nick']))
                continue
            self.report_list.append(Report.merge_report(shop_report[0], multi_shop_report[0], shop))
            for i in range(len(campaigns_id)):
                self.report_list.append(Report.merge_report(campaigns_report[i], multi_campaigns_report[i], shop, campaign_list[i]))
        logger.info('finish collect report')

class CollectSYBReport(CollectReport):

    def __init__(self, date):
        CollectReport.__init__(self, date)
        self.soft_code = 2

    def get_shop_list(self):
        """获取省油宝 shop_list"""

        time_now = datetime.datetime.now()
        shop_list = []
        shop_status_list = Shop.get_all_normal_shop_status_in_syb()
        shop_info_list = Shop.get_all_shop_info(2)
        shop_info_dict = {}
        for shop in shop_info_list:
            shop_info_dict[shop['_id']] = {'access_token':shop['access_token'], 'sid':shop['_id'], \
                    'subway_token':shop['subway_token'], 'nick':shop['nick']}
        for shop in shop_status_list:
            shop_info = shop_info_dict.get(shop['_id'], None)
            if not shop_info:
                continue
            shop_info['days'] = 30
            if shop.has_key('auto_campaign_id'):
                shop_info[shop['auto_campaign_id']] = '省油宝长尾计划'
            if shop.get('auto_campaign_init_time', None):
                shop_info['auto_campaign_days'] = (time_now - shop['auto_campaign_init_time']).days
            if shop.has_key('key_campaign_id'):
                shop_info[shop['key_campaign_id']] = '省油宝加力计划'
            if shop.get('key_campaign_init_time', None):
                shop_info['key_campaign_days'] = (time_now - shop['key_campaign_init_time']).days
            use_days = min(shop_info.get('auto_campaign_days', 0), shop_info.get('key_campaign_days', 0))
            shop_info['days'] = min(shop_info['days'], use_days)
            shop_list.append(shop_info)
        
        return shop_list

    def write_report(self):
        """将报表写到文件里"""
        
        file_obj = file(CURRENT_DIR+'data/report_data/report'+str(self.today)+'.csv', 'w')    
        for report in self.report_list:
            file_obj.write(Report.to_string(report))
        file_obj.close()

def collect_report_script():
    today = datetime.date.today()
    syb_obj = CollectSYBReport(today)
    syb_obj.collect_report()
    syb_obj.write_report()
    try:
        pass
    except Exception,e:
        logger.exception('collect_report_script error: %s', str(e))
        send_sms('13738141586', 'collect_report_script error: %s' % (str(e)))
    else:
        logger.info('collect_report_script ok')

if __name__ == '__main__':
    collect_report_script()
