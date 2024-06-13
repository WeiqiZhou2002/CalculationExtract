#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : density_of_states.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:36 
@Description: 
"""
from .base_calculation import BaseCalculation
import numpy as np
from public.tools.Electronic import Spin
from public.tools.helper import parseVarray

class DensityOfStates(BaseCalculation):
    def __init__(self, file_parsers: dict):
        self.atomicCharge = None
        self.atomicMagnetization = None
        self.linearMagneticMoment = None
        super().__init__(file_parsers)

    def getTotalDos(self):
        if self.vasprunParser is not None:
            return self.vasprunParser.getTotalDos()
        elif 'doscar' in self.file_parser:
            self.file_parser['doscar'].setup()
            return self.file_parser['doscar'].getTotalDos()
        else:
            return {}

    def getPartialDos(self):
        if self.vasprunParser is not None:
            return self.vasprunParser.getPartialDos()
        elif 'doscar' in self.file_parser:
            return self.file_parser['doscar'].getPartialDos()
        else:
            return {}



    def getGapFromDos(self, energies=None):
        """
            态密度能隙
            :return
        """
        if self.vasprunParser is None:
            return {}
        child = self.vasprunParser.root.find("./calculation[last()]/dos/i[@name='efermi']")
        efermi = float(child.text)
        tdos = self.getTotalDos()
        isSpin = tdos["IsSpinPolarized"]
        number = tdos["NumberOfGridPoints"]
        Energies = tdos["Energies"]
        TdosData = tdos["TdosData"]
        energies = []
        tdosdata = []
        for t in TdosData.values():
            tdosdata.append(t)
            energies.append(Energies)  # 存储两份energy，用于自旋情况计算能隙标记
        energies = np.array(energies)
        tdosdata = np.array(tdosdata)
        energies = energies - efermi
        epcEnergy = (energies[0][-1] - energies[0][0]) / number
        epcDOS = 0.1

        if isSpin:
            index00 = -1
            index10 = -1
            index01 = index00
            index11 = index10
            for i in range(number):
                if -epcEnergy <= energies[0][i] <= epcEnergy:
                    if tdosdata[0][i] <= epcDOS:  # tdosdata数据库中存储均为非负数，判断是否为零时只需确定正方向误差即可。
                        index00 = i
                        break
                    # print("tdosdata<= epcDOS", tdosdata[0][index00])
            for i in range(number):
                if -epcEnergy <= energies[1][i] <= epcEnergy:
                    if tdosdata[1][i] <= epcDOS:
                        index10 = i
                        break
            if index00 == -1 or index10 == -1:
                return {"GapFromDOS": "Metal"}
            else:
                # print(index00, index10, index01, index11)
                #   for i in range(number):  #冗余代码
                #      print("i am here===================",i)
                #      if -epcEnergy <= energies[0][i] <= epcEnergy:
                #           index00 = i
                #          break
                for i in range(index00, len(energies[0])):
                    # print(i)
                    if tdosdata[0][i] > epcDOS:
                        index01 = i
                        break
                # for i in range(number): #冗余代码
                #    if -epcEnergy <= energies[1][i] <= epcEnergy:
                #        index1 = i
                #        break
                for i in range(index10, len(energies[0])):
                    # print(i)
                    if tdosdata[1][i] > epcDOS:
                        index11 = i
                        break
                if (energies[0][index01] < energies[1][index10]):
                    return {"GapFromDOS": "Metal"}
                elif (energies[1][index11] < energies[0][index10]):
                    return {"GapFromDOS": "Metal"}
                else:
                    gapValue = min(energies[0][index01], energies[1][index11]) - max(energies[0][index00],
                                                                                     energies[1][index10])
                    # print(index01, index11, index10, index00)
                    return {
                        "GapFromDOS": gapValue,
                        "VBMfromDOS": max(energies[0][index00], energies[1][index10]),
                        "CBMfromDOS": min(energies[0][index01], energies[1][index11])
                    }
        else:
            index0 = -1
            index1 = -1
            for i in range(number):
                if -epcEnergy <= energies[0][i] <= epcEnergy:
                    if tdosdata[0][i] <= epcDOS:
                        index0 = i
                        break
            if index0 == -1:
                return {"GapFromDOS": "Metal"}
            else:
                # for i in range(number):
                #    if -epcEnergy <= energies[0][i] <= epcEnergy:
                #        index0 = i
                #        break
                for i in range(index0, len(energies[0])):
                    if tdosdata[0][i] > epcDOS:
                        index1 = i
                        break
                gapValue = energies[0][index1] - energies[0][index0],
                # print(index0, index1)
                return {
                    "GapFromDOS": gapValue,
                    "VBMfromDOS": energies[0][index0],
                    "CBMfromDOS": energies[0][index1]
                }



    def to_bson(self):
        doc = self.basicDoc
        if self.outcarParser is not None:
            self.atomicCharge, self.atomicMagnetization = self.outcarParser.getAtomicChargeAndAtomicMagnetization()
        if self.oszicarParser is not None:
            self.linearMagneticMoment = self.oszicarParser.getLinearMagneticMoment()
        doc['ProcessData'] = {
            'ElectronicSteps': self.getElectronicSteps()
        }
        doc['Properties'] = {
            "ThermodynamicProperties": self.getThermoDynamicProperties(),
            "ElectronicProperties": {
                'AtomicCharge': self.atomicCharge,
                'TotalDos': self.getTotalDos(),
                'PartialDOS': self.getPartialDos(),
                'GapFromDOS': self.getGapFromDos()
            },
            'MagneticProperties': {
                'AtomicMagnetization': self.atomicMagnetization,
                'LinearMagneticMoment': self.linearMagneticMoment,
            }
        }
        doc['Files'] = [parser.filename for parser in self.file_parser.values()]

        return doc