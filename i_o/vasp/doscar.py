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
        IsSpinPolarized = False
        line_index = 6 + self.N

        return {
            "IsSpinPolarized": IsSpinPolarized,
            "NumberOfGridPoints": self.N,
            "NumberOfIons": self.NIon,
            "DecomposedLength": DecomposedLength,
            "IsLmDecomposed": IsLmDecomposed,
            "Energies": Energies,
            "PartialDosData": PartialDosData
        }
