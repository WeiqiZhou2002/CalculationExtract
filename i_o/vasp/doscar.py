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

    def setup(self):
        self.NIon = int(self.lines[0].split()[0])
        self.N = int(self.lines[5].split()[2])
        self.getTotalDos()

    def getTotalDos(self):
        IsSpinPolarized = False
        self.energies = np.zeros(self.N)
        self.total = None
        for i in range(self.N):
            fields = np.array(self.lines[6 + i].split(), dtype=float)
            if i == 0:
                if len(fields) == 3:  # energy, total
                    IsSpinPolarized = False
                    self.total = np.zeros((1, self.N))
                else:  # energy, spin-up, spin-down
                    IsSpinPolarized = True
                    self.total = np.zeros((2, self.N))
            self.energies[i] = fields[0]
            if IsSpinPolarized:
                self.total[0, i] = fields[1]
                self.total[1, i] = fields[2]
            else:
                self.total[0, i] = fields[1]
        return {
            "IsSpinPolarized": IsSpinPolarized,
            "NumberOfGridPoints": self.N,
            "Energies": self.energies,
            "TdosData": self.total
        }

    def getPatialDos(self):
        projected = None
        IsSpinPolarized = False
        IsLmProjected = False
        line_index = 6 + self.N
        DecomposedLength = 0
        for i in range(self.NIon):
            line_index += 1
            for j in range(self.N):
                fields = np.array(self.lines[line_index].split(), dtype=float)
                line_index += 1
                DecomposedLength = len(fields) - 1
                if i == 0 and j == 0:
                    if len(fields) == 4:  # spd
                        IsSpinPolarized = False
                        IsLmProjected = False
                        projected = np.zeros((self.NIon, 3, 1, self.N))
                    elif len(fields) == 5:  # spdf
                        IsSpinPolarized = False
                        IsLmProjected = False
                        projected = np.zeros((self.NIon, 4, 1, self.N))
                    elif len(fields) == 7:  # spd with spin polarization
                        IsSpinPolarized = True
                        IsLmProjected = False
                        projected = np.zeros((self.NIon, 3, 2, self.N))
                    elif len(fields) == 9:  # spdf with spin polarization
                        IsSpinPolarized = True
                        IsLmProjected = False
                        projected = np.zeros((self.NIon, 4, 2, self.N))
                    elif len(fields) == 10:  # partial orbital of spd without spin
                        IsSpinPolarized = False
                        IsLmProjected = True
                        projected = np.zeros((self.NIon, 9, 1, self.N))
                    elif len(fields) == 17:  # partial orbitals of spdf without spin
                        IsSpinPolarized = False
                        IsLmProjected = True
                        projected = np.zeros((self.NIon, 16, 1, self.N))
                    elif len(fields) == 19:  # partial orbital of spd with spin
                        IsSpinPolarized = True
                        IsLmProjected = True
                        projected = np.zeros((self.NIon, 9, 2, self.N))
                    else:  # partial orbitals of spdf with spin
                        IsSpinPolarized = True
                        IsLmProjected = True
                        projected = np.zeros((self.NIon, 16, 2, self.N))
                if IsLmProjected:
                    if IsSpinPolarized:
                        for k in range(16 if len(fields) > 19 else 9):
                            projected[i, k, 0, j] = fields[1 + k * 2]
                            projected[i, k, 1, j] = fields[2 + k * 2]
                    else:
                        for k in range(16 if len(fields) > 10 else 9):
                            projected[i, k, 0, j] = fields[1 + k]
                else:
                    if IsSpinPolarized:
                        for k in range(4 if len(fields) > 7 else 3):
                            projected[i, k, 0, j] = fields[1 + k * 2]
                            projected[i, k, 1, j] = fields[2 + k * 2]
                    else:
                        for k in range(4 if len(fields) > 4 else 3):
                            projected[i, k, 0, j] = fields[1 + k]

        return {
            "IsSpinPolarized": IsSpinPolarized,
            "NumberOfGridPoints": self.N,
            "NumberOfIons": self.NIon,
            "DecomposedLength": DecomposedLength,
            "IsLmDecomposed": IsLmProjected,
            "Energies": self.energies,
            "PartialDosData": projected
        }
