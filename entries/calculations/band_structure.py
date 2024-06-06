#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : band_structure.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:35 
@Description: 
"""
from .base_calculation import BaseCalculation
import numpy as np
from public.tools.Electronic import Spin
from public.tools.helper import parseVarray


class BandStructure(BaseCalculation):
    def __init__(self, file_parsers: dict):
        self.atomicCharge = None
        self.atomicMagnetization = None
        self.linearMagneticMoment = None
        super().__init__(file_parsers)



    def getGapFromBand(self):
        """
                    能带能隙
                    :return
                """
        if self.vasprunParser is not None:
            eigenval = self.vasprunParser.getEigenValues()
        # elif 'eigenval' in self.file_parser:
        #    eigenval = self.file_parser['eigenval'].getEigenValues()
        else:
            return {}
        isSpin = eigenval["IsSpinPolarized"]
        number = eigenval["NumberOfGeneratedKPoints"]
        BandsNum = eigenval["NumberOfBand"]
        Energies = eigenval["EigenvalData"]
        Kpoints = eigenval["KPoints"]
        efermi = eigenval.get('FermiEnergy',None)
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

    def getProjectedEigenvalOnIonOrbitals(self):
        """
        提取分原子能带投影
        :return:
        """
        NumberOfGeneratedKPoints = 0
        NumberOfBand = 0
        IsSpinPolarized = False
        NumberOfIons = 0
        DecomposedLength = 0
        IsLmDecomposed = False
        KPoints = None
        Data = {}
        if self.vasprunParser is None:
            return {}
        child = self.vasprunParser.root.find("./calculation[last()]/projected/array")
        if child is None:
            return None
        KPoints = self.vasprunParser.kPoints
        NumberOfGeneratedKPoints = len(KPoints)

        fields = []
        for field in child.findall('field'):
            fields.append(field.text.strip())
        DecomposedLength = len(fields)
        IsLmDecomposed = True if DecomposedLength == 9 or DecomposedLength == 16 else False

        # 获取原数据格式
        data = []
        for s in child.find('set').findall('set'):  # spin
            spin = Spin.up if s.attrib["comment"] == "spin 1" else Spin.down
            spins = []
            for i, kpoint in enumerate(s.findall('set')):
                kpoints = []
                for j, band in enumerate(kpoint.findall('set')):
                    irons = parseVarray(band)
                    kpoints.append(irons)
                spins.append(kpoints)
            data.append(spins)
        # print(data)
        # 数据格式变换
        NumberOfIons = len(data[0][0][0])
        NumberOfBand = len(data[0][0])
        IsSpinPolarized = True if len(data) == 2 else False
        # spin -> kpoint -> band -> iron -> orbital
        # spin-> iron -> kpoint -> band -> orbital
        # 调整维度
        data_array = np.array(data)
        data_trans = np.transpose(data_array, (0, 3, 1, 2, 4))
        data = data_trans.tolist()

        # 格式保存
        for s in range(len(data)):
            spindata = []
            for i in range(NumberOfIons):
                ironsdata = []
                for j in range(NumberOfGeneratedKPoints):
                    points = []
                    for k in range(NumberOfBand):
                        bands = {}
                        for l in range(DecomposedLength):
                            bands[fields[l]] = data[s][i][j][k][l]
                        points.append(bands)
                    ironsdata.append(points)
                spindata.append(ironsdata)
            if s == 0:
                Data[Spin.up] = spindata
            elif s == 1:
                Data[Spin.down] = spindata
        return {
            "NumberOfGeneratedKPoints": NumberOfGeneratedKPoints,
            "NumberOfBand": NumberOfBand,
            "IsSpinPolarized": IsSpinPolarized,
            "NumberOfIons": NumberOfIons,
            "Decomposed": fields,
            "DecomposedLength": DecomposedLength,
            "IsLmDecomposed": IsLmDecomposed,
            "KPoints": KPoints,
            # "Data": Data
            # 数据太大，导致不能写入数据库
            "Data": {}
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
                'EigenValues': self.file_parser['eigenval'].getEigenValues(),
                'ProjectedEigenVal_on_IonOrbitals': self.getProjectedEigenvalOnIonOrbitals(),
                'GapFromBand': self.getGapFromBand()
            },
            'MagneticProperties': {
                'AtomicMagnetization': self.atomicMagnetization,
                'LinearMagneticMoment': self.linearMagneticMoment,
            }
        }
        doc['Files'] = [parser.filename for parser in self.file_parser.values()]

        return doc
