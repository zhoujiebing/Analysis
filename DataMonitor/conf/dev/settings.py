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

sys.path.append(os.path.join(os.path.dirname(__file__),'../../../comm_lib/'))
sys.path.append(os.path.join(os.path.dirname(__file__),'../../../TaobaoOpenPythonSDK/'))
sys.path.append(os.path.join(os.path.dirname(__file__),'../../../backends/'))
sys.path.append(os.path.join(os.path.dirname(__file__),'../../../Webpage/'))

#北斗1 省油宝2
SOFT_CODE_SETTING = None 
def set_soft_code(soft_code):
    global SOFT_CODE_SETTING
    SOFT_CODE_SETTING = soft_code

    print "soft code:", soft_code
    from Analysis.conf import set_env
    set_env.getEnvReady(SOFT_CODE_SETTING)

CACHE_DIR = '/home/zhoujiebing/Analysis/DataMonitor/cache/'
MARKET_CHECK_SETTING = {
        'CHANGE':0,
        'ADD':1
        }
ORDER_CHECK_SETTING = {
        'ADD':1
        }
