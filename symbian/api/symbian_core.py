"""
Symbian-X86 LOOX OS - Core Python Compatibility Layer
Implements Symbian Active Objects, Cleanup/Leave semantics, CenRep, PubSub,
Security Capabilities, and Drive Letter Mapping.
"""

import os
import sys
import time
import json
import threading

# Standard Symbian Error Codes
KErrNone = 0
KErrNotFound = -1
KErrGeneral = -2
KErrCancel = -3
KErrNoMemory = -4
KErrNotSupported = -5
KErrArgument = -6
KErrAlreadyExists = -11
KErrPathNotFound = -12
KErrPermissionDenied = -46

# Symbian Capabilities
CAP_TCB = 1 << 0
CAP_COMM_DD = 1 << 1
CAP_POWER_MGMT = 1 << 2
CAP_MULTIMEDIA_DD = 1 << 3
CAP_READ_DEVICE_DATA = 1 << 4
CAP_WRITE_DEVICE_DATA = 1 << 5
CAP_DRM = 1 << 6
CAP_TRUSTED_UI = 1 << 7
CAP_PROT_SERV = 1 << 8
CAP_DISK_ADMIN = 1 << 9
CAP_NETWORK_CONTROL = 1 << 10
CAP_ALL_FILES = 1 << 11
CAP_SW_EVENT = 1 << 12
CAP_NETWORK_SERVICES = 1 << 13
CAP_LOCAL_SERVICES = 1 << 14
CAP_READ_USER_DATA = 1 << 15
CAP_WRITE_USER_DATA = 1 << 16
CAP_LOCATION = 1 << 17
CAP_SURROUNDINGS_DD = 1 << 18
CAP_USER_ENVIRONMENT = 1 << 19

CAPABILITY_NAMES = {
    "TCB": CAP_TCB,
    "CommDD": CAP_COMM_DD,
    "PowerMgmt": CAP_POWER_MGMT,
    "MultimediaDD": CAP_MULTIMEDIA_DD,
    "ReadDeviceData": CAP_READ_DEVICE_DATA,
    "WriteDeviceData": CAP_WRITE_DEVICE_DATA,
    "DRM": CAP_DRM,
    "TrustedUI": CAP_TRUSTED_UI,
    "ProtServ": CAP_PROT_SERV,
    "DiskAdmin": CAP_DISK_ADMIN,
    "NetworkControl": CAP_NETWORK_CONTROL,
    "AllFiles": CAP_ALL_FILES,
    "SwEvent": CAP_SW_EVENT,
    "NetworkServices": CAP_NETWORK_SERVICES,
    "LocalServices": CAP_LOCAL_SERVICES,
    "ReadUserData": CAP_READ_USER_DATA,
    "WriteUserData": CAP_WRITE_USER_DATA,
    "Location": CAP_LOCATION,
    "SurroundingsDD": CAP_SURROUNDINGS_DD,
    "UserEnvironment": CAP_USER_ENVIRONMENT
}

class SymbianLeave(Exception):
    def __init__(self, reason=KErrGeneral, message="Symbian User::Leave"):
        super().__init__(f"{message} (Reason: {reason})")
        self.reason = reason

class User:
    @staticmethod
    def Leave(reason):
        raise SymbianLeave(reason)

    @staticmethod
    def LeaveIfError(error):
        if error < 0:
            raise SymbianLeave(error)

    @staticmethod
    def LeaveIfNull(obj):
        if obj is None:
            raise SymbianLeave(KErrNoMemory)

    @staticmethod
    def After(seconds):
        time.sleep(seconds)

class TRequestStatus:
    def __init__(self, initial=KErrNone):
        self.status = initial

    def set(self, val):
        self.status = val

    def get(self):
        return self.status

class CActive:
    EPriorityIdle = -100
    EPriorityLow = -20
    EPriorityStandard = 0
    EPriorityUserInput = 10
    EPriorityHigh = 20

    def __init__(self, priority=EPriorityStandard):
        self.priority = priority
        self.iStatus = TRequestStatus()
        self.is_active = False

    def SetActive(self):
        self.is_active = True

    def Cancel(self):
        if self.is_active:
            self.DoCancel()
            self.is_active = False
            self.iStatus.set(KErrCancel)

    def RunL(self):
        raise NotImplementedError

    def DoCancel(self):
        pass

    def RunError(self, error):
        return error

class CActiveScheduler:
    _instance = None

    def __init__(self):
        self.active_objects = []
        self.running = False

    @classmethod
    def Install(cls, scheduler):
        cls._instance = scheduler

    @classmethod
    def Current(cls):
        if cls._instance is None:
            cls._instance = CActiveScheduler()
        return cls._instance

    @classmethod
    def Add(cls, ao):
        curr = cls.Current()
        if ao not in curr.active_objects:
            curr.active_objects.append(ao)

    @classmethod
    def Remove(cls, ao):
        curr = cls.Current()
        if ao in curr.active_objects:
            curr.active_objects.remove(ao)

    @classmethod
    def Start(cls):
        curr = cls.Current()
        curr.running = True
        while curr.running:
            # Sort by priority
            active = [ao for ao in curr.active_objects if ao.is_active and ao.iStatus.get() != -999999]
            if active:
                active.sort(key=lambda x: x.priority, reverse=True)
                highest = active[0]
                highest.is_active = False
                try:
                    highest.RunL()
                except SymbianLeave as e:
                    highest.RunError(e.reason)
                except Exception:
                    highest.RunError(KErrGeneral)
            else:
                time.sleep(0.01)

    @classmethod
    def Stop(cls):
        curr = cls.Current()
        curr.running = False

class CenRep:
    """Central Repository: Persistent transactional key-value store"""
    def __init__(self, uid, base_dir=None):
        self.uid = uid
        if base_dir is None:
            base_dir = os.environ.get("SYMBIAN_CENREP_DIR", "/tmp/symbian_cenrep")
        os.makedirs(base_dir, exist_ok=True)
        self.filepath = os.path.join(base_dir, f"rep_0x{uid:08X}.json")
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(str(key), default)

    def set(self, key, value):
        self.data[str(key)] = value
        self.save()
        return KErrNone

    def delete(self, key):
        if str(key) in self.data:
            del self.data[str(key)]
            self.save()
            return KErrNone
        return KErrNotFound

class RProperty:
    """Publish and Subscribe System"""
    _properties = {}
    _lock = threading.Lock()

    @classmethod
    def Define(cls, category, key, attr=0):
        with cls._lock:
            cls._properties[(category, key)] = None
        return KErrNone

    @classmethod
    def Set(cls, category, key, value):
        with cls._lock:
            cls._properties[(category, key)] = value
        return KErrNone

    @classmethod
    def Get(cls, category, key):
        with cls._lock:
            if (category, key) in cls._properties:
                return KErrNone, cls._properties[(category, key)]
        return KErrNotFound, None

class SymbianDriveManager:
    """Symbian Drive Resolver (C:, D:, E:, Z:)"""
    @staticmethod
    def resolve_path(symbian_path, target_drive="C:"):
        path = symbian_path.replace("\\", "/")
        if path.startswith("!:"):
            path = target_drive + path[2:]

        drive = path[:2].upper()
        rel = path[2:].lstrip("/")

        base = os.environ.get("SYMBIAN_ROOT", "/opt/symbian")

        if drive == "C:":
            # System root
            return os.path.join(base, "sys_drive", rel)
        elif drive == "D:":
            # User Data / Documents
            user_doc = os.path.expanduser("~/Documents")
            return os.path.join(user_doc, rel)
        elif drive == "E:":
            # Removable / Mass memory
            return os.path.join("/media", rel)
        elif drive == "Z:":
            # ROM (Symbian Core Files)
            return os.path.join(base, "rom", rel)
        else:
            return os.path.join(base, "sys_drive", rel)
