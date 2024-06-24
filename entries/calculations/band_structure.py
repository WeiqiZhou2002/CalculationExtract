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
        efermi = eigenval.get('FermiEnergy', None)
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

    def getEigenData(self):
        eigen_vasprun = None
        eigen_eigen = None
        eigen_procar = None
        if self.vasprunParser is not None:
            eigen_vasprun =  self.vasprunParser.getEigenValues()
        if 'eigenval' in self.file_parser:
            eigen_eigen =  self.file_parser['eigenval'].getEigenValues()
        if 'procar' in self.file_parser:
            eigen_procar =  self.file_parser['procar'].getEigenValues()
        if eigen_vasprun is not None and eigen_eigen is not None:
            if not self.compare_with_tolerance(eigen_vasprun, eigen_eigen):
                # Handle the case where the results do not match within tolerance
                print("Warning: Mismatch between vasprun and eigenval eigenval beyond tolerance.")
                print(self.vasprunParser.filename)
                return {
                    "vasprun": eigen_vasprun,
                    "eigenval": eigen_eigen
                }
        if eigen_vasprun is not None and eigen_procar is not None:
            if not self.compare_with_tolerance(eigen_vasprun, eigen_procar):
                # Handle the case where the results do not match within tolerance
                print("Warning: Mismatch between vasprun and procar eigenval beyond tolerance.")
                print(self.vasprunParser.filename)
                return {
                    "vasprun": eigen_vasprun,
                    "procar": eigen_procar
                }
        return eigen_vasprun if eigen_vasprun is not None else (
                eigen_eigen if eigen_eigen is not None else (
                eigen_procar if eigen_procar is not None else {}))

    def getProjectedEigenvalOnIonOrbitals(self):
        projected_vasprun = None
        projected_procar = None
        if self.vasprunParser is not None:
            projected_vasprun = self.vasprunParser.getProjectedEigenvalOnIonOrbitals()
        if 'procar' in self.file_parser:
            projected_procar = self.file_parser['procar'].getProjectedEigenvalOnIonOrbitals()
        if projected_vasprun is not None and projected_procar is not None:
            if not self.compare_with_tolerance(projected_vasprun, projected_procar):
                # Handle the case where the results do not match within tolerance
                print("Warning: Mismatch between vasprun and procar projected eigenval on Ion orbitals beyond tolerance.")
                print(self.vasprunParser.filename)
                return {
                    "vasprun": projected_vasprun,
                    "procar": projected_procar
                }
        return projected_vasprun if projected_vasprun is not None else (
            projected_procar if projected_procar is not None else {})

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
                'EigenValues': self.getEigenData(),
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
