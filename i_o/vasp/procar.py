#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : procar.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:29 
@Description: 
"""
from public.tools.Electronic import Spin
import re


class Procar:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.lines = f.readlines()
            f.close()
        nkpoints = 0
        nbands = 0
        nions = 0
        current_kpoint = 0
        spin = Spin.down

        KPoints = []
        eigenvalues = []
        EigenvalOcc = []
        spin_index = 0


        for line in self.lines:
            line = line.strip()

            if line.startswith("# of k-points:"):
                parts = line.split()
                nkpoints = int(parts[3])
                nbands = int(parts[7])
                nions = int(parts[11])


                if spin_index == 0:
                    eigenvalues = [[[] for _ in range(nkpoints)] for _ in range(2)]
                    EigenvalOcc = [[[] for _ in range(nkpoints)] for _ in range(2)]
                    KPoints = [[0.0, 0.0, 0.0] for _ in range(nkpoints)]

                spin_index += 1
                spin_index %= 2
            elif line.startswith("k-point"):
                parts = line.split()
                current_kpoint = int(parts[1]) - 1
                kpoint_coords = [float(coord) for coord in re.findall(r'-?\d+\.\d+', ' '.join(parts[2:6]))]
                KPoints[current_kpoint] = kpoint_coords

            elif line.startswith("band"):
                parts = line.split()
                eigenval_data = float(parts[4])
                eigenval_occ = float(parts[7])
                eigenvalues[spin_index][current_kpoint].append(eigenval_data)
                EigenvalOcc[spin_index][current_kpoint].append(eigenval_occ)

        self.nkpoints = nkpoints
        self.nbands = nbands
        self.nions = nions
        self.KPoints = KPoints
        self.eigenvalues = eigenvalues
        self.occupancies = EigenvalOcc
        self.IsSpinPolarized = True if spin_index == 0 else False

    def getEigenValues(self):
        EigenvalData = {}
        EigenvalOcc = {}
        if self.IsSpinPolarized:
            EigenvalData['spin 1'] = self.eigenvalues[0]
            EigenvalData['spin 2'] = self.eigenvalues[1]
            EigenvalOcc['spin 1'] = self.occupancies[0]
            EigenvalOcc['spin 2'] = self.occupancies[1]
        else:
            EigenvalData['spin 1'] = self.eigenvalues[0]
            EigenvalOcc['spin 1'] = self.occupancies[0]
        return {
            "NumberOfGeneratedKPoints": self.nkpoints,
            "NumberOfBand": self.nbands,
            "IsSpinPolarized": self.IsSpinPolarized,
            "KPoints": self.KPoints,
            "EigenvalData": EigenvalData,
            "EigenvalOcc": EigenvalOcc
        }
