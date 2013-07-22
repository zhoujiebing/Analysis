#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: xieguanfu 
@contact: xieguanfu@maimiaotech.com
@date: 2013-07-12 10:52:00
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
import re
import sys
import datetime

if __name__ == '__main__':
    sys.path.append('../../')

from DataAnalysis.conf.settings import CURRENT_DIR,syb_db
from DataAnalysis.db_model.shop_db import Shop
from CommonTools.logger import logger
from CommonTools.send_tools import send_sms, DIRECTOR
from tao_models.logistics_address_search import LogisticsAddressSearch
from tao_models.taobao_user_seller_get import UserSellerGet
from tao_models.taobao_trade_fullinfo_get import TradeFullinfoGet
from tao_models.taobao_trades_sold_get  import TradesSoldGet
if __name__=="__main__":
    from tao_models.conf.settings import set_taobao_client
    set_taobao_client('12685542', '6599a8ba3455d0b2a043ecab96dfa6f9')

class SellerInfoCollect(object):
    _conn=syb_db["CommonInfo"]

    @classmethod
    def get_seller_info(cls):
        user_list=Shop.get_all_shop_info(2)
        print len(user_list)
        user_list=user_list[11500:]
        total=len(user_list)
        index=0
        for user in user_list:
            nick=user["nick"]
            access_token=user.get("access_token")
            if access_token is None :
                print "%s session不存在" %(nick)
                continue
            index+=1
            print "总共:%d 个用户,开始获取第%d个用户 %s 信息" %(total,index,nick)
            if user.get("deadline") is not None and  user.get("deadline")<datetime.datetime.now():
                print "%s过期,跳过" %(nick) 
                continue
            try:
               seller= cls.get_single_seller_info(nick,access_token)
               cls.save_seller_info_temp(seller)
            except Exception,e:
                #import traceback
                #traceback.print_exc()
                print str(e)
    @classmethod
    def get_single_seller_info(cls,nick,access_token):
        user=UserSellerGet.get_user_seller(access_token)
        address_list=LogisticsAddressSearch.get_logistics_address(access_token)
        if address_list is not None:
            address_list=[address.toDict() for address in address_list]
        else:
            address_list=[]
        seller=cls.get_seller_info_by_nick(nick,access_token)
        ret_dict={}
        user= user.toDict()
        user["seller_credit"]=user["seller_credit"].toDict()
        ret_dict.update(user)
        if seller is not None:
            ret_dict.update(seller)
        ret_dict["address"]=address_list
        return ret_dict
    
    @classmethod
    def save_seller_info_temp(cls,user):
        nick=user["nick"]
        filter={"nick":nick}
        cls._conn["seller_info"].update(filter,user,upsert=True) 
    
    @classmethod
    def get_seller_info_by_nick(cls,nick, access_token):
        today = datetime.date.today()
        start_created_str = str(today - datetime.timedelta(days=15))
        end_created_str = str(today)
        fields = 'tid'
        TradesSoldGet.PAGE_SIZE=1
        total_trade_list = TradesSoldGet.get_trades_sold_list(access_token, start_created_str, end_created_str,fields, True)
        if len(total_trade_list) == 0:
            return None
        trade = TradeFullinfoGet.get_trade_info(access_token, total_trade_list[0].tid, 'seller_mobile, seller_phone, seller_name,seller_email,seller_nick ')
        return trade.toDict()
    @classmethod
    def get_seller_from_db(cls):
        """获取 3钻以上的杭州地址卖家 """
        cursor=cls._conn["seller_info"].find({})
        seller_list=[seller for seller in cursor]
        file_seller=open(CURRENT_DIR+"/data/seller_info.csv","w")
        for seller in seller_list:
            seller_credit=seller["seller_credit"]
            if seller_credit.get("level",0)<8:
                continue
            address_list=seller["address"]
            flag=False
            temp={}
            for address in address_list:
                if address["get_def"] and "杭州" in address["city"] :
                    flag=True
                    temp=address
                    break
            if flag:
                info= "%s,%s,%s,%s,%s,%s,%s\n" %(seller["nick"],temp.get("contact_name",""),seller.get("seller_mobile",""),seller.get("seller_phone","")\
                        ,seller.get("seller_email",""),seller_credit.get("level",0),seller["type"])
                print info
                file_seller.write(info)

if __name__=="__main__":
    SellerInfoCollect.get_seller_info()
    #user=SellerInfoCollect.get_single_seller_info("6201b160a531aed44eec6fc2ZZ3e248053b1a94ad723b31130334991")
    #SellerInfoCollect.save_seller_info_temp(user)
    #SellerInfoCollect.get_seller_from_db()
