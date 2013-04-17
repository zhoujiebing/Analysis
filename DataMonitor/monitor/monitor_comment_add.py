#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:  zhoujiebing
@contact: zhoujiebing@maimiaotech.com
@date: 2013-02-27 10:16
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
import re
import sys
import urllib2
if __name__ == '__main__':
    sys.path.append('../../')

from DataMonitor.conf.settings import CACHE_DIR

import HTMLParser
parser = HTMLParser.HTMLParser()

def get_record_comment(id_name):
    file_date = file(CACHE_DIR+id_name+'_comment').read().split('\n')
    comment_type = file_date[0].split(',')
    if len(comment_type) >= 2:
        return (comment_type[0], comment_type[1])
    else:
        return ('nick', 'comment')

def write_record_comment(id_name, nick, comment):
    file_obj = file(CACHE_DIR+id_name+'_comment', 'w')
    file_obj.write('%s,%s\n' % (nick, comment))
    file_obj.close()

def monitor_comment_add(id_name='省油宝', id='ts-1796606'):
    return_info = ''
    comment_list = get_first_page_comment(id)
    (old_nick, old_comment) = get_record_comment(id)
    first_comment = comment_list[0]
    bad_comment = False
    for comment in comment_list:
        comment['comment'] = parser.unescape(comment['suggestion']).encode('utf8')
        comment['comment'] = comment['comment'].replace('\n','')
        if old_nick == comment['userNick'] and hash(old_comment) == hash(comment['comment']):
            break
        print comment['userNick']+' : '+comment['comment']
        return_info += id_name+'新评价: ' + comment['comment'] + '\n'

    write_record_comment(id, first_comment['userNick'], first_comment['comment'])
    return return_info
    
def getWebPage(url):
    wp = urllib2.urlopen(url)
    content = wp.read()
    return content

def getUrl(id, day):
    url = 'http://fuwu.taobao.com/score/query_suggest.do?service_code='+id+'&callback=jsonp_reviews_list'
    return url

def get_first_page_comment(id):
    true = 'true'
    null = 'null'
    for day in range(1,2):
        url = getUrl(id, str(day))
        content = getWebPage(url).split('\n')
        comment_dict = eval(content[1][19:-2])
        comment_list = comment_dict['comments']
        return comment_list

if __name__ == '__main__':
    print monitor_comment_add()
