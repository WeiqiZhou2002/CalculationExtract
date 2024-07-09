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

import os
import linecache
from public.calculation_type import CalType


class Incar:
    """
    incar file paser
    """

    def __init__(self, filepath):
        self.filename = filepath
        self.dict = {}
        self.calculationType = None
        self.kpoint_path = self.findKpointPath()
        with open(self.filename, 'r') as f:
            self.lines = f.readlines()
            for line in self.lines:
                if line.startswith('!'):
                    line = line[1:].strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    if key.startswith('#'):
                        key = key[1:].strip()
                    # value = value.split('#')[0].split('!')[0].strip()
                    value = value.split()[0].strip()
                    try:
                        value = float(value) if 'E' in value or '.' or 'e' in value else int(value)
                    except ValueError:
                        pass
                    self.dict[key] = value
            f.close()

    def findKpointPath(self):
        directory = os.path.dirname(self.filename)
        kPointPath = os.path.join(directory, 'KPOINTS')
        return kPointPath if os.path.exists(kPointPath) else None

    def getCalType(self):
        para_list = ['IBRION', 'LORBIT', 'LOPTICS', 'LEPSILON', 'LCALCEPS', 'ISIF', 'MAGMOM']
        parameters = {key: self.dict.get(key, None) for key in para_list}

        if parameters['IBRION'] in [1, 2, 3]:
            return CalType.GeometryOptimization
        if parameters['IBRION'] == -1 and parameters.get('KPOINT') and self.kpoint_path and linecache.getline(
                self.kpoint_path, 3).lower().startswith('l'):
            return CalType.BandStructure
        if ('LOPTICS' in parameters and parameters['LOPTICS']) or parameters['IBRION'] in [7, 8] or \
                (parameters['IBRION'] == 5 and (
                        'LEPSILON' in parameters and parameters['LEPSILON'] or 'LCALCEPS' in parameters and parameters[
                    'LCALCEPS'])) or \
                (parameters['IBRION'] == 6 and (
                        'LEPSILON' in parameters and parameters['LEPSILON'] or 'LCALCEPS' in parameters and parameters[
                    'LCALCEPS'])):
            return CalType.DielectricProperties
        if parameters['IBRION'] == -1 and parameters['LORBIT']:
            return CalType.DensityOfStates
        if parameters['IBRION'] == -1:
            return CalType.StaticCalculation
        if parameters['IBRION'] in [5, 6] and parameters['ISIF'] >= 3:
            return CalType.ElasticProperties
        if parameters['MAGMOM'] is not None:
            return CalType.MagneticProperties

        raise ValueError('无法判断提取类型，无法提取')

    def fill_parameters(self, paradict: dict):
        """
        向paradict中填充incar文件中多出的参数
        :param paradict:
        :return:
        """
        paradict = paradict
        if paradict is not None:
            for key in self.dict:
                if key not in paradict.keys():
                    paradict[key] = self.dict[key]
        else:
            paradict=self.dict
        return paradict
