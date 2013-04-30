#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: garcia.wul@alibaba-inc.com
@date: 2012-10-15 11:12
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
from CommonTools.report_tools import Report
SOFT_LIST = ['省油宝长尾计划', '省油宝加力计划', '广撒网计划', '喜宝计划', '极品飞车', '懒人开车', '疯狂车手', '大麦']

class Compare:
    """
    store the compare result 
    """
    def __init__(self):
        self.total = 0
        self.result = [[0, 0, 0] for x in range(3)]

def compare_campain(syb, another):
    """
    compare two campaign in three sides, multi_roi multi_pay and roi
    """
    compare_result = []
    delta = another['multi_roi'] - syb['multi_roi'] + 0.000001
    compare_result.append(1+int(round(delta/abs(delta+0.00001))))
    delta = another['multi_pay'] - syb['multi_pay'] + 0.000001
    compare_result.append(1+int(round(delta/abs(delta+0.00001))))
    delta = another['roi'] - syb['roi'] + 0.000001
    compare_result.append(1+int(round(delta/abs(delta+0.00001))))
    return compare_result

def analysis(campaigns, _number_dict):
    """
    main method
    """
    if len(campaigns) < 1 or campaigns[0]['campaign'].find('省油宝长尾计划') == -1:
        return
    syb = campaigns[0]
    FLAG_LIST = [False for x in range(len(SOFT_LIST))]
    CAM_LIST = [None for x in range(len(SOFT_LIST))]
    for i in range(1, len(campaigns)):
        campaign_name = campaigns[i]['campaign']
        for j in range(1,len(SOFT_LIST)):
            if campaign_name.find(SOFT_LIST[j]) != -1:
                FLAG_LIST[j] = True
                _number_dict[SOFT_LIST[j]].total += 1
                CAM_LIST[j] = campaigns[i]

    for i in range(len(FLAG_LIST)):
        if FLAG_LIST[i]:
            result = compare_campain(syb, CAM_LIST[i])
            for j in range(len(result)):
                _number_dict[SOFT_LIST[i]].result[j][result[j]] += 1

def analysis_campaign_horizontal(file_name):
    """
    多个计划的 横向对比分析
    """
    NICK = None
    CAMPAIGN_LIST = []
    NUMBER_DICT = {}
    content = '' 
    for key in SOFT_LIST[1:]:
        NUMBER_DICT[key] = Compare()

    for line in file(file_name):
        campaign = Report.parser_report(line)
        if not campaign:
            continue
        if not NICK or campaign['nick'] == NICK:
            if campaign['campaign'].find('省油宝长尾计划') != -1:
                CAMPAIGN_LIST.insert(0, campaign)
            else:
                CAMPAIGN_LIST.append(campaign)
            if not NICK:
                NICK = campaign['nick'] 
        else:
            NICK = campaign['nick']
            analysis(CAMPAIGN_LIST, NUMBER_DICT)
            CAMPAIGN_LIST = []
    content += '下面为相应指标好的个数\n'
    for key in NUMBER_DICT:
        _compare_result = NUMBER_DICT[key]
        content += '省油宝长尾计划 与 ' + key + ': ' + str(_compare_result.total)
        _result = _compare_result.result
        content += '\n多天ROI: %d    %d\n' % (_result[0][0], _result[0][2])
        content += '多天成交额: %d    %d\n' % (_result[1][0], _result[1][2])
        content += '单天ROI: %d    %d\n' % (_result[2][0], _result[2][2])
    return content

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print 'input arg'
        exit(0)
    print analysis_campaign_horizontal(sys.argv[1])
