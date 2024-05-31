#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : geometry_optimization.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:35 
@Description: 
"""
from .base_calculation import BaseCalculation


class GeometryOptimization(BaseCalculation):
    def __init__(self, file_parsers: dict):
        super().__init__(file_parsers)
