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
import warnings

from public.tools.Electronic import Spin
import re
import numpy as np


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
        eigenvaluesData = []
        EigenvalOcc = []
        spin_index = 0
        fields = []
        done = False
        data = []
        spin = None
        occupancy = None
        eigenvalues = None

        for i in range(len(self.lines)):
            line = self.lines[i].strip()

            if line.startswith("# of k-points:"):
                parts = line.split()
                nkpoints = int(parts[3])
                nbands = int(parts[7])
                nions = int(parts[11])
                if spin_index == 0:

                    KPoints = [[0.0, 0.0, 0.0] for _ in range(nkpoints)]
                spin_index += 1
                spin_index %= 2
                if spin is not None:
                    data.append(spin)
                if occupancy is not None:
                    EigenvalOcc.append(occupancy)
                if eigenvalues is not None:
                    eigenvaluesData.append(eigenvalues)
                occupancy = [[] for _ in range(nkpoints)]
                eigenvalues = [[] for _ in range(nkpoints)]
                spin=[[] for _ in range(nkpoints)]
            elif line.startswith("k-point"):
                parts = line.split()
                current_kpoint = int(parts[1]) - 1
                kpoint_coords = [float(coord) for coord in re.findall(r'-?\d+\.\d+', ' '.join(parts[2:6]))]
                KPoints[current_kpoint] = kpoint_coords
            elif line.startswith("band"):
                parts = line.split()
                eigenval_data = float(parts[4])
                eigenval_occ = float(parts[7])
                eigenvalues[current_kpoint].append(eigenval_data)
                occupancy[current_kpoint].append(eigenval_occ)
            elif line.startswith("ion") and done:
                band = []
                for j in range(nions):
                    irons = []
                    curline = self.lines[i + j + 1].strip().split()
                    for num in curline[1:-1]:
                        irons.append(float(num))
                    band.append(irons)
                spin[current_kpoint].append(band)
            elif line.startswith("ion") and not done:
                parts = line.split()
                for part in parts[1:-1]:
                    fields.append(part)
                done = True
                band=[]
                for j in range(nions):
                    irons = []
                    curline = self.lines[i+j+1].strip().split()
                    for num in curline[1:-1]:
                        irons.append(float(num))
                    band.append(irons)
                spin[current_kpoint].append(band)
        data.append(spin)
        EigenvalOcc.append(occupancy)
        eigenvaluesData.append(eigenvalues)


        self.nkpoints = nkpoints
        self.nbands = nbands
        self.nions = nions
        self.KPoints = KPoints
        self.eigenvalues = eigenvaluesData
        self.occupancies = EigenvalOcc
        self.IsSpinPolarized = True if spin_index == 0 else False
        self.fields = fields
        data_array = np.array(data)
        if data[0] is not None:
            data_trans = np.transpose(data_array, (0, 3, 1, 2, 4))
        else:
            data_trans = data_array
        self.data = data_trans.tolist()

    def getEigenValues(self):
        if len(self.lines) < 5:
            warnings.warn(f"File {self.filename} is too short to be a valid PROCAR file.")
            return {}
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

    def getProjectedEigenvalOnIonOrbitals(self):
        if len(self.lines) < 5:
            warnings.warn(f"File {self.filename} is too short to be a valid PROCAR file.")
            return {}
        DecomposedLength = len(self.fields)
        IsLmDecomposed = True if DecomposedLength == 9 or DecomposedLength == 16 else False
        Data = {}
        for s in range(len(self.data)):
            spindata = []
            for i in range(self.nions):
                ironsdata = []
                for j in range(self.nkpoints):
                    points = []
                    for k in range(self.nbands):
                        bands = {}
                        for l in range(DecomposedLength):
                            bands[self.fields[l]] = self.data[s][i][j][k][l]
                        points.append(bands)
                    ironsdata.append(points)
                spindata.append(ironsdata)
            if s == 0:
                Data[Spin.up] = spindata
            elif s == 1:
                Data[Spin.down] = spindata
        return {
            "NumberOfGeneratedKPoints": self.nkpoints,
            "NumberOfBand": self.nbands,
            "IsSpinPolarized": self.IsSpinPolarized,
            "NumberOfIons": self.nions,
            "Decomposed": self.fields,
            "DecomposedLength": DecomposedLength,
            "IsLmDecomposed": IsLmDecomposed,
            "KPoints": self.KPoints,
            "Data": Data  # usually big
        }
