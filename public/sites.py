"""
文件用于定义site
"""


from typing import Union, Tuple, List
import numpy as np

from public.tools.periodic_table import PTable


class Atom:
    """
    构建原子信息
    """
    def __init__(self, atomicsymbol: str):
        self.atomicsymbol = atomicsymbol
        self.atomicnumber = PTable().detailed[atomicsymbol]["Atomic no"]
        self.atomicmass = PTable().detailed[atomicsymbol]["Atomic mass"]


class Site:
    """
    构建站点对象
    """

    def __init__(self, coords: Union[Tuple, List, np.ndarray],
                 atom: Atom, force=None):

        self.coords = coords
        self.atom = atom
        self.force = force
        self.Occupancy = 1.0
        self.Magmom = 0.0


    def set_occupancy(self, occ: float):
        """
        设置occupancy值
        :param occ:
        :return:
        """
        self.Occupancy = occ

    def set_magmom(self, mag: float):
        """
        设置magmom值
        :param mag:
        :return:
        """
        self.Magmom = mag
