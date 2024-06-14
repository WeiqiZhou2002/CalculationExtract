import unittest
from unittest.mock import mock_open, patch
import numpy as np

from i_o.vasp.procar import Procar
from i_o.vasp.chgcar import Chgcar


class TestProcar(unittest.TestCase):

    def setUp(self):
        with open("testdata/PROCAR", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        # 测试初始化方法
        procar = Procar("fakefile")
        self.assertEqual(procar.filename, "fakefile")
        self.assertEqual(procar.nkpoints, 0)
        self.assertEqual(procar.nbands, 0)
        self.assertEqual(procar.nions, 0)

    @patch("builtins.open", new_callable=mock_open)
    def test_read_procar_file(self, mock_file):
        # 设置 mock 文件内容
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        # 测试读取 PROCAR 文件
        procar = Procar("fakefile")
        self.assertEqual(procar.nkpoints, 75)
        self.assertEqual(procar.nbands, 252)
        self.assertEqual(procar.nions, 48)
        self.assertEqual(procar.KPoints[0], [0.0, 0.0, 0.0])
        self.assertEqual(procar.eigenvalues[0][0][0], -53.70320926)
        self.assertEqual(procar.occupancies[0][0][0], 2.00000000)
        self.assertEqual(procar.IsSpinPolarized, False)


class TestChgcar(unittest.TestCase):

    def setUp(self):
        # 设置模拟的 CHGCAR 文件内容
        with open("testdata/CHGCAR", "r") as file:
            self.mock_data = file.read()

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_init(self, mock_file):
        # 测试初始化方法，确保类属性正确初始化
        chgcar = Chgcar("fakefile")
        self.assertEqual(chgcar.filename, "fakefile")
        self.assertEqual(chgcar.NGX, 0)
        self.assertEqual(chgcar.NGY, 0)
        self.assertEqual(chgcar.NGZ, 0)
        self.assertTrue((chgcar.GRID == np.zeros((0, 0, 0))).all())

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_empty_file(self, mock_file):
        # 测试处理空文件的情况
        with self.assertRaises(ValueError) as context:
            chgcar = Chgcar("fakefile")
            info = chgcar.getChgcarInfo()
        self.assertIn("File fakefile is too short to be a valid CHGCAR file.", str(context.exception))

    @patch("builtins.open", new_callable=mock_open)
    def test_get_chgcar_info(self, mock_file):
        # 设置 mock 文件内容为 self.mock_data
        mock_file.return_value.readlines.return_value = self.mock_data.splitlines()
        chgcar = Chgcar("fakefile")
        info = chgcar.getChgcarInfo()
        self.assertEqual(info["NGX"], 72)
        self.assertEqual(info["NGY"], 72)
        self.assertEqual(info["NGZ"], 320)
        # expected_grid = [[[0.1, 0.2], [0.3, 0.4]], [[0.5, 0.6], [0.7, 0.8]]]
        # self.assertEqual(info["GRID"], expected_grid)
        # sample too large, wait to be finished


if __name__ == "__main__":
    unittest.main()
