# Symbian-X86 LOOX OS Build & Release Guide

This guide describes how to build, test in QEMU, create bootable ISOs, and install Symbian-X86 LOOX OS on real Fujitsu FMV-BIBLO LOOX M/G30 hardware.

---

## 1. Quick Start

All operations must be run from `/media/a1/game p/buffy-work/projects/gemi oooossss/symbian-x86-loox/`.

```bash
# Step 1: Run comprehensive test suite
cd "/media/a1/game p/buffy-work/projects/gemi oooossss/symbian-x86-loox"
python3 tests/test_symbian_api.py
python3 tests/test_sis_installer.py

# Step 2: Build complete ISO image
./scripts/build.sh

# Step 3: Test boot in QEMU (emulating Intel Atom LOOX hardware)
./scripts/run-qemu.sh
```

---

## 2. Build Pipeline Architecture

```
 scripts/build.sh
        │
        ├── scripts/build-kernel.sh  --> Assembles tailored i686 Atom N450 kernel & initramfs
        │
        ├── scripts/build-rootfs.sh  --> Rootless rootfs constructor (unshare -rm)
        │                                - Installs LXDE + Openbox + LightDM
        │                                - Installs Symbian Compatibility Framework
        │                                - Installs SIS/SISX package tools
        │                                - Installs low-memory Firefox & VLC profiles
        │                                - Configures zram swap and Atom power settings
        │
        └── scripts/build-iso.sh     --> Packages bootable hybrid ISO with GRUB 2 BIOS MBR
```

---

## 3. Flashing to USB & Installation on Fujitsu LOOX M/G30

### Flashing to USB:
```bash
# Identify USB drive (e.g. /dev/sdX)
sudo dd if=output/symbian-x86-loox.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

### Hardware Booting:
1. Insert the USB drive into any USB port of the Fujitsu LOOX M/G30.
2. Power on the netbook and press **F12** to enter the boot menu (or **F2** for BIOS setup).
3. Select the USB flash drive and press **Enter**.
4. GRUB 2 displays the Symbian-X86 LOOX OS boot menu.
5. Choose **"Live Symbian-X86 Desktop"** to test without modifying internal storage, or **"Install Symbian-X86 LOOX OS"** to install directly to the internal 2.5" SATA HDD/SSD.
