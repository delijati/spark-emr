import unittest
import os
import moto
import pytest
from spark_emr.__main__ import main

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "config.yaml")


class TestMain(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_cli(self):
        self.assertRaises(SystemExit, main, [])
        out, err = self.capsys.readouterr()
        self.assertTrue(
            "{start,status,list,stop}" in out)

    def test_cli_start(self):
        self.assertRaises(SystemExit, main, ["start"])
        out, err = self.capsys.readouterr()
        self.assertTrue(
            "required: --name, --cmdline, --package" in
            err)

    def test_cli_stop(self):
        self.assertRaises(SystemExit, main, ["stop"])
        out, err = self.capsys.readouterr()
        self.assertTrue("required: --cluster-id" in err)

    def test_cli_status(self):
        self.assertRaises(SystemExit, main, ["status"])
        out, err = self.capsys.readouterr()
        self.assertTrue("required: --cluster-id" in err)

    def test_cli_list(self):
        with moto.mock_emr():
            main(["list", "--config", CONFIG])
            out, err = self.capsys.readouterr()
            self.assertTrue("id, name, reason, state, created" in out)
