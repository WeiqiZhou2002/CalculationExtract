#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : poscar.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:30 
@Description: 
"""
import numpy as np
from public.tools.periodic_table import PTable
from public.composition import Composition
from public.lattice import Lattice


class Poscar:
    def __init__(self, poscarPath):
        self.poscarPath = poscarPath

        if self.poscarPath is None:
            raise ValueError('File content error, not parse!')
        with open(self.poscarPath, 'r') as f:
            self.lines = f.readlines()
        self.lattice = None
        self.composition = None
        self.volume = None
        self.numberOfSites = None
        self.ionicSteps = None
        self.electronicSteps = None
        self.thermoDynamicProperties = None
        self.hasSetup = False
        self.calculationType = None
        self.simplestFormula = None
        self.generalFormula = None
        self.numberOfElements = None
        self.spaceGroup = None
        self.pointGroup = None
        self.crystalSystem = None
        self.resourceUsage = None
        self.cellStress_s = None
        self.cellStress_e = None
        self.electronicProperties = None
        self.magneticProperties = None
        self.atomicCharge = None
        self.atomicMagnetization = None
        self.totalDos = None
        self.partialDos = None
        self.kPoints = None
        self.eigenValues = None
        self.gapFromBand = None
        self.gapFromDos = None
        self.projectedEigen = None
        self.dielectricData = None
        self.opticalProperties = None
        self.linearMagneticMoment = None
        self.elasticProperties = None

    def setup(self):
        self.lattice = self.getLattice()
        self.composition = self.getComposition()
        self.sites_s = self.getSites(isinit=True)
        self.sites_e = self.getSites(isinit=False)
        self.volume = self.getVolume()
        self.numberOfSites = self.getNumberOfSites()
        self.kPoints = self.getKPoints()

    def getComposition(self):
        elements = self.lines[5].split()
        counts = list(map(int, self.lines[6].split()))
        composition = []
        for element, count in zip(elements, counts):
            composition.append(Composition(atomic_symbol=element,
                                           atomic_number=PTable().detailed[element]["Atomic no"],
                                           atomic_mass=PTable().detailed[element]["Atomic mass"],
                                           amount=count))
        return composition

    def getLattice(self):
        matrix = [
            list(map(float, self.lines[2].split())),
            list(map(float, self.lines[3].split())),
            list(map(float, self.lines[4].split()))
        ]
        lattice = Lattice(matrix)

        return lattice

    def getVolume(self):
        matrix = np.array([
            list(map(float, self.lines[2].split())),
            list(map(float, self.lines[3].split())),
            list(map(float, self.lines[4].split()))
        ])
        vol = np.dot(matrix[0], np.cross(matrix[1], matrix[2]))
        return float(abs(vol))

    def getNumberOfSites(self):
        counts = list(map(int, self.lines[6].split()))
        number_of_sites_from_counts = sum(counts)
        return number_of_sites_from_counts
