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
import sys
import urllib2
import datetime

if __name__ == '__main__':
    sys.path.append('/home/zhoujiebing/Analysis/')

from DataAnalysis.conf.settings import CURRENT_DIR
from CommonTools.ztc_order_tools import ZtcOrder, SOFT_CODE
from CommonTools.logger import logger
from CommonTools.send_tools import send_sms

class ZtcOrderCollect(ZtcOrder):
    
    def __init__(self, today):
        #获取所有直通车软件
        self.id_data = SOFT_CODE.items()
        self.today = today
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.id_name = ''
        self.order_dict = ZtcOrder.get_store_order(self.id_data, CURRENT_DIR, self.today)
    
    def write_order(self):
        file_name = ZtcOrder.get_file_name(CURRENT_DIR, self.today)
        file_obj = file(file_name, 'w')
        for key in self.order_dict:
            soft_order_dict = self.order_dict[key]
            for order in soft_order_dict.values():
                outer = str(key)+','+order['nick']+','+order['version']+','+order['deadline']+','+order['payTime']+'\n'
                file_obj.write(outer)
        file_obj.close()

    def get_order(self):
        for id_info in self.id_data:
            self.id_name = id_info[0]
            id = id_info[1]
            print 'id_name: ',self.id_name
            store_order = self.order_dict[self.id_name]
            order_list = self.get_order_by_soft(id, str(self.today))
            print 'order_list len: ',len(order_list)
            for order in order_list:
                key = ZtcOrder.hash_ztc_order(order)
                if not store_order.has_key(key):
                    store_order[key] = order

    def getWebPage(self, url):
        wp = urllib2.urlopen(url)
        content = wp.read()
        return content
    
    def getUrl(self, id, day):
        url = 'http://fuwu.taobao.com/serv/rencSubscList.do?serviceCode=' + id + '&currentPage=' + day + '&pageCount=' + day
        return url
    
    def get_order_by_soft(self, id, today):
        """
        order:{'nick': '\xe4\xb9\x89**\xe5\x9f\x8e', 'version': '\xe9\x95\xbf\xe5\xb0\xbe\xe7\x89\x88', 'deadline': '3\xe4\xb8\xaa\xe6\x9c\x88', 'isB2CSeller': '0', 'rateSum': '2_4', 'rateNum': '', 'payTime': '2013-03-05 15:16:58', 'isTryoutSubed': 0, 'isPlanSubed': '0'}
        """
        order_list = []
        for page in range(1,16):
            flag = False
            url = self.getUrl(id, str(page))
            content = self.getWebPage(url).split('\n')
            page_dict = ZtcOrder.eval_ztc_order(content[1])
            page_list = page_dict['data']
            for order in page_list:
                if order['payTime'].find(today) != -1:
                    order_nick = order['nick']
                    if order_nick.find('<font title="') != -1:
                        order_nick = order_nick.split('"')
                        order['nick'] = order_nick[1]
                    order_list.append(order)
                    flag = True
            if not flag and order['payTime'].find(str(self.yesterday)) != -1:
                break

        return order_list

def collect_order_script(_days=0):
    today = datetime.date.today() - datetime.timedelta(days=_days)
    try:
        ztc = ZtcOrderCollect(today)
        ztc.get_order()
        ztc.write_order()
    except Exception,e:
        logger.error('collect_order_script %s: %s' % (str(today), str(e)))
        send_sms('13738141586', 'collect_order_script %s: %s' % (str(today), str(e)))
    else:
        logger.info('collect_order_script %s ok', str(today))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        collect_order_script()
    else:
        collect_order_script(int(sys.argv[1]))
