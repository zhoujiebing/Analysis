#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:  zhoujiebing
@contact: zhoujiebing@maimiaotech.com
@date: 2012-08-25 16:18
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
import os
import re
import urllib2

ORDER_TYPE = ['1个月','3个月','6个月','1年','7天']
NUM_TYPE = ['pay_num','free_num','comment_num','grade']
KEYS = ['id_name'] + ORDER_TYPE + ['add_num'] + NUM_TYPE

class ZtcReport:

    @classmethod
    def get_file_name(self, current_dir, date):
        return current_dir + 'data/ztc_data/ztc' + str(date) + '.csv'

    @classmethod
    def parser_ztc_report(self, line):
        """解析直通车 报表"""
        
        #软件名称,1个月,3个月,6个月,1年,7天,总共新增,付费用户,免费用户,评价数,评价分
        report = {}
        line_data = line.split(',')
        for i in range(len(KEYS)):
            report[KEYS[i]] = line_data[i]
        report[KEYS[i]] = line_data[i].replace('\n', '')
        return report

    @classmethod
    def to_string(self, report):
        string_list = [str(report[key]) for key in KEYS]
        return ','.join(string_list)



