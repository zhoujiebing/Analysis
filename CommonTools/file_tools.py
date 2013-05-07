#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Wu Liang
@contact: garcia.wul@alibaba-inc.com
@date: 2013-04-25 15:22
@version: 0.0.0
@license: Copyright alibaba-inc.com
@copyright: Copyright alibaba-inc.com

"""
import os

class FileTools:

    @classmethod
    def write_list_to_file(self, file_name, line_data):
        if os.path.isfile(file_name):
            file_obj = open(file_name, 'a')
        else:
            file_obj = open(file_name, 'w')
        
        for line in line_data:
            file_obj.write(line)
        file_obj.close()
        
if __name__ == '__main__':
    line_data = [str(i)+'\n' for i in range(10)]
    FileTools.write_list_to_file('test',line_data)
