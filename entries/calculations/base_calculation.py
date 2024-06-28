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
        ele_vasprun = None
        para = self.parm['EDIFF']
        ele_oszicar = None
        if self.vasprunParser is not None:
            ele_vasprun = self.vasprunParser.getElectronicSteps()
        if 'oszicar' in self.file_parser:
            ele_oszicar = self.file_parser['oszicar'].getElectronicSteps(para)
        if ele_vasprun is not None and ele_oszicar is not None:
            if not self.compare_with_tolerance(ele_vasprun, ele_oszicar):
                # Handle the case where the results do not match within tolerance
                print("Warning: Mismatch between vasprun and oszicar electronic steps beyond tolerance.")
                print(self.vasprunParser.filename)
                return {
                    "vasprun": ele_vasprun,
                    "oszicar": ele_oszicar
                }
        return ele_vasprun if ele_vasprun is not None else (
            ele_oszicar if ele_oszicar is not None else {})

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
            if child is not None:
                fermienergy = float(child.text)
            elif 'outcar' in self.file_parser:
                fermienergy = self.file_parser['outcar'].getEfermi()
        if fermienergy == 0:
            return {
                'TotalEnergy': 'N/A',
                'FermiEnergy': 'N/A',
                'EnergyPerAtom': 'N/A',
                'FormationEnergy': 'N/A'
            }
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

    def compare_with_tolerance(self, value1, value2, tolerance=0.1):
        return True
        # if isinstance(value1, dict) and isinstance(value2, dict):
        #     return self.compare_dicts_with_tolerance(value1, value2, tolerance)
        # elif isinstance(value1, list) and isinstance(value2, list):
        #     return self.compare_lists_with_tolerance(value1, value2, tolerance)
        # elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
        #     return abs(value1 - value2) <= tolerance
        # else:
        #     return value1 == value2


    def compare_dicts_with_tolerance(self, dict1, dict2, tolerance=0.1):
        common_keys = set(dict1.keys()).intersection(set(dict2.keys()))

        for key in common_keys:
            value1, value2 = dict1[key], dict2[key]
            if isinstance(value1, dict) and isinstance(value2, dict):
                if not self.compare_dicts_with_tolerance(value1, value2, tolerance):
                    return False
            elif isinstance(value1, list) and isinstance(value2, list):
                return self.compare_lists_with_tolerance(value1, value2, tolerance)
            elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                if abs(value1 - value2) > tolerance:
                    return False
            else:
                if value1 != value2:
                    return False

        return True

    def compare_lists_with_tolerance(self, list1, list2, tolerance=0.1):
        if len(list1) != len(list2):
            return False

        for item1, item2 in zip(list1, list2):
            if isinstance(item1, dict) and isinstance(item2, dict):
                if not self.compare_dicts_with_tolerance(item1, item2, tolerance):
                    return False
            elif isinstance(item1, (int, float)) and isinstance(item2, (int, float)):
                if abs(item1 - item2) > tolerance:
                    return False
            elif isinstance(item1, list) and isinstance(item2, list):
                return self.compare_lists_with_tolerance(item1, item2, tolerance)
            else:
                if item1 != item2:
                    return False

        return True
    @abstractmethod
    def to_bson(self):
        pass
