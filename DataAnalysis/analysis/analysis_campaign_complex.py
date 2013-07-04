#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2013-05-23 11:12
@version: 1.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
if __name__ == '__main__':
    import sys
    sys.path.append('../../')
from CommonTools.report_tools import Report, MAIN_KEYS 
from DataAnalysis.db_model.shop_db import Shop 

def analysis_campaign_complex(file_name, campaign_name, nick_list=[]):
    """详细分析 某个计划"""
    
    analysis_obj = AnalysisCampaign(file_name, nick_list)
    return analysis_obj.analysis_campaign_complex(campaign_name)

class AnalysisCampaign:
    
    def __init__(self, file_name, nick_list=[]): 
        self.report_list = []
        for line in file(file_name):
            campaign = Report.parser_report(line)
            if not campaign:
                continue
            if len(nick_list) > 0:
                if campaign['nick'] not in nick_list:
                    continue
            self.report_list.append(campaign)
    
    def collect_campaigns(self, campaign_name):
        
        self.campaign_list = []
        for campaign in self.report_list:
            if campaign['campaign'] == '账户整体情况':
                shop = campaign
                continue
            if campaign['campaign'].find(campaign_name) != -1:
                if campaign['nick'] != shop['nick']:
                    print '出现不一致:',shop['nick']
                Report.add_shop(campaign, shop)
                #排除非正常 数据
                if campaign['count_days'] <= 0:
                    continue
                if campaign['multi_cost'] > campaign['shop_multi_cost'] or \
                        campaign['multi_pay'] > campaign['shop_multi_pay']:
                    continue
                self.campaign_list.append(campaign)
    
    def analysis_campaign_click(self, campaign_name):
        """流量统计"""

        self.collect_campaigns(campaign_name)
        keys = ['pv_lower_10', 'avg_pv_lower_10', 'click_lower_10', \
                'click_lower_20', 'avg_click_lower_10', 'avg_click_lower_20']
        count_dict = {}
        for key in keys:
            count_dict[key] = 0
        
        bad_num = 0
        for campaign in self.campaign_list:
            if  campaign['pv'] <= 0:
                bad_num += 1
                continue
            campaign['avg_pv'] = campaign['multi_pv'] / campaign['count_days']
            campaign['avg_click'] = campaign['multi_click'] / campaign['count_days']
            if campaign['pv'] <= 10:
                count_dict['pv_lower_10'] += 1
            if campaign['avg_pv'] <= 20:
                count_dict['avg_pv_lower_10'] += 1
            if campaign['click'] <= 10:
                count_dict['click_lower_10'] += 1
            if campaign['click'] <= 20:
                count_dict['click_lower_20'] += 1
            
            if campaign['avg_click'] <= 10:
                count_dict['avg_click_lower_10'] += 1
                print 'avg_click_lower_10: ', campaign['nick']
            if campaign['avg_click'] <= 20:
                count_dict['avg_click_lower_20'] += 1
        campaign_num = campaign_num - bad_num
        content = ''
        content += '%s pv>0的数量: %d , pv为0的数量: %d\n' % (campaign_name, campaign_num, bad_num)
        for key in keys:
            content += '%s 数量:%d, 比例:%.3f \n' % (key, count_dict[key], float(count_dict[key]) / campaign_num)
        return content

    def analysis_campaign_cost(self, campaign_name):
        """花费预算统计"""

        self.collect_campaigns(campaign_name)
        shop_status_list = Shop.get_all_normal_shop_status(2)
        shop_status_dict = {}
        for shop in shop_status_list:
            shop_status_dict[str(shop['nick'])] = shop
        
        bad_num = 0
        sum_budget = 0.0
        sum_cost_budget = 0.0 
        sum_multi_cost_budget = 0.0
        for campaign in self.campaign_list:
            shop = shop_status_dict.get(str(campaign['nick']), None)
            if not shop:
                bad_num += 1
                continue
            budget = None
            if campaign_name == '省油宝长尾计划' and shop.has_key('auto_campaign_settings'):
                budget = shop['auto_campaign_settings']['budget']
            elif campaign_name == '省油宝加力计划' and shop.has_key('key_campaign_settings'):
                budget = shop['key_campaign_settings']['budget']
            if budget:
                campaign['budget'] = budget
                campaign['cost_budget'] = campaign['cost'] / budget
                campaign['avg_cost'] = campaign['multi_cost'] / campaign['count_days']
                campaign['multi_cost_budget'] = campaign['avg_cost'] / budget
                sum_budget += campaign['budget']
                sum_cost_budget += campaign['cost_budget']
                sum_multi_cost_budget += campaign['multi_cost_budget']
            else:
                bad_num += 1
             
        campaign_num = campaign_num - bad_num
        content = ''
        content += '找到设置的计划数量: %d , 没找到: %d\n' % (campaign_num, bad_num)
        content += '预算的平均值:%d元\n' % (sum_budget / campaign_num / 100)
        content += '%s单天花费占预算的比例 平均值:%.3f\n' % \
                (campaign_name, sum_cost_budget / campaign_num)
        content += '%s日均花费占预算的比例 平均值:%.3f\n' % \
                (campaign_name, sum_multi_cost_budget / campaign_num)
        return content

    def analysis_campaign_complex(self, campaign_name):

        self.collect_campaigns(campaign_name)
        cancel_num = 0
        zero_pv = 0
        multi_zero_pv = 0
        
        multi_roi_zero = 0
        multi_roi_unzero = 0
        multi_roi_bigger_2 = 0
        
        sum_key_dict = {}
        main_keys = ['multi_cost_percent', 'multi_pay_percent']
        for key in MAIN_KEYS:
            main_keys.append(key)
            main_keys.append('shop_'+key)

        for key in main_keys:
            sum_key_dict[key] = 0
        
        daily_keys = ['multi_pv', 'multi_click', 'multi_cost', 'multi_pay', 'multi_pay_count']
        for key in daily_keys:
            sum_key_dict['daily_'+key] = 0

        multi_cost_percent_bigger_9 = 0
        multi_cost_percent_bigger_5 = 0
        click_lower_20 = 0
        avg_click_lower_20 = 0
        
        for campaign in self.campaign_list:
            if campaign['campaign'].find('CANCEL') != -1:
                cancel_num += 1
                continue
            if campaign['pv'] <= 0:
                zero_pv += 1
            elif campaign['click'] < 20:
                click_lower_20 += 1
                
            if campaign['multi_pv'] <= 0:
                multi_zero_pv += 1
            elif float(campaign['multi_click']) / campaign['count_days'] < 20:
                avg_click_lower_20 += 1
            
            for key in main_keys:
                sum_key_dict[key] += campaign[key]
            for key in daily_keys:
                sum_key_dict['daily_'+key] += float(campaign[key]) / campaign['count_days']
            
            if campaign['multi_cost_percent'] >= 0.9:
                multi_cost_percent_bigger_9 += 1
            if campaign['multi_cost_percent'] >= 0.5:
                multi_cost_percent_bigger_5 += 1

            if campaign['multi_roi'] <= 0:
                multi_roi_zero += 1
            else:
                multi_roi_unzero += 1
                if campaign['multi_roi'] >= 2:
                    multi_roi_bigger_2 += 1
        
        campaign_num = len(self.campaign_list) - cancel_num
        unzero_pv = campaign_num - zero_pv
        multi_unzero_pv = campaign_num - multi_zero_pv
        
        content = '**********'+campaign_name + ' 分析**********\n'
        content += '总计划数量：%d, 停用数量：%d\n' % (campaign_num, cancel_num)
        content += '\n----------单天报表分析----------\n'
        content += '昨日 展现为0数：%d, 占比：%.1f, 不为0数：%d\n' % (zero_pv, \
                float(zero_pv) / campaign_num, unzero_pv)
        content += '昨日 平均花费：%.1f, 平均成交额：%.1f, 平均ROI：%.1f, 平均转化率：%.3f\n' % (\
                sum_key_dict['cost'] / unzero_pv / 100, \
                sum_key_dict['pay'] / unzero_pv / 100, \
                sum_key_dict['pay'] / sum_key_dict['cost'], \
                sum_key_dict['pay_count'] / (sum_key_dict['click']+0.01))

        content += '昨日 平均展现：%d, 平均点击：%d, 平均CPC：%.1f, 平均点击率：%.3f,\n' % (\
                sum_key_dict['pv'] / unzero_pv, \
                sum_key_dict['click'] / unzero_pv, \
                sum_key_dict['cost'] / sum_key_dict['click'] / 100, \
                sum_key_dict['click'] / (sum_key_dict['pv']+0.01))
        
        content += '昨日 点击少于20 数：%d, 占比：%.3f\n' % (click_lower_20, \
                float(click_lower_20) / unzero_pv)
        
        content += '\n----------多天报表分析----------\n'
        content += '日均 展现为0数：%d, 占比：%.1f, 不为0数：%d\n' % (multi_zero_pv, \
                float(multi_zero_pv) / campaign_num, multi_unzero_pv)
        content += '日均 花费：%.1f, 日均成交额：%.1f, 日均ROI：%.1f, 日均转化率：%.3f\n' % (\
                sum_key_dict['daily_multi_cost'] / multi_unzero_pv / 100, \
                sum_key_dict['daily_multi_pay'] / multi_unzero_pv / 100, \
                sum_key_dict['daily_multi_pay'] / sum_key_dict['daily_multi_cost'],\
                sum_key_dict['daily_multi_pay_count'] / (sum_key_dict['daily_multi_click']+0.01))

        content += '日均 展现：%d, 日均点击：%d, 日均CPC：%.1f, 日均点击率：%.3f, \n' % (\
                sum_key_dict['daily_multi_pv'] / multi_unzero_pv, \
                sum_key_dict['daily_multi_click'] / multi_unzero_pv, \
                sum_key_dict['daily_multi_cost'] / sum_key_dict['daily_multi_click'] / 100, \
                sum_key_dict['daily_multi_click'] / (sum_key_dict['daily_multi_pv']+0.01))
        
        content += '日均 点击少于20 数量：%d, 占比：%.3f\n' % (avg_click_lower_20, \
                float(avg_click_lower_20) / multi_unzero_pv)
        
        content += '\n----------其他多天报表分析----------\n'
        content += 'ROI大于0数：%d,占比：%.1f，ROI大于2数：%d，占比：%.1f\n' %\
                (multi_roi_unzero, float(multi_roi_unzero) / multi_unzero_pv, \
                multi_roi_bigger_2, float(multi_roi_bigger_2) / multi_unzero_pv)

        content += '花费占全店花费比 不小于0.9的 比例：%.2f, 不小于0.5的 比例：%.2f\n' % (\
                float(multi_cost_percent_bigger_9) / multi_unzero_pv, \
                float(multi_cost_percent_bigger_5) / multi_unzero_pv)
        content += '所有计划多天花费占所有全店多天 花费的比例：%.2f,所有计划多天成交占所有全店多天成交的比例：%.2f\n\n' % \
                (sum_key_dict['multi_cost'] / sum_key_dict['shop_multi_cost'],\
                sum_key_dict['multi_pay'] / sum_key_dict['shop_multi_pay'])
       
        return content

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'input arg: file_name, campaign_name'
        exit(0)
    print analysis_campaign_complex(sys.argv[1], sys.argv[2])

