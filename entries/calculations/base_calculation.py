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
        self.file_parser = file_parsers
        if file_parsers['vasprun'] is not None:
            self.lattice_init = file_parsers['vasprun'].lattice_init
            self.lattice_final = file_parsers['vasprun'].lattice_final
            self.composition = file_parsers['vasprun'].composition
            self.sites_init = file_parsers['vasprun'].sites_init
            self.sites_final = file_parsers['vasprun'].sites_final


    @abstractmethod
    def to_bson(self):
        pass
