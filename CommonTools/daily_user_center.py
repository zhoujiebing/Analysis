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

daily_update_script()
send_add_order_and_support()
daily_report_script()
