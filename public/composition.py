#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : composition.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:38 
@Description: 
"""
from monty.json import MSONable


class Composition(MSONable):
    def __init__(self, atomic_symbol, atomic_number, atomic_mass, amount):
        self.atomic_symbol = atomic_symbol
        self.atomic_number = atomic_number
        self.atomic_mass = atomic_mass
        self.amount = amount

    def as_dict(self) -> dict:
        return {
            "AtomicSymbol": self.atomic_symbol,
            "AtomicNumber": self.atomic_number,
            "AtomicMass": self.atomic_mass,
            "Amount": self.amount
        }