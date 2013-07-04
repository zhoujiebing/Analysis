#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
sys.path.append('../')

from DataAnalysis.collect.collect_report import collect_report_script
from DataAnalysis.analysis.analysis_campaign_script import analysis_campaign_script
from DataAnalysis.analysis.analysis_campaign_optimise import analysis_campaign_optimise 

collect_report_script()
analysis_campaign_script()
analysis_campaign_optimise()
