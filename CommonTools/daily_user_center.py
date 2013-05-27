#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
sys.path.append('../')

file_path = '../'
from DataAnalysis.collect.user_center_script import daily_update_script
from DataAnalysis.send.send_self_order import send_add_order_and_support
from DataAnalysis.analysis.analysis_user_center import daily_report_script
from DataAnalysis.collect.user_report_script import renew_account_script
#更新user_center 并将更新导入到百会CRM
daily_update_script()
send_add_order_and_support()
#日常订单统计报表
daily_report_script()
#电话续费报表
renew_account_script()
