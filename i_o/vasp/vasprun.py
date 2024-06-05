#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract
@File       : vasprun.py
@IDE        : PyCharm
@Author     : zychen@cnic.cn & wzhou255@wisc.edu
@Date       : 2024/5/30 16:22
@Description:
"""

import time
import xml.etree.cElementTree as ET
import numpy as np
import linecache
import os

from public.tools.Electronic import Spin
from public.tools.periodic_table import PTable
from public.lattice import Lattice
from public.sites import Site, Atom
from public.composition import Composition
from public.tools.helper import parseVarray
from public.calculation_type import CalType
from entries.calculations import CalculateEntries
from public.structure import Structure


class Vasprun:

    def __init__(self, vaspPath):
        self.output_structure = None
        self.input_structure = None
        self.filename = vaspPath
        tree = ET.parse(vaspPath)
        if tree is None:
            raise ValueError('File content error, not parse!')
        self.root = tree.getroot()
        self.calculationType = None
        self.kPointPath = None
        self.lattice_init = None
        self.lattice_final = None
        self.latticeParameters_init = None
        self.latticeParameters_final = None
        self.composition = None
        self.parameters = None
        self.sites_init = None
        self.sites_final = None
        self.volume_init = None
        self.volume_final = None
        self.numberOfSites = None
        self.startTime = None
        self.software = None
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
        self.cellStress_init = None
        self.cellStress_final = None
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
        self.lattice_init = self.getLatticeParameters(isinit=True)
        self.lattice_final = self.getLatticeParameters(isinit=False)
        self.composition = self.getComposition()
        self.calculationType = self.getCalType()
        self.parameters = self.getParameters()
        self.sites_init = self.getSites(isinit=True)
        self.sites_final = self.getSites(isinit=False)
        self.volume_init = self.getVolume(isinit=True)
        self.volume_final = self.getVolume(isinit=False)
        self.numberOfSites = self.getNumberOfSites()
        self.startTime = self.getStartTime()
        self.software = self.getSoftware()
        self.kPoints = self.getKPoints()
        self.kPointPath = self.findKpointPath()
        self.input_structure = Structure(lattice=self.lattice_init, composition=self.composition, sites=self.sites_init)
        self.input_structure.setup()
        self.output_structure = Structure(lattice=self.lattice_final, composition=self.composition,
                                          sites=self.sites_final)
        self.output_structure.setup()

    def findPara(self, parameters: list):
        """
        获取指定的参数
        :return:
        """
        parameters_dict = {}
        xpath1 = "./incar/i"
        xpath2 = "./incar/v"
        xpath3 = "./parameters//i"
        xpath4 = "./parameters//v"
        for para in parameters:
            flag = False
            if para == 'ALGO':
                parameters_dict[para] = 'Normal'
            for xpath in [xpath1, xpath2, xpath3, xpath4]:
                child = self.root.findall(xpath)
                for child2 in child:
                    if child2.attrib['name'] == para:
                        flag = True
                        if 'type' in child2.attrib.keys():
                            if child2.attrib['type'] == 'int':
                                parameters_dict[para] = int(child2.text.strip())
                            elif child2.attrib['type'] == 'string':
                                parameters_dict[para] = child2.text.strip(' ')
                            elif child2.attrib['type'] == 'logical':
                                if 'F' in child2.text:
                                    parameters_dict[para] = False
                                else:
                                    parameters_dict[para] = True
                        else:
                            if child2.tag == 'v':
                                parameters_dict[para] = [float(t) for t in child2.text.split()]
                            elif child2.tag == 'i':
                                parameters_dict[para] = float(child2.text.strip())
                        break
                if flag:
                    break
        if 'ENCUT' in parameters and 'ENCUT' not in parameters_dict.keys():
            if parameters_dict['PREC'] == 'normal':
                enmax = []
                composition = self.composition
                for doc in composition:
                    symbol = doc['AtomicSymbol']
                    em = PTable().enmax[symbol]
                    enmax.append(em)
                parameters_dict['ENCUT'] = max(enmax)
        return parameters_dict

    def getCalType(self):
        para_list = ['IBRION', 'LORBIT', 'LOPTICS', 'LEPSILON', 'LCALCEPS', 'ISIF', 'MAGMOM']
        parameters = self.findPara(para_list)
        if parameters['IBRION'] == 1 or parameters['IBRION'] == 2 or parameters['IBRION'] == 3:
            return CalType.GeometryOptimization
        if parameters['IBRION'] == -1 and linecache.getline(self.kPointPath, 3).lower().startswith(
                'l'):  # kpoints generation para
            return CalType.BandStructure
        if ('LOPTICS' in parameters.keys() and parameters['LOPTICS']) or parameters['IBRION'] == 7 or parameters[
            'IBRION'] == 8 \
                or (parameters['IBRION'] == 5 and (('LEPSILON' in parameters.keys() and parameters['LEPSILON']) or (
                'LCALCEPS' in parameters.keys() and parameters['LCALCEPS']))) \
                or (parameters['IBRION'] == 6 and (('LEPSILON' in parameters.keys() and parameters['LEPSILON']) or (
                'LCALCEPS' in parameters.keys() and parameters['LCALCEPS']))):
            return CalType.DielectricProperties
        if parameters['IBRION'] == -1 and parameters['LORBIT']:
            return CalType.DensityOfStates
        if parameters['IBRION'] == -1:
            return CalType.StaticCalculation
        if (parameters['IBRION'] == 5 or parameters['IBRION'] == 6) and parameters['ISIF'] >= 3:
            return CalType.ElasticProperties

        if 'MAGMOM' in parameters.keys():
            return CalType.MagneticProperties
        raise ValueError('无法判断提取类型，无法提取')

    def findKpointPath(self):
        directory = os.path.dirname(self.filename)
        kPointPath = os.path.join(directory, 'KPOINTS')
        return kPointPath if os.path.exists(kPointPath) else None

    def getLatticeParameters(self, isinit: bool = False):
        if isinit:
            child = self.root.find("./structure[@name='initialpos']/crystal/varray[@name='basis']")
        else:
            child = self.root.find("./structure[@name='finalpos']/crystal/varray[@name='basis']")
        matrix = [
            list(map(float, child[0].text.split())),
            list(map(float, child[1].text.split())),
            list(map(float, child[2].text.split()))
        ]
        lattice = Lattice(matrix)
        return lattice

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

    def getParameters(self):
        calType = self.calculationType
        kpoints = {}
        pseudopotential = []
        parameters_dict = {}
        geometry_optim = ['PREC', 'ISPIN', 'ISTART', 'ICHARG', 'ENCUT', 'NELM', 'ALGO', 'EDIFF', 'EDIFFG',
                          'ISMEAR', 'SIGMA', 'GGA', 'NBANDS', 'NEDOS', 'IBRION', 'ISIF', 'NSW', 'LORBIT',
                          'ISYM', 'LDAU', 'LHFCALC', 'LWAVE', 'LCHARG']
        StaticDosBand_calculation = ['PREC', 'ISPIN', 'ISTART', 'ICHARG', 'ENCUT', 'NELM', 'ALGO', 'EDIFF', 'EDIFFG',
                                     'ISMEAR', 'SIGMA', 'GGA', 'NBANDS', 'NEDOS', 'IBRION', 'ISIF', 'LORBIT',
                                     'ISYM', 'LDAU', 'LHFCALC', 'LWAVE', 'LCHARG', 'LELF', 'LOPTICS', 'CSHIFT',
                                     'MAGMOM', 'LAECHG']
        dielectric_calculation = ['PREC', 'ISPIN', 'ISTART', 'ICHARG', 'ENCUT', 'NELM', 'ALGO', 'EDIFF', 'EDIFFG',
                                  'ISMEAR', 'SIGMA', 'GGA', 'NBANDS', 'NEDOS', 'IBRION', 'ISIF', 'LORBIT',
                                  'ISYM', 'LWAVE', 'LCHARG', 'LOPTICS', 'CSHIFT', 'MAGMOM']
        timepredict = ['PREC', 'ISPIN', 'IBRION', 'EDIFF', 'EDIFFG', 'ISIF', 'NSW', 'ALGO', 'ENCUT', 'NELECT',
                       'LOPTICS', 'LHFCALC']
        if calType == CalType.GeometryOptimization:
            parameters_dict = self.findPara(geometry_optim)
        elif calType == CalType.StaticCalculation or CalType.DensityOfStates or CalType.BandStructure or CalType.ElasticProperties or CalType.MagneticProperties:
            parameters_dict = self.findPara(StaticDosBand_calculation)
            if parameters_dict['LDAU']:
                parameters_dict['LDAUTYPE'] = self.findPara(['LDAUTYPE'])['LDAUTYPE']
                parameters_dict['LDAUL'] = self.findPara(['LDAUL'])['LDAUL']
                parameters_dict['LDAUU'] = self.findPara(['LDAUU'])['LDAUU']
                parameters_dict['LDAUJ'] = self.findPara(['LDAUJ'])['LDAUJ']
                parameters_dict['LDAUPRINT'] = self.findPara(['LDAUPRINT'])['LDAUPRINT']
            if parameters_dict['LHFCALC']:
                parameters_dict['AEXX'] = self.findPara(['AEXX'])['AEXX']
                parameters_dict['HFSCREEN'] = self.findPara(['HFSCREEN'])['HFSCREEN']
                parameters_dict['LMAXFOCK'] = self.findPara(['LMAXFOCK'])['LMAXFOCK']
        elif calType == CalType.DielectricProperties:
            parameters_dict = self.findPara(dielectric_calculation)
        else:
            parameters_dict = self.findPara(timepredict)
        child = self.root.find("./kpoints/generation")
        # Kpoint信息： band 提取与其他不同，分情况
        if calType == CalType.BandStructure:
            if child.attrib['param'] == 'listgenerated':
                for child2 in child:
                    if child2.attrib == {'type': 'int', 'name': 'divisions'}:
                        kpoints['KgridDivision'] = child2.text.strip()
                HighsymPoints = []
                for v in child.findall('v'):
                    HighsymPoints.append([float(i) for i in v.text.split()])
                kpoints['HighsymPoints'] = HighsymPoints
            parameters_dict['KpointsPath'] = kpoints
        else:
            if child.attrib['param'] == 'Gamma':
                kpoints['GammaCentered'] = True
            else:
                kpoints['GammaCentered'] = False
            for child2 in child:
                if child2.attrib == {'type': 'int', 'name': 'divisions'}:
                    kpoints['KgridDivision'] = [int(i) for i in child2.text.split()]
                if child2.attrib == {'name': 'shift'}:
                    kpoints['Meshshift'] = [float(i) for i in child2.text.split()]
            child = self.root.find("./kpoints/varray[@name='kpointlist']")
            count = 0
            for _ in child:
                count += 1
            kpoints['totalnums'] = count
            parameters_dict['Kpoints'] = kpoints
        # 赝势信息
        child = self.root.find("./atominfo/array[@name='atomtypes']/set")
        for child2 in child:
            pseudopotential.append(child2[4].text.strip(' '))
        parameters_dict['PseudoPotential'] = pseudopotential
        return parameters_dict

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


    def getDielectricData(self):
        """
            提取与频率相关的介电函数数据
            :return:
        """
        # dielectricData = {}
        energy = []
        imag_part = []
        real_part = []
        imag = []
        real = []
        for event, elem in ET.iterparse(self.filename):
            tag = elem.tag
            if tag == "dielectricfunction":
                imag = [[float(l) for l in r.text.split()] for r in
                        elem.find("imag").find("array").find("set").findall("r")]
                real = [[float(l) for l in r.text.split()] for r in
                        elem.find("real").find("array").find("set").findall("r")]
                break  # break 多个 dielectricfunction 只取得第一个die..
        for e in imag:
            energy.append(e[0])
            imag_part.append(e[1:])
        for e in real:
            real_part.append(e[1:])
        dielectricData = {
            'Energy': energy,
            'real_part': real_part,
            'imag_part': imag_part
        }
        return dielectricData

    def getEigenValues(self):
        """
        提取本征值数据
        :return:
        """
        NumberOfGeneratedKPoints = 0
        NumberOfBand = 0
        IsSpinPolarized = False
        KPoints = None
        EigenvalData = {}
        EigenvalOcc = {}
        child = self.root.find("./calculation[last()]/dos/i[@name='efermi']")
        efermi = float(child.text)
        child = self.root.find("./calculation[last()]/eigenvalues/array/set")
        if child is None:
            return None
        KPoints = self.kPoints
        NumberOfGeneratedKPoints = len(KPoints)
        for s in child.findall('set'):
            spin = Spin.up if s.attrib["comment"] == "spin 1" else Spin.down
            data = []
            occ = []
            for k in s.findall("set"):
                t = np.array(parseVarray(k))
                data.append(list(t[:, 0]))
                occ.append(list(t[:, 1]))
            NumberOfBand = len(data[0])
            # 按能带存储
            EigenvalEnergyData = np.array(data).transpose()
            EigenvalEnergyOcc = np.array(occ).transpose()

            EigenvalData[spin] = EigenvalEnergyData.tolist()
            EigenvalOcc[spin] = EigenvalEnergyOcc.tolist()

            if spin == Spin.down:
                IsSpinPolarized = True
        # NumberOfBand = len(EigenvalData[Spin['up']][0])
        return {
            "NumberOfGeneratedKPoints": NumberOfGeneratedKPoints,
            "NumberOfBand": NumberOfBand,
            "IsSpinPolarized": IsSpinPolarized,
            "KPoints": KPoints,
            "FermiEnergy": efermi,
            "EigenvalData": EigenvalData,
            "EigenvalOcc": EigenvalOcc
        }