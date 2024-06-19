
import unittest
import warnings
from unittest.mock import mock_open, patch
import numpy as np


from i_o.vasp.doscar import Doscar
from i_o.vasp.eigenval import Eigenval
from i_o.vasp.incar import Incar
from i_o.vasp.oszicar import Oszicar
from i_o.vasp.outcar import Outcar
from i_o.vasp.poscar import Poscar
from i_o.vasp.procar import Procar
from i_o.vasp.chgcar import Chgcar



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

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            procar = Procar("fakefile")
            info = procar.getEigenValues()
            self.assertTrue(len(w) > 0)
            self.assertTrue(any(item.category == UserWarning for item in w))
            self.assertTrue(
                any("File fakefile is too short to be a valid PROCAR file." in str(item.message) for item in w))
            self.assertEqual(info, {})

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
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            chgcar = Chgcar("fakefile")
            info = chgcar.getChgcarInfo()
            self.assertTrue(len(w) > 0)
            self.assertTrue(any(item.category == UserWarning for item in w))
            self.assertTrue(
                any("File fakefile is too short to be a valid CHGCAR file." in str(item.message) for item in w))
            self.assertEqual(info, {})

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
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            doscar = Doscar("fakefile")
            info = doscar.getTotalDos()
            self.assertTrue(len(w) > 0)
            self.assertTrue(any(item.category == UserWarning for item in w))
            self.assertTrue(
                any("File fakefile is too short to be a valid DOSCAR file." in str(item.message) for item in w))
            self.assertEqual(info, {})


    @patch("builtins.open", new_callable=mock_open)
    def test_get_totalDos(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        doscar = Doscar("fakefile")
        info = doscar.getTotalDos()
        self.assertEqual(info["IsSpinPolarized"], True)
        self.assertEqual(info["NumberOfGridPoints"], 301)
        self.assertEqual(info["Energies"][0], -56.924)
        self.assertEqual(info["TdosData"][0][0], 0)
        # whole list check


class TestEigenval(unittest.TestCase):

    def setUp(self):
        with open("testdata/EIGENVAL", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        eigenval = Eigenval("fakefile")
        self.assertEqual(eigenval.filename, "fakefile")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            eigenval = Eigenval("fakefile")
            info = eigenval.getEigenValues()
            self.assertTrue(len(w) > 0)
            self.assertTrue(any(item.category == UserWarning for item in w))
            self.assertTrue(
                any("File fakefile is too short to be a valid EIGENVAL file." in str(item.message) for item in w))
            self.assertEqual(info, {})


    @patch("builtins.open", new_callable=mock_open)
    def test_get_eigenval(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        eigenval = Eigenval("fakefile")
        info = eigenval.getEigenValues()
        self.assertEqual(info["NumberOfGeneratedKPoints"], 180)
        self.assertEqual(info["NumberOfBand"], 32)
        self.assertEqual(info["IsSpinPolarized"], True)
        self.assertEqual(info["KPoints"][1][0], 0.02631579)
        self.assertEqual(info["EigenvalData"]["spin 1"][0][0], -6.901047)
        self.assertEqual(info["EigenvalOcc"]["spin 1"][0][0], 1.0)
        # whole list check


class TestIncar(unittest.TestCase):

    def setUp(self):
        with open("testdata/INCAR", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        incar = Incar("fakefile")
        self.assertEqual(incar.filename, "fakefile")
        self.assertEqual(incar.calculationType, None)

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        with self.assertRaises(ValueError) as context:
            incar = Incar("fakefile")
            calType = incar.getCalType()
        self.assertIn("无法判断提取类型，无法提取", str(context.exception))

    @patch("builtins.open", new_callable=mock_open)
    def test_get_caltype(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        incar = Incar("fakefile")
        caltype = incar.getCalType()
        self.assertEqual(caltype, 'DensityOfStates')


class TestOszicar(unittest.TestCase):

    def setUp(self):
        with open("testdata/OSZICAR", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        oszicar = Oszicar("fakefile")
        self.assertEqual(oszicar.filename, "fakefile")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        oszicar = Oszicar("fakefile")
        info = oszicar.getLinearMagneticMoment()
        self.assertEqual(info, 0)

    @patch("builtins.open", new_callable=mock_open)
    def test_get_caltype(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        oszicar = Oszicar("fakefile")
        info = oszicar.getLinearMagneticMoment()
        self.assertEqual(info, 0.0004)


class TestOutcar(unittest.TestCase):

    def setUp(self):
        with open("testdata/OUTCAR", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        outcar = Outcar("fakefile")
        self.assertEqual(outcar.filename, "fakefile")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            outcar = Outcar("fakefile")
            info = outcar.getResourceUsage()
            self.assertTrue(len(w) > 0)
            self.assertTrue(any(item.category == UserWarning for item in w))
            self.assertTrue(
                any("File fakefile is too short to be a valid OUTCAR file." in str(item.message) for item in w))
            self.assertEqual(info, {})

    @patch("builtins.open", new_callable=mock_open)
    def test_get_resourceUsage(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        outcar = Outcar("fakefile")
        info = outcar.getResourceUsage()
        self.assertEqual(info, {'AverageMemory': 0.0,
                                'ElapsedTime': 242.138,
                                'MaxMemory': 445736.0,
                                'SystemTime': 1.757,
                                'TotalCores': 28,  # 哪来的
                                'TotalCpuTime': 240.004,
                                'UserTime': 238.247})

    @patch("builtins.open", new_callable=mock_open)
    def test_get_ACandAM(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        outcar = Outcar("fakefile")
        info = outcar.getAtomicChargeAndAtomicMagnetization()
        self.assertEqual(info[0][0], {'d': 0.0, 'p': 3.472, 's': 1.569, 'tot': 5.042})


class TestOutcarEL(unittest.TestCase):

    def setUp(self):
        with open("testdata/OUTCAR_EL", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open)
    def test_get_EP(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        outcar = Outcar("fakefile")
        info = outcar.getElasticProperties()
        self.assertEqual(info['AnisotropyIndex'], 0.37962790312568373)


class TestPoscar(unittest.TestCase):

    def setUp(self):
        with open("testdata/POSCAR", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        poscar = Poscar("fakefile")
        self.assertEqual(poscar.filename, "fakefile")

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            poscar = Poscar("fakefile")
            poscar.setup()
            self.assertTrue(len(w) > 0)
            self.assertTrue(any(item.category == UserWarning for item in w))
            self.assertTrue(
                any("File fakefile is too short to be a valid POSCAR file." in str(item.message) for item in w))
            self.assertEqual(poscar.sites, None)

    @patch("builtins.open", new_callable=mock_open)
    def test_get_info(self, mock_file):
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        poscar = Poscar("fakefile")
        poscar.setup()
        self.assertEqual(poscar.volume, 545.0027442269759)
        self.assertEqual(poscar.numberOfSites, 48)


if __name__ == "__main__":
    unittest.main()
