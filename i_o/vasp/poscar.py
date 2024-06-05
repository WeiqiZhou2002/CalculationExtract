#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : poscar.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:30 
@Description: 
"""
import numpy as np
from public.tools.periodic_table import PTable
from public.composition import Composition
from public.lattice import Lattice
from public.structure import Structure
from public.sites import Atom,Site


class Poscar:
    def __init__(self, filename):
        self.filename = filename

        if self.filename is None:
            raise ValueError('File content error, not parse!')
        with open(self.filename, 'r') as f:
            self.lines = f.readlines()
        self.lattice = None
        self.composition = None
        self.volume = None
        self.numberOfSites = None
        self.structure = None
        self.sites = None

    def setup(self):
        self.lattice = self.getLattice()
        self.composition = self.getComposition()
        self.volume = self.getVolume()
        self.numberOfSites = self.getNumberOfSites()
        self.sites = self.getSites()
        self.structure = Structure(lattice=self.lattice, composition=self.composition,sites=self.sites)
        self.structure.setup()


    def getComposition(self):
        elements = self.lines[5].split()
        counts = list(map(int, self.lines[6].split()))
        composition = []
        for element, count in zip(elements, counts):
            composition.append(Composition(atomic_symbol=element,
                                           atomic_number=PTable().detailed[element]["Atomic no"],
                                           atomic_mass=PTable().detailed[element]["Atomic mass"],
                                           amount=count))
        return composition

    def getLattice(self):
        matrix = [
            list(map(float, self.lines[2].split())),
            list(map(float, self.lines[3].split())),
            list(map(float, self.lines[4].split()))
        ]
        lattice = Lattice(matrix)

        return lattice

    def getVolume(self):
        matrix = np.array([
            list(map(float, self.lines[2].split())),
            list(map(float, self.lines[3].split())),
            list(map(float, self.lines[4].split()))
        ])
        vol = np.dot(matrix[0], np.cross(matrix[1], matrix[2]))
        return float(abs(vol))

    def getNumberOfSites(self):
        counts = list(map(int, self.lines[6].split()))
        number_of_sites_from_counts = sum(counts)
        return number_of_sites_from_counts

    def getSites(self):
        coords_start_line = 8
        sites = []
        atom_index = 0
        if self.lines[8].strip().lower() in ["direct", "cartesian"]:
            coords_start_line += 1
        for comp in self.composition:
            atom = Atom(comp.atomic_symbol)
            for _ in range(comp.amount):
                coords = list(map(float, self.lines[coords_start_line + atom_index].split()[:3]))
                site = Site(coords=coords, atom=atom)
                sites.append(site)
                atom_index += 1
        return sites