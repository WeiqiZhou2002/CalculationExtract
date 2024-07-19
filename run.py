#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : run.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:08 
@Description: 
"""
import argparse

from user_view import vasp_extract


def getArgument():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--source', default='vasp', help='data source: vasp, icsd, oqmd, materialproject, etc.')
    parser.add_argument('--root_dir', default='../test_data/39', help='calculation files root path')
    parser.add_argument('--log',action='store_true', default=False, help='if start log ')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = getArgument()
    if args.source == 'vasp':
        vasp_extract(args.root_dir, args.log)
    # 其他数据源 补充
    # elif
    # elif