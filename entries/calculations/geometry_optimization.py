#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : geometry_optimization.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:35 
@Description: 
"""
from public.lattice import Lattice
from public.structure import Structure
from .base_calculation import BaseCalculation
import numpy as np



class GeometryOptimization(BaseCalculation):
    def __init__(self, file_parsers: dict):

        super().__init__(file_parsers)


    def getIonicSteps(self):
        if self.vasprunParser is not None:
            return self.vasprunParser.getIonicSteps()
        elif 'oszicar' in self.file_parser:
            return self.file_parser['oszicar'].getIonicSteps()
        else:
            return {}

    def getGapFromBand(self):
        """
                    能带能隙
                    :return
                """
        if self.vasprunParser is not None:
            eigenval = self.vasprunParser.getEigenValues()
        elif 'eigenval' in self.file_parser:
            eigenval = self.file_parser['eigenval'].getEigenValues()
        else:
            return {}
        isSpin = eigenval["IsSpinPolarized"]
        number = eigenval["NumberOfGeneratedKPoints"]
        BandsNum = eigenval["NumberOfBand"]
        Energies = eigenval["EigenvalData"]
        Kpoints = eigenval["KPoints"]
        if self.vasprunParser is not None:
            efermi = eigenval["FermiEnergy"]
        elif 'outcar' in self.file_parser:
            efermi = self.file_parser['outcar'].getEfermi()
        energies = []
        kpoints = []
        for t in Energies.values():
            energies.append(t)
            kpoints.append(Kpoints)  # 存储两份kpoints，用于自旋情况计算能隙标记
        energies = np.array(energies)
        # print(energies)
        energies = energies - efermi
        # print(kpoints)

        if isSpin:
            index00 = []
            index10 = []
            index01 = []
            index11 = []
            vbmE0 = []  # cbm data
            cbmE0 = []  # vbm data
            vbmE1 = []  # cbm data
            cbmE1 = []  # vbm data
            kindex0 = -1
            kindex1 = -1
            for i in range(BandsNum):
                if min(energies[0][i]) * max(energies[0][i]) < 0:
                    return {"GapFromBand": "Metal"}
                else:
                    if min(energies[0][i]) < 0.0 or min(energies[0][i]) == 0.0:  # below fermi
                        for j in range(number):
                            if energies[0][i][j] == max(energies[0][i]):
                                index00.append(j)
                                vbmE0.append(energies[0][i][j])
                                # print("the vbm band number is :", i, "kpints is :", kpoints[0][j], "energy is :",
                                #       energies[0][i][j])
                    else:  # above fermi
                        for j in range(number):
                            if energies[0][i][j] == min(energies[0][i]):
                                index01.append(j)
                                cbmE0.append(energies[0][i][j])
                                # print("the cbm band number is :", i, "kpints is :", kpoints[0][j], "energy is :",
                                #       energies[0][i][j])
                    # print(index00, index01)

                if min(energies[1][i]) * max(energies[1][i]) < 0:
                    return {"GapFromBand": "Metal"}
                else:
                    if min(energies[1][i]) < 0.0 or min(energies[1][i]) == 0.0:  # below fermi
                        for j in range(number):
                            if energies[1][i][j] == max(energies[1][i]):
                                index10.append(j)
                                vbmE1.append(energies[1][i][j])
                                # print("the vbm band number is :", i, "kpints is :", kpoints[1][j], "energy is :",
                                #       energies[1][i][j])
                    else:  # above fermi
                        for j in range(number):
                            if energies[1][i][j] == min(energies[1][i]):
                                index11.append(j)
                                cbmE1.append(energies[1][i][j])
                                # print("the cbm band number is :", i, "kpints is :", kpoints[1][j], "energy is :",
                                #       energies[1][i][j])

            if min(cbmE0) < min(cbmE1):
                cbmEnergy = min(cbmE0)
                kindex1 = cbmE0.index(cbmEnergy)
            else:
                cbmEnergy = min(cbmE1)
                kindex1 = cbmE1.index(cbmEnergy)
            if max(vbmE0) < max(vbmE1):
                vbmEnergy = max(vbmE1)
                kindex0 = vbmE1.index(vbmEnergy)
            else:
                vbmEnergy = max(vbmE0)
                kindex0 = vbmE0.index(vbmEnergy)

            gapValue = cbmEnergy - vbmEnergy
            if kindex0 == kindex1:
                gaptype = "direct gap"
            else:
                gaptype = "indirect gap"
            return {
                "GapFromBand": gapValue,
                "GapType": gaptype,
                "VBMFromBand": vbmEnergy,
                "CBMFromBand": cbmEnergy
            }
        else:
            index00 = []
            index01 = []
            vbmE0 = []  # cbm data
            cbmE0 = []  # vbm data
            kindex0 = -1
            kindex1 = -1
            for i in range(BandsNum):
                if min(energies[0][i]) * max(energies[0][i]) < 0:
                    return {"GapFromBand": "Metal"}
                else:
                    if min(energies[0][i]) < 0.0 or min(energies[0][i]) == 0.0:  # below fermi
                        for j in range(number):
                            if energies[0][i][j] == max(energies[0][i]):
                                index00.append(j)
                                vbmE0.append(energies[0][i][j])
                                # print("the vbm band number is :", i, "kpints is :", kpoints[0][j], "energy is :",
                                #       energies[0][i][j])
                    else:  # above fermi
                        for j in range(number):
                            if energies[0][i][j] == min(energies[0][i]):
                                index01.append(j)
                                cbmE0.append(energies[0][i][j])
                                # print("the cbm band number is :", i, "kpints is :", kpoints[0][j], "energy is :",
                                #       energies[0][i][j])
                    # print(index00, index01)

            cbmEnergy = min(cbmE0)
            kindex1 = cbmE0.index(cbmEnergy)
            vbmEnergy = max(vbmE0)
            kindex0 = vbmE0.index(vbmEnergy)
            gapValue = cbmEnergy - vbmEnergy
            if kindex0 == kindex1:
                gaptype = "direct gap"
            else:
                gaptype = "indirect gap"
            return {
                "GapFromBand": gapValue,
                "GapType": gaptype,
                "VBMFromBand": vbmEnergy,
                "CBMFromBand": cbmEnergy
            }


    def to_bson(self):
        doc = self.basicDoc
        doc['ProcessData'] = {
            'IonicSteps': self.getIonicSteps(),
            'ElectronicSteps': self.getElectronicSteps()
        }
        doc['Properties'] = {
            'GapFromGeo': self.getGapFromBand()  # TODO: gapFromGeo的计算方法和gapFromBand一样？
        }
        doc['Files'] = [parser.filename for parser in self.file_parser.values()]

        return doc
