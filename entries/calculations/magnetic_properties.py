#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : magnetic_properties.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:37 
@Description: 
"""
from .base_calculation import BaseCalculation


class MagneticProperties(BaseCalculation):
    def __init__(self, file_parsers: dict):
        self.atomicCharge = None
        self.atomicMagnetization = None
        self.linearMagneticMoment = None
        super().__init__(file_parsers)


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
                'AtomicCharge': self.atomicCharge
                # 'BaderCharge': None
            },
            'MagneticProperties': {
                'AtomicMagnetization': self.atomicMagnetization,
                'LinearMagneticMoment': self.linearMagneticMoment,
            },
        }
        doc['Files'] = [self.vasprunParser.vaspPath, self.file_parser['incar'].filename,
                        self.file_parser['outcar'].filename, self.file_parser['kpoint'].filename,
                        self.file_parser['oszicar'].filename]

        return doc