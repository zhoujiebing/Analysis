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
import time
if __name__ == '__main__':
    sys.path.append('../../')

import datetime
from CommonTools.logger import logger
from CommonTools.send_tools import send_sms
from DataAnalysis.conf.settings import CURRENT_DIR
from user_center.conf.settings import WORKER_DICT
from user_center.services.shop_db_service import ShopDBService

def send_update_user(limit_time):
    """获取需要同步到百会的卖家信息"""
    
    file_obj = file(CURRENT_DIR+'data/update_user.csv', 'w')
    update_list = ShopDBService.get_update_shop_list(limit_time)
    file_obj.write('卖家,电话,姓名,专属客服\n')
    for shop in update_list:
        shop['seller_name'] = shop.get('seller_name', '')
        shop['seller_mobile'] = shop.get('seller_mobile', '')
        shop['worker_name'] = WORKER_DICT[shop['worker_id']]
        if shop['update_time'] <= limit_time:
            continue
        if not shop['seller_name']:
            continue
        print '%(nick)s, %(seller_mobile)s, %(seller_name)s, %(worker_name)s' % (shop)
        file_obj.write('%(nick)s, %(seller_mobile)s, %(seller_name)s, %(worker_name)s\n' % (shop))
    file_obj.close()

        
if __name__ == '__main__':
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    limit_time = datetime.datetime.combine(yesterday, datetime.time())
    send_update_user()
