#!/usr/bin/env python3
"""
Unit and Integration Tests for Symbian SIS/SISX Package Management
"""

import os
import sys
import shutil
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from symbian.package.sis_parser import SisParser
from symbian.package.sis_installer import SymbianPackageManager
from symbian.api.symbian_core import KErrNone

class TestSisInstaller(unittest.TestCase):
    def setUp(self):
        self.test_root = "/tmp/test_symbian_root"
        os.environ["SYMBIAN_ROOT"] = self.test_root
        os.environ["XDG_DATA_HOME"] = os.path.join(self.test_root, "applications")
        os.makedirs(self.test_root, exist_ok=True)
        self.mgr = SymbianPackageManager(sys_root=self.test_root)
        self.pkg_path = os.path.join(BASE, "packages", "notes.sisx")

    def tearDown(self):
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root, ignore_errors=True)

    def test_parse_sisx(self):
        pkg = SisParser.parse(self.pkg_path)
        self.assertEqual(pkg.app_name, "Symbian Notes")
        self.assertEqual(pkg.vendor_name, "Fujitsu-Symbian")
        self.assertEqual(pkg.uid3, 0x2000E002)
        self.assertEqual(pkg.version_string(), "1.2.0")
        caps = pkg.capability_list()
        self.assertIn("ReadUserData", caps)
        self.assertIn("WriteUserData", caps)
        self.assertTrue(len(pkg.files) >= 1)

    def test_install_and_uninstall(self):
        # 1. Install
        res = self.mgr.install(self.pkg_path, target_drive="C:")
        self.assertEqual(res, KErrNone)

        # Verify registry entry
        rec = self.mgr.registry.get("0x2000E002")
        self.assertIsNotNone(rec)
        self.assertEqual(rec["name"], "Symbian Notes")

        # Verify installed files exist
        for f in rec["installed_files"]:
            self.assertTrue(os.path.exists(f), f"File was not installed: {f}")

        # Verify desktop file exists
        self.assertTrue(os.path.exists(rec["desktop_file"]))

        # 2. Uninstall
        res_un = self.mgr.uninstall("0x2000E002")
        self.assertEqual(res_un, KErrNone)

        # Verify files were removed
        for f in rec["installed_files"]:
            self.assertFalse(os.path.exists(f), f"File was not uninstalled: {f}")

        # Verify registry entry was removed
        self.assertIsNone(self.mgr.registry.get("0x2000E002"))

if __name__ == "__main__":
    unittest.main()
