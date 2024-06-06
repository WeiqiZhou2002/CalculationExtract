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
import linecache

from db.mongo.mongo_client import Mongo
from entries.calculations import CalculateEntries
from i_o.vasp.chgcar import Chgcar
from i_o.vasp.doscar import Doscar
from i_o.vasp.eigenval import Eigenval
from i_o.vasp.elfcar import Elfcar
from i_o.vasp.incar import Incar
from i_o.vasp.poscar import Poscar
from i_o.vasp.kpoints import Kpoints
from i_o.vasp.outcar import Outcar
from i_o.vasp.oszicar import Oszicar
from i_o.vasp.locpot import Locpot
from i_o.vasp.procar import Procar
from i_o.vasp.vasprun import Vasprun
import os
from tqdm import tqdm

from i_o.vasp.xdatcar import Xdatcar
from public.calculation_type import CalType

input_files = {'INCAR', 'KPOINTS', 'OSZICAR', 'OUTCAR', 'POSCAR', 'vasprun.xml''XDATCAR', 'DOSCAR',
               'PROCAR', 'ELFCAR', 'CHGCAR', 'EIGENVAL'}


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
    mongo = Mongo(host=host, port=port)
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
            elif file_name.upper() == 'XDATCAR':
                file_parsers['xdatcar'] = Xdatcar(full_path)
            elif file_name.upper() == 'DOSCAR':
                file_parsers['doscar'] = Doscar(full_path)
            elif file_name.upper() == 'PROCAR':
                file_parsers['procar'] = Procar(full_path)
            elif file_name.upper() == 'ELFCAR':
                file_parsers['elfcar'] = Elfcar(full_path)
            elif file_name.upper() == 'CHGCAR':
                file_parsers['chgcar'] = Chgcar(full_path)
            elif file_name.upper() == 'EIGENVAL':
                file_parsers['eigenval'] = Eigenval(full_path)
        # 从名字或Incar 和 Vasprun对象中获取计算类型，优先名字
        parm = {}
        if 'vasprun' in file_parsers and 'incar' in file_parsers:
            parm = file_parsers['vasprun'].parameters
            parm = file_parsers['incar'].fill_parameters(parm)
        elif 'vasprun' in file_parsers:
            parm = file_parsers['vasprun'].parameters
        elif 'incar' in file_parsers:
            parm = file_parsers['incar'].fill_parameters(parm)
        else:
            raise ValueError(
                f"INCAR or vasprun.xml file is required to determine the calculation type in directory {file}")
        cal_type = CalType.from_parameters(file, collections, parm)
        # 根据计算类型创建计算对象
        cal_entry = CalculateEntries[cal_type](file_parsers)
        bson = cal_entry.to_bson()
        # 保存到数据库
        mongo.save_one(bson, database, cal_type)

    mongo.close()
    outFile.close()


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


# def getCalType(rootPath, collections, parm):
    # if len(collections) == 1:
    #     return collections[0]
    # else:
    #     name = rootPath.lower()
    #     if 'static' in name:
    #         return CalType.StaticCalculation
    #     elif 'dos' in name or 'density' in name:
    #         return CalType.DensityOfStates
    #     elif 'geometry' in name or 'scf' in name or 'optim' in name:
    #         return CalType.GeometryOptimization
    #     elif 'band' in name:
    #         return CalType.BandStructure
    #     elif 'elastic' in name:
    #         return CalType.ElasticProperties
    #     elif 'dielectric' in name:
    #         return CalType.DielectricProperties
    #
    # para_list = ['IBRION', 'LORBIT', 'LOPTICS', 'LEPSILON', 'LCALCEPS', 'ISIF', 'MAGMOM']
    # parameters = {key: parm.get(key, None) for key in para_list}
    # if parameters['IBRION'] == 1 or parameters['IBRION'] == 2 or parameters['IBRION'] == 3:
    #     return CalType.GeometryOptimization
    # if parameters['IBRION'] == -1 and linecache.getline(os.path.join(rootPath, 'KPOINTS'), 3).lower().startswith(
    #         'l'):  # kpoints generation para
    #     return CalType.BandStructure
    # if ('LOPTICS' in parameters.keys() and parameters['LOPTICS']) or parameters['IBRION'] == 7 or parameters[
    #     'IBRION'] == 8 \
    #         or (parameters['IBRION'] == 5 and (('LEPSILON' in parameters.keys() and parameters['LEPSILON']) or (
    #         'LCALCEPS' in parameters.keys() and parameters['LCALCEPS']))) \
    #         or (parameters['IBRION'] == 6 and (('LEPSILON' in parameters.keys() and parameters['LEPSILON']) or (
    #         'LCALCEPS' in parameters.keys() and parameters['LCALCEPS']))):
    #     return CalType.DielectricProperties
    # if parameters['IBRION'] == -1 and parameters['LORBIT']:
    #     return CalType.DensityOfStates
    # if parameters['IBRION'] == -1:
    #     return CalType.StaticCalculation
    # if (parameters['IBRION'] == 5 or parameters['IBRION'] == 6) and parameters['ISIF'] >= 3:
    #     return CalType.ElasticProperties
    #
    # if 'MAGMOM' in parameters.keys():
    #     return CalType.MagneticProperties
    # raise ValueError('无法判断提取类型，无法提取')
