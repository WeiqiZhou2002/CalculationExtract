from enum import Enum


class Spin(enumerate):
    up = '0'
    down = '1'


class Orbitals(enumerate):
    s = 0
    py = 1
    pz = 2
    px = 3
    dxy = 4
    dyz = 5
    dz2 = 6
    dxz = 7
    dx2 = 8
    f_3 = 9
    f_2 = 10
    f_1 = 11
    f0 = 12
    f1 = 13
    f2 = 14
    f3 = 15


class OrbitalType(enumerate):
    s = 0
    p = 1
    d = 2
    f = 3


