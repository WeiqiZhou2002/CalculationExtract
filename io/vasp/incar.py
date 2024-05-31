#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : DataCollectionSoftware
@File       : incar.py
@IDE        : PyCharm
@Author     : zychen@cnic.cn
@Date       : 2023/9/4 11:09
@Description: Parser INCAR File
"""


class Incar:
    """
    incar file paser
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.dict = {}
        with open(self.filepath, 'r') as f:
            self.lines = f.readlines()
            for line in self.lines:
                if '=' in line:
                    line = line.split('=')
                    self.dict[line[0].strip(' ')] = line[1].strip(' ').strip('\n')
            f.close()
    def fill_parameters(self, paradict: dict):
        """
        向paradict中填充incar文件中多出的参数
        :param paradict:
        :return:
        """
        paradict = paradict
        for key in self.dict:
            if key not in paradict.keys():
                paradict[key] = self.dict[key]
        return paradict
