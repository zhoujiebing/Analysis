#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:  zhoujiebing
@contact: zhoujiebing@maimiaotech.com
@date: 2012-08-25 16:18
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
import re
import urllib2
import sys
if __name__ == '__main__':
    sys.path.append('../../')

from DataMonitor.conf.settings import CACHE_DIR, ORDER_CHECK_SETTING

def get_record_order(id_name):
    file_date = file(CACHE_DIR+id_name+'_order').read().split('\n')
    order_type = file_date[0].split(',')
    if len(order_type) >= 3:
        return (order_type[0], order_type[1], int(order_type[2]))
    else:
        return ('nick','time', 3)

def write_record_order(id_name, nick, time, num):
    file_obj = file(CACHE_DIR+id_name+'_order', 'w')
    file_obj.write('%s,%s,%d\n' % (nick, time, num))
    file_obj.close()

def monitor_order_add(id_name='省油宝', id='ts-1796606'):
    
    return_info = ''
    order_list = get_first_page_order(id)
    (old_nick, old_time, num) = get_record_order(id)

    if num >= 3:
        first_order = order_list[0]
        add_order = 0
        for order in order_list:
            if old_nick == order['nick'] and old_time == order['payTime']:
                break
            add_order += 1
            num = 0
        if add_order < ORDER_CHECK_SETTING['ADD']:
            return_info = id_name+'30分钟内新增订单数为:%d, 低于警报界限:%d.\n' % (add_order, ORDER_CHECK_SETTING['ADD'])
        print 'add_order:',add_order
        write_record_order(id, first_order['nick'], first_order['payTime'], 0)
    else:
        num += 1
        write_record_order(id, old_nick, old_time, num)

    return return_info

def getWebPage(url):
    wp = urllib2.urlopen(url)
    content = wp.read()
    return content

def getUrl(id, day):
    url = 'http://fuwu.taobao.com/serv/rencSubscList.do?serviceCode=' + id + '&currentPage=' + day + '&pageCount=' + day
    return url

def get_first_page_order(id):
    flag = False
    currentPage = 'currentPage'
    pageCount = 'pageCount'
    rateNum = 'rateNum'
    rateSum = 'rateSum'
    isB2CSeller = 'isB2CSeller'
    nick = 'nick'
    deadline = 'deadline'
    version = 'version'
    isPlanSubed = 'isPlanSubed'
    payTime = 'payTime'
    data = 'data'
    isTryoutSubed = 'isTryoutSubed'
    for day in range(1,2):
        url = getUrl(id, str(day))
        content = getWebPage(url).split('\n')
        order_dict = eval(content[1])
        order_list = order_dict['data']
        return order_list

if __name__ == '__main__':
    print 'monitor_order_add:', monitor_order_add()
    
