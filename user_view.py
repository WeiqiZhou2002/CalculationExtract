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
import sys
import time

from db.mongo.mongo_client import Mongo
from entries.calculations import CalculateEntries
from i_o.vasp.incar import Incar
from i_o.vasp.poscar import Poscar
from i_o.vasp.kpoints import Kpoints
from i_o.vasp.outcar import Outcar
from i_o.vasp.oszicar import Oszicar
from i_o.vasp.locpot import Locpot
from i_o.vasp.vasprun import Vasprun
import os
from tqdm import tqdm

from public.calculation_type import CalType

input_files = {'INCAR', 'KPOINTS', 'OSZICAR', 'OUTCAR', 'POSCAR', 'vasprun.xml'}


def vasp_extract(root_path: str, log):
    """

    :param root_path:
    :return:
    """
    print(os.getcwd())
    s = time.strftime("%Y-%m-%d_%H_%M_%S")
    print('Vasp files extraction task start ..........')

    database = input('please input database name: (default: VaspData)')
    if database == '':
        database = 'VaspData'
    collections = []
    collections_all = [CalType.BandStructure, CalType.StaticCalculation, CalType.GeometryOptimization,
                       CalType.DensityOfStates, CalType.DielectricProperties, CalType.ElasticProperties,
                       CalType.MagneticProperties]
    collect = input(
        'please select collections: \n1.BandStructure, \n2.StaticCalculation, \n3.GeometryOptimization, \n4.DensityOfStates, \n5.DielectricProperties, \n6.ElasticProperties, \n7.MagneticProperties.\n input nums（1 2 4）')
    if collect == '':
        collections = collections_all
    else:
        for i in collect.split():
            collections.append(collections_all[int(i) - 1])
    host = input('please input db host: (default localhost)')
    if host == '':
        host = 'localhost'
    port = input('please input db port: (default 27017)')
    if port == '':
        port = '27017'
    port = int(port)
    user = input('please input source user: (default: vasp)')
    if user == '':
        user = 'vasp'
    group = input(f'please input source user group: (default: {user})')
    if group == '':
        group = user
    file_list = findPaths(root_path)
    print('Files Dir：', root_path)
    print('Files Number：', len(file_list))
    print('User：', user)
    print('Group：', group)
    print('Database：', database)
    print('Collections：', collections)
    print('host & port：', host, ' ', port)
    error_files = {'no_take': [], 'error': []}
    if log:
        outfile_path = os.path.join(os.getcwd(), 'log', database + '_' + user + '_' + group + '_' + s + '.txt')
        outFile = open(outfile_path, 'w', encoding='utf8')
    else:
        outFile = sys.stdout
    # 找到所有的vasp计算文件夹
    file_list = findPaths(root_path)
    for file in tqdm(file_list, total=len(file_list)):
        # 遍历文件夹，获取所有的vasp计算文件
        # 根据文件名创建 解析类，对文件进行解析
        # 保存在字典格式中 {'incar': Incar(), 'poscar': Poscar(), 'outcar': Outcar(), 'locpot': Locpot()}
        file_parsers = {}
        # 遍历目录中所有文件
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
            elif file_name.upper() == 'KPOINTS':
                file_parsers['kpoints'] = Kpoints(full_path)
            elif file_name.upper() == 'OSZICAR':
                file_parsers['oszicar'] = Oszicar(full_path)
        # 从Incar  或 Vasprun对象中获取计算类型，优先vasprun
        if 'vasprun' in file_parsers:
            cal_type = file_parsers['vasprun'].getCalType()
        elif 'incar' in file_parsers:
            cal_type = file_parsers['incar'].getCalType()
        else:
            raise ValueError(
                f"INCAR or vasprun.xml file is required to determine the calculation type in directory {file}")

        # 根据计算类型创建计算对象
        cal_entry = CalculateEntries[cal_type](file_parsers)
        bson = cal_entry.to_bson()
        # 保存到数据库
        mongo = Mongo(host=host,port=port,db=database,collection=cal_type)
        # to_mongo
        mongo.save_one(bson)


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
