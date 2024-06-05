#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : dielectric_properties.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:36 
@Description: 
"""
import math

from .base_calculation import BaseCalculation

class DielectricProperties(BaseCalculation):
    def __init__(self, file_parsers: dict):
        self.atomicCharge = None
        self.atomicMagnetization = None
        self.linearMagneticMoment = None
        super().__init__(file_parsers)

    def getOpticalProperties(self):
        """
        提取介电函数信息
        :return:
        """
        if self.vasprunParser is None:
            return {}
        data = self.vasprunParser.getDielectricData()
        energy = data['Energy']
        numOfEnergyPoints = len(energy)
        real_part = data['real_part']
        imag_part = data['imag_part']
        # dielectric data are complex values
        # dielectricDataValue = complex(real_part, imag_part)
        # dielectricDataName = ["εxx", "εyy", "εzz", "εxy", "εyz", "εzx"]
        # xxName = "εxx"
        # yyName = "εyy"
        # zzName = "εzz"
        # xyName = "εxy"
        # yzName = "εyz"
        # zxName = "εzx"
        #
        # DieDataRealxx = []
        # DieDataRealyy = []
        # DieDataRealzz = []
        # DieDataRealxy = []
        # DieDataRealyz = []
        # DieDataRealzx = []
        # DieDataImagxx = []
        # DieDataImagyy = []
        # DieDataImagzz = []
        # DieDataImagxy = []
        # DieDataImagyz = []
        # DieDataImagzx = []
        #
        # for i in range(numOfEnergyPoints):
        #     DieDataRealxx[i] = real_part[i, 0]
        #     DieDataRealyy[i] = real_part[i, 1]
        #     DieDataRealzz[i] = real_part[i, 2]
        #     DieDataRealxy[i] = real_part[i, 3]
        #     DieDataRealyz[i] = real_part[i, 4]
        #     DieDataRealzx[i] = real_part[i, 5]
        #
        #     DieDataImagxx[i] = imag_part[i, 0]
        #     DieDataImagyy[i] = imag_part[i, 1]
        #     DieDataImagzz[i] = imag_part[i, 2]
        #     DieDataImagxy[i] = imag_part[i, 3]
        #     DieDataImagyz[i] = imag_part[i, 4]
        #     DieDataImagzx[i] = imag_part[i, 5]

        n_w_data = []  # 折射率 （refractive index）
        l_w_data = []  # 能量损失谱（energy-loss spectrum/function）
        k_w_data = []  # 消光系数（extinction index）
        alpha_data = []  # 吸收系数（adsorption coefficient）
        r_w_data = []  # 反射率（reflectivity/reflection coefficient）
        sigma_real_data = []  # 光电导率（optical conductivity）
        sigma_imag_data = []

        # 定义参数
        c = 2.9979 * math.pow(10, 8)
        h = 6.62607 * math.pow(10, -34)
        e = 1.602176 * math.pow(10, -19)
        epsilon0 = 8.8542 * math.pow(10, -12)
        eps = 0.000001
        for i in range(numOfEnergyPoints):
            n_w_group = []
            l_w_group = []
            k_w_group = []
            alpha_group = []
            r_w_group = []
            sigma_real_group = []
            sigma_imag_group = []

            for j in range(6):
                real = real_part[i][j]
                imag = imag_part[i][j]
                n_w = math.sqrt(math.sqrt(real * real + imag * imag) + real) / math.sqrt(2)
                l_w = imag / (real * real + imag * imag) if real != 0 and imag != 0 else 0.
                k_w = math.sqrt(math.sqrt(real * real + imag * imag) - real) / math.sqrt(2)
                alpha = 4 * math.pi * energy[i] * e * k_w / (h * c)
                r_w = ((n_w - 1) ** 2 + k_w ** 2) / ((n_w + 1) ** 2 + k_w ** 2)
                w = 2 * math.pi * energy[i] * e / h
                sigma = -epsilon0 * w * (real - 1 + imag * 1j) * 1j
                sigma_real = sigma.real
                sigma_imag = sigma.imag
                n_w_group.append(n_w)
                l_w_group.append(l_w)
                k_w_group.append(k_w)
                alpha_group.append(alpha)
                r_w_group.append(r_w)
                sigma_real_group.append(sigma_real)
                sigma_imag_group.append(sigma_imag)
            n_w_data.append(n_w_group)
            l_w_data.append(l_w_group)
            k_w_data.append(k_w_group)
            alpha_data.append(alpha_group)
            r_w_data.append(r_w_group)
            sigma_real_data.append(sigma_real_group)
            sigma_imag_data.append(sigma_imag_group)
            # print(sigma_real_data)
        opticalPropereties = {
            "NumberofEnergyPoints": numOfEnergyPoints,
            "Energies": energy,
            "DielectricFunctions": {
                "RealPart": real_part,
                'ImaginaryPart': imag_part
            },
            "RefractiveIndex": {
                "Data": n_w_data
            },
            "Energy_lossSpectrumFunction": {
                "Data": l_w_data
            },
            "ExtinctionIndex": {
                "Data": k_w_data
            },
            "AdsorptionCoefficient": {
                "Data": alpha_data
            },
            "ReflectivityCoefficient": {
                "Data": r_w_data
            },
            "OpticalConductivity": {
                "RealPart": sigma_real_data,
                "ImaginaryPart": sigma_imag_data
            }
        }
        return opticalPropereties


    def to_bson(self):
        doc = self.basicDoc
        if self.outcarParser is not None:
            self.atomicCharge, self.atomicMagnetization = self.outcarParser.getAtomicChargeAndAtomicMagnetization()
        if self.oszicarParser is not None:
            self.linearMagneticMoment = self.oszicarParser.getLinearMagneticMoment()
        doc['ProcessData'] = {
            'ElectronicSteps': self.getElectronicSteps()
        }
        doc['Properties'] = {
            "ThermodynamicProperties": self.getThermoDynamicProperties(),
            "ElectronicProperties": {
                'AtomicCharge': self.atomicCharge
                # 'BaderCharge': None
            },
            'MagneticProperties': {
                'AtomicMagnetization': self.atomicMagnetization,
                'LinearMagneticMoment': self.linearMagneticMoment,
            },
            'OpticalProperties': self.getOpticalProperties()
        }
        doc['Files'] = [parser.filename for parser in self.file_parser.values()]

        return doc
