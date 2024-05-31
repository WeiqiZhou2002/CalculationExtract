#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : user_view.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:12 
@Description: 
"""

from entries.calculations import CalculateEntries
from public.calculation_type import CalType


calType = CalType.BandStructure
cal = CalculateEntries[calType]()
print(cal)

def vasp_extract(root_path: str):
    """

    :param root_path:
    :return:
    """
    # 找到所有的vasp计算文件夹
    # 遍历
    for file_path in paths:
        # 遍历文件夹，获取所有的vasp计算文件
        # 根据文件名创建 解析类，对文件进行解析
        # 保存在字典格式中 {'incar': Incar(), 'poscar': Poscar(), 'outcar': Outcar(), 'locpot': Locpot()}
        file_parsers = {}
        # 从Incar  或 Vasprun对象中获取计算类型
        calType = incar.cal_type
        # 根据计算类型创建计算对象
        cal_entry = CalculateEntries[calType](file_parsers)
        bson = cal_entry.to_bson()
        # 保存到数据库
