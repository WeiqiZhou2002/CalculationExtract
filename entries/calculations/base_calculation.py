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
        self.parm = {}
        if 'vasprun' in file_parsers and 'incar' in file_parsers:
            self.parm = file_parsers['vasprun'].parameters
            self.parm= file_parsers['incar'].fill_parameters(self.parm)
        elif 'vasprun' in file_parsers:
            self.parm = file_parsers['vasprun'].parameters
        elif 'incar' in file_parsers:
            self.parm = file_parsers['incar'].fill_parameters(self.parm)
        if 'kpoints' in file_parsers and 'Kpoints' not in self.parm:
            self.parm['kpoints'] = file_parsers['kpoints'].getKpoints()
        if 'vasprun' in file_parsers:
            self.vasprunParser = file_parsers['vasprun']
            self.vasprunParser.setup()
            self.input_structure = self.vasprunParser.input_structure
            self.output_structure = self.vasprunParser.output_structure

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
                'CalculationType': self.vasprunParser.calculationType,
            }
        elif 'poscar' in file_parsers and 'incar' in file_parsers:
            self.poscarParser = file_parsers['poscar']
            self.poscarParser.setup()
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
        if self.vasprunParser is not None:
            return self.vasprunParser.getElectronicSteps()
        if 'oszicar' in self.file_parser:
            para = self.parm['EDIFF']
            steps = self.file_parser['oszicar'].getElectronicSteps(para)
            return steps
        else:
            return {}

    def getThermoDynamicProperties(self):
        if self.vasprunParser is None:
            doc = {
                'TotalEnergy': 'N/A',
                'FermiEnergy': 'N/A',
                'EnergyPerAtom': 'N/A',
                'FormationEnergy': 'N/A'
            }
            return doc
        fermienergy = 0
        child = self.vasprunParser.root.find("./calculation[last()]/energy/i[@name='e_fr_energy']")
        totalenergy = float(child.text)
        numberofatoms = int(self.vasprunParser.root.find("./atominfo/atoms").text)
        if self.vasprunParser is not None:
            child = self.vasprunParser.root.find("./calculation[last()]/dos/i[@name='efermi']")
            fermienergy = float(child.text)
        elif 'outcar' in self.file_parser:
            fermienergy = self.file_parser['outcar'].getEfermi()
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
