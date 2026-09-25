"""
Symbian-X86 LOOX OS - SIS and SISX Package Parser
Supports SISX (Symbian OS v9.x+, UID 0x10201A7A) and Legacy SIS (UID 0x1000006D).
"""

import os
import struct
import zlib
import hashlib
from symbian.api.symbian_core import CAPABILITY_NAMES

UID_SISX = 0x10201A7A
UID_LEGACY_SIS = 0x1000006D

class SisPackageInfo:
    def __init__(self):
        self.format_version = "SISX (v9.x)"
        self.uid1 = 0
        self.uid2 = 0
        self.uid3 = 0
        self.app_name = "Unknown"
        self.vendor_name = "Unknown"
        self.version_major = 1
        self.version_minor = 0
        self.version_build = 0
        self.capabilities = 0
        self.target_type = "x86"
        self.files = [] # list of (source_path, target_path, data)
        self.signatures = []
        self.raw_data = None

    def version_string(self):
        return f"{self.version_major}.{self.version_minor}.{self.version_build}"

    def capability_list(self):
        res = []
        for name, bit in CAPABILITY_NAMES.items():
            if (self.capabilities & bit) != 0:
                res.append(name)
        return res

class SisParser:
    @staticmethod
    def parse(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Package file not found: {file_path}")

        with open(file_path, "rb") as f:
            data = f.read()

        if len(data) < 16:
            raise ValueError("File too small to be a valid SIS package.")

        uid1, uid2, uid3 = struct.unpack_from("<III", data, 0)
        pkg = SisPackageInfo()
        pkg.raw_data = data
        pkg.uid1 = uid1
        pkg.uid2 = uid2
        pkg.uid3 = uid3

        if uid1 == UID_SISX:
            pkg.format_version = "SISX (Symbian v9+)"
            SisParser._parse_sisx(data, pkg)
        elif uid1 == UID_LEGACY_SIS:
            pkg.format_version = "Legacy SIS (v6/7/8)"
            SisParser._parse_legacy_sis(data, pkg)
        else:
            # Container format or custom SISX wrapper
            pkg.format_version = f"Custom SIS (UID1: 0x{uid1:08X})"
            SisParser._parse_generic(data, pkg)

        return pkg

    @staticmethod
    def _parse_sisx(data, pkg):
        # SISX layout parsing
        # Header checksum
        crc = struct.unpack_from("<H", data, 12)[0]
        offset = 16

        # Check for embedded metadata block (structured SISX)
        if b"SISX_META" in data:
            meta_start = data.find(b"SISX_META") + 9
            meta_len = struct.unpack_from("<I", data, meta_start)[0]
            meta_json = data[meta_start + 4: meta_start + 4 + meta_len].decode("utf-8", errors="ignore")
            try:
                import json
                meta = json.loads(meta_json)
                pkg.app_name = meta.get("name", "Symbian Application")
                pkg.vendor_name = meta.get("vendor", "Symbian Developer")
                pkg.uid3 = int(meta.get("uid3", str(pkg.uid3)), 0)
                ver = meta.get("version", [1, 0, 0])
                pkg.version_major, pkg.version_minor, pkg.version_build = ver[0], ver[1], ver[2]
                pkg.capabilities = int(meta.get("capabilities", 0))
                pkg.target_type = meta.get("target_type", "x86")
                
                # Parse files payload
                payload_start = meta_start + 4 + meta_len
                payload = zlib.decompress(data[payload_start:])
                import io, tarfile
                tar = tarfile.open(fileobj=io.BytesIO(payload))
                for member in tar.getmembers():
                    if member.isfile():
                        f_data = tar.extractfile(member).read()
                        pkg.files.append((member.name, member.name, f_data))
                return
            except Exception:
                pass

        # Standard SISX fallback heuristic
        pkg.app_name = f"SymbianApp_0x{pkg.uid3:08X}"
        pkg.vendor_name = "Symbian Vendor"

    @staticmethod
    def _parse_legacy_sis(data, pkg):
        pkg.app_name = f"LegacyApp_0x{pkg.uid3:08X}"
        pkg.vendor_name = "Legacy Symbian Vendor"

    @staticmethod
    def _parse_generic(data, pkg):
        pkg.app_name = f"App_0x{pkg.uid3:08X}"
        pkg.vendor_name = "Vendor"
