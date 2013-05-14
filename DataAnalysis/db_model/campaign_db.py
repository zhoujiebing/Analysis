#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Wu Liang
@contact: garcia.wul@alibaba-inc.com
@date: 2012-12-10 19:54
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
from xuancw.services.campaign_service import AutoProCampaignService as CampaignServiceXCW
from shengyb.service.campaign_service import CampaignService as CampaignServiceSYB 

import datetime
from tao_models.simba_campaign_budget_get import SimbaCampaignBudgetGet
from tao_models.simba_rpt_campaignbase_get import SimbaRptCampaignbaseGet
from tao_models.simba_rpt_campaigneffect_get import SimbaRptCampaigneffectGet

class Campaign:

    @classmethod
    def get_campaign_budget(cls, soft_code, access_token, nick, campaign_id):
        """
        实时获得计划预算信息
        """
        campaign_budget = SimbaCampaignBudgetGet.campaign_budget_get(access_token, nick, int(campaign_id))
        return campaign_budget.budget

    @classmethod
    def get_campaign_rpt(cls, soft_code, nick, sid, campaign_id, days, search_info):
        """
        获得计划报表
        """
        if datetime.datetime.now().hour >= 8:
            start_date = datetime.datetime.combine(datetime.date.today(), datetime.time()) - datetime.timedelta(days=days)
            end_date = datetime.datetime.combine(datetime.date.today(), datetime.time()) - datetime.timedelta(days=1)
        else:
            start_date = datetime.datetime.combine(datetime.date.today(), datetime.time()) - datetime.timedelta(days=days+1)
            end_date = datetime.datetime.combine(datetime.date.today(), datetime.time()) - datetime.timedelta(days=2)
        campaigns_report = CampaignRptSearchService.camp_rpt_search([campaign_id], nick, 
                int(sid), start_date, end_date, {'base':True, 'effect':True}, True, search_info)
        campaign_report_dict = {}
        campaign_report_dict['cost'] = 0
        if campaigns_report[0]['base'] and not campaigns_report[0]['base'].has_key('failed_msg'):
            campaign_report_dict['cost'] = campaigns_report[0]['base']['cost']
        campaign_report_dict['pay'] = 0 
        if campaigns_report[0]['effect'] and not campaigns_report[0]['effect'].has_key('failed_msg'):
            campaign_report_dict['pay'] = campaigns_report[0]['effect']['indirectpay'] + \
                                         campaigns_report[0]['effect']['directpay']
        campaign_report_dict['fav'] = 0 
        if campaigns_report[0]['effect'] and not campaigns_report[0]['effect'].has_key('failed_msg'):
            campaign_report_dict['fav'] = campaigns_report[0]['effect']['favshopcount'] + \
                                         campaigns_report[0]['effect']['favitemcount']
        return campaign_report_dict

    @classmethod
    def get_shop_campaigns(self, soft_code, access_token, nick, sid):
        """获取店铺里的所有计划 访问db"""

        if soft_code == 1:
            campaign_service_obj = CampaignServiceXCW(access_token, nick, sid)
        elif soft_code == 2:
            campaign_service_obj = CampaignServiceSYB(access_token, nick, sid)
        #TODO db重构后 这里 也修改
        return campaign_service_obj.get_campaigns_simba()
    
