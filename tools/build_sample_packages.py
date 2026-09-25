#!/usr/bin/env python3
"""
Build Sample SISX Packages for Symbian-X86 LOOX OS
"""

import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from symbian.package.makesis import create_sisx_package
from symbian.api.symbian_core import CAP_READ_USER_DATA, CAP_WRITE_USER_DATA, CAP_ALL_FILES, CAP_DISK_ADMIN

OUTPUT_DIR = os.path.join(BASE, "packages")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Notes app
create_sisx_package(
    output_path=os.path.join(OUTPUT_DIR, "notes.sisx"),
    app_name="Symbian Notes",
    vendor_name="Fujitsu-Symbian",
    uid3=0x2000E002,
    version=(1, 2, 0),
    capabilities=CAP_READ_USER_DATA | CAP_WRITE_USER_DATA,
    files_dict={
        "!:\\sys\\bin\\notes.exe": os.path.join(BASE, "applications", "notes", "notes.py"),
        "!:\\resource\\apps\\notes.png": os.path.join(BASE, "desktop", "lxde", "icons", "Symbian-Belle", "apps", "notes.png")
    }
)

# 2. Calculator app
create_sisx_package(
    output_path=os.path.join(OUTPUT_DIR, "calculator.sisx"),
    app_name="Calculator",
    vendor_name="Fujitsu-Symbian",
    uid3=0x2000E003,
    version=(2, 0, 1),
    capabilities=0,
    files_dict={
        "!:\\sys\\bin\\calculator.exe": os.path.join(BASE, "applications", "calculator", "calculator.py"),
        "!:\\resource\\apps\\calculator.png": os.path.join(BASE, "desktop", "lxde", "icons", "Symbian-Belle", "apps", "calculator.png")
    }
)

# 3. File Manager app
create_sisx_package(
    output_path=os.path.join(OUTPUT_DIR, "filemanager.sisx"),
    app_name="Symbian File Manager",
    vendor_name="Fujitsu-Symbian",
    uid3=0x2000E004,
    version=(1, 5, 0),
    capabilities=CAP_ALL_FILES | CAP_DISK_ADMIN | CAP_READ_USER_DATA | CAP_WRITE_USER_DATA,
    files_dict={
        "!:\\sys\\bin\\filemanager.exe": os.path.join(BASE, "applications", "filebrowser", "filebrowser.py"),
        "!:\\resource\\apps\\filemanager.png": os.path.join(BASE, "desktop", "lxde", "icons", "Symbian-Belle", "apps", "filemanager.png")
    }
)

print("[PACKAGES] Built sample SISX packages in 'packages/' successfully.")
