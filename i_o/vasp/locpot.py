#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : locpot.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:47 
@Description: 
"""

class Locpot:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.lines = f.readlines()
            f.close()
