import numpy as np
from math import cos, sin, tan


def cubic():
    """
    cubic path
    :return:
    """
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "X": np.array([0.0, 0.5, 0.0]),
        "R": np.array([0.5, 0.5, 0.5]),
        "M": np.array([0.5, 0.5, 0.0]),
    }
    path = [["\\Gamma", "X", "M", "\\Gamma", "R", "X"], ["M", "R"]]
    return {"kpoints": kpoints, "path": path}


def fcc():
    """
    fcc path
    :return:
    """
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "K": np.array([3.0 / 8.0, 3.0 / 8.0, 3.0 / 4.0]),
        "L": np.array([0.5, 0.5, 0.5]),
        "U": np.array([5.0 / 8.0, 1.0 / 4.0, 5.0 / 8.0]),
        "W": np.array([0.5, 1.0 / 4.0, 3.0 / 4.0]),
        "X": np.array([0.5, 0.0, 0.5]),
    }
    path = [
        ["\\Gamma", "X", "W", "K", "\\Gamma", "L", "U", "W", "L", "K"],
        ["U", "X"],
    ]
    return {"kpoints": kpoints, "path": path}


def bcc():
    """
    bcc path
    :return:
    """
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "H": np.array([0.5, -0.5, 0.5]),
        "P": np.array([0.25, 0.25, 0.25]),
        "N": np.array([0.0, 0.0, 0.5]),
    }
    path = [["\\Gamma", "H", "N", "\\Gamma", "P", "H"], ["P", "N"]]
    return {"kpoints": kpoints, "path": path}


def tet():
    """
    tet path
    :return:
    """
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "A": np.array([0.5, 0.5, 0.5]),
        "M": np.array([0.5, 0.5, 0.0]),
        "R": np.array([0.0, 0.5, 0.5]),
        "X": np.array([0.0, 0.5, 0.0]),
        "Z": np.array([0.0, 0.0, 0.5]),
    }
    path = [
        ["\\Gamma", "X", "M", "\\Gamma", "Z", "R", "A", "Z"],
        ["X", "R"],
        ["M", "A"],
    ]
    return {"kpoints": kpoints, "path": path}


def bctet1(a, c):
    """
    bctet1 path
    :param a:
    :param c:
    :return:
    """
    eta = (1 + c ** 2 / a ** 2) / 4.0
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "M": np.array([-0.5, 0.5, 0.5]),
        "N": np.array([0.0, 0.5, 0.0]),
        "P": np.array([0.25, 0.25, 0.25]),
        "X": np.array([0.0, 0.0, 0.5]),
        "Z": np.array([eta, eta, -eta]),
        "Z_1": np.array([-eta, 1 - eta, eta]),
    }
    path = [["\\Gamma", "X", "M", "\\Gamma", "Z", "P", "N", "Z_1", "M"], ["X", "P"]]
    return {"kpoints": kpoints, "path": path}


def bctet2(a, c):
    """
    bctet2 path
    :param a:
    :param c:
    :return:
    """
    eta = (1 + a ** 2 / c ** 2) / 4.0
    zeta = a ** 2 / (2 * c ** 2)
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "N": np.array([0.0, 0.5, 0.0]),
        "P": np.array([0.25, 0.25, 0.25]),
        "\\Sigma": np.array([-eta, eta, eta]),
        "\\Sigma_1": np.array([eta, 1 - eta, -eta]),
        "X": np.array([0.0, 0.0, 0.5]),
        "Y": np.array([-zeta, zeta, 0.5]),
        "Y_1": np.array([0.5, 0.5, -zeta]),
        "Z": np.array([0.5, 0.5, -0.5]),
    }
    path = [["\\Gamma", "X", "Y", "\\Sigma", "\\Gamma", "Z", "\\Sigma_1", "N", "P", "Y_1", "Z"], ["X", "P"]]
    return {"kpoints": kpoints, "path": path}


def orc():
    """
    orc path
    :return:
    """
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "R": np.array([0.5, 0.5, 0.5]),
        "S": np.array([0.5, 0.5, 0.0]),
        "T": np.array([0.0, 0.5, 0.5]),
        "U": np.array([0.5, 0.0, 0.5]),
        "X": np.array([0.5, 0.0, 0.0]),
        "Y": np.array([0.0, 0.5, 0.0]),
        "Z": np.array([0.0, 0.0, 0.5]),
    }
    path = [
        ["\\Gamma", "X", "S", "Y", "\\Gamma", "Z", "U", "R", "T", "Z"],
        ["Y", "T"],
        ["U", "X"],
        ["S", "R"],
    ]
    return {"kpoints": kpoints, "path": path}


def orcf1(a, b, c):
    """
    orcf1 path
    :param a:
    :param b:
    :param c:
    :return:
    """
    zeta = (1 + a ** 2 / b ** 2 - a ** 2 / c ** 2) / 4
    eta = (1 + a ** 2 / b ** 2 + a ** 2 / c ** 2) / 4

    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "A": np.array([0.5, 0.5 + zeta, zeta]),
        "A_1": np.array([0.5, 0.5 - zeta, 1 - zeta]),
        "L": np.array([0.5, 0.5, 0.5]),
        "T": np.array([1, 0.5, 0.5]),
        "X": np.array([0.0, eta, eta]),
        "X_1": np.array([1, 1 - eta, 1 - eta]),
        "Y": np.array([0.5, 0.0, 0.5]),
        "Z": np.array([0.5, 0.5, 0.0]),
    }
    path = [
        ["\\Gamma", "Y", "T", "Z", "\\Gamma", "X", "A_1", "Y"],
        ["T", "X_1"],
        ["X", "A", "Z"],
        ["L", "\\Gamma"],
    ]
    return {"kpoints": kpoints, "path": path}


def orcf2(a, b, c):
    """
    orcf2 path
    :param a:
    :param b:
    :param c:
    :return:
    """
    phi = (1 + c ** 2 / b ** 2 - c ** 2 / a ** 2) / 4
    eta = (1 + a ** 2 / b ** 2 - a ** 2 / c ** 2) / 4
    delta = (1 + b ** 2 / a ** 2 - b ** 2 / c ** 2) / 4
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "C": np.array([0.5, 0.5 - eta, 1 - eta]),
        "C_1": np.array([0.5, 0.5 + eta, eta]),
        "D": np.array([0.5 - delta, 0.5, 1 - delta]),
        "D_1": np.array([0.5 + delta, 0.5, delta]),
        "L": np.array([0.5, 0.5, 0.5]),
        "H": np.array([1 - phi, 0.5 - phi, 0.5]),
        "H_1": np.array([phi, 0.5 + phi, 0.5]),
        "X": np.array([0.0, 0.5, 0.5]),
        "Y": np.array([0.5, 0.0, 0.5]),
        "Z": np.array([0.5, 0.5, 0.0]),
    }
    path = [
        ["\\Gamma", "Y", "C", "D", "X", "\\Gamma", "Z", "D_1", "H", "C"],
        ["C_1", "Z"],
        ["X", "H_1"],
        ["H", "Y"],
        ["L", "\\Gamma"],
    ]
    return {"kpoints": kpoints, "path": path}


def orcf3(a, b, c):
    """
    orcf3 path
    :param a:
    :param b:
    :param c:
    :return:
    """
    zeta = (1 + a ** 2 / b ** 2 - a ** 2 / c ** 2) / 4
    eta = (1 + a ** 2 / b ** 2 + a ** 2 / c ** 2) / 4
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "A": np.array([0.5, 0.5 + zeta, zeta]),
        "A_1": np.array([0.5, 0.5 - zeta, 1 - zeta]),
        "L": np.array([0.5, 0.5, 0.5]),
        "T": np.array([1, 0.5, 0.5]),
        "X": np.array([0.0, eta, eta]),
        "X_1": np.array([1, 1 - eta, 1 - eta]),
        "Y": np.array([0.5, 0.0, 0.5]),
        "Z": np.array([0.5, 0.5, 0.0]),
    }
    path = [
        ["\\Gamma", "Y", "T", "Z", "\\Gamma", "X", "A_1", "Y"],
        ["X", "A", "Z"],
        ["L", "\\Gamma"],
    ]
    return {"kpoints": kpoints, "path": path}


def orci(a, b, c):
    """
    orci path
    :param a:
    :param b:
    :param c:
    :return:
    """
    zeta = (1 + a ** 2 / c ** 2) / 4
    eta = (1 + b ** 2 / c ** 2) / 4
    delta = (b ** 2 - a ** 2) / (4 * c ** 2)
    mu = (a ** 2 + b ** 2) / (4 * c ** 2)
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "L": np.array([-mu, mu, 0.5 - delta]),
        "L_1": np.array([mu, -mu, 0.5 + delta]),
        "L_2": np.array([0.5 - delta, 0.5 + delta, -mu]),
        "R": np.array([0.0, 0.5, 0.0]),
        "S": np.array([0.5, 0.0, 0.0]),
        "T": np.array([0.0, 0.0, 0.5]),
        "W": np.array([0.25, 0.25, 0.25]),
        "X": np.array([-zeta, zeta, zeta]),
        "X_1": np.array([zeta, 1 - zeta, -zeta]),
        "Y": np.array([eta, -eta, eta]),
        "Y_1": np.array([1 - eta, eta, -eta]),
        "Z": np.array([0.5, 0.5, -0.5]),
    }
    path = [
        ["\\Gamma", "X", "L", "T", "W", "R", "X_1", "Z", "\\Gamma", "Y", "S", "W"],
        ["L_1", "Y"],
        ["Y_1", "Z"],
    ]
    return {"kpoints": kpoints, "path": path}


def orcc(a, b):
    """
    orcc path
    :param a:
    :param b:
    :return:
    """
    zeta = (1 + a ** 2 / b ** 2) / 4
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "A": np.array([zeta, zeta, 0.5]),
        "A_1": np.array([-zeta, 1 - zeta, 0.5]),
        "R": np.array([0.0, 0.5, 0.5]),
        "S": np.array([0.0, 0.5, 0.0]),
        "T": np.array([-0.5, 0.5, 0.5]),
        "X": np.array([zeta, zeta, 0.0]),
        "X_1": np.array([-zeta, 1 - zeta, 0.0]),
        "Y": np.array([-0.5, 0.5, 0]),
        "Z": np.array([0.0, 0.0, 0.5]),
    }
    path = [["\\Gamma", "X", "S", "R", "A", "Z", "\\Gamma", "Y", "X_1", "A_1", "T", "Y"], ["Z", "T"]]
    return {"kpoints": kpoints, "path": path}


def hex():
    """
    hex path
    :return:
    """
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "A": np.array([0.0, 0.0, 0.5]),
        "H": np.array([1.0 / 3.0, 1.0 / 3.0, 0.5]),
        "K": np.array([1.0 / 3.0, 1.0 / 3.0, 0.0]),
        "L": np.array([0.5, 0.0, 0.5]),
        "M": np.array([0.5, 0.0, 0.0]),
    }
    path = [
        ["\\Gamma", "M", "K", "\\Gamma", "A", "L", "H", "A"],
        ["L", "M"],
        ["K", "H"],
    ]
    return {"kpoints": kpoints, "path": path}


def rhl1(alpha):
    """
    rhl1 path
    :param alpha:
    :return:
    """
    eta = (1 + 4 * cos(alpha)) / (2 + 4 * cos(alpha))
    nu = 3.0 / 4.0 - eta / 2.0
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "B": np.array([eta, 0.5, 1.0 - eta]),
        "B_1": np.array([1.0 / 2.0, 1.0 - eta, eta - 1.0]),
        "F": np.array([0.5, 0.5, 0.0]),
        "L": np.array([0.5, 0.0, 0.0]),
        "L_1": np.array([0.0, 0.0, -0.5]),
        "P": np.array([eta, nu, nu]),
        "P_1": np.array([1.0 - nu, 1.0 - nu, 1.0 - eta]),
        "P_2": np.array([nu, nu, eta - 1.0]),
        "Q": np.array([1.0 - nu, nu, 0.0]),
        "X": np.array([nu, 0.0, -nu]),
        "Z": np.array([0.5, 0.5, 0.5]),
    }
    path = [
        ["\\Gamma", "L", "B_1"],
        ["B", "Z", "\\Gamma", "X"],
        ["Q", "F", "P_1", "Z"],
        ["L", "P"],
    ]
    return {"kpoints": kpoints, "path": path}


def rhl2(alpha):
    """
    rhl2 path
    :param alpha:
    :return:
    """
    eta = 1 / (2 * tan(alpha / 2.0) ** 2)
    nu = 3.0 / 4.0 - eta / 2.0
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "F": np.array([0.5, -0.5, 0.0]),
        "L": np.array([0.5, 0.0, 0.0]),
        "P": np.array([1 - nu, -nu, 1 - nu]),
        "P_1": np.array([nu, nu - 1.0, nu - 1.0]),
        "Q": np.array([eta, eta, eta]),
        "Q_1": np.array([1.0 - eta, -eta, -eta]),
        "Z": np.array([0.5, -0.5, 0.5]),
    }
    path = [["\\Gamma", "P", "Z", "Q", "\\Gamma", "F", "P_1", "Q_1", "L", "Z"]]
    return {"kpoints": kpoints, "path": path}


def mcl(b, c, alpha):
    """
    mcl path
    :param b:
    :param c:
    :param alpha:
    :return:
    """
    eta = (1 - b * cos(alpha) / c) / (2 * sin(alpha) ** 2)
    nu = 0.5 - eta * c * cos(alpha) / b
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "A": np.array([0.5, 0.5, 0.0]),
        "C": np.array([0.0, 0.5, 0.5]),
        "D": np.array([0.5, 0.0, 0.5]),
        "D_1": np.array([0.5, 0.5, -0.5]),
        "E": np.array([0.5, 0.5, 0.5]),
        "H": np.array([0.0, eta, 1.0 - nu]),
        "H_1": np.array([0.0, 1.0 - eta, nu]),
        "H_2": np.array([0.0, eta, -nu]),
        "M": np.array([0.5, eta, 1.0 - nu]),
        "M_1": np.array([0.5, 1 - eta, nu]),
        "M_2": np.array([0.5, 1 - eta, nu]),
        "X": np.array([0.0, 0.5, 0.0]),
        "Y": np.array([0.0, 0.0, 0.5]),
        "Y_1": np.array([0.0, 0.0, -0.5]),
        "Z": np.array([0.5, 0.0, 0.0]),
    }
    path = [
        ["\\Gamma", "Y", "H", "C", "E", "M_1", "A", "X", "H_1"],
        ["M", "D", "Z"],
        ["Y", "D"],
    ]
    return {"kpoints": kpoints, "path": path}


def mclc1(a, b, c, alpha):
    """
    mclc1 path
    :param a:
    :param b:
    :param c:
    :param alpha:
    :return:
    """
    zeta = (2 - b * cos(alpha) / c) / (4 * sin(alpha) ** 2)
    eta = 0.5 + 2 * zeta * c * cos(alpha) / b
    psi = 0.75 - a ** 2 / (4 * b ** 2 * sin(alpha) ** 2)
    phi = psi + (0.75 - psi) * b * cos(alpha) / c
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "N": np.array([0.5, 0.0, 0.0]),
        "N_1": np.array([0.0, -0.5, 0.0]),
        "F": np.array([1 - zeta, 1 - zeta, 1 - eta]),
        "F_1": np.array([zeta, zeta, eta]),
        "F_2": np.array([-zeta, -zeta, 1 - eta]),
        "I": np.array([phi, 1 - phi, 0.5]),
        "I_1": np.array([1 - phi, phi - 1, 0.5]),
        "L": np.array([0.5, 0.5, 0.5]),
        "M": np.array([0.5, 0.0, 0.5]),
        "X": np.array([1 - psi, psi - 1, 0.0]),
        "X_1": np.array([psi, 1 - psi, 0.0]),
        "X_2": np.array([psi - 1, -psi, 0.0]),
        "Y": np.array([0.5, 0.5, 0.0]),
        "Y_1": np.array([-0.5, -0.5, 0.0]),
        "Z": np.array([0.0, 0.0, 0.5]),
    }
    path = [
        ["\\Gamma", "Y", "F", "L", "I"],
        ["I_1", "Z", "F_1"],
        ["Y", "X_1"],
        ["X", "\\Gamma", "N"],
        ["M", "\\Gamma"],
    ]
    return {"kpoints": kpoints, "path": path}


def mclc2(a, b, c, alpha):
    """
    mclc2 path
    :param a:
    :param b:
    :param c:
    :param alpha:
    :return:
    """
    zeta = (2 - b * cos(alpha) / c) / (4 * sin(alpha) ** 2)
    eta = 0.5 + 2 * zeta * c * cos(alpha) / b
    psi = 0.75 - a ** 2 / (4 * b ** 2 * sin(alpha) ** 2)
    phi = psi + (0.75 - psi) * b * cos(alpha) / c
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "N": np.array([0.5, 0.0, 0.0]),
        "N_1": np.array([0.0, -0.5, 0.0]),
        "F": np.array([1 - zeta, 1 - zeta, 1 - eta]),
        "F_1": np.array([zeta, zeta, eta]),
        "F_2": np.array([-zeta, -zeta, 1 - eta]),
        "F_3": np.array([1 - zeta, -zeta, 1 - eta]),
        "I": np.array([phi, 1 - phi, 0.5]),
        "I_1": np.array([1 - phi, phi - 1, 0.5]),
        "L": np.array([0.5, 0.5, 0.5]),
        "M": np.array([0.5, 0.0, 0.5]),
        "X": np.array([1 - psi, psi - 1, 0.0]),
        "X_1": np.array([psi, 1 - psi, 0.0]),
        "X_2": np.array([psi - 1, -psi, 0.0]),
        "Y": np.array([0.5, 0.5, 0.0]),
        "Y_1": np.array([-0.5, -0.5, 0.0]),
        "Z": np.array([0.0, 0.0, 0.5]),
    }
    path = [
        ["\\Gamma", "Y", "F", "L", "I"],
        ["I_1", "Z", "F_1"],
        ["N", "\\Gamma", "M"],
    ]
    return {"kpoints": kpoints, "path": path}


def mclc3(a, b, c, alpha):
    """
    mclc3 path
    :param a:
    :param b:
    :param c:
    :param alpha:
    :return:
    """
    mu = (1 + b ** 2 / a ** 2) / 4.0
    delta = b * c * cos(alpha) / (2 * a ** 2)
    zeta = mu - 0.25 + (1 - b * cos(alpha) / c) / (4 * sin(alpha) ** 2)
    eta = 0.5 + 2 * zeta * c * cos(alpha) / b
    phi = 1 + zeta - 2 * mu
    psi = eta - 2 * delta
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "F": np.array([1 - phi, 1 - phi, 1 - psi]),
        "F_1": np.array([phi, phi - 1, psi]),
        "F_2": np.array([1 - phi, -phi, 1 - psi]),
        "H": np.array([zeta, zeta, eta]),
        "H_1": np.array([1 - zeta, -zeta, 1 - eta]),
        "H_2": np.array([-zeta, -zeta, 1 - eta]),
        "I": np.array([0.5, -0.5, 0.5]),
        "M": np.array([0.5, 0.0, 0.5]),
        "N": np.array([0.5, 0.0, 0.0]),
        "N_1": np.array([0.0, -0.5, 0.0]),
        "X": np.array([0.5, -0.5, 0.0]),
        "Y": np.array([mu, mu, delta]),
        "Y_1": np.array([1 - mu, -mu, -delta]),
        "Y_2": np.array([-mu, -mu, -delta]),
        "Y_3": np.array([mu, mu - 1, delta]),
        "Z": np.array([0.0, 0.0, 0.5]),
    }
    path = [
        ["\\Gamma", "Y", "F", "H", "Z", "I", "F_1"],
        ["H_1", "Y_1", "X", "\\Gamma", "N"],
        ["M", "\\Gamma"],
    ]
    return {"kpoints": kpoints, "path": path}


def mclc4(a, b, c, alpha):
    """
    mclc4 path
    :param a:
    :param b:
    :param c:
    :param alpha:
    :return:
    """
    mu = (1 + b ** 2 / a ** 2) / 4.0
    delta = b * c * cos(alpha) / (2 * a ** 2)
    zeta = mu - 0.25 + (1 - b * cos(alpha) / c) / (4 * sin(alpha) ** 2)
    eta = 0.5 + 2 * zeta * c * cos(alpha) / b
    phi = 1 + zeta - 2 * mu
    psi = eta - 2 * delta
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "F": np.array([1 - phi, 1 - phi, 1 - psi]),
        "F_1": np.array([phi, phi - 1, psi]),
        "F_2": np.array([1 - phi, -phi, 1 - psi]),
        "H": np.array([zeta, zeta, eta]),
        "H_1": np.array([1 - zeta, -zeta, 1 - eta]),
        "H_2": np.array([-zeta, -zeta, 1 - eta]),
        "I": np.array([0.5, -0.5, 0.5]),
        "M": np.array([0.5, 0.0, 0.5]),
        "N": np.array([0.5, 0.0, 0.0]),
        "N_1": np.array([0.0, -0.5, 0.0]),
        "X": np.array([0.5, -0.5, 0.0]),
        "Y": np.array([mu, mu, delta]),
        "Y_1": np.array([1 - mu, -mu, -delta]),
        "Y_2": np.array([-mu, -mu, -delta]),
        "Y_3": np.array([mu, mu - 1, delta]),
        "Z": np.array([0.0, 0.0, 0.5]),
    }
    path = [
        ["\\Gamma", "Y", "F", "H", "Z", "I"],
        ["H_1", "Y_1", "X", "\\Gamma", "N"],
        ["M", "\\Gamma"],
    ]
    return {"kpoints": kpoints, "path": path}


def mclc5(a, b, c, alpha):
    """
    mclc5 path
    :param a:
    :param b:
    :param c:
    :param alpha:
    :return:
    """
    zeta = (b ** 2 / a ** 2 + (1 - b * cos(alpha) / c) / sin(alpha) ** 2) / 4
    eta = 0.5 + 2 * zeta * c * cos(alpha) / b
    mu = eta / 2 + b ** 2 / (4 * a ** 2) - b * c * cos(alpha) / (2 * a ** 2)
    nu = 2 * mu - zeta
    rho = 1 - zeta * a ** 2 / b ** 2
    omega = (4 * nu - 1 - b ** 2 * sin(alpha) ** 2 / a ** 2) * c / (2 * b * cos(alpha))
    delta = zeta * c * cos(alpha) / b + omega / 2 - 0.25
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "F": np.array([nu, nu, omega]),
        "F_1": np.array([1 - nu, 1 - nu, 1 - omega]),
        "F_2": np.array([nu, nu - 1, omega]),
        "H": np.array([zeta, zeta, eta]),
        "H_1": np.array([1 - zeta, -zeta, 1 - eta]),
        "H_2": np.array([-zeta, -zeta, 1 - eta]),
        "I": np.array([rho, 1 - rho, 0.5]),
        "I_1": np.array([1 - rho, rho - 1, 0.5]),
        "L": np.array([0.5, 0.5, 0.5]),
        "M": np.array([0.5, 0.0, 0.5]),
        "N": np.array([0.5, 0.0, 0.0]),
        "N_1": np.array([0.0, -0.5, 0.0]),
        "X": np.array([0.5, -0.5, 0.0]),
        "Y": np.array([mu, mu, delta]),
        "Y_1": np.array([1 - mu, -mu, -delta]),
        "Y_2": np.array([-mu, -mu, -delta]),
        "Y_3": np.array([mu, mu - 1, delta]),
        "Z": np.array([0.0, 0.0, 0.5]),
    }
    path = [
        ["\\Gamma", "Y", "F", "L", "I"],
        ["I_1", "Z", "H", "F_1"],
        ["H_1", "Y_1", "X", "\\Gamma", "N"],
        ["M", "\\Gamma"],
    ]
    return {"kpoints": kpoints, "path": path}


def tria():
    """
    tria path
    :return:
    """
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "L": np.array([0.5, 0.5, 0.0]),
        "M": np.array([0.0, 0.5, 0.5]),
        "N": np.array([0.5, 0.0, 0.5]),
        "R": np.array([0.5, 0.5, 0.5]),
        "X": np.array([0.5, 0.0, 0.0]),
        "Y": np.array([0.0, 0.5, 0.0]),
        "Z": np.array([0.0, 0.0, 0.5]),
    }
    path = [
        ["X", "\\Gamma", "Y"],
        ["L", "\\Gamma", "Z"],
        ["N", "\\Gamma", "M"],
        ["R", "\\Gamma"],
    ]
    return {"kpoints": kpoints, "path": path}


def trib():
    """
    trib path
    :return:
    """
    kpoints = {
        "\\Gamma": np.array([0.0, 0.0, 0.0]),
        "L": np.array([0.5, -0.5, 0.0]),
        "M": np.array([0.0, 0.0, 0.5]),
        "N": np.array([-0.5, -0.5, 0.5]),
        "R": np.array([0.0, -0.5, 0.5]),
        "X": np.array([0.0, -0.5, 0.0]),
        "Y": np.array([0.5, 0.0, 0.0]),
        "Z": np.array([-0.5, 0.0, 0.5]),
    }
    path = [
        ["X", "\\Gamma", "Y"],
        ["L", "\\Gamma", "Z"],
        ["N", "\\Gamma", "M"],
        ["R", "\\Gamma"],
    ]
    return {"kpoints": kpoints, "path": path}
