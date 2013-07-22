#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Wu Liang
@contact: garcia.wul@alibaba-inc.com
@date: 2013-04-16 17:30
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
import os,sys
CURRENT_DIR=os.path.normpath(os.path.join(os.path.dirname(__file__),"../"))
import logging
logger = logging.getLogger('Analysis')
hdlr = logging.FileHandler(CURRENT_DIR+"/log")
hdlr.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s-%(levelname)s: %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

