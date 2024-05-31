"""
文件用于定义晶格结构
"""
from typing import List, Union
import numpy as np


class Lattice:
    """
    构建一个晶体对象
    """

    def __init__(self, matrix: Union[List[float], List[List[float]], np.ndarray]):
        m = np.array(matrix, dtype=np.float64).reshape((3, 3))
        m.setflags(write=False)
        self.matrix = m

