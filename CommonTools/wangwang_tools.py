#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2013-06-03 15:17
@version: 0.0.0
@license: Copyright Maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
if __name__ == '__main__':
    import sys
    sys.path.append('../')
import datetime
from CommonTools.string_tools import parser_string_to_date

def parse_wangwang_talk_record(file_name, start_date, end_date):
    """解析聊天nick"""
    
    pre_market_effect = {}
    wangwang_records = {}
    init_data = start_date
    while init_data <= end_date:
        wangwang_records[init_data] = {}
        init_data += datetime.timedelta(days=1)

    for line in file(file_name):
        line_data = line.split(',')
        if len(line_data) < 4:
            continue
        service_date = parser_string_to_date(line_data[0])
        service_nick = line_data[2]
        worker = line_data[3]
        if worker.find('麦苗科技') == -1:
            continue
        if service_nick.find(':') != -1:
            service_nick = service_nick.split(':')[0]
        if start_date <= service_date <= end_date:
            if not pre_market_effect.has_key(worker):
                pre_market_effect[worker] = {'service_num':0}

            pre_market_effect[worker]['service_num'] += 1
            wangwang_records[service_date][service_nick] = worker 

    return (pre_market_effect, wangwang_records)

if __name__ == '__main__':
    (pre_market_effect, wangwang_records) = parse_wangwang_talk_record('wangwang_record.csv', \
            datetime.date(2013,6,1), datetime.date(2013,6,7))
    import pdb
    pdb.set_trace()
