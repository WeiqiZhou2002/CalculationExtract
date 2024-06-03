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
from public.structure import Structure

class BaseCalculation(ABC):
    def __init__(self, file_parsers: dict):
        self.structure = None
        self.file_parser = file_parsers
        if file_parsers['vasprun'] is not None:
            self.input_structure = file_parsers['vasprun'].input_structure
            self.output_structure = file_parsers['vasprun'].output_structure
        
    @abstractmethod
    def to_bson(self):
        pass
