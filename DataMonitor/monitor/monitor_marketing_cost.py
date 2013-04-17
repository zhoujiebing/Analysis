#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Wu Liang
@contact: garcia.wul@alibaba-inc.com
@date: 2013-02-26 18:17
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
import sys
if __name__ == '__main__':
    sys.path.append('../../')

from DataMonitor.conf.settings import CACHE_DIR, MARKET_CHECK_SETTING

from tao_models.conf import set_env as tao_models_set_env
from tao_models.conf.settings import set_taobao_client
set_taobao_client('21065688', '74aecdce10af604343e942a324641891')
tao_models_set_env.getEnvReady()

from tao_models.simba_account_balance_get import SimbaAccountBalanceGet

def get_record_money():
    file_date = file(CACHE_DIR+'money').read().split('\n')
    return float(file_date[0]) if file_date[0] else 0

def write_record_money(money):
    file_obj = file(CACHE_DIR+'money', 'w')
    file_obj.write(str(money)+'\n')
    file_obj.close()

def get_current_money():
    access_token = '61018247b953db26c94a563642f900eb1283a1b09bc079b1101933802'
    nick = '麦苗科技营销'
    balance = SimbaAccountBalanceGet.get_account_balance(access_token, nick)
    return float(balance)

def monitor_marketing_cost():
    return_info = ''
    current_money = get_current_money()
    old_money = get_record_money()
    if old_money <= current_money and current_money != 0:
        cost = current_money - old_money
        if cost <= MARKET_CHECK_SETTING['CHANGE']:
            return_info = '麦苗科技营销10分钟内花费为:%.1f元, 低于警报界限:%d元.\n' %(cost, MARKET_CHECK_SETTING['CHANGE'])
            
    print 'current_money:',current_money
    write_record_money(current_money)
    return return_info

if __name__ == '__main__':
    print 'monitor_marketing_cost:', monitor_marketing_cost()
