#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - SIS/SISX Package Manager Engine & CLI (symbian-pkg)
Handles installation, uninstallation, listing, capability validation, and desktop integration.
"""

import os
import sys
import argparse
import shutil
from symbian.package.sis_parser import SisParser
from symbian.api.symbian_core import CenRep, SymbianDriveManager, KErrNone, KErrNotFound, KErrAlreadyExists

REGISTRY_UID = 0x101F75B8

class SymbianPackageManager:
    def __init__(self, sys_root=None):
        if sys_root is None:
            sys_root = os.environ.get("SYMBIAN_ROOT", "/opt/symbian")
        self.sys_root = sys_root
        self.registry = CenRep(REGISTRY_UID, base_dir=os.path.join(self.sys_root, "system", "data", "cenrep"))

    def install(self, pkg_path, target_drive="C:"):
        print(f"[SYMBIAN-PKG] Parsing package: {pkg_path}...")
        pkg = SisParser.parse(pkg_path)

        uid_str = f"0x{pkg.uid3:08X}"
        if self.registry.get(uid_str):
            print(f"[SYMBIAN-PKG] Warning: Package {pkg.app_name} ({uid_str}) is already installed. Reinstalling...")

        print(f"[SYMBIAN-PKG] Package: {pkg.app_name} v{pkg.version_string()}")
        print(f"[SYMBIAN-PKG] Vendor:  {pkg.vendor_name}")
        print(f"[SYMBIAN-PKG] UID3:    {uid_str}")
        print(f"[SYMBIAN-PKG] Target Architecture: {pkg.target_type}")
        print(f"[SYMBIAN-PKG] Capabilities: {', '.join(pkg.capability_list()) or 'None'}")

        installed_files = []
        app_binary_path = None
        app_icon_path = None

        # Extract & install files
        for arcname, relpath, data in pkg.files:
            # Resolve target path
            host_path = SymbianDriveManager.resolve_path(arcname, target_drive)
            os.makedirs(os.path.dirname(host_path), exist_ok=True)
            with open(host_path, "wb") as f:
                f.write(data)
            
            # Make executables executable
            if "sys/bin" in host_path or host_path.endswith(".exe") or host_path.endswith(".bin"):
                os.chmod(host_path, 0o755)
                if not app_binary_path:
                    app_binary_path = host_path

            if host_path.endswith(".png") or host_path.endswith(".svg"):
                if not app_icon_path:
                    app_icon_path = host_path

            installed_files.append(host_path)
            print(f"  -> Installed: {host_path}")

        # Desktop integration (.desktop file)
        desktop_entry = self._create_desktop_entry(pkg, app_binary_path, app_icon_path)

        # Record in Registry
        record = {
            "name": pkg.app_name,
            "vendor": pkg.vendor_name,
            "version": pkg.version_string(),
            "uid3": uid_str,
            "capabilities": pkg.capability_list(),
            "target_type": pkg.target_type,
            "installed_files": installed_files,
            "desktop_file": desktop_entry
        }
        self.registry.set(uid_str, record)
        print(f"[SYMBIAN-PKG] Successfully installed {pkg.app_name} ({uid_str})!\n")
        return KErrNone

    def uninstall(self, uid_or_name):
        pkg_key = uid_or_name if uid_or_name.startswith("0x") else None
        record = None

        if pkg_key:
            record = self.registry.get(pkg_key)
        else:
            # Search by name
            for k, rec in self.registry.data.items():
                if rec.get("name", "").lower() == uid_or_name.lower():
                    pkg_key = k
                    record = rec
                    break

        if not record:
            print(f"[SYMBIAN-PKG] Error: Package '{uid_or_name}' not found.")
            return KErrNotFound

        print(f"[SYMBIAN-PKG] Uninstalling {record.get('name')} ({pkg_key})...")
        # Remove installed files
        for f in record.get("installed_files", []):
            if os.path.exists(f):
                try:
                    os.remove(f)
                    print(f"  -> Removed: {f}")
                except Exception as e:
                    print(f"  -> Failed to remove {f}: {e}")

        # Remove desktop entry
        desk = record.get("desktop_file")
        if desk and os.path.exists(desk):
            os.remove(desk)
            print(f"  -> Removed desktop shortcut: {desk}")

        # Clean private directory
        priv_dir = os.path.join(self.sys_root, "private", pkg_key)
        if os.path.exists(priv_dir):
            shutil.rmtree(priv_dir, ignore_errors=True)
            print(f"  -> Removed private storage: {priv_dir}")

        self.registry.delete(pkg_key)
        print(f"[SYMBIAN-PKG] Successfully uninstalled {record.get('name')}.\n")
        return KErrNone

    def list_installed(self):
        print("\n=== Installed Symbian Applications ===")
        if not self.registry.data:
            print("  (No Symbian packages installed)")
            print("======================================\n")
            return

        for uid, rec in self.registry.data.items():
            print(f"• {rec.get('name')} [{uid}]")
            print(f"    Version: {rec.get('version')} | Vendor: {rec.get('vendor')}")
            print(f"    Arch:    {rec.get('target_type')}")
            print(f"    Caps:    {', '.join(rec.get('capabilities', [])) or 'None'}")
        print("======================================\n")

    def info(self, pkg_path):
        pkg = SisParser.parse(pkg_path)
        print("\n=== Symbian Package Information ===")
        print(f"  Package:      {pkg.app_name}")
        print(f"  Vendor:       {pkg.vendor_name}")
        print(f"  Version:      {pkg.version_string()}")
        print(f"  UID3:         0x{pkg.uid3:08X}")
        print(f"  Format:       {pkg.format_version}")
        print(f"  Architecture: {pkg.target_type}")
        print(f"  Capabilities: {', '.join(pkg.capability_list()) or 'None'}")
        print(f"  Files Count:  {len(pkg.files)}")
        for arc, _, _ in pkg.files:
            print(f"    - {arc}")
        print("====================================\n")

    def _create_desktop_entry(self, pkg, binary_path, icon_path):
        apps_dir = os.environ.get("XDG_DATA_HOME", "/usr/share/applications")
        if not os.path.exists(apps_dir):
            apps_dir = os.path.join(self.sys_root, "applications")
        os.makedirs(apps_dir, exist_ok=True)

        exec_cmd = binary_path if binary_path else f"/opt/symbian/bin/symbian-run 0x{pkg.uid3:08X}"
        icon = icon_path if icon_path else "symbian-app"

        content = f"""[Desktop Entry]
Type=Application
Name={pkg.app_name}
Comment={pkg.vendor_name} Symbian Application
Exec={exec_cmd}
Icon={icon}
Terminal=false
Categories=Symbian;Utility;
"""
        desk_path = os.path.join(apps_dir, f"symbian-0x{pkg.uid3:08X}.desktop")
        try:
            with open(desk_path, "w", encoding="utf-8") as f:
                f.write(content)
            return desk_path
        except Exception:
            return None

def main():
    parser = argparse.ArgumentParser(description="Symbian-X86 Package Manager (symbian-pkg)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # install
    p_inst = subparsers.add_parser("install", help="Install a .sis or .sisx package")
    p_inst.add_argument("package", help="Path to .sis / .sisx file")
    p_inst.add_argument("--target", default="C:", help="Target drive (C: or E:)")

    # uninstall
    p_uninst = subparsers.add_parser("uninstall", help="Uninstall a package by UID3 or name")
    p_uninst.add_argument("uid_or_name", help="UID3 (e.g. 0x2000E001) or package name")

    # list
    subparsers.add_parser("list", help="List installed Symbian packages")

    # info
    p_info = subparsers.add_parser("info", help="Display package details")
    p_info.add_argument("package", help="Path to .sis / .sisx file")

    args = parser.parse_args()
    mgr = SymbianPackageManager()

    if args.command == "install":
        sys.exit(mgr.install(args.package, args.target))
    elif args.command == "uninstall":
        sys.exit(mgr.uninstall(args.uid_or_name))
    elif args.command == "list":
        mgr.list_installed()
    elif args.command == "info":
        mgr.info(args.package)

if __name__ == "__main__":
    main()
