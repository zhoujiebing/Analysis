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

CACHE_DIR = '/home/zhoujiebing/Analysis/DataMonitor/cache/'
MARKET_CHECK_SETTING = {
        'CHANGE':0,
        'ADD':1
        }
ORDER_CHECK_SETTING = {
        'ADD':1
        }
