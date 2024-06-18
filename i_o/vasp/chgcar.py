#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : chgcar.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:22 
@Description: 
"""
import re
import warnings

import numpy as np


class Chgcar:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.lines = f.readlines()
            f.close()
        self.NGX = 0
        self.NGY = 0
        self.NGZ = 0
        self.GRID = np.zeros((0, 0, 0))

    def getChgcarInfo(self):
        if len(self.lines) < 5:
            warnings.warn(f"File {self.filename} is too short to be a valid CHGCAR file.")
            return {}
        site_line = self.lines[6].strip()
        site_numbers = list(map(int, re.split(r'\s+', site_line)))
        site_length = sum(site_numbers)
        start_line = 8 + site_length + 1
        if start_line >= len(self.lines):
            raise ValueError(f"File {self.filename} does not contain enough lines for the grid information.")
        grid_line = self.lines[start_line].strip()
        ngx, ngy, ngz = map(int, re.split(r'\s+', grid_line)[0:3])
        self.NGX = ngx
        self.NGY = ngy
        self.NGZ = ngz
        self.GRID = np.zeros((ngx, ngy, ngz))

        data_lines = self.lines[start_line + 1:]

        flat_data = []
        for line in data_lines:
            if 'augmentation' in line:
                break
            flat_data.extend(map(float, re.split(r'\s+', line.strip())))

        index = 0
        for i in range(ngx):
            for j in range(ngy):
                for k in range(ngz):
                    self.GRID[i, j, k] = flat_data[index]
                    index += 1
        doc = {}
        doc["NGX"] = self.NGX
        doc["NGY"] = self.NGY
        doc["NGZ"] = self.NGZ
        doc["GRID"] = self.GRID.tolist()
        return doc


