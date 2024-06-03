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
from abc import ABC, abstractmethod


class BaseCalculation(ABC):
    def __init__(self, file_parsers: dict):
        self.file_parser = file_parsers

    @abstractmethod
    def to_bson(self):
        pass
