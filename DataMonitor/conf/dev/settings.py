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

CURRENT_PATH=os.path.normpath(os.path.join(os.path.dirname(__file__),"../"))
CACHE_DIR = CURRENT_PATH+'/cache/'
MARKET_CHECK_SETTING = {
        'CHANGE':0,
        'ADD':1,
        'TIME':10,
        'NUM':10
        }
ORDER_CHECK_SETTING = {
        'ADD':1,
        'TIME':30,
        'NUM':30
        }

