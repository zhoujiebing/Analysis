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
     
    #syb common_info
    dest_conn = pymongo.Connection(host='wp.maimiaotech.com', port=2007)
    dest_conn.drop_database('CommonInfo')
    dest_conn.copy_database('CommonInfo', 'CommonInfo', 'syb.maimiaotech.com:2011')

    #bd common_info
    dest_conn = pymongo.Connection(host='wp.maimiaotech.com', port=1996)
    dest_conn.drop_database('CommonInfo')
    dest_conn.copy_database('CommonInfo', 'CommonInfo', 'xcw.maimiaotech.com:27017')
