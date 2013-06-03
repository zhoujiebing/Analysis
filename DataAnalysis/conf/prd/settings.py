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
import logging
import pymongo
from pymongo import Connection

sys.path.append(os.path.join(os.path.dirname(__file__),'../../../TaobaoOpenPythonSDK/'))
sys.path.append(os.path.join(os.path.dirname(__file__),'../../../backends/'))
sys.path.append(os.path.join(os.path.dirname(__file__),'../../../comm_lib/'))

#北斗1 省油宝2
SOFT_CODE_SETTING = None 
def set_soft_code(soft_code):
    global SOFT_CODE_SETTING
    SOFT_CODE_SETTING = soft_code

    print "soft code:", soft_code
    from Analysis.conf import set_env
    set_env.getEnvReady(SOFT_CODE_SETTING)
    
CURRENT_DIR = '/home/zhoujiebing/Analysis/DataAnalysis/'
logger = logging.getLogger("DataAnalysis")
hdlr = logging.FileHandler(CURRENT_DIR+'data/report_log')
hdlr.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s-%(levelname)s: %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

if pymongo.version.startswith("2.5"):
    import bson.objectid
    import bson.json_util
    pymongo.objectid = bson.objectid
    pymongo.json_util = bson.json_util
    sys.modules['pymongo.objectid'] = bson.objectid
    sys.modules['pymongo.json_util'] = bson.json_util

#MONGODB SETTINGS
MGDBS = {
        'syb1':{
            'HOST':'192.168.10.246',
            'PORT':2010,
        },
        'syb2':{
            'HOST':'192.168.10.243',
            'PORT':2010,
        },
        'bd':{
            'HOST':'xcw.maimiaotech.com',
            'PORT':27017,
        }
    }

#利用mongodb 自带的connection poll 来管理数据库连接
host_url = []
for key in ['syb1', 'syb2']:
    host_url.append('%s:%i' % (MGDBS[key]['HOST'], MGDBS[key]['PORT']))
host_url = ','.join(host_url)
syb_db = pymongo.MongoReplicaSetClient(host=host_url, replicaSet='syb_db_replset')
bd_db = Connection(host=MGDBS['bd']['HOST'],port=MGDBS['bd']['PORT'])
