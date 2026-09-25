#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - makesis Package Builder
Creates valid .sisx packages with metadata, UID headers, and compressed payloads.
"""

import os
import sys
import struct
import zlib
import json
import io
import tarfile
from symbian.package.sis_parser import UID_SISX
from symbian.api.symbian_core import CAPABILITY_NAMES

def create_sisx_package(output_path, app_name, vendor_name, uid3, version, capabilities, files_dict, target_type="x86"):
    """
    Creates a SISX package file.
    :param output_path: destination .sisx file path
    :param app_name: name of application
    :param vendor_name: vendor/author
    :param uid3: numeric UID3 (e.g. 0x2000E001)
    :param version: tuple of (major, minor, build)
    :param capabilities: integer bitmask of capabilities
    :param files_dict: dictionary mapping target_path (e.g. "!:\\sys\\bin\\app.exe") to host source path
    :param target_type: 'x86' or 'arm'
    """
    # 1. Prepare tarball of files
    tar_buf = io.BytesIO()
    with tarfile.open(fileobj=tar_buf, mode="w") as tar:
        for target_path, source_path in files_dict.items():
            if os.path.exists(source_path):
                tar.add(source_path, arcname=target_path)
    
    compressed_payload = zlib.compress(tar_buf.getvalue(), level=9)

    # 2. Prepare metadata JSON
    meta = {
        "name": app_name,
        "vendor": vendor_name,
        "uid3": f"0x{uid3:08X}",
        "version": list(version),
        "capabilities": capabilities,
        "target_type": target_type
    }
    meta_bytes = json.dumps(meta).encode("utf-8")

    # 3. Assemble binary structure
    # Header: UID1 (0x10201A7A), UID2 (0x1000007A), UID3, Checksum (0)
    header = struct.pack("<IIII", UID_SISX, 0x1000007A, uid3, 0xABCD)
    
    marker = b"SISX_META"
    meta_len = struct.pack("<I", len(meta_bytes))

    with open(output_path, "wb") as f:
        f.write(header)
        f.write(marker)
        f.write(meta_len)
        f.write(meta_bytes)
        f.write(compressed_payload)

    print(f"[MAKESIS] Successfully created SISX package: {output_path} (UID3: 0x{uid3:08X})")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: makesis.py <output.sisx> <app_name> <uid3> <version> [files...]")
        sys.exit(1)
