#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract
@File       : vasprun.py
@IDE        : PyCharm
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:22
@Description:
"""
import linecache
import math
import os.path
import time
import xml.etree.cElementTree as ET
import numpy as np

from public.periodic_table import PTable
from public.lattice import Lattice

class VaspParser():

    def __init__(self, vaspPath, collections):
        super().__init__(vaspPath)
        self.vaspPath = vaspPath
        self.collections = collections

        tree = ET.parse(vaspPath)
        if tree is None:
            raise ValueError('File content error, not parse!')
        self.root = tree.getroot()
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

    def getLatticeParameters(self, isinit: bool = False):
        if isinit:
            child = self.root.find("./structure[@name='initialpos']/crystal/varray[@name='basis']")
        else:
            child = self.root.find("./structure[@name='finalpos']/crystal/varray[@name='basis']")
        a = child[0].text.split()
        a = [float(i) for i in a]
        b = child[1].text.split()
        b = [float(i) for i in b]
        c = child[2].text.split()
        c = [float(i) for i in c]
        lattice = Lattice([a, b, c])

        a0 = math.sqrt(np.dot(a, a))
        b0 = math.sqrt(np.dot(b, b))
        c0 = math.sqrt(np.dot(c, c))
        alpha = np.arccos(np.dot(a, c) / (a0 * c0))
        beta = np.arccos(np.dot(b, c) / (b0 * c0))
        gamma = np.arccos(np.dot(a, b) / (a0 * b0))
        latticeParameters = {
            'a': a0,
            'b': b0,
            'c': c0,
            'alpha': alpha,
            'beta': beta,
            'gamma': gamma
        }
        return lattice, latticeParameters

    def getComposition(self):
        composition = {}
        composition_full = []
        child = self.root.find("./atominfo/array[@name='atoms']/set")
        for child2 in child:
            count = 1
            if child2[0].text.strip(' ') in composition.keys():
                count += composition[child2[0].text.strip(' ')]
            composition.update({child2[0].text.strip(' '): count})
        for spec in composition.keys():
            atom = {
                "AtomicSymbol": spec,
                "AtomicNumber": PTable().detailed[spec]["Atomic no"],
                "AtomicMass": PTable().detailed[spec]["Atomic mass"],
                "Amount": composition[spec]
            }
            composition_full.append(atom)
        return composition_full

    def getVolume(self, isinit: bool = False):
        if isinit:
            child = self.root.find("./structure[@name='initialpos']/crystal/i[@name='volume']")
        else:
            child = self.root.find("./structure[@name='finalpos']/crystal/i[@name='volume']")
        return float(child.text)