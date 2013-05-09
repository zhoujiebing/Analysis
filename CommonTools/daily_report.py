#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

file_path = '../../'
collect_report = os.path.join(file_path, 'DataAnalysis/collect/collect_report.py')
analysis_report = os.path.join(file_path, 'DataAnalysis/analysis/analysis_campaign_script.py')
collect_self_order = os.path.join(file_path, 'DataAnalysis/collect/collect_self_order.py')
send_self_order = os.path.join(file_path, 'DataAnalysis/analysis/analysis_self_order_script.py')

#ps = subprocess.Popen('python %s' % (collect_report), shell=True)
#ps.wait()

#ps = subprocess.Popen('python %s' % (analysis_report), shell=True)
#ps.wait()

ps = subprocess.Popen('python %s' % (collect_self_order), shell=True)
ps.wait()

ps = subprocess.Popen('python %s' % (send_self_order), shell=True)
ps.wait()
