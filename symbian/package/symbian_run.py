#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Symbian Application Runner & Architecture Bridge (symbian-run)
Executes native x86 Symbian applications directly; provides fallback ARM translation bridge
for legacy ARM binaries.
"""

import os
import sys
import struct
import subprocess

def inspect_binary_arch(file_path):
    if not os.path.exists(file_path):
        return "NOT_FOUND"

    with open(file_path, "rb") as f:
        magic = f.read(4)
        if magic == b"\x7fELF":
            # ELF binary
            f.seek(18)
            e_machine = struct.unpack("<H", f.read(2))[0]
            if e_machine == 3:
                return "x86"
            elif e_machine == 62:
                return "x86_64"
            elif e_machine == 40:
                return "arm"
            else:
                return f"elf_unknown_{e_machine}"
        elif magic[:4] == b"EPOC" or magic[:2] == b"MZ":
            return "e32image"
        elif magic.startswith(b"#!"):
            return "script"
        else:
            return "unknown"

def run_application(target_path, app_args=[]):
    arch = inspect_binary_arch(target_path)
    print(f"[SYMBIAN-RUN] Launching: {target_path} (Detected Architecture: {arch})")

    # Set up sandbox and environment
    env = os.environ.copy()
    env["SYMBIAN_ROOT"] = os.environ.get("SYMBIAN_ROOT", "/opt/symbian")

    if arch in ("x86", "x86_64", "script"):
        # Native execution - maximum performance, lowest RAM overhead on Intel Atom
        cmd = [target_path] + app_args
        return subprocess.call(cmd, env=env)

    elif arch == "arm":
        # Legacy ARM Symbian binary - invoke ARM emulation bridge
        print("[SYMBIAN-RUN] Legacy ARM binary detected.")
        print("[SYMBIAN-RUN] Routing through ARM Emulation Translation Bridge (qemu-arm)...")
        
        arm_runner = shutil_which("qemu-arm") or shutil_which("qemu-arm-static")
        if arm_runner:
            cmd = [arm_runner, target_path] + app_args
            return subprocess.call(cmd, env=env)
        else:
            print("[SYMBIAN-RUN] Error: ARM user-mode emulator (qemu-arm) is not currently installed.")
            print("[SYMBIAN-RUN] Native x86 recompilation is recommended for optimal Atom N450 performance.")
            return 127

    elif arch == "e32image":
        # Symbian E32Image binary
        print("[SYMBIAN-RUN] E32Image binary detected.")
        eka2_runner = shutil_which("eka2l1")
        if eka2_runner:
            cmd = [eka2_runner, target_path] + app_args
            return subprocess.call(cmd, env=env)
        else:
            print("[SYMBIAN-RUN] EKA2L1 bridge not found. Please recompile for native x86 Symbian.")
            return 127
    else:
        # Fallback direct execution
        cmd = [target_path] + app_args
        return subprocess.call(cmd, env=env)

def shutil_which(cmd):
    import shutil
    return shutil.which(cmd)

def main():
    if len(sys.argv) < 2:
        print("Usage: symbian-run <application_path_or_uid> [arguments...]")
        sys.exit(1)

    target = sys.argv[1]
    args = sys.argv[2:]

    # Resolve UID3 if provided (e.g. 0x2000E001)
    if target.startswith("0x"):
        from symbian.package.sis_installer import SymbianPackageManager
        mgr = SymbianPackageManager()
        rec = mgr.registry.get(target)
        if rec and rec.get("installed_files"):
            for f in rec["installed_files"]:
                if "sys/bin" in f or f.endswith(".exe") or f.endswith(".bin"):
                    target = f
                    break

    sys.exit(run_application(target, args))

if __name__ == "__main__":
    main()
