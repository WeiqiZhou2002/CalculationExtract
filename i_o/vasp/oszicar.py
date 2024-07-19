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
import re


class Oszicar:
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
        if not self.lines:
            return {}
        LinearMagneticMoment = 0.
        for line in self.lines:
            line = line.strip('\n').strip(' ')
            if 'mag=' in line:
                # 找到 mag= 的位置
                start_index = line.find('mag=') + len('mag=')
                # 提取紧随其后的值
                values_str = line[start_index:].strip()
                values = values_str.split()
                if values:
                    LinearMagneticMoment = float(values[0])
                    break  # 只需要提取第一个 mag 值
        return LinearMagneticMoment

    def getElectronicSteps(self, EDIFF):
        if not self.lines:
            return {}
        electronicSteps = []
        energys = []
        totalenergydiffs = []

        first = True
        for line in self.lines:
            if re.match(r'^[A-Za-z]{3}', line):
                parts = re.split(r'\s+', line.strip())
                if '*' not in parts[1] and int(parts[1]) == 1 and not first:
                    if EDIFF >= totalenergydiffs[-1]:
                        eleconvergency = True
                    else:
                        eleconvergency = False
                    doc = {
                        'TotalEnergy': energys,
                        'TotalEnergyDiff': totalenergydiffs,
                        'EleConvergency': eleconvergency
                    }
                    electronicSteps.append(doc)
                    energys = []
                    totalenergydiffs = []
                try:
                    energy = float(parts[2])
                except ValueError as e:
                    energy = None
                energys.append(energy)
                try:
                    total = float(parts[3])
                except ValueError as e:
                    total = None
                totalenergydiffs.append(total)
                first = False

        if not totalenergydiffs:
            return {}
        else:
            if EDIFF >= totalenergydiffs[-1]:
                eleconvergency = True
            else:
                eleconvergency = False

        doc = {
            'TotalEnergy': energys,
            'TotalEnergyDiff': totalenergydiffs,
            'EleConvergency': eleconvergency
        }
        electronicSteps.append(doc)

        return electronicSteps

    def getIonicSteps(self):
        if not self.lines:
            return {}
        ionSteps = {}
        energies = []
        totalenergydiffs = []
        for line in self.lines:
            if re.match(r'^\s*\d+\s+F', line):
                parts = re.split(r'\s+|=', line.strip())
                try:
                    total_energy = float(parts[3])  # Extracting value after 'F='
                except ValueError as e:
                    total_energy = "N/A"
                try:
                    energy_diff = float(parts[10])  # Extracting value after 'dE='
                except ValueError as e:
                    energy_diff = "N/A"
                energies.append(total_energy)
                totalenergydiffs.append(energy_diff)
        ionSteps['TotalEnergy'] = energies
        ionSteps['TotalEnergyDiff'] = totalenergydiffs
        return ionSteps
