#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : DataCollectionSoftware
@File       : outcar.py
@IDE        : PyCharm
@Author     : zychen@cnic.cn
@Date       : 2023/9/5 9:12
@Description: Parser OUTCAR file
"""
import re
import warnings

import numpy as np


class Outcar:
    """
    parser outcar
    """

    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.lines = f.readlines()
            f.close()

    def getResourceUsage(self):
        """
        Get ResourceUsage
        :return:
        """
        if len(self.lines) < 5:
            warnings.warn(f"File {self.filename} is too short to be a valid OUTCAR file.")
        resourceUsage = {}
        for line in self.lines:
            line = line.strip('\n').strip(' ')
            if line.find('running on') != -1:
                line2 = line.split()
                if "N/A" not in line2:
                    resourceUsage['TotalCores'] = int(line2[2])
            if line.find('Total CPU time used (sec):') != -1:
                line2 = line.split(':')
                if "N/A" not in line2:
                    resourceUsage['TotalCpuTime'] = float(line2[1])
            elif line.find('User time (sec):') != -1:
                line2 = line.split(':')
                if "N/A" not in line2:
                    resourceUsage['UserTime'] = float(line2[1])
            elif line.find('System time (sec):') != -1:
                line2 = line.split(':')
                if "N/A" not in line2:
                    resourceUsage['SystemTime'] = float(line2[1])
            elif line.find('Elapsed time (sec):') != -1:
                line2 = line.split(':')
                if "N/A" not in line2:
                    resourceUsage['ElapsedTime'] = float(line2[1])
            elif line.find('Maximum memory used (kb):') != -1:
                line2 = line.split(':')
                if line2[1].strip() != 'N/A':
                    resourceUsage['MaxMemory'] = float(line2[1])
            elif line.find('Average memory used (kb):') != -1:
                line2 = line.split(':')
                if line2[1].strip() != 'N/A':
                    resourceUsage['AverageMemory'] = float(line2[1])
        return resourceUsage

    def getAtomicChargeAndAtomicMagnetization(self):
        charge = []
        mag_x = []  # 仅考虑线性磁矩
        header = []
        all_lines = self.lines
        # for line in reverse_readfile(self.filename):
        #     clean = line.strip()
        #     all_lines.append(clean)
        # For single atom systems, VASP doesn't print a total line, so
        # reverse parsing is very difficult
        read_charge = False
        read_mag_x = False

        # all_lines.reverse()
        for line in all_lines:
            clean = line.strip()
            if read_charge or read_mag_x:
                if clean.startswith("# of ion"):
                    header = re.split(r"\s{2,}", clean.strip())
                    header.pop(0)
                else:
                    m = re.match(r"\s*(\d+)\s+(([\d\.\-]+)\s+)+", clean)
                    if m:
                        toks = [float(i) for i in re.findall(r"[\d\.\-]+", clean)]
                        toks.pop(0)
                        if read_charge:
                            charge.append(dict(zip(header, toks)))
                        elif read_mag_x:
                            mag_x.append(dict(zip(header, toks)))
                    elif clean.startswith("tot"):
                        read_charge = False
                        read_mag_x = False
            if clean == "total charge":
                charge = []
                read_charge = True
                read_mag_x = False
            elif clean == "magnetization (x)":
                mag_x = []
                read_mag_x = True
                read_charge = False
        mag = mag_x
        magnetization = tuple(mag)
        charge = tuple(charge)

        return charge, magnetization

    def getElasticProperties(self):
        """
        计算弹性属性
        ElasticModuleMatrix: 弹性模量矩阵Cij
        ComplianceMatrix: 弹性柔度矩阵 Sij
        AveragingBulkModulus: 平均弹性模量 B, _Voigt（简写BV）, _Reuss（简写BR）, _Hill（简写BH）
        AveragingShearModulus: 平均剪切弹性模量 G ---- _Voigt（简写GV）, _Reuss（简写GR）, _Hill（简写GH）
        AveragingYoungModulus: 平均杨氏模量 E  ---- _Voigt（简写EV）, _Reuss（简写ER）, _Hill（简写EH）
        PoissonRatio: 泊松比v ----_Voigt（简写νV）、_Reuss（简写νR）、_Hill（简写νH）
        AnisotropyIndex: 各向异性指数 A
        :return:
        """

        # ElasticModuleMatrix: 弹性模量矩阵Cij
        all_lines = []
        for line in self.lines:
            clean = line.strip()
            all_lines.append(clean)

        all_lines.reverse()
        matrix_lines = []
        for i in range(len(all_lines)):
            if all_lines[i] == 'ELASTIC MODULI  (kBar)':
                matrix_lines = all_lines[i - 8: i - 2].copy()
        matrix_lines.reverse()
        # print(matrix_lines)
        matrix_init = []
        for line in matrix_lines:
            row = line.strip().split()[1:]
            row[3], row[4], row[5] = row[4], row[5], row[3]
            matrix_init.append(row)
        matrix_init[3], matrix_init[4], matrix_init[5] = matrix_init[4], matrix_init[5], matrix_init[3]
        # print(mart_init)

        # ComplianceMatrix: 弹性柔度矩阵 Sij
        matrix = np.array(matrix_init).astype(np.float32)
        matrix_inv = np.linalg.inv(matrix)

        # 计算 AveragingBulkModulus: 平均弹性模量 B, _Voigt（简写BV）, _Reuss（简写BR）, _Hill（简写BH）
        BV = (matrix[0][0] + matrix[1][1] + matrix[2][2]) / 9 + (matrix[0][1] + matrix[1][2] + matrix[0][2]) * 2 / 9
        BR = 1. / ((matrix_inv[0][0] + matrix_inv[1][1] + matrix_inv[2][2]) + (
                matrix_inv[0][1] + matrix_inv[1][2] + matrix_inv[0][2]) * 2)
        BH = 0.5 * (BV + BR)

        # 计算 AveragingShearModulus: 平均剪切弹性模量 G ---- _Voigt（简写GV）, _Reuss（简写GR）, _Hill（简写GH）
        GV = (matrix[0][0] + matrix[1][1] + matrix[2][2] - matrix[0][1] - matrix[1][2] - matrix[0][2]) / 15 + \
             (matrix[3][3] + matrix[4][4] + matrix[5][5]) / 5
        GR = 1. / (4 * (matrix_inv[0][0] + matrix_inv[1][1] + matrix_inv[2][2] - matrix_inv[0][1] - matrix_inv[1][2] -
                        matrix_inv[0][2]) / 15 +
                   (matrix_inv[3][3] + matrix_inv[4][4] + matrix_inv[5][5]) / 5)
        GH = 0.5 * (GV + GR)

        def cal_AveragingYoungModulus(B, G):
            return 9 * B * G / (3 * B + G)

        def cal_PoissonRatio(B, G):
            return (3 * B - 2 * G) / (3 * B + G) / 2

        # 计算 AveragingYoungModulus: 平均杨氏模量 E  ---- _Voigt（简写EV）, _Reuss（简写ER）, _Hill（简写EH）
        EV = cal_AveragingYoungModulus(BV, GV)
        ER = cal_AveragingYoungModulus(BR, GR)
        EH = cal_AveragingYoungModulus(BH, GH)

        # 计算 PoissonRatio: 泊松比v ----_Voigt（简写νV）、_Reuss（简写νR）、_Hill（简写νH）
        VV = cal_PoissonRatio(BV, GV)
        VR = cal_PoissonRatio(BR, GR)
        VH = cal_PoissonRatio(BH, GH)

        # 计算 AnisotropyIndex: 各向异性指数 A
        A = 5 * GV / GR + BV / BR - 6

        properties = {
            'ElasticModuleMatrix': matrix_init,
            'ComplianceMatrix': matrix_inv.tolist(),
            'AveragingBulkModulus': {
                'AveragingBulkModulus_Voigt': BV,
                'AveragingBulkModulus_Reuss': BR,
                'AveragingBulkModulus_Hill': BH
            },
            'AveragingShearModulus': {
                'AveragingShearModulus_Voigt': GV,
                'AveragingShearModulus_Reuss': GR,
                'AveragingShearModulus_Hill': GH
            },
            'AveragingYoungModulus': {
                'AveragingYoungModulus_Voigt': EV,
                'AveragingYoungModulus_Reuss': ER,
                'AveragingYoungModulus_Hill': EH
            },
            'PoissonRatio': {
                'PoissonRatio_Voigt': VV,
                'PoissonRatio_Reuss': VR,
                'PoissonRatio_Hill': VH
            },
            'AnisotropyIndex': A
        }
        return properties

    def getEfermi(self):
        """
        Extract E-fermi value from the OUTCAR file.
        """
        for line in self.lines:
            if 'E-fermi' in line:
                parts = line.split()
                efermi_index = parts.index('E-fermi') + 2
                efermi_value = float(parts[efermi_index])
                return efermi_value
        return None
