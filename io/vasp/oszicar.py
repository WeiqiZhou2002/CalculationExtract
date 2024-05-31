#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : DataCollectionSoftware
@File       : oszicar.py
@IDE        : PyCharm
@Author     : zychen@cnic.cn
@Date       : 2023/9/5 11:01
@Description:
"""
import os.path


class OsziCar:
    """
    解析oszicar文件
    """

    def __init__(self, filename):
        self.filename = filename

        with open(self.filename, 'r') as f:
            self.lines = f.readlines()
            f.close()

    def getLinearMagneticMoment(self):
        """
        提取线性磁矩
        TODO: 提取最后一个值还是所有值
        :return:
        """
        LinearMagneticMoment = {}
        for line in self.lines:
            line = line.strip('\n').strip(' ')
            if line.find('mag=') != -1:
                line2 = line.split('=')
                LinearMagneticMoment = float(line2[-1])
            else:
                LinearMagneticMoment = 0.
        return LinearMagneticMoment
