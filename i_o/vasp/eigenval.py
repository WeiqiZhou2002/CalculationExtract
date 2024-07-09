#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import numpy as np
import warnings
import re

class KPoint:
    def __init__(self, name, coords):
        self.name = name
        self.coords = np.array(coords)

class EigenValues:
    def __init__(self, kpoints, eigenvalues):
        self.kpoints = kpoints
        self.eigenvalues = eigenvalues

class Eigenval:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.lines = f.readlines()

    def getEigenValues(self):
        """
        Extract eigenvalue data
        :return:
        """

        if len(self.lines) < 6:
            warnings.warn(f"File {self.filename} is too short to be a valid EIGENVAL file.")
            return {}
        self.isSpin = int(self.lines[0].split()[3])

        # Get the number of k-points and bands
        header_fields = self.lines[5].split()
        self.n = int(header_fields[1])
        self.nBands = int(header_fields[2])

        # Initialize kpoints and eigenvalues
        self.kpoints = [None] * self.n
        self.eigenvalues = None
        self.occupancies = None
        NumberOfBand = self.nBands
        IsSpinPolarized = (self.isSpin != 1)
        line_index = 6  # Start reading from the 7th line (index 6)
        if len(self.lines) < 7:
            return {
                "NumberOfGeneratedKPoints": "N/A",
                "NumberOfBand": NumberOfBand,
                "IsSpinPolarized": IsSpinPolarized,
                "KPoints": "N/A",
                "EigenvalData": "N/A",
                "EigenvalOcc": "N/A"
            }

        if self.isSpin == 1:
            for i in range(self.n):
                line_index += 1  # Skip a line for k-point header
                line = self.lines[line_index].strip()
                if re.match(r'^[0-9]+\.\s+kpoint:', line):
                    kpoint_coords = list(map(float, line.split()[2:5]))
                else:
                    kpoint_coords = list(map(float, line.split()[:3]))
                self.kpoints[i] = KPoint(str(i), kpoint_coords)
                line_index += 1
                if self.eigenvalues is None:
                    self.eigenvalues = np.zeros((1, self.n, self.nBands))
                    self.occupancies = np.zeros((1, self.n, self.nBands))
                for j in range(self.nBands):
                    fields = self.lines[line_index].split()
                    self.eigenvalues[0, i, j] = float(fields[1])
                    self.occupancies[0, i, j] = float(fields[2])
                    line_index += 1
        else:
            for i in range(self.n):
                line_index += 1  # Skip a line for k-point header
                kpoint_coords = list(map(float, self.lines[line_index].split()[:3]))
                self.kpoints[i] = KPoint(str(i), kpoint_coords)
                line_index += 1
                if self.eigenvalues is None:
                    self.eigenvalues = np.zeros((2, self.n, self.nBands))
                    self.occupancies = np.zeros((2, self.n, self.nBands))
                for j in range(self.nBands):
                    fields = self.lines[line_index].split()
                    self.eigenvalues[0, i, j] = float(fields[1])
                    self.eigenvalues[1, i, j] = float(fields[2])
                    self.occupancies[0, i, j] = float(fields[3])
                    self.occupancies[1, i, j] = float(fields[4])
                    line_index += 1

        self.EigenValues = EigenValues(self.kpoints, self.eigenvalues)
        NumberOfGeneratedKPoints = len(self.kpoints)

        KPoints = self.kpoints
        EigenvalData = {}
        EigenvalOcc = {}

        if IsSpinPolarized:
            EigenvalData['spin 1'] = self.eigenvalues[0].tolist()
            EigenvalData['spin 2'] = self.eigenvalues[1].tolist()
            EigenvalOcc['spin 1'] = self.occupancies[0].tolist()
            EigenvalOcc['spin 2'] = self.occupancies[1].tolist()
        else:
            EigenvalData['spin 1'] = self.eigenvalues[0].tolist()
            EigenvalOcc['spin 1'] = self.occupancies[0].tolist()

        return {
            "NumberOfGeneratedKPoints": NumberOfGeneratedKPoints,
            "NumberOfBand": NumberOfBand,
            "IsSpinPolarized": IsSpinPolarized,
            "KPoints": [kpoint.coords.tolist() for kpoint in KPoints],
            "EigenvalData": EigenvalData,
            "EigenvalOcc": EigenvalOcc
        }



