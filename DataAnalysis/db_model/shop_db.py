#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2013-04-16 19:45
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
import datetime
if __name__ == '__main__':
    import sys
    sys.path.append('../../')
from DataAnalysis.conf.settings import syb_db, bd_db 
from user_center.services.shop_db_service import ShopDBService

class Shop(object):

    syb_conn = syb_db['CommonInfo']
    bd_conn = bd_db['CommonInfo']
    
    @classmethod
    def upsert_cs_message(cls, nick, message_dict):
        """更新用户留言"""
            
        nick = str(nick)
        shops = cls.syb_conn['shop_status'].find({'nick':nick})
        if shops.count() != 1:
            return False
        message_dict['sid'] = shops[0]['_id']
        message_dict['message_time'] = datetime.datetime.now()
        cls.syb_conn['cs_message'].update({'nick':nick}, {'$set':message_dict}, upsert=True)
        return True

    @classmethod
    def get_all_shop_info(cls, soft_code):
        """获取所有shop_info"""
            
        if soft_code == 1:
            shops_info = cls.bd_conn['shop_info'].find()
        elif soft_code == 2:
            shops_info = cls.syb_conn['shop_info'].find()
        shops_info = [shop for shop in shops_info]
        return shops_info

    @classmethod
    def get_all_shop_status(cls, soft_code):
        """获取所有shop_status"""

        if soft_code == 1:
            shops_status = cls.bd_conn['shop_status'].find()
        elif soft_code == 2:
            shops_status = cls.syb_conn['shop_status'].find()
        shops_status = [shop for shop in shops_status]
        return shops_status

    @classmethod
    def get_all_normal_shop_status(cls, soft_code):
        """获取soft_code的所有正常shop_status"""
        
        shop_status_list = Shop.get_all_shop_status(soft_code)
        normal_shop_list = []
        for shop_status in shop_status_list:
            if shop_status.get('session_expired', False):
                continue
            if shop_status.get('insuff_level', False):
                continue
            normal_shop_list.append(shop_status)

        return normal_shop_list

def analysis_deal_keyword():
    shop_status_list = Shop.get_all_normal_shop_status(2)
    for shop_status in shop_status_list:
        sdate = shop_status.get('deal_keyword_start_date', None)
        edate = shop_status.get('deal_keyword_end_date', None)
        if sdate and edate:
            print '%s, %s, %s' % (shop_status['nick'], str(sdate.date()), str(edate.date()))
        else:
            print '为空 %s, %s, %s' % (shop_status['nick'], str(sdate), str(edate))

def analysis_key_campaign():
    shop_status_list = Shop.get_all_normal_shop_status(2)
    for shop_status in shop_status_list:
        edate = shop_status.get('key_campaign_optimize_time', None)
        if shop_status.get('key_campaign_cancel_status', True):
            continue
        if edate:
            print '%s, %s' % (shop_status['nick'], str(edate.date()))

if __name__ == '__main__':
    analysis_key_campaign()
