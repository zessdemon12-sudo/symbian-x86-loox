#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - Master Build Orchestrator
# Builds complete OS based on Tiny Core Linux 15.x x86:
# Kernel, Remastered Core, Desktop (LXQt + Openbox), Symbian Subsystem, ISO & USB
# Target: Fujitsu FMV-BIBLO LOOX M/G30 (Intel Atom N450)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================================="
echo "    Starting Symbian-X86 LOOX OS Full Build Pipeline"
echo "    Base Engine: Tiny Core Linux 15.x (x86 32-bit)"
echo "    Target: Fujitsu FMV-BIBLO LOOX M/G30 (Intel Atom N450)"
echo "    Working Directory: $BASE_DIR"
echo "=========================================================="

# Step 1: Run unit tests
echo "[STEP 1/5] Running Symbian compatibility & package tests..."
python3 "$BASE_DIR/tests/test_symbian_api.py"
python3 "$BASE_DIR/tests/test_sis_installer.py"

# Step 2: Build Visual Assets & Sample SISX packages
echo "[STEP 2/5] Compiling visual assets & SISX packages..."
python3 "$BASE_DIR/tools/generate_symbian_assets.py"
python3 "$BASE_DIR/tools/build_sample_packages.py"

# Step 3: Remaster Tiny Core Linux Base & Symbian Subsystem
echo "[STEP 3/5] Remastering Tiny Core Linux 15.x with Symbian-X86 & LXQt..."
bash "$SCRIPT_DIR/remaster-tinycore.sh"

# Step 4: Bootable Hybrid ISO Generation
echo "[STEP 4/5] Generating Bootable Hybrid ISO..."
bash "$SCRIPT_DIR/build-iso.sh"

# Step 5: Bootable FAT32/Syslinux USB Image Generation
echo "[STEP 5/5] Generating Native FAT32/Syslinux USB Image..."
bash "$SCRIPT_DIR/build-usb-image.sh"

echo "=========================================================="
echo "    🎉 Symbian-X86 LOOX OS Build Succeeded!"
echo "    Output files located in: $BASE_DIR/output"
echo "=========================================================="
ls -lh "$BASE_DIR/output"/*.img "$BASE_DIR/output"/*.iso "$BASE_DIR/output/boot"/*
