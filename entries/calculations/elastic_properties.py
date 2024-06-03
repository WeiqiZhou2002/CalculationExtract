#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : elastic_properties.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:36 
@Description: 
"""
from public.lattice import Lattice
from public.structure import Structure
from .base_calculation import BaseCalculation



class ElasticProperties(BaseCalculation):
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

    def to_bson(self):
        doc = self.basicDoc
        doc['ProcessData'] = {
            'IonicSteps': self.getIonicSteps(),
            'ElectronicSteps': self.getElectronicSteps()
        }
        doc['Properties'] = {
            'ElasticProperties': self.outcarParser.getElasticProperties()
        }
        doc['Files'] = [self.vasprunParser.vaspPath, self.file_parser['incar'].filepath,
                        self.file_parser['outcar'].filepath, self.file_parser['kpoint'].filepath,
                        self.file_parser['oszicar'].filepath]

        return doc
