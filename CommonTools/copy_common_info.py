#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Chen Ke
@contact: chenke@MaimiaoTech.com
@date: 2012-09-26 16:32
@version: 0.0.0
@license: Copyright MaimiaoTech.com
@copyright: Copyright MaimiaoTech.com

"""
import pymongo

if __name__ == '__main__':
    dest_conn = pymongo.Connection(port=2007)
    dest_conn.drop_database('CommonInfo')
    dest_conn.copy_database('CommonInfo', 'CommonInfo', 'syb.maimiaotech.com:1990')

