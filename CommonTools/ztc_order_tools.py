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
from sgmllib import SGMLParser

class MySgmlParser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.label = False
        self.num_list = []

    def start_td(self, attrs):
        self.label = True

    def end_td(self):
        self.label = False

    def handle_data(self, data):
        if self.label:
            data = data.strip()
            if data.isdigit():
                self.num_list.append(int(data))

SOFT_APP = {
        '麦苗':{'page_id':678882, 'isv_id':847721042, 'app_list':['省油宝', '北斗', '麦苗淘词']},
        '点越':{'page_id':223037, 'isv_id':599244911, 'app_list':['智驾宝', '懒人开车', '魔镜看看']},
        '喜宝':{'page_id':249825, 'isv_id':669952568, 'app_list':['超级车手']},
        '派生':{'page_id':556281, 'isv_id':836440495, 'app_list':['开车精灵']},
        '世奇':{'page_id':183061, 'isv_id':499456566, 'app_list':['淘快车', '淘快词']},
        '思正':{'page_id':351841, 'isv_id':734268441, 'app_list':['疯狂标签', '疯狂海报', '疯狂排名', '疯狂车手']},
        '名传':{'page_id':690262, 'isv_id':897211958, 'app_list':['车神']},
        '万青':{'page_id':486444, 'isv_id':804767803, 'app_list':['好又快']},
        '大麦':{'page_id':387653, 'isv_id':750452133, 'app_list':['大麦优驾']},
        '将行':{'page_id':886856, 'isv_id':928006811, 'app_list':['智能淘词', '智能车手']},
        '思麦':{'page_id':298806, 'isv_id':308297792, 'app_list':['如意营销', '如意掌柜', '如意快车']},
        '聚连':{'page_id':486316, 'isv_id':804599509, 'app_list':['聚灵神']},
        '爱聚':{'page_id':1014055, 'isv_id':890019595, 'app_list':['开车宝']},
        '快云':{'page_id':965376, 'isv_id':1042417251, 'app_list':['超级快车']},
        '云贝':{'page_id':898867, 'isv_id':931059416, 'app_list':['极品飞车']},
        '比格希勃':{'page_id':1114906, 'isv_id':1132351118, 'app_list':['车道推广']},
        '三易':{'page_id':747335, 'isv_id':297838437, 'app_list':['三易店长','三易标题','三易开车']},
        '灵希':{'page_id':950568, 'isv_id':1030783172, 'app_list':['智能快车']},
        '艾德思奇':{'page_id':1013903, 'isv_id':1063488426, 'app_list':['车博士']},
        '悦淘':{'page_id':1084584, 'isv_id':1113383671, 'app_list':['定向领航员']},
        '深度':{'page_id':292220, 'isv_id':692125945, 'app_list':['百宝箱','省钱车手']},
        '奕众':{'page_id':928504, 'isv_id':1024005379, 'app_list':['领航者']},
        '泰岳':{'page_id':1030662, 'isv_id':1084621530, 'app_list':['推广王']},
        '商聪':{'page_id':182580, 'isv_id':469163586, 'app_list':['壹商宝']},
        '大唐':{'page_id':38125, 'isv_id':370702873, 'app_list':['宝贝排名专家','宝贝上下架','开车助手']},

        }

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
        '智能车手':'ts-1812500',
        '疯狂车手':'ts-1813498',
        '魔镜看看':'ts-1809313',
        '如意快车':'ts-1819813',
        '超级快车':'FW_GOODS-1834824',
        '聚灵神':'FW_GOODS-1836541',
        '开车宝':'FW_GOODS-1839667',
        '车道推广':'FW_GOODS-1841777',
        '三易开车':'ts-1808594',
        '智能快车':'FW_GOODS-1874272',
        '车博士':'FW_GOODS-1866739',
        '定向领航员':'FW_GOODS-1863421',
        '领航者':'FW_GOODS-1869087',
        '推广王':'FW_GOODS-1840738',
        '壹商宝':'FW_GOODS-1868309',
        '开车助手':'ts-12682',
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
                if not order or not order_dict.has_key(order['id_name']):
                    continue
                key = ZtcOrder.hash_ztc_order(order)
                order_dict[order['id_name']][key] = order
        return order_dict

    @classmethod
    def parser_ztc_order(self, line):
        """讲以行形式存储的 网页订单数据 转化成dict"""

        #str(key)+','+order['nick']+','+order['version']+','+order['deadline']+','+order['payTime']+'\n'
        order = {}
        line_data = line.split(',')
        if len(line_data) < 5:
            return None
        order['id_name'] = line_data[0]
        order['nick'] = line_data[1]
        order['version'] = line_data[2]
        order['deadline'] = line_data[3]
        order['payTime'] = line_data[4].replace('\n', '')
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
    def get_total_num(self, service_code):
        """获取 粗略 总数 信息"""
        url =  'http://fuwu.taobao.com/ser/detail.htm?service_code=' + service_code
        #keys 与ztc_report_tools 中的NUM_TYPE 呼应
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
            if str_num.find('少于100') != -1:
                total_num[keys[i]] = 0
                i += 1
                continue
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
    
    @classmethod
    def get_exact_num2(self):
        """获取精准 数字"""
        
        url = 'http://fuwu.taobao.com/serv/shop_index.htm?spm=0.0.0.0.PzIJIc&page_id=678882&isv_id=847721042&page_rank=2&tab_type=1'
        wp = urllib2.urlopen(url)
        content = wp.read()
        r = re.compile(r'(?s)<d>(?P<data>[\d]+)</d>')
        for m in r.finditer(content):
            v = m.group("data")
            print v.strip()
    

    @classmethod
    def get_exact_num(self, page_id, isv_id):
        """获取精准 数字"""
        
        url = 'http://fuwu.taobao.com/serv/shop_index.htm?page_id=%d&tab_type=1&isv_id=%d' % (page_id, isv_id)
        wp = urllib2.urlopen(url)
        content = wp.read()
        parser = MySgmlParser()
        parser.feed(content)
        return parser.num_list

    @classmethod
    def get_exact_num_dict(self):
        exact_num_dict = {}
        for soft in SOFT_APP.values():
            num_list = ZtcOrder.get_exact_num(soft['page_id'], soft['isv_id'])
            app_list = soft['app_list']
            print 'app_list: ', ','.join(app_list)
            print 'num_list: ', num_list
            for i in range(len(app_list)):
                app = app_list[i]
                exact_num_dict[app] = (num_list[i*2], num_list[i*2+1])
                #print '%s, %d, %d' % (app, num_list[i*2], num_list[i*2+1])
        return exact_num_dict 

if __name__ == '__main__':
    print ZtcOrder.get_exact_num(249825, 669952568)
