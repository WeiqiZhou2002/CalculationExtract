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
from io.vasp.incar import Incar
from io.vasp.poscar import Poscar
from io.vasp.kpoints import Kpoints
from io.vasp.outcar import Outcar
from io.vasp.oszicar import Oszicar
from io.vasp.locpot import Locpot
from io.vasp.vasprun import Vasprun
import os
from tqdm import tqdm


calType = CalType.BandStructure
cal = CalculateEntries[calType]()
print(cal)
input_files = {'INCAR', 'KPOINT', 'OSZICAR', 'OUTCAR', 'POSCAR', 'vasprun.xml'}

def vasp_extract(root_path: str):
    """

    :param root_path:
    :return:
    """
    # 找到所有的vasp计算文件夹
    file_list = findPaths(root_path)
    for file in tqdm(file_list, total=len(file_list)):
        # 遍历文件夹，获取所有的vasp计算文件
        # 根据文件名创建 解析类，对文件进行解析
        # 保存在字典格式中 {'incar': Incar(), 'poscar': Poscar(), 'outcar': Outcar(), 'locpot': Locpot()}
        file_parsers = {}
        #遍历目录中所有文件
        for file_name in os.listdir(file):
            full_path = os.path.join(file, file_name)
            if file_name.upper() == 'INCAR':
                file_parsers['incar'] = Incar(full_path)
            elif file_name.upper() == 'POSCAR':
                file_parsers['poscar'] = Poscar(full_path)
            elif file_name.upper() == 'OUTCAR':
                file_parsers['outcar'] = Outcar(full_path)
            elif file_name.upper() == 'LOCPOT':
                file_parsers['locpot'] = Locpot(full_path)
            elif file_name.lower() == 'vasprun.xml':
                file_parsers['vasprun'] = Vasprun(full_path)
            elif file_name.upper() == 'KPOINT':
                file_parsers['kpoints'] = Kpoints(full_path)
            elif file_name.upper() == 'OSZICAR':
                file_parsers['oszicar'] = Oszicar(full_path)
        # 从Incar  或 Vasprun对象中获取计算类型
        if 'incar' in file_parsers:
            cal_type = file_parsers['incar'].cal_type()
        elif 'vasprun' in file_parsers:
            cal_type = file_parsers['vasprun'].cal_type()
        else:
            raise ValueError(
                f"INCAR or vasprun.xml file is required to determine the calculation type in directory {file}")

        # 根据计算类型创建计算对象
        cal_entry = CalculateEntries[calType](file_parsers)
        bson = cal_entry.to_bson()
        # 保存到数据库

def findPaths(rootPath):
    total_path = []
    file_list = os.listdir(rootPath)
    if not input_files.intersection(file_list):
        for file in file_list:
            if os.path.isdir(os.path.join(rootPath, file)):
                paths = findPaths(os.path.join(rootPath, file))
                for path in paths:
                    total_path.append(path)
    else:
        total_path.append(rootPath)
        for file in file_list:
            if os.path.isdir(os.path.join(rootPath, file)):
                paths = findPaths(os.path.join(rootPath, file))
                for path in paths:
                    total_path.append(path)
    return total_path
