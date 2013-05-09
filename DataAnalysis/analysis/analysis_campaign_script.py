#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebing
@contact: zhoujiebing@maimiaotech.com
@date: 2012-11-06 10:29
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
import os
import sys
import datetime
if __name__ == '__main__':
    sys.path.append('../../')

from CommonTools.send_tools import send_email_with_text, send_sms
from CommonTools.logger import logger
from DataAnalysis.conf.settings import CURRENT_DIR
from DataAnalysis.analysis.analysis_campaign_simple import analysis_campaign_simple
from DataAnalysis.analysis.analysis_campaign_complex import analysis_campaign_complex
from DataAnalysis.analysis.analysis_campaign_horizontal import analysis_campaign_horizontal

def analysis_campaign(report_file):
    content = ''
    content += analysis_campaign_complex(report_file, '省油宝长尾计划')
    content += analysis_campaign_complex(report_file, '省油宝加力计划')
    content += analysis_campaign_simple(report_file)
    content += analysis_campaign_horizontal(report_file)
    return content

def analysis_campaign_script():
    today = str(datetime.date.today())
    report_file = CURRENT_DIR+'data/report_data/report' + today + '.csv'
    if not os.path.exists(report_file):
        logger.error('analysis_campaign error: %s not exists ' % (report_file))
        return None
    try:
        content = analysis_campaign(report_file)
        sendTo = ['zhoujiebing@maimiaotech.com', 'tangxijin@maimiaotech.com', \
            'chenke@maimiaotech.com', 'liyangmin@maimiaotech.com']
        #for send_to in sendTo:
        #    send_email_with_text(send_to, content, today+'_省油宝日常分析')
        send_email_with_text('zhoujiebing@maimiaotech.com', content, today+'_省油宝日常分析')
    except Exception,e:
        logger.exception('analysis_campaign error: %s' % (str(e)))
        send_sms('13738141586', 'analysis_campaign error: %s' % (str(e)))
    else:
        logger.info('analysis_campaign ok')

if __name__ == '__main__':
    analysis_campaign_script()
    #print analysis_campaign('/home/zhoujiebing/Analysis/DataAnalysis/data/report_data/report2013-04-17.csv')

