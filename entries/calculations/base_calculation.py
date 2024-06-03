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
from public.structure import Structure
from public.tools.Electronic import Spin
from public.tools.helper import parseVarray
import numpy as np


class BaseCalculation(ABC):
    def __init__(self, file_parsers: dict):
        self.structure = None
        self.file_parser = file_parsers
        self.parm = None
        if file_parsers['vasprun'] is not None:
            self.vasprunParser = file_parsers['vasprun']
            self.input_structure = self.vasprunParser.input_structure
            self.output_structure = self.vasprunParser.output_structure
            self.basicDoc = {
                'InputStructure': self.input_structure.to_bson(),
                'OutputStructure': self.output_structure.to_bson(),
                'Parameters': self.vasprunParser.parameters,
                'Software': self.vasprunParser.software,
                'StartTime': self.vasprunParser.startTime,
                'ResourceUsage': self.vasprunParser.resourceUsage,
                'ProcessData': {},
                'Properties': {},
                'Files': [],
                'CalculationType': self.vasprunParser.calculationType
            }
            self.parm=self.vasprunParser.parameters
        elif file_parsers['poscar'] is not None and file_parsers['incar'] is not None:
            poscarParser = file_parsers['poscar']
            self.output_structure = poscarParser.structure
            self.basicDoc = {
                'InputStructure': {},
                'OutputStructure': self.output_structure.to_bson(),
                'ProcessData': {},
                'Properties': {},
                'Files': [],
                'CalculationType': file_parsers['incar'].getCalType()
            }
        else:
            raise ValueError("不可同时无vasprun或poscar和incar")
        self.parm = file_parsers['incar'].fill_parameters(self.parm)
        self.outcarParser = file_parsers['outcar']
        self.oszicarParser = file_parsers['oszicar']

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
        child = self.vasprunParser.root.find("./calculation[last()]/dos/i[@name='efermi']")
        efermi = float(child.text)
        child = self.vasprunParser.root.find("./calculation[last()]/eigenvalues/array/set")
        if child is None:
            return None
        KPoints = self.vasprunParser.kPoints
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

    def getElectronicSteps(self):
        electronicSteps = []
        for child in self.vasprunParser.root:
            if child.tag == 'calculation':
                energys = []
                cputimes = []
                totalenergydiffs = []
                for child2 in child:
                    if child2.tag == 'scstep':
                        for child3 in child2:
                            if child3.attrib == {'name': 'total'}:
                                times = child3.text.split()
                                if len(times) == 1:
                                    times = times[0]
                                    times = [times[: times.find('.') + 3], times[times.find('.') + 3:]]
                                if '*' in times[1]:
                                    cputime = 'NAN'
                                else:
                                    cputime = float(times[1])
                                cputimes.append(cputime)
                            if child3.tag == 'energy':
                                for child4 in child3:
                                    if child4.attrib == {'name': 'e_fr_energy'}:
                                        energy = float(child4.text)
                                        energys.append(energy)

                energy_pre = 0.0
                for energy in energys:
                    totalenergydiffs.append(energy - energy_pre)
                    energy_pre = energy

                para = self.parm['EDIFF']
                if para >= totalenergydiffs[-1]:
                    eleconvergency = True
                else:
                    eleconvergency = False
                doc = {
                    'TotalEnergy': energys,
                    'EleStepCpuTime': cputimes,
                    'TotalEnergyDiff': totalenergydiffs,
                    'EleConvergency': eleconvergency
                }
                electronicSteps.append(doc)
        return electronicSteps


    @abstractmethod
    def to_bson(self):
        pass
