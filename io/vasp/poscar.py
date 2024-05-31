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
import math
import os.path
import time
import xml.etree.cElementTree as ET
import numpy as np

from public.periodic_table import PTable
from public.lattice import Lattice
from public.sites import Site
from public.composition import Composition
class PoscarParser:
    def __init__(self, poscarPath, collections):
        self.vaspPath = poscarPath
        self.collections = collections

        if self.poscarPath is None:
            raise ValueError('File content error, not parse!')
        with open(self.poscarPath, 'r') as f:
            self.lines = f.readlines()
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
        self.calculationType = self.getCalculationType()
        self.lattice_s, self.latticeParameters_s = self.getLatticeParameters(isinit=True)
        self.lattice_e, self.latticeParameters_e = self.getLatticeParameters(isinit=False)
        self.composition = self.getComposition()
        self.parameters = self.getParameters()
        self.sites_s = self.getSites(isinit=True)
        self.sites_e = self.getSites(isinit=False)
        self.volume_s = self.getVolume(isinit=True)
        self.volume_e = self.getVolume(isinit=False)
        self.numberOfSites = self.getNumberOfSites()
        self.startTime = self.getStartTime()
        self.software = self.getSoftware()
        self.resourceUsage = self.getResourceUsage()
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
