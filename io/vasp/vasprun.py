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
import math
import time
import xml.etree.cElementTree as ET
import numpy as np

from public.tools.periodic_table import PTable
from public.lattice import Lattice
from public.sites import Site, Atom
from public.composition import Composition
from public.tools.helper import parseVarray




class VasprunParser():

    def __init__(self, vaspPath, collections):
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
            atom = Composition(atomic_symbol=spec,
                               atomic_number=PTable().detailed[spec]["Atomic no"],
                               atomic_mass=PTable().detailed[spec]["Atomic mass"],
                               amount=composition[spec])
            composition_full.append(atom)
        return composition_full

    def getVolume(self, isinit: bool = False):
        if isinit:
            child = self.root.find("./structure[@name='initialpos']/crystal/i[@name='volume']")
        else:
            child = self.root.find("./structure[@name='finalpos']/crystal/i[@name='volume']")
        return float(child.text)

    def getSites(self, isinit: bool = False):
        specs = []
        sites = []
        forces = []
        paras = self.parameters
        child = self.root.find("./atominfo/array[@name='atoms']/set")
        for child2 in child:
            specs.append(child2[0].text.strip(' '))
        if isinit:
            child = self.root.find("./structure[@name='initialpos']/varray")
            forces = [None for _ in range(len(specs))]
        else:
            force_child = self.root.find("./calculation[last()]/varray[@name='forces']")
            for force in force_child:
                forces.append([float(x) for x in force.text.split()])

            child = self.root.find("./structure[@name='finalpos']/varray")

        for i in range(len(specs)):
            p = child[i].text.split()
            p = [float(x) for x in p]
            sites.append(Site(p, Atom(specs[i]), forces[i]))

        if 'MAGMOM' in paras.keys() and len(paras['MAGMOM']) == len(sites):
            magmom = paras['MAGMOM']
        else:
            magmom = [0. for _ in range(len(sites))]

        for i in range(len(sites)):
            sites[i].set_magmom(magmom[i])

        return sites

    def getNumberOfSites(self):
        child = self.root.find("./atominfo/atoms")
        return int(child.text)

    def getSoftware(self):
        software = {}
        for child in self.root:
            if child.tag == 'generator':
                for child2 in child:
                    if child2.attrib == {'name': "program", 'type': "string"}:
                        software['SoftwareName'] = child2.text.strip(' ')
                    elif child2.attrib == {'name': "version", 'type': "string"}:
                        software['SoftwareVersion'] = child2.text.strip(' ')
                    elif child2.attrib == {'name': "subversion", 'type': "string"}:
                        software['Subversion'] = child2.text.strip(' ').replace("    ", " ")
                    elif child2.attrib == {'name': "platform", 'type': "string"}:
                        software['Platform'] = child2.text.strip(' ')
                return software

    def getStartTime(self):
        sdata = ''
        stime = ''
        for child in self.root:
            if child.tag == 'generator':
                for child2 in child:
                    if child2.attrib == {'name': "date", 'type': "string"}:
                        sdata = child2.text
                    elif child2.attrib == {'name': "time", 'type': "string"}:
                        stime = child2.text
                timearray = time.strptime(sdata + stime, "%Y %m %d %H:%M:%S ")
                timestyle = time.strftime("%Y-%m-%d %H:%M:%S", timearray)
                return timestyle

    def getReciprocalLattice(self, isinit: bool = False):
        """
                获取reciprocallattice
                :param isinit:
                :return:
                """
        if isinit:
            child = self.root.find("./structure[@name='initialpos']/crystal/varray[@name='rec_basis']")
        else:
            child = self.root.find("./structure[@name='finalpos']/crystal/varray[@name='rec_basis']")
        a = child[0].text.split()
        a = [float(i) for i in a]
        b = child[1].text.split()
        b = [float(i) for i in b]
        c = child[2].text.split()
        c = [float(i) for i in c]
        return np.array([a, b, c]).reshape((3, 3))


    def getKPoints(self):
        """
        提取 点
        :return:
        """
        child = self.root.find("./kpoints/varray[@name='kpointlist']")
        data = parseVarray(child)
        return data


