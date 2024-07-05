#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : kpoints.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:45 
@Description: 
"""


class Kpoints:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.lines = f.readlines()
            f.close()

    def getKpoints(self):
        if 'line_mode' in self.lines[2].lower() or 'line-mode' in self.lines[2].lower():
            kgrid_division = int(self.lines[1].strip().split(" ")[0])

            high_sym_points = []
            for line in self.lines[4:]:
                if line.strip():
                    point = list(map(float, line.split()[:3]))
                    if not high_sym_points or high_sym_points[-1] != point:
                        high_sym_points.append(point)

            return {
                "KgridDivision": kgrid_division,
                "HighSymPoints": high_sym_points
            }
        else:
            gamma_centered = False
            if "Gamma" in self.lines[2] or "G" in self.lines[2]:
                gamma_centered = True
            kgrid_division = list(map(float, self.lines[3].strip().split()))
            meshshift = list(map(float, self.lines[4].strip().split()))
            return {
                "GammaCentered": gamma_centered,
                "KgridDivision": kgrid_division,
                "Meshshift": meshshift
            }