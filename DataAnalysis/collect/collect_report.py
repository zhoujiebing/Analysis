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
from DataAnalysis.db_model.shop_db import Shop 
from CommonTools.send_tools import send_sms, DIRECTOR
from CommonTools.report_tools import Report
from CommonTools.string_tools import parser_string_to_date
from report_db.services.rpt_sum_search_service import RptSumSearchService
from tao_models.conf.settings import set_taobao_client
from tao_models.simba_campaigns_get import SimbaCampaignsGet
from tao_models.common.exceptions import InvalidAccessTokenException

class CollectReport:
    
    def __init__(self, date):
        self.today = date
        header = u'账户,计划,当天ROI,当天花费,成交额,当天点击,平均点击花费,成交笔数,收藏,当天转化率,多天ROI,多天花费,多天成交额,多天收藏,天数,店铺id\n'
        self.header = header.encode('utf-8')
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

        start_date = self.today - datetime.timedelta(days=1)
        end_date = start_date
        logger.info('start collect report')
        for shop in self.shop_list:
            logger.info('正在抓取帐号 %s 的报表信息' % shop['nick'])
            try:
                shop_report = RptSumSearchService.cust_rpt_sum_search(shop['nick'], shop['sid'], start_date, end_date,\
                        {'base':True, 'effect':True}, True, shop)
                multi_shop_report = RptSumSearchService.cust_rpt_sum_search(shop['nick'], shop['sid'], \
                        end_date - datetime.timedelta(days=shop['days']), end_date,\
                        {'base':True, 'effect':True}, True, shop)
                
                #目前使用API获取,以后可以改用使用db
                campaigns = SimbaCampaignsGet.get_campaign_list(shop['access_token'], shop['nick'])
                campaigns_id = []
                campaigns_dict = {}
                for campaign in campaigns:
                    campaign = campaign.toDict()
                    campaigns_id.append(campaign['campaign_id'])
                    campaigns_dict[campaign['campaign_id']] = campaign
                
                campaigns_report = RptSumSearchService.camp_rpt_sum_search(campaigns_id, shop['nick'], \
                        shop['sid'], start_date, end_date, {'base':True, 'effect':True}, True, shop)
                multi_campaigns_report = RptSumSearchService.camp_rpt_sum_search(campaigns_id, shop['nick'], \
                        shop['sid'], end_date - datetime.timedelta(days=shop['days']), end_date, \
                        {'base':True, 'effect':True}, True, shop)
            except InvalidAccessTokenException,e:
                logger.error('%s : InvalidAccessTokenException' % (shop['nick']))
                continue
            except Exception,e:
                continue
            self.report_list.append(Report.merge_report(shop_report[0], multi_shop_report[0], shop))
            for i in range(len(campaigns_id)):
                if campaigns_report[i]['campaignid'] != multi_campaigns_report[i]['campaignid']:
                    logger.info('%s 出现单体计划报表与多天计划报表不一致' % shop['nick'])
                self.report_list.append(Report.merge_report(campaigns_report[i], multi_campaigns_report[i], shop, campaigns_dict[campaigns_report[i]['campaignid']]))
        
        logger.info('finish collect report')
            

class CollectSYBReport(CollectReport):

    def __init__(self, date):
        self.soft_code = 2
        CollectReport.__init__(self, date)
        set_taobao_client('12685542', '6599a8ba3455d0b2a043ecab96dfa6f9')

    def get_shop_list(self):
        """获取省油宝 shop_list"""

        time_now = datetime.datetime.now()
        shop_list = []
        shop_status_list = Shop.get_all_normal_shop_status(self.soft_code)
        shop_info_list = Shop.get_all_shop_info(self.soft_code)
        shop_info_dict = {}
        for shop in shop_info_list:
            if shop.has_key('access_token'):
                shop_info_dict[shop['_id']] = {'access_token':shop['access_token'], 'sid':shop['_id'], \
                    'subway_token':shop['subway_token'], 'nick':shop['nick']}
        for shop in shop_status_list:
            shop_info = shop_info_dict.get(shop['_id'], None)
            if not shop_info:
                continue
            shop_info['days'] = 30
            use_days = []
            campaign_ids = shop.get('auto_campaign_ids', [])
            for campaign_id in campaign_ids:
                campaign_setting = shop[str(campaign_id)]
                shop_info[campaign_id] = '省油宝长尾计划‘
                if campaign_setting.get('auto_campaign_init_time', False):
                    use_days.append((time_now-campaign_setting['auto_campaign_init_time']).days)
                if campaign_setting.get('auto_campaign_cancel_status', False):
                    shop_info[campaign_id] = '省油宝长尾计划_CANCEL'
                
            campaign_ids = shop.get('key_campaign_ids', [])
            for campaign_id in campaign_ids:
                campaign_setting = shop[str(campaign_id)]
                shop_info[campaign_id] = '省油宝加力计划'
                if campaign_setting.get('key_campaign_init_time', False):
                    use_days.append((time_now- campaign_setting['key_campaign_init_time']).days)
                if campaign_setting.get('key_campaign_cancel_status', False):
                    shop_info[campaign_id] = '省油宝加力计划_CANCEL'

            use_days = max(use_days)
            if use_days <= 0:
                continue
            shop_info['days'] = min(shop_info['days'], use_days)
            shop_list.append(shop_info)
        
        return shop_list

    def write_report(self):
        """将报表写到文件里"""
        
        file_obj = file(CURRENT_DIR+'data/report_data/syb_report'+str(self.today)+'.csv', 'w')    
        for report in self.report_list:
            if report:
                file_obj.write(Report.to_string(report))
        file_obj.close()

class CollectBDReport(CollectReport):

    def __init__(self, date):
        self.soft_code = 1
        CollectReport.__init__(self, date)
        set_taobao_client('21065688', '74aecdce10af604343e942a324641891')

    def get_shop_list(self):
        """获取北斗 shop_list"""

        time_now = datetime.datetime.now()
        shop_list = []
        shop_status_list = Shop.get_all_normal_shop_status(self.soft_code)
        shop_info_list = Shop.get_all_shop_info(self.soft_code)
        shop_info_dict = {}
        for shop in shop_info_list:
            if not shop.has_key('subway_token'):
                continue
            shop_info_dict[shop['_id']] = {'access_token':shop['access_token'], 'sid':shop['_id'], \
                    'subway_token':shop['subway_token']}
        
        for shop in shop_status_list:
            shop_info = shop_info_dict.get(shop['_id'], None)
            if not shop_info:
                continue
            #北斗没有 auto_campaign_init_time 统一取 30天
            shop_info['days'] = 30
            if shop.has_key('auto_campaign_id'):
                shop_info[shop['auto_campaign_id']] = '北斗专属计划'
            
            shop_info['nick'] = shop['nick']
            shop_list.append(shop_info)
        
        return shop_list

    def write_report(self):
        """将报表写到文件里"""
        
        file_obj = file(CURRENT_DIR+'data/report_data/bd_report'+str(self.today)+'.csv', 'w')    
        for report in self.report_list:
            if report:
                file_obj.write(Report.to_string(report))
        file_obj.close()


def collect_report_script():
    today = datetime.date.today()
    try:
        syb_obj = CollectSYBReport(today)
        syb_obj.collect_report()
        syb_obj.write_report()
        bd_obj = CollectBDReport(today)
        bd_obj.collect_report()
        bd_obj.write_report()
    
    except Exception,e:
        logger.exception('collect_report_script error: %s', str(e))
        send_sms(DIRECTOR['PHONE'], 'collect_report_script error: %s' % (str(e)))
    else:
        logger.info('collect_report_script ok')

if __name__ == '__main__':
    collect_report_script()
