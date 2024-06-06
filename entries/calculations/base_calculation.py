#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : base_calculation.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/31 14:25 
@Description: 
"""
from abc import ABC, abstractmethod
from public.tools.Electronic import Spin
from public.tools.helper import parseVarray
import numpy as np

from public.tools.periodic_table import PTable


class BaseCalculation(ABC):
    def __init__(self, file_parsers: dict):
        self.structure = None
        self.file_parser = file_parsers
        self.parm = None
        self.vasprunParser = None
        if 'outcar' in file_parsers:
            self.outcarParser = file_parsers['outcar']
        else:
            self.outcarParser = None
        if 'vasprun' in file_parsers:
            self.vasprunParser = file_parsers['vasprun']
            self.vasprunParser.setup()
            self.input_structure = self.vasprunParser.input_structure
            self.output_structure = self.vasprunParser.output_structure
            self.parm = self.vasprunParser.parameters
            if 'incar' in file_parsers:
                self.parm = file_parsers['incar'].fill_parameters(self.parm)
            self.basicDoc = {
                'InputStructure': self.input_structure.to_bson(),
                'OutputStructure': self.output_structure.to_bson(),
                'Parameters': self.parm,
                'Software': self.vasprunParser.software,
                'StartTime': self.vasprunParser.startTime,
                'ResourceUsage': self.outcarParser.getResourceUsage(),
                'ProcessData': {},
                'Properties': {},
                'Files': [],
                'CalculationType': self.vasprunParser.calculationType
            }
            self.parm = self.vasprunParser.parameters
        elif 'poscar' in file_parsers and 'incar' in file_parsers:
            self.poscarParser = file_parsers['poscar']
            self.poscarParser.setup()
            self.parm = file_parsers['incar'].fill_parameters(self.parm)
            self.input_structure = self.poscarParser.structure
            self.basicDoc = {
                'InputStructure': self.input_structure.to_bson(),
                'OutputStructure': {},
                'Parameters': self.parm,
                'ResourceUsage': self.outcarParser.getResourceUsage(),
                'ProcessData': {},
                'Properties': {},
                'Files': [],
                'CalculationType': file_parsers['incar'].getCalType()
            }
        else:
            raise ValueError("不可同时无vasprun或poscar和incar")

        if 'oszicar' in file_parsers:
            self.oszicarParser = file_parsers['oszicar']
        else:
            self.oszicarParser = None



    def getElectronicSteps(self):
        electronicSteps = []
        if self.vasprunParser is None:
            return electronicSteps
        for child in self.vasprunParser.root:
            if child.tag == 'calculation':
                energys = []
                cputimes = []
                totalenergydiffs = []
                for child2 in child:
                    if child2.tag == 'scstep':
                        for child3 in child2:
                            if child3.attrib == {'name': 'total'}:
                                times = child3.text.split()
                                if len(times) == 1:
                                    times = times[0]
                                    times = [times[: times.find('.') + 3], times[times.find('.') + 3:]]
                                if '*' in times[1]:
                                    cputime = 'NAN'
                                else:
                                    cputime = float(times[1])
                                cputimes.append(cputime)
                            if child3.tag == 'energy':
                                for child4 in child3:
                                    if child4.attrib == {'name': 'e_fr_energy'}:
                                        energy = float(child4.text)
                                        energys.append(energy)

                energy_pre = 0.0
                for energy in energys:
                    totalenergydiffs.append(energy - energy_pre)
                    energy_pre = energy

                para = self.parm['EDIFF']
                if para >= totalenergydiffs[-1]:
                    eleconvergency = True
                else:
                    eleconvergency = False
                doc = {
                    'TotalEnergy': energys,
                    'EleStepCpuTime': cputimes,
                    'TotalEnergyDiff': totalenergydiffs,
                    'EleConvergency': eleconvergency
                }
                electronicSteps.append(doc)
        return electronicSteps

    def getThermoDynamicProperties(self):
        if self.vasprunParser is None:
            doc = {
                'TotalEnergy': 'N/A',
                'FermiEnergy': 'N/A',
                'EnergyPerAtom': 'N/A',
                'FormationEnergy': 'N/A'
            }
            return doc
        child = self.vasprunParser.root.find("./calculation[last()]/energy/i[@name='e_fr_energy']")
        totalenergy = float(child.text)
        child = self.vasprunParser.root.find("./calculation[last()]/dos/i[@name='efermi']")
        numberofatoms = int(self.vasprunParser.root.find("./atominfo/atoms").text)
        fermienergy = float(child.text)
        energyPerAtom = totalenergy / numberofatoms
        formation_energy = 0.0
        composition = self.vasprunParser.composition
        energy_atoms = 0.
        for comp in composition:
            if comp.atomic_symbol in PTable().atom_energy:
                energy_atoms += PTable().atom_energy[comp.atomic_symbol] * comp.amount
            else:
                energy_atoms = 0.
                break
        if energy_atoms != 0.:
            formation_energy = (totalenergy - energy_atoms) / self.vasprunParser.numberOfSites

        doc = {
            'TotalEnergy': totalenergy,
            'FermiEnergy': fermienergy,
            'EnergyPerAtom': energyPerAtom,
            'FormationEnergy': formation_energy
        }
        return doc

    @abstractmethod
    def to_bson(self):
        pass
