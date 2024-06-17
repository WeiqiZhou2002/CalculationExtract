import io
import unittest
from unittest.mock import mock_open, patch
import numpy as np
import xml.etree.ElementTree as ET

from i_o.vasp.doscar import Doscar
from i_o.vasp.procar import Procar
from i_o.vasp.chgcar import Chgcar
from i_o.vasp.vasprun import Vasprun


class TestProcar(unittest.TestCase):

    def setUp(self):
        with open("testdata/PROCAR", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        procar = Procar("fakefile")
        self.assertEqual(procar.filename, "fakefile")
        self.assertEqual(procar.nkpoints, 0)
        self.assertEqual(procar.nbands, 0)
        self.assertEqual(procar.nions, 0)

    @patch("builtins.open", new_callable=mock_open)
    def test_read_procar_file(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        procar = Procar("fakefile")
        self.assertEqual(procar.nkpoints, 75)
        self.assertEqual(procar.nbands, 252)
        self.assertEqual(procar.nions, 48)
        self.assertEqual(procar.KPoints[0], [0.0, 0.0, 0.0])
        self.assertEqual(procar.eigenvalues[0][0][0], -53.70320926)
        self.assertEqual(procar.occupancies[0][0][0], 2.00000000)
        self.assertEqual(procar.IsSpinPolarized, False)

    @patch("builtins.open", new_callable=mock_open)
    def test_get_projected_info(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        procar = Procar("fakefile")
        info = procar.getProjectedEigenvalOnIonOrbitals()
        self.assertEqual(info["Decomposed"], ['s', 'py', 'pz', 'px', 'dxy', 'dyz', 'dz2', 'dxz', 'x2-y2'])
        self.assertEqual(info["DecomposedLength"], 9)
        self.assertEqual(info["IsLmDecomposed"], True)


class TestChgcar(unittest.TestCase):

    def setUp(self):
        with open("testdata/CHGCAR", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        chgcar = Chgcar("fakefile")
        self.assertEqual(chgcar.filename, "fakefile")
        self.assertEqual(chgcar.NGX, 0)
        self.assertEqual(chgcar.NGY, 0)
        self.assertEqual(chgcar.NGZ, 0)
        self.assertTrue((chgcar.GRID == np.zeros((0, 0, 0))).all())

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        with self.assertRaises(ValueError) as context:
            chgcar = Chgcar("fakefile")
            info = chgcar.getChgcarInfo()
        self.assertIn("File fakefile is too short to be a valid CHGCAR file.", str(context.exception))

    @patch("builtins.open", new_callable=mock_open)
    def test_get_chgcar_info(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        chgcar = Chgcar("fakefile")
        info = chgcar.getChgcarInfo()
        self.assertEqual(info["NGX"], 72)
        self.assertEqual(info["NGY"], 72)
        self.assertEqual(info["NGZ"], 320)
        # expected_grid = [[[0.1, 0.2], [0.3, 0.4]], [[0.5, 0.6], [0.7, 0.8]]]
        # self.assertEqual(info["GRID"], expected_grid)
        # sample too large, wait to be finished

class TestDoscar(unittest.TestCase):

    def setUp(self):
        with open("testdata/DOSCAR", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        doscar = Doscar("fakefile")
        self.assertEqual(doscar.filename, "fakefile")
        self.assertEqual(doscar.NIon, None)
        self.assertEqual(doscar.N, None)
        self.assertEqual(doscar.energies, None)
        self.assertEqual(doscar.total, None)
        self.assertEqual(doscar.projected, None)


    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        with self.assertRaises(ValueError) as context:
            doscar = Doscar("fakefile")
            doscar.setup()
        self.assertIn("File fakefile is too short to be a valid DOSCAR file.", str(context.exception))

    @patch("builtins.open", new_callable=mock_open)
    def test_get_totalDos(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        doscar = Doscar("fakefile")
        doscar.setup()
        info = doscar.getTotalDos()
        self.assertEqual(info["IsSpinPolarized"], True)
        self.assertEqual(info["NumberOfGridPoints"], 301)
        self.assertEqual(info["Energies"][0], -56.924)
        self.assertEqual(info["TdosData"][0][0], 0)
        # whole list check


# class TestVasprun(unittest.TestCase):
#
#     def setUp(self):
#         # 设置模拟的 Vasprun 文件内容
#         with open("testdata/vasprun.xml", "r") as file:
#             self.mock_data = file.read()
#
#     @patch("builtins.open", new_callable=mock_open, read_data="")
#     def test_init_empty_file(self, mock_file):
#         with self.assertRaises(ValueError) as context:
#             vasprun = Vasprun("fakefile")
#         self.assertIn("File content error, not parse!", str(context.exception))
#
#     @patch("builtins.open", new_callable=mock_open)
#     def test_init_valid_file(self, mock_file):
#         # 设置 ET.parse 正常解析模拟的文件内容
#         mock_file.return_value.__enter__.return_value = io.StringIO(self.mock_data)
#
#         vasprun = Vasprun("testdata/vasprun.xml")
#         self.assertEqual(vasprun.filename, "vasprun.xml")
#         self.assertIsNotNone(vasprun.root)
#
#     @patch("builtins.open", new_callable=mock_open)
#     @patch("xml.etree.ElementTree.parse")
#     def test_get_software(self,mock_parse, mock_file):
#         # 设置 mock 文件内容为 self.mock_data
#         mock_file.return_value.readline.return_value = self.mock_data
#         mock_parse.return_value = ET.ElementTree(ET.fromstring(self.mock_data))
#
#         vasprun = Vasprun("testdata/vasprun.xml")
#         software_info = vasprun.getSoftware()
#         self.assertEqual(software_info["SoftwareName"], "VASP")
#         self.assertEqual(software_info["SoftwareVersion"], "5.4.4")
#         self.assertEqual(software_info["Subversion"], "subver 1.0")
#         self.assertEqual(software_info["Platform"], "Linux")

if __name__ == "__main__":
    unittest.main()
