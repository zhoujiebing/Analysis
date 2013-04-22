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
import os
import re
import urllib2

SOFT_CODE = {
        '省油宝':'ts-1796606',
        '北斗':'ts-1797607',
        '麦苗淘词':'ts-1817244',
        '懒人开车':'ts-1796016',
        '超级车手':'ts-29097',
        '淘快词':'ts-25420',
        '开车精灵':'ts-25811',
        '淘快车':'ts-21434',
        '智驾宝':'ts-24944',
        '好又快':'ts-29132',
        '大麦优驾':'ts-1808369',
        '车神':'ts-1804425',
        '极品飞车':'ts-1810074',
        '智能淘词':'ts-1813497',
        '疯狂车手':'ts-1813498',
        '魔镜看看':'ts-1809313',
        '如意快车':'ts-1819813',
        '超级快车':'FW_GOODS-1834824',
        '聚灵神':'FW_GOODS-1836541',
        '开车宝':'FW_GOODS-1839667',
        }

class ZtcOrder:

    @classmethod
    def get_file_name(self, current_dir, date):
        return current_dir + 'data/order_data/order' + str(date) + '.csv'

    @classmethod
    def get_store_order(self, id_data, current_dir, date):
        """获取date 当天的所有订单"""

        order_dict = {}
        for id_info in id_data:
            id_name = id_info[0]
            order_dict[id_name] = {}
        file_name = ZtcOrder.get_file_name(current_dir, date)
        if os.path.isfile(file_name):
            for line in file(file_name):
                order = ZtcOrder.parser_ztc_order(line)
                key = ZtcOrder.hash_ztc_order(order)
                order_dict[order['id_name']][key] = order
        return order_dict

    def write_order(self):
        file_name = ZtcOrder.get_file_name(CURRENT_DIR, self.today)
        file_obj = file(file_name, 'w')
        for key in self.order_dict:
            soft_order_dict = self.order_dict[key]
            for order in soft_order_dict.values():
                outer = str(key)+','+order['nick']+','+order['version']+','+order['deadline']+','+order['payTime']+'\n'
                file_obj.write(outer)
        file_obj.close()
    @classmethod
    def parser_ztc_order(self, line):
        """讲以行形式存储的 网页订单数据 转化成dict"""

        #str(key)+','+order['nick']+','+order['version']+','+order['deadline']+','+order['payTime']+'\n'
        order = {}
        line_data = line.split(',')
        order['id_name'] = line_data[0]
        order['nick'] = line_data[1]
        order['version'] = line_data[2]
        order['deadline'] = line_data[3]
        order['payTime'] = line_data[4]
        return order 

    @classmethod
    def hash_ztc_order(self, order):
        """计算 ztc 订单 的 hash"""

        return hash(order['nick']+order['version']+order['deadline']+order['payTime'][:-1])

    @classmethod
    def eval_ztc_order(self, content):
        """将string 的ztc order 转换 成 dict"""

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
        planUrl = 'planUrl'
        
        return eval(content)
    
    @classmethod
    def get_total_num(self, id):
        """获取 粗略 总数 信息"""
        url =  'http://fuwu.taobao.com/ser/detail.htm?service_code=' + id 
        keys = ['grade', 'comment_num', 'pay_num', 'free_num', 'pv']
        wp = urllib2.urlopen(url)
        content = wp.read()
        total_num = {}
        r = re.compile(r'(?s)<span class="(count|grade)">(?P<data>[^<]+)</span>')
        i = 0
        for m in r.finditer(content):
            v = m.group("data")
            str_num = v.strip().replace(',', '')
            factor = 1
            if str_num.find('万') != -1:
                factor = 10000
            str_num = re.findall('[\d.]+', str_num)
            num = str_num[0]
            if factor != 1:
                num = str(int(float(num)*factor))
            total_num[keys[i]] = num
            #print total_num[keys[i]]
            i += 1
        
        return total_num
       
if __name__ == '__main__':
    ZtcOrder.get_total_num('ts-1796606')
