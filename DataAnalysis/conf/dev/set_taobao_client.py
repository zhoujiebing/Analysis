#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Li Yangmin
@contact: liyangmin@maimiaotech.com
@date: 2012-11-16 14:38
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""

from tao_models.conf.settings import  set_taobao_client

def set_tao_client(article_code):
    if article_code == 'ts-1796606':
        set_taobao_client('12685542', '6599a8ba3455d0b2a043ecab96dfa6f9')
    elif article_code == 'ts-1797607':
        set_taobao_client('21065688', '74aecdce10af604343e942a324641891')
    else:
        print 'article_code error: '+article_code
