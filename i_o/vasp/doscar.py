import warnings

import numpy as np


class Doscar:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'r') as f:
            self.lines = f.readlines()
        self.NIon = None
        self.N = None
        self.energies = None
        self.total = None
        self.projected = None

    def getTotalDos(self):
        if len(self.lines) <= 5:
            warnings.warn(f"File {self.filename} is too short to be a valid DOSCAR file.")
            return {}
        self.NIon = int(self.lines[0].split()[0])
        self.N = int(self.lines[5].split()[2])
        IsSpinPolarized = False
        self.energies = np.zeros(self.N)
        self.total = {}
        data1 = []
        data2 = []
        for i in range(self.N):
            fields = np.array(self.lines[6 + i].split(), dtype=float)
            if i == 0:
                if len(fields) == 3:  # energy, total
                    IsSpinPolarized = False
                    data1=[]
                    data2=[]
                else:  # energy, spin-up, spin-down
                    IsSpinPolarized = True
                    data1 = []
            self.energies[i] = fields[0]
            if IsSpinPolarized:
                data1.append(fields[1])
                data2.append(fields[2])
            else:
                data1.append(fields[1])
        self.total['0']=list(data1)
        if IsSpinPolarized:
            self.total['1']=list(data2)
        return {
            "IsSpinPolarized": IsSpinPolarized,
            "NumberOfGridPoints": self.N,
            "Energies": self.energies.tolist(),
            "TdosData": self.total
        }

    def getPartialDos(self):
        if len(self.lines) < 5:
            warnings.warn(f"File {self.filename} is too short to be a valid EIGENVAL file.")
            return {}
        self.NIon = int(self.lines[0].split()[0])
        self.N = int(self.lines[5].split()[2])
        projected = None
        IsSpinPolarized = False
        IsLmProjected = False
        line_index = 6 + self.N
        DecomposedLength = 0
        orbitals = []
        PartialDosData = []
        for i in range(self.NIon):
            line_index += 1
            fields = np.array(self.lines[line_index].split(), dtype=float)
            if len(fields) == 4:  # spd
                IsSpinPolarized = False
                IsLmProjected = False
                orbitals = ['s', 'p', 'd']
                projected = {orb: [] for orb in orbitals}
            elif len(fields) == 5:  # spdf
                IsSpinPolarized = False
                IsLmProjected = False
                orbitals = ['s', 'p', 'd', 'f']
                projected = {orb: [] for orb in orbitals}
            elif len(fields) == 7:  # spd with spin polarization
                IsSpinPolarized = True
                IsLmProjected = False
                orbitals = ['s', 'p', 'd']
                projected = {orb: {'up': [], 'down': []} for orb in orbitals}
            elif len(fields) == 9:  # spdf with spin polarization
                IsSpinPolarized = True
                IsLmProjected = False
                orbitals = ['s', 'p', 'd', 'f']
                projected = {orb: {'up': [], 'down': []} for orb in orbitals}
            elif len(fields) == 10:  # partial orbital of spd without spin
                IsSpinPolarized = False
                IsLmProjected = True
                orbitals = ['s', 'py', 'pz', 'px', 'dxy', 'dyz', 'dz2', 'dxz', 'dx2-y2']
                projected = {orb: [] for orb in orbitals}
            elif len(fields) == 17:  # partial orbitals of spdf without spin
                IsSpinPolarized = False
                IsLmProjected = True
                orbitals = ['s', 'py', 'pz', 'px', 'dxy', 'dyz', 'dz2', 'dxz', 'dx2-y2', 'fy(3x2-y2)', 'fxyz',
                            'fyz2', 'fz3', 'fxz2', 'fz(x2-y2)', 'fx(x2-3y2)']
                projected = {orb: [] for orb in orbitals}
            elif len(fields) == 19:  # partial orbital of spd with spin
                IsSpinPolarized = True
                IsLmProjected = True
                orbitals = ['s', 'py', 'pz', 'px', 'dxy', 'dyz', 'dz2', 'dxz', 'dx2-y2']
                projected = {orb: {'up': [], 'down': []} for orb in orbitals}
            else:  # partial orbitals of spdf with spin
                IsSpinPolarized = True
                IsLmProjected = True
                orbitals = ['s', 'py', 'pz', 'px', 'dxy', 'dyz', 'dz2', 'dxz', 'dx2-y2', 'fy(3x2-y2)', 'fxyz',
                            'fyz2', 'fz3', 'fxz2', 'fz(x2-y2)', 'fx(x2-3y2)']
                projected = {orb: {'up': [], 'down': []} for orb in orbitals}
            for j in range(self.N):
                fields = np.array(self.lines[line_index].split(), dtype=float)
                line_index += 1
                DecomposedLength = len(fields) - 1
                if IsLmProjected:
                    if IsSpinPolarized:
                        DecomposedLength = DecomposedLength / 2
                        for k, orb in enumerate(orbitals):
                            projected[orb]['up'].append(fields[1 + k * 2])
                            projected[orb]['down'].append(fields[2 + k * 2])
                    else:
                        for k, orb in enumerate(orbitals):
                            projected[orb].append(fields[1 + k])
                else:
                    if IsSpinPolarized:
                        DecomposedLength = DecomposedLength / 2
                        for k, orb in enumerate(orbitals):
                            projected[orb]['up'].append(fields[1 + k * 2])
                            projected[orb]['down'].append(fields[2 + k * 2])
                    else:
                        for k, orb in enumerate(orbitals):
                            projected[orb].append(fields[1 + k])
            PartialDosData.append(projected)

        return {
            "IsSpinPolarized": IsSpinPolarized,
            "NumberOfGridPoints": self.N,
            "NumberOfIons": self.NIon,
            "DecomposedLength": DecomposedLength,
            "IsLmDecomposed": IsLmProjected,
            "Energies": self.energies.tolist(),
            "PartialDosData": PartialDosData
        }
