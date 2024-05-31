#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : base_calculation.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/31 14:25 
@Description: 
"""


class BaseCalculation:
    def __init__(self, file_parsers: dict):
        self.file_parser = file_parsers
