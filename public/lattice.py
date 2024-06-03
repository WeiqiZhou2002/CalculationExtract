#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract
@File       : lattice.py
@IDE        : PyCharm
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 16:35
@Description:
"""
import numpy as np
from monty.json import MSONable
from typing import List,Union
from numpy._typing import ArrayLike
from public.tools.typing import PbcLike


class Lattice(MSONable):
    def __init__(self, matrix: Union[List[float], List[List[float]], np.ndarray]) -> None:
        matrix = np.array(matrix, dtype=np.float64).reshape((3, 3))
        matrix.setflags(write=False)
        self.matrix = matrix

    def from_parameters(self, a, b, c, alpha, beta, gamma) :
        """
        从晶胞参数构建晶格矩阵
        :param a:
        :param b:
        :param c:
        :param alpha:
        :param beta:
        :param gamma:
        :return:
        """
        matrix = np.zeros((3, 3))

        return self(matrix)

    def as_dict(self) -> dict:
        return {"matrix": self.matrix.tolist()}

    def parameters(self) -> tuple[float, float, float, float, float, float]:
        """
        返回晶胞参数 a, b, c, alpha, beta, gamma
        :return:
        """
        pass


if __name__ == '__main__':
    matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    lattice = Lattice(matrix)
    la = Lattice.from_parameters(1, 1, 1, 90, 90, 90)
    print(lattice.matrix)
    print(lattice.as_dict())

