#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : static_calculation.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:34 
@Description: 
"""
from public.tools.periodic_table import PTable
from .base_calculation import BaseCalculation


class StaticCalculation(BaseCalculation):
    def __init__(self, file_parsers: dict):
        self.atomicCharge = None
        self.atomicMagnetization = None
        self.linearMagneticMoment = None
        super().__init__(file_parsers)

    def getThermoDynamicProperties(self):
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
            'ThermodynamicProperties': self.getThermoDynamicProperties(),
            'ElectronicProperties': {
                'AtomicCharge': self.atomicCharge,
                # 'BaderCharge': '',
                # 'GapFromXXX': '',  # TODO 如何提取 Static gap value
            },
            'MagneticProperties': {
                'AtomicMagnetization': self.atomicMagnetization,
                'LinearMagneticMoment': self.linearMagneticMoment
            }
        }
        doc['Files'] = [self.vasprunParser.vaspPath, self.file_parser['incar'].filepath,
                        self.file_parser['outcar'].filepath, self.file_parser['kpoint'].filepath,
                        self.file_parser['oszicar'].filepath]

        return doc
