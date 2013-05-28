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
import sys
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'input arg'
        exit(0) 
    dest_conn = pymongo.Connection(port=2007)
    str_sid = sys.argv[1]
    dest_conn.drop_database(str_sid)
    dest_conn.copy_database(str_sid, str_sid, 'syb.maimiaotech.com:2010')
        
