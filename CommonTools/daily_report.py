#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
sys.path.append('../')

from CommonTools.copy_online_db import copy_online_db
from DataAnalysis.collect.collect_report import collect_report_script
from DataAnalysis.analysys.analysis_campaign_script import analysis_campaign_script

copy_online_db()
collect_report_script()
analysis_campaign_script()
