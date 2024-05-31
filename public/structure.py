#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : structure.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:34 
@Description: 
"""
import json
from abc import abstractmethod, ABC
from hashlib import md5
from typing import List
import spglib as spg
from math import sqrt, pi
from pymatgen.core.structure import Structure as PyStr
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer as sga

from public.lattice import Lattice
from public.composition import Composition
from public.sites import Site
from public.tools.pointGroupInfo import pointgroup_symbol_num
from public.tools.highSymmetryKPath import *


class Structure:

    def __init__(self,
                 lattice: Lattice = None,
                 composition: List[Composition] = None,
                 sites: List[Site] = None):
        self.lattice = lattice
        self.composition = composition
        self.sites = sites
        self.volume = None
        self.formula = None
        self.simplestFormula = None
        self.generalFormula = None
        self.numberOfElements = None
        self.numberOfSites = None
        self.stoichiometry = None
        self.latticeParameters = None
        self.spaceGroup = None
        self.pointGroup = None
        self.crystalSystem = None
        self.bravaisLattice = None
        self.reciprocalLattice = None
        self.primitiveLattice = None
        self.conventionalLattice = None
        self.highSymmetryKPath = None
        self.prototype = None
        self.cellStress = None
        self.sitesDoc = None
        self.hashId = None


    @abstractmethod
    def setup(self):
        pass

    def getSpacePointGroup(self):
        """
        获取空间群,点群
        :return:
           space
        """
        if self.sites is None or self.lattice is None:
            raise ValueError('warning: please input lattice or sites!')

        lattice = self.lattice.matrix
        sites = self.sites
        pos = [i.coords for i in sites]
        numbers = [i.atom.atomicnumber for i in sites]
        cell = (lattice, pos, numbers)
        dataset = spg.get_symmetry_dataset(cell, symprec=0.01, angle_tolerance=5)
        if dataset is None:
            raise ValueError('无法计算得出space group')
        spaceGroup_type = spg.get_spacegroup_type(dataset["hall_number"])
        spaceGroup = {
            "spacegroupSymbol": spaceGroup_type['international_short'],
            "spacegroupInternationalSymbol": spaceGroup_type['international_full'],
            "SchoenfliesSymbol": spaceGroup_type['schoenflies'],
            "spacegroupNumber": spaceGroup_type['number'],
            "hallNumber": dataset['hall_number'],
            "hallSymbol": spaceGroup_type['hall_symbol']
        }
        pointGroupSymbol = dataset['pointgroup']
        pointGroup = {
            "pointgroupSymbol": pointGroupSymbol,
            "pointgroupNumber": pointgroup_symbol_num[pointGroupSymbol]
        }
        return spaceGroup, pointGroup

    def getNSites(self):
        """
        获取site个数
        :return:
           n
        """
        n = 0
        for atom in self.composition:
            n += atom.amount
        return n

    def getNElements(self):
        """
        获取元素个数
        :return:
           n
        """
        return len(self.composition)

    def getFormula(self):
        """
        获取化学式
        :return:
        """
        formula = ''
        for atom in self.composition:
            if atom.amount != 1:
                formula = formula + atom.atomic_symbol + str(atom.amount)
            else:
                formula = formula + atom.atomic_symbol
        return formula

    def getSimplestFormula(self):
        """
        获取最简化学式
        :return:
        """
        formula = ''
        nums = []
        common = 1
        for atom in self.composition:
            nums.append(atom.amount)
        for i in range(min(nums)):
            flag = True
            for num in nums:
                if num % (i + 1) != 0:
                    flag = False
                    break
            if flag:
                common = i + 1
        for atom in self.composition:
            if atom.amount / common != 1:
                formula = formula + atom.atomic_symbol + str(int(atom.amount / common))
            else:
                formula = formula + atom.atomic_symbol
        return formula

    def getStoichiometry(self):
        """
        获取stoichiometry
        :return:
        """
        stoichiometry = []
        sum = float(self.numberOfSites)
        for atom in self.composition:
            atom2 = {
                "AtomicSymbol": atom.atomic_symbol,
                "AtomicNumber": atom.atomic_number,
                "AtomicMass": atom.atomic_mass,
                "AtomicPercent": atom.amount / sum
            }
            stoichiometry.append(atom2)
        return stoichiometry

    def getLatticeParameters(self):
        """
        获取晶格常数
        :return:
        """
        lattice = self.lattice.matrix
        a = lattice[0]
        b = lattice[1]
        c = lattice[2]
        a0 = sqrt(np.dot(a, a))
        b0 = sqrt(np.dot(b, b))
        c0 = sqrt(np.dot(c, c))
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
        return latticeParameters

    def getCrystalSystem(self):
        """
        获取晶系
        :return:
        """
        crystalsystem = {}
        number = self.spaceGroup["spacegroupNumber"]
        if number <= 2:
            crystalsystem = "Triclinic"
        elif number <= 15:
            crystalsystem = "Monoclinic"
        elif number <= 74:
            crystalsystem = "Orthorhombic"
        elif number <= 142:
            crystalsystem = "Tetragonal"
        elif number <= 167:
            crystalsystem = "Trigonal"
        elif number <= 194:
            crystalsystem = "Hexagonal"
        elif number <= 230:
            crystalsystem = "Cubic"
        return crystalsystem

    def getBravaisLattice(self):
        """
        获取bravaislattice
        :return:
        """
        latticesystem = self.crystalSystem
        spacenumber = self.spaceGroup["spacegroupNumber"]
        spacesymbol = self.spaceGroup["spacegroupSymbol"]
        if spacenumber in [146, 148, 155, 160, 161, 166, 167]:
            latticesystem = "Rhombohedral"
        elif latticesystem == "Trigonal":
            latticesystem = "Hexagonal"
        if latticesystem == "Triclinic":
            return "SimpleTriclinic"
        elif latticesystem == "Monoclinic":
            if "P" in spacesymbol:
                return "SimpleMonoclinic"
            elif "C" in spacesymbol:
                return "BaseCenteredMonoclinic"
        elif latticesystem == "Orthorhombic":
            if "P" in spacesymbol:
                return "SimpleOrthorhombic"
            elif "C" in spacesymbol or "A" in spacesymbol:
                return "BaseCenteredOrthorhombic"
            elif "I" in spacesymbol:
                return "BodyCentredOrthorhombic"
            elif "F" in spacesymbol:
                return "FaceCenteredOrthorhombic"
        elif latticesystem == "Tetragonal":
            if "P" in spacesymbol:
                return "SimpleTetragonal"
            elif "I" in spacesymbol:
                return "BodyCenteredTetragonal"
        elif latticesystem == "Rhombohedral":
            return "SimpleRhombohedral"
        elif latticesystem == "Hexagonal":
            return "SimpleRhombohedral"
        elif latticesystem == "Cubic":
            if "P" in spacesymbol:
                return "SimpleCubic"
            elif "I" in spacesymbol:
                return "BodyCentredCubic"
            elif "F" in spacesymbol:
                return "FaceCenteredCubic"

    def getReciprocalLattice(self):
        """
        获取ReciprocalLattice
        :return:
        """
        lattice = self.lattice.matrix
        return np.linalg.inv(lattice)

    def getVolume(self):
        """
        计算体积
        :return:
        """
        a = self.lattice.matrix[0]
        b = self.lattice.matrix[1]
        c = self.lattice.matrix[2]
        volume = a.dot(np.cross(b, c))
        return volume

    def getPrimitiveLattice(self):
        """
        获取primitivelattice
        :return:
        """
        if self.sites is None or self.lattice is None:
            raise ValueError('warning: please input lattice or sites!')
        lattice = self.lattice.matrix
        sites = self.sites
        pos = [i.coords for i in sites]
        numbers = [i.atom.atomicnumber for i in sites]
        cell = (lattice, pos, numbers)
        lattice, _, _ = spg.find_primitive(cell, symprec=0.001, angle_tolerance=5)
        return lattice

    def getConventionalLattice(self):
        """
        获取conventionallattice
        :return:
        """
        if self.sites is None or self.lattice is None:
            raise ValueError('warning: please input lattice or sites!')
        lattice = self.lattice.matrix
        sites = self.sites
        pos = [i.coords for i in sites]
        numbers = [i.atom.atomicnumber for i in sites]
        struct = PyStr(lattice, numbers, pos)
        conventional_struct = sga(struct).get_conventional_standard_structure()
        conventional_lattice = conventional_struct.lattice.matrix
        return conventional_lattice

    def getHighSymmetryKPath(self):
        """
        生成布里渊区高对称点路径的lattice类型
        :return:
        """
        # TODO: a,b,c参数的来源需再校核
        bravaislattice = self.bravaisLattice
        lattice = self.conventionalLattice
        a = lattice[0]
        b = lattice[1]
        c = lattice[2]
        a0 = sqrt(np.dot(a, a))
        b0 = sqrt(np.dot(b, b))
        c0 = sqrt(np.dot(c, c))
        alpha = np.arccos(np.dot(a, c) / (a0 * c0))
        reclattice = self.reciprocalLattice
        a = reclattice[0]
        b = reclattice[1]
        c = reclattice[2]
        a1 = sqrt(np.dot(a, a))
        b1 = sqrt(np.dot(b, b))
        c1 = sqrt(np.dot(c, c))
        kalpha = np.arccos(np.dot(a, c) / (a1 * c1))
        kbeta = np.arccos(np.dot(b, c) / (b1 * c1))
        kgamma = np.arccos(np.dot(a, b) / (a1 * b1))
        prilattice = self.primitiveLattice
        a = prilattice[0]
        c = prilattice[2]
        a2 = sqrt(np.dot(a, a))
        c2 = sqrt(np.dot(c, c))
        alpha2 = np.arccos(np.dot(a, c) / (a2 * c2))
        kpath = {}
        if bravaislattice == 'SimpleCubic':
            kpath = cubic()
        elif bravaislattice == 'FaceCenteredCubic':
            kpath = fcc()
        elif bravaislattice == 'BodyCenteredCubic':
            kpath = bcc()
        elif bravaislattice == 'SimpleTetragonal':
            kpath = tet()
        elif bravaislattice == 'BodyCenteredTetragonal':
            if a0 > c0:
                kpath = bctet1(a0, c0)
            else:
                kpath = bctet2(a0, c0)
        elif bravaislattice == 'SimpleOrthorhombic':
            kpath = orc()
        elif bravaislattice == 'FaceCenteredOrthorhombic':
            if 1 / a0 ** 2 > 1 / b0 ** 2 + 1 / c0 ** 2:
                kpath = orcf1(a0, b0, c0)
            elif 1 / a0 ** 2 < 1 / b0 ** 2 + 1 / c0 ** 2:
                kpath = orcf2(a0, b0, c0)
            else:
                kpath = orcf3(a0, b0, c0)
        elif bravaislattice == 'BodyCenteredOrthorhombic':
            kpath = orci(a0, b0, c0)
        elif bravaislattice == 'BaseCenteredOrthorhombic':
            kpath = orcc(a0, b0)
        elif bravaislattice == 'SimpleHexagonal':
            kpath = hex()
        elif bravaislattice == 'SimpleRhombohedral':
            if alpha2 < 90 * pi / 180:
                kpath = rhl1(alpha2)
            else:
                kpath = rhl2(alpha2)
        elif bravaislattice == 'SimpleMonoclinic':
            kpath = mcl(b0, c0, alpha)
        elif bravaislattice == 'BaseCenteredMonoclinic':
            if kgamma > 90 * pi / 180:
                kpath = mclc1(a0, b0, c0, alpha)
            elif kgamma == 90 * pi / 180:
                kpath = mclc2(a0, b0, c0, alpha)
            elif kgamma < 90 * pi / 180 and b0 * cos(alpha) / c0 + b0 ** 2 * sin(alpha) ** 2 / a0 ** 2 < 1:
                kpath = mclc3(a0, b0, c0, alpha)
            elif kgamma < 90 * pi / 180 and b0 * cos(alpha) / c0 + b0 ** 2 * sin(alpha) ** 2 / a0 ** 2 == 1:
                kpath = mclc4(a0, b0, c0, alpha)
            elif kgamma < 90 * pi / 180 and b0 * cos(alpha) / c0 + b0 ** 2 * sin(alpha) ** 2 / a0 ** 2 > 1:
                kpath = mclc5(a0, b0, c0, alpha)
        elif bravaislattice == 'SimpleTriclinic':
            if kalpha > 90 * pi / 180 and kbeta > 90 * pi / 180 and kgamma >= 90 * pi / 180:
                kpath = tria()
            elif kalpha < 90 * pi / 180 and kbeta < 90 * pi / 180 and kgamma <= 90 * pi / 180:
                kpath = trib()
        if kpath != {}:
            for key in kpath['kpoints'].keys():
                kpath['kpoints'][key] = kpath['kpoints'][key].tolist()
        return kpath

    def getSitesList(self):
        if self.sites is None:
            raise ValueError('sites 不能为空')
        sitesList = []
        for site in self.sites:
            doc = {
                'Position': site.coords,
                'Atom': {
                    'AtomicSymbol': site.atom.atomicsymbol,
                    'AtomicNumber': site.atom.atomicnumber,
                    'AtomicMass': site.atom.atomicmass
                },
                'Occupancy': site.Occupancy,
                'Magmom': site.Magmom,
                'Force': site.force
            }
            sitesList.append(doc)
        return sitesList

    def getHashValue(self):
        hash_sites = []
        if self.sitesDoc is None:
            raise ValueError('sites doc 不能为空！')
        for site in self.sitesDoc:
            hash_site = {
                'Position': site['Position'],
                'Atom': site['Atom'],
                'Occupancy': site['Occupancy'],
            }
            hash_sites.append(hash_site)
        hash_create_doc = {
            'Formula': self.formula,
            'LatticeParameters': self.latticeParameters,
            'SpaceGroup_Number': self.spaceGroup['spacegroupNumber'],
            'Sites': hash_sites
        }
        hash_value = md5(json.dumps(hash_create_doc).encode('utf8')).hexdigest()
        return hash_value


