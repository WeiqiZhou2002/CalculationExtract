import unittest
import os

import numpy as np

from i_o.vasp.vasprun import Vasprun


class TestVasprun(unittest.TestCase):
    def setUp(self):
        self.test_file = "testdata/vasprun.xml"

    def test_initialization(self):
        vasprun = Vasprun(self.test_file)
        self.assertIsNotNone(vasprun.root)
        self.assertEqual(vasprun.filename, self.test_file)

    def test_getLatticeParameters(self):
        vasprun = Vasprun(self.test_file)
        init_lattice = vasprun.getLatticeParameters(isinit=True)
        final_lattice = vasprun.getLatticeParameters(isinit=False)
        self.assertIsNotNone(init_lattice)
        self.assertIsNotNone(final_lattice)


    def test_getComposition(self):
        vasprun = Vasprun(self.test_file)
        composition = vasprun.getComposition()
        self.assertIsNotNone(composition)
        self.assertEqual(len(composition), 3)
        self.assertEqual(composition[0].atomic_symbol, 'O')
        self.assertEqual(composition[1].atomic_symbol, 'Ti')
        self.assertEqual(composition[2].atomic_symbol, 'U')

    def test_getVolume(self):
        vasprun = Vasprun(self.test_file)
        init_volume = vasprun.getVolume(isinit=True)
        final_volume = vasprun.getVolume(isinit=False)
        self.assertEqual(init_volume, 545.00274423)
        self.assertEqual(final_volume, 576.80049773)

    def test_getParameters(self):
        vasprun = Vasprun(self.test_file)
        vasprun.setup()
        parameters = vasprun.getParameters()
        self.assertIsNotNone(parameters)
        self.assertEqual(parameters['PREC'], 'accurate')
        self.assertEqual(parameters['ISPIN'], 2)
        self.assertEqual(parameters['ENCUT'], 500.0)
        self.assertEqual(parameters['IBRION'], 2)

    def test_getSoftware(self):
        vasprun = Vasprun(self.test_file)
        software = vasprun.getSoftware()
        self.assertIsNotNone(software)
        self.assertEqual(software['SoftwareName'], 'vasp')
        self.assertEqual(software['SoftwareVersion'], '5.4.4.18Apr17-6-g9f103f2a35')

    def test_getStartTime(self):
        vasprun = Vasprun(self.test_file)
        start_time = vasprun.getStartTime()
        self.assertEqual(start_time, "2018-01-25 15:48:48")


if __name__ == "__main__":
    unittest.main()
