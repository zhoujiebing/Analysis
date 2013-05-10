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
from xuancw.services.shop_service import ShopService as ShopServiceXCW
from shengyb.service.shop_service import ShopService as ShopServiceSYB
from user_center.services.shop_db_service import ShopDBService

class Shop(object):

    @classmethod
    def get_shop_info(cls, soft_code, shop_id):
        """根据shop_id获得店铺基本信息"""

        if soft_code == 1:
            return ShopServiceXCW.get_shop_info_by_sid(int(shop_id))
        elif soft_code == 2:
            return ShopServiceSYB.get_shop_info_by_sid(int(shop_id))

    @classmethod
    def get_shop_status(cls, soft_code, shop_id):
        """根据shop_id获得店铺设置信息"""

        if soft_code == 1:
            return ShopServiceXCW.get_shop_status_by_sid(int(shop_id))
        elif soft_code == 2:
            return ShopServiceSYB.get_shop_status_by_sid(int(shop_id))

    @classmethod
    def get_all_shop_info(cls, soft_code):
        """获取所有shop_info"""
        
        if soft_code == 1:
            return ShopServiceXCW.get_all_shop_info_list()
        elif soft_code == 2:
            return ShopServiceSYB.get_all_shop_info_list()

    @classmethod
    def get_all_shop_status(cls, soft_code):
        """获取所有shop_status"""

        if soft_code == 1:
            return ShopServiceXCW.get_all_shop_status_list()
        elif soft_code == 2:
            return ShopServiceSYB.get_all_shop_status()

    @classmethod
    def get_all_normal_shop_status_in_syb(cls):
        """获取省油宝的所有正常shop_status"""
        
        shop_status_list = Shop.get_all_shop_status(2)
        normal_shop_list = []
        for shop_status in shop_status_list:
            if shop_status.get('session_expired', False):
                continue
            if shop_status.get('insuff_level', False):
                continue
            normal_shop_list.append(shop_status)

        return normal_shop_list
    
    @classmethod
    def get_all_normal_shop_status_in_bd(cls):
        """获取北斗的所有正常shop_status"""

        pass
    
    @classmethod
    def store_shop_to_center(cls, nick, article_code, deadline):
        """存储用户数据到数据中心"""
        
        if article_code == 'ts-1796606':
            shop_info = ShopServiceSYB.get_shop_info_by_nick(nick)
            if not shop_info:
                return None
            seller = ShopServiceSYB.get_seller_info_by_nick(nick, shop_info['access_token'])
        elif article_code == 'ts-1797607':
            shop_info = ShopServiceXCW.get_shop_info_by_nick(nick)
            if not shop_info:
                return None
            seller = ShopServiceXCW.get_seller_info_by_nick(nick, shop_info['access_token'])

        shop = {'nick':str(nick), 'sid':int(shop_info['_id'])}
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
