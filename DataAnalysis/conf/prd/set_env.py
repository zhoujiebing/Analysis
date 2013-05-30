#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2012-12-17 13:34
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
import os
import sys

currDir = os.path.normpath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(currDir,os.path.pardir))
PROJECT_PAR = os.path.normpath(os.path.join(PROJECT_ROOT,os.path.pardir))

#自动竞价依赖report_db
BACKENDS = os.path.normpath(os.path.join(currDir, '../../../backends/'))
sys.path.append(BACKENDS)

#自动竞价依赖tao_model
COMM_LIB = os.path.normpath(os.path.join(currDir, '../../../comm_lib/'))
sys.path.append(COMM_LIB)

#自动竞价依赖service 包括省油宝 和 选词王
WEBPAGE_LIB = os.path.normpath(os.path.join(currDir, '../../../Webpage/'))
sys.path.append(WEBPAGE_LIB)

def getEnvReady(soft_code=1):
    #将当前项目的父目录加入sys.path
    sys.path.insert(0,PROJECT_PAR)

    #设置各个依赖库的自己的环境依赖,即调用依赖库自己的getEnvReady方法
    from report_db.conf import set_env as report_db_set_env 
    report_db_set_env.getEnvReady()

    from tao_models.conf import set_env as tao_models_set_env 
    tao_models_set_env.getEnvReady()
    
    if soft_code == 1:
        from xuancw.conf import set_env as xcw_set_env
        xcw_set_env.getEnvReady()
    elif soft_code == 2:
        from shengyb.conf import set_env as syb_set_env
        syb_set_env.getEnvReady()
