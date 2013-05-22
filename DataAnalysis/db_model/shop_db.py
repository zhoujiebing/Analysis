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
    def get_shop_info_by_sid(cls, soft_code, shop_id):
        """根据shop_id获得店铺基本信息"""

        pass

    @classmethod
    def get_shop_status_by_sid(cls, soft_code, shop_id):
        """根据shop_id获得店铺设置信息"""

        pass

    @classmethod
    def get_shop_info_by_nick(cls, soft_code, nick):
        """根据nick获得店铺基本信息"""

        pass

    @classmethod
    def get_shop_status_by_nick(cls, soft_code, nick):
        """根据nick获得店铺设置信息"""

        pass

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
        """获取省油宝的所有正常shop_status"""
        
        shop_status_list = Shop.get_all_shop_status(soft_code)
        normal_shop_list = []
        for shop_status in shop_status_list:
            if shop_status.get('session_expired', False):
                continue
            if shop_status.get('insuff_level', False):
                continue
            normal_shop_list.append(shop_status)

        return normal_shop_list
    
    @classmethod
    def store_shop_to_center(cls, nick, sid, article_code, deadline, access_token):
        """存储用户数据到数据中心"""
        
        shop = {'nick':str(nick), 'sid':int(sid)}
        try:
            if article_code == 'ts-1796606':
                seller = ShopServiceSYB.get_seller_info_by_nick(nick, access_token)
            elif article_code == 'ts-1797607':
                seller = ShopServiceXCW.get_seller_info_by_nick(nick, access_token)
        except Exception, e:
            return None
        if seller:
            shop['seller_mobile'] = seller.get('seller_mobile', '')
            shop['seller_name'] = seller.get('seller_name', '')
            shop['seller_email'] = seller.get('seller_email', '')
        
        shop['worker_id'] = ShopDBService.allocate_one_shop()
        shop[article_code+'_deadline'] = deadline
        shop[article_code+'_status'] = '初始化'
        shop['update_time'] = datetime.datetime.now()
        shop['flag'] = True
        ShopDBService.upsert_shop(shop)
        return shop

if __name__ == '__main__':
    shops_info = Shop.get_all_shop_info(1) 
    print len(shops_info)
