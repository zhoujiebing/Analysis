#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

file_path = '/home/zhoujiebing/Analysis/'
collect_report = os.path.join(file_path, 'DataAnalysis/collect/collect_report.py')
analysis_report = os.path.join(file_path, 'DataAnalysis/analysis/analysis_campaign_script.py')

ps = subprocess.Popen('python %s' % (collect_report), shell=True)
ps.wait()

ps = subprocess.Popen('python %s' % (analysis_report), shell=True)
ps.wait()
