#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : __init__.py.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/31 14:23 
@Description: 
"""

from .band_structure import BandStructure
from .static_calculation import StaticCalculation
from .geometry_optimization import GeometryOptimization
from .elastic_properties import ElasticProperties
from .magnetic_properties import MagneticProperties
from .density_of_states import DensityOfStates
from .dielectric_properties import DielectricProperties

CalculateEntries = {
    'BandStructure': BandStructure,
    'StaticCalculation': StaticCalculation,
    'GeometryOptimization': GeometryOptimization,
    'ElasticProperties': ElasticProperties,
    'MagneticProperties': MagneticProperties,
    'DensityOfStates': DensityOfStates,
    'DielectricProperties': DielectricProperties
}
