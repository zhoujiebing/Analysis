#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:xieguanfu 
@contact: xieguanfu@maimiaotech.com
@date: 2012-12-16 18:24
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
from report_db.services.campaign_rpt_search_service import CampaignRptSearchService
from tao_models.conf.settings import set_taobao_client
from tao_models.simba_campaigns_get import SimbaCampaignsGet
from tao_models.common.exceptions import InvalidAccessTokenException
from user_center.services.order_db_service import OrderDBService

class CollectReport:
    
    def __init__(self, date):
        self.report_list = []
        self.date_list=[15,30]
        #self.date_list=[15,21,30,35]
        self.order_date=date

    def collect_report(self,shop_list):
        """搜集报表数据"""
	active_user_dict={}
        for i in self.date_list:
            active_user_dict[i]=0
        no_active_dict={}
        for shop in shop_list:
            try:
                nick=shop["nick"]
                sid=shop["_id"]
                access_token=shop["access_token"]
                subway_token=shop["subway_token"]
                obj_dict={}
                obj_dict["nick"]=shop["nick"]
                campaign_id_list=shop.get("campaign_id_list",None)
                if campaign_id_list is None or  len(campaign_id_list)==0:
                    obj_dict["type"]="no_auto_campaign"
                    no_active_dict[nick]=obj_dict
                    continue

                search_info = { 'nick' :nick, 'access_token' : access_token, 'subway_token' : subway_token, 'sid' : sid }
                print "%s\t%s" %(nick,campaign_id_list)
		#if shop["nick"]=="gt0068gt":
		#    import pdb
		#    pdb.set_trace()
                for date_type in self.date_list:
                    end=shop["order_cycle_start"]+datetime.timedelta(days=(date_type-1))
		    if end>=datetime.datetime.now().date():
			end=datetime.datetime.now().date()-datetime.timedelta(days=1)
                    start=end-datetime.timedelta(days=6)
                    rpt_list = CampaignRptSearchService.camp_rpt_search(campaign_id_list, shop["nick"], sid,start, end, {'base':True,'effect':True}, True, search_info)
                    rpt_dict=self.merge_rpt(rpt_list)
		    if rpt_dict is None:
			print "%s 计划报表获取失败" % shop["nick"]
			continue
                    if rpt_dict["impressions"]>0:
                        active_user_dict[date_type]+=1
            except Exception,e:
                print str(e)
		import traceback
		traceback.print_exc()
	count=len(shop_list)
	header="%s日订购用户,且服务已经开始用户数:%s" %(self.order_date,count)
	print header
	for date_type,active_count in active_user_dict.iteritems():
	    print "%s天活跃数:%s 比例:%s" %(date_type,active_count,active_count/float(count))	
        print active_user_dict

                    

    def merge_rpt(cls,rpt_list):
        rpt_dict={"impressions":0,"pay":0,"directpay":0,"indirectpay":0}
        for rpt in rpt_list:
	    if "failed_msg" in rpt["base"] or "failed_msg" in rpt["effect"]:
		return None 
	    impressions=rpt["base"]["impressions"]
	    rpt_dict["impressions"]+=impressions
	    directpay=rpt["effect"]["directpay"]
	    indirectpay=rpt["effect"]["indirectpay"]
	    rpt_dict["directpay"]+=directpay
	    rpt_dict["indirectpay"]+=indirectpay
	    rpt_dict["pay"]+=(indirectpay+indirectpay)

        return rpt_dict


class CollectSYBReport(CollectReport):

    def __init__(self, date):
        self.soft_code = 2
        set_taobao_client('12685542', '6599a8ba3455d0b2a043ecab96dfa6f9')
        self.date_list=[15,21,30,35]
        self.order_date=date
	self.article_code="ts-1796606"
        CollectReport.__init__(self, date)

    def get_shop_list(self):
        """获取省油宝 shop_list"""
        order_list=OrderDBService.get_all_orders_list()
        user_all_orders={}
        for order in order_list:
            if order["nick"] not in user_all_orders:
                user_all_orders[order["nick"]]=[]
            user_all_orders[order["nick"]].append(order)
        shop_list = []
        shop_info_list = Shop.get_all_shop_info(self.soft_code)
        shop_status_list = Shop.get_all_shop_status(self.soft_code)
	shop_status_dict={}
	for shop_status in shop_status_list:
	    shop_status_dict[shop_status["nick"]]=shop_status	

        for shop in shop_info_list:
            #if shop.get("deadline",None) is  None or  shop["deadline"].date()<self.order_date:
            #    continue
	    #if shop["nick"]=="金丝草批发仓库":
	    #    import pdb
	    #    pdb.set_trace()
            if shop["nick"] not in  user_all_orders:
                continue
            if shop["nick"] not in  shop_status_dict:
                continue
            flag=False
            is_new=False
	    #import pdb
	    #pdb.set_trace()
            for order in user_all_orders[shop["nick"]]:
		if order["article_code"] !=self.article_code:
		    continue
                if order["create"].date() != self.order_date:
                    continue
                if order["order_cycle_start"].date()>self.order_date+datetime.timedelta(days=15):
                    print "%s订单的服务期还没开始" % order["nick"]
                    continue
                flag=True
                if not is_new and order["biz_type"]==1:
                    is_new=True
            if not flag:
                continue
	    shop_status=shop_status_dict[shop["nick"]]
	    campaign_ids=self.get_campaign_ids(shop_status)	
	    
            shop["order_cycle_start"]=self.order_date
            shop["is_new"]=is_new
	    shop["campaign_id_list"]=campaign_ids
            shop_list.append(shop)
        self.shop_list=shop_list
	print "shop list==%s" % len(shop_list)
        return shop_list

    def get_campaign_ids(self,shop_status):
	campaign_ids=[]
	if "auto_campaign_ids" in  shop_status or "key_campaign_ids" in shop_status:
	    campaign_ids.extend(shop_status.get("auto_campaign_ids",[]))
	    campaign_ids.extend(shop_status.get("key_campaign_ids",[]))
	elif "auto_campaign_id" in shop_status:
	    if shop_status["auto_campaign_id"] is not None:
		campaign_ids.append(shop_status["auto_campaign_id"])
	return campaign_ids
	    
		

if __name__ == '__main__':
    d=datetime.date(2013,04,21)
    syb=CollectSYBReport(d)
    shop_list=syb.get_shop_list()
    #print len(shop_list)
    syb.collect_report(shop_list)
