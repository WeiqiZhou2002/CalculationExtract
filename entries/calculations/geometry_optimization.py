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
        ionicsteps = {}
        sites = self.vasprunParser.sites_e
        sites_new = []
        lattice = None
        structures = []
        all_forces = []
        stresses = []
        energy_next = 0.0
        energys = []
        cputimes = []
        totalenergydiffs = []
        for child in self.vasprunParser.root:
            if child.tag == 'calculation':
                for child2 in child:
                    if child2.tag == 'structure':
                        for child3 in child2:
                            if child3.tag == 'crystal':
                                a = child3[0][0].text.split()
                                a = [float(i) for i in a]
                                b = child3[0][1].text.split()
                                b = [float(i) for i in b]
                                c = child3[0][2].text.split()
                                c = [float(i) for i in c]
                                lattice = Lattice([a, b, c])
                            if child3.tag == 'varray':
                                i = 0
                                sites_new = []
                                for site in sites:
                                    coords = [float(i) for i in child3[i].text.split()]
                                    site.coords = coords
                                    sites_new.append(site)
                                    i += 1
                        composition = self.vasprunParser.composition
                        structure = Structure(lattice=lattice, composition=composition, sites=sites_new)
                        structure.setup()
                        structure_doc = structure.to_bson()
                        structures.append(structure_doc)
                    if child2.attrib == {'name': 'forces'}:
                        i = 0
                        forces = []
                        for child3 in child2:
                            force = {'Force': [float(x) for x in child3.text.split()],
                                     'Atom': {
                                         'AtomicSymbol': sites[i].atom.atomicsymbol,
                                         'AtomicNumber': sites[i].atom.atomicnumber,
                                         'AtomicMass': sites[i].atom.atomicmass
                                     }
                                     }
                            forces.append(force)
                            i += 1
                        all_forces.append(forces)
                    if child2.attrib == {'name': 'stress'}:
                        a = [float(i) for i in child2[0].text.split()]
                        b = [float(i) for i in child2[1].text.split()]
                        c = [float(i) for i in child2[2].text.split()]
                        stress = [a, b, c]
                        stresses.append(stress)
                    if child2.tag == 'energy':
                        for child3 in child2:
                            if child3.attrib == {'name': 'e_fr_energy'}:
                                energy_now = float(child3.text)
                                energys.append(energy_now)
                    if child2.tag == 'time':
                        cputime = float(child2.text.split()[1])
                        cputimes.append(cputime)
        ionicsteps['TotalEnergy'] = energys
        ionicsteps['IonStepCpuTime'] = cputimes
        ionicsteps['StepStructure'] = structures
        ionicsteps['StepForces'] = all_forces
        ionicsteps['StepStress'] = stresses

        energy_pre = 0.0
        for energy in energys:
            totalenergydiffs.append(energy - energy_pre)
            energy_pre = energy

        ionicsteps['TotalEnergyDiff'] = totalenergydiffs
        para = self.parm['EDIFFG']
        if para >= 0:
            if totalenergydiffs[-1] <= para:
                ionicsteps['IonConvergency'] = True
            else:
                ionicsteps['IonConvergency'] = False
        else:
            ionicsteps['IonConvergency'] = True
            for line in all_forces[-1]:
                for ele in line['Force']:
                    if abs(ele) > abs(para):
                        ionicsteps['IonConvergency'] = False
        return ionicsteps


    def getGapFromBand(self):
        """
                    能带能隙
                    :return
                """
        eigenval = self.vasprunParser.eigenValues
        if eigenval is None:
            eigenval = self.getEigenValues()
        isSpin = eigenval["IsSpinPolarized"]
        number = eigenval["NumberOfGeneratedKPoints"]
        BandsNum = eigenval["NumberOfBand"]
        Energies = eigenval["EigenvalData"]
        Kpoints = eigenval["KPoints"]
        efermi = eigenval["FermiEnergy"]
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
        doc['Files'] = [self.vasprunParser.vaspPath, self.file_parser['incar'].filepath,
                        self.file_parser['outcar'].filepath, self.file_parser['kpoint'].filepath]

        return doc
