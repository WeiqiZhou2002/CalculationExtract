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
        LinearMagneticMoment = 0.
        for line in self.lines:
            line = line.strip('\n').strip(' ')
            if line.find('mag=') != -1:
                line2 = line.split('=')
                LinearMagneticMoment = float(line2[-1])
        return LinearMagneticMoment

    def getElectronicSteps(self, EDIFF):
        electronicSteps = []
        energys = []
        totalenergydiffs = []
        first = True
        for line in self.lines:
            if re.match(r'^[A-Za-z]{3}', line):
                parts = re.split(r'\s+', line.strip())
                if int(parts[1]) == 1 and not first:
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
                energy = float(parts[2])
                energys.append(energy)
                totalenergydiffs.append(float(parts[3]))
                first = False

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
        ionSteps = {}
        energies = []
        totalenergydiffs = []
        for line in self.lines:
            if re.match(r'^\s*\d+\s+F', line):
                parts = re.split(r'\s+|=', line.strip())
                total_energy = float(parts[3])  # Extracting value after 'F='
                energy_diff = float(parts[10])  # Extracting value after 'dE='
                energies.append(total_energy)
                totalenergydiffs.append(energy_diff)
        ionSteps['TotalEnergy'] = energies
        ionSteps['TotalEnergyDiff'] = totalenergydiffs
        return ionSteps
