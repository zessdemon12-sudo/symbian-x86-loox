#!/usr/bin/env python3
"""
Unit Tests for Symbian Core Runtime & Compatibility Layer
"""

import os
import sys
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from symbian.api.symbian_core import (
    User, SymbianLeave, CActive, CActiveScheduler, CenRep, RProperty,
    SymbianDriveManager, KErrNone, KErrNotFound, KErrNoMemory,
    CAP_NETWORK_SERVICES, CAP_USER_ENVIRONMENT
)

class DummyActiveObject(CActive):
    def __init__(self, priority=CActive.EPriorityStandard):
        super().__init__(priority)
        self.ran = False

    def RunL(self):
        self.ran = True
        CActiveScheduler.Stop()

    def DoCancel(self):
        pass

class TestSymbianCore(unittest.TestCase):
    def test_leave_and_trap(self):
        with self.assertRaises(SymbianLeave) as ctx:
            User.Leave(KErrNoMemory)
        self.assertEqual(ctx.exception.reason, KErrNoMemory)

    def test_active_scheduler(self):
        sched = CActiveScheduler()
        CActiveScheduler.Install(sched)
        ao = DummyActiveObject()
        CActiveScheduler.Add(ao)
        ao.SetActive()
        CActiveScheduler.Start()
        self.assertTrue(ao.ran)

    def test_cenrep(self):
        test_dir = "/tmp/test_symbian_cenrep"
        rep = CenRep(0x10200001, base_dir=test_dir)
        rep.set(0x1, 42)
        rep.set("setting_str", "LOOX_OS")
        self.assertEqual(rep.get(0x1), 42)
        self.assertEqual(rep.get("setting_str"), "LOOX_OS")
        rep.delete(0x1)
        self.assertIsNone(rep.get(0x1))

    def test_pubsub_property(self):
        RProperty.Define(0x1000, 0x1)
        RProperty.Set(0x1000, 0x1, 100)
        err, val = RProperty.Get(0x1000, 0x1)
        self.assertEqual(err, KErrNone)
        self.assertEqual(val, 100)

    def test_drive_resolver(self):
        c_path = SymbianDriveManager.resolve_path("C:\\sys\\bin\\test.exe")
        self.assertTrue(c_path.endswith("sys_drive/sys/bin/test.exe"))
        d_path = SymbianDriveManager.resolve_path("D:\\MyData\\file.txt")
        self.assertTrue("Documents" in d_path or "MyData" in d_path)

if __name__ == "__main__":
    unittest.main()
