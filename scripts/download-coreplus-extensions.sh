#!/bin/bash
# ==============================================================================
# Symbian-X86 LOOX OS - CorePlus Extension Ingestion Engine
# Downloads Wireless tools, full Firmware collection, ndiswrapper,
# non-US keymaps, and remastering tools from Tiny Core Linux repos.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
REPO_15="http://repo.tinycorelinux.net/15.x/x86/tcz"
REPO_10="http://repo.tinycorelinux.net/10.x/x86/tcz"
DEST="$BASE_DIR/kernel/tinycore/tcz_apps"

mkdir -p "$DEST"

echo "=========================================================="
echo "    [DOWNLOAD] Ingesting CorePlus Extensions for LOOX OS"
echo "=========================================================="

COREPLUS_PACKAGES=(
    # Non-US Keyboard Support
    "kmaps.tcz"

    # Remastering Tools
    "ezremaster.tcz"
    "advcomp.tcz"
    "mkisofs-tools.tcz"
    "syslinux.tcz"

    # Wireless Networking & Tools
    "wifi.tcz"
    "wireless-6.6.8-tinycore.tcz"
    "wireless_tools.tcz"
    "libiw.tcz"
    "wpa_supplicant-dbus.tcz"
    "iw.tcz"
    "libnl.tcz"
    "pci-utils.tcz"
    "libpci.tcz"

    # Complete Wireless & NIC Firmware Collection
    "firmware-atheros.tcz"
    "firmware-broadcom_bcm43xx.tcz"
    "firmware-intel.tcz"
    "firmware-intel_e100.tcz"
    "firmware-ipw2100.tcz"
    "firmware-ipw2200.tcz"
    "firmware-iwimax.tcz"
    "firmware-iwl8000.tcz"
    "firmware-iwl9000.tcz"
    "firmware-iwlwifi.tcz"
    "firmware-marvel.tcz"
    "firmware-myri10ge.tcz"
    "firmware-netxen.tcz"
    "firmware-openfwwf.tcz"
    "firmware-ralinkwifi.tcz"
    "firmware-rtl_nic.tcz"
    "firmware-rtlwifi.tcz"
    "firmware-ti-connectivity.tcz"
    "firmware-ueagle-atm.tcz"
    "firmware-vxge.tcz"
    "firmware-zd1211.tcz"
    "firmware-chelsio.tcz"
    "firmware-tigon.tcz"
    "firmware-amd-ucode.tcz"
)

# 1. Download CorePlus Packages
echo "[1/4] Downloading CorePlus packages from 15.x repo..."
for pkg in "${COREPLUS_PACKAGES[@]}"; do
    if [ ! -f "$DEST/$pkg" ]; then
        echo " -> Fetching $pkg..."
        curl -s --connect-timeout 10 --retry 3 -o "$DEST/$pkg" "$REPO_15/$pkg" || {
            echo " [WARN] Failed to download $pkg from 15.x"
            rm -f "$DEST/$pkg"
        }
    else
        echo " [OK] $pkg already cached"
    fi

    # Fetch .dep file if available
    if [ ! -f "$DEST/${pkg}.dep" ]; then
        curl -s --connect-timeout 5 -o "$DEST/${pkg}.dep" "$REPO_15/${pkg}.dep" 2>/dev/null || true
        # If empty, delete
        [ ! -s "$DEST/${pkg}.dep" ] && rm -f "$DEST/${pkg}.dep"
    fi
done

# 2. Download Ndiswrapper
echo "[2/4] Downloading ndiswrapper from 10.x repo..."
if [ ! -f "$DEST/ndiswrapper.tcz" ]; then
    echo " -> Fetching ndiswrapper.tcz..."
    curl -s --connect-timeout 10 --retry 3 -o "$DEST/ndiswrapper.tcz" "$REPO_10/ndiswrapper.tcz" || {
        echo " [WARN] Failed to download ndiswrapper.tcz"
        rm -f "$DEST/ndiswrapper.tcz"
    }
fi
if [ ! -f "$DEST/ndiswrapper.tcz.dep" ]; then
    curl -s --connect-timeout 5 -o "$DEST/ndiswrapper.tcz.dep" "$REPO_10/ndiswrapper.tcz.dep" 2>/dev/null || true
fi

# 3. Resolve any missing sub-dependencies
echo "[3/4] Checking and resolving sub-dependencies..."
for depfile in "$DEST"/*.dep; do
    [ -f "$depfile" ] || continue
    while IFS= read -r subdep; do
        subdep=$(echo "$subdep" | tr -d '\r' | xargs)
        [ -z "$subdep" ] && continue
        [[ "$subdep" != *.tcz ]] && subdep="${subdep}.tcz"
        # Substitute kernel version wildcard if present
        subdep="${subdep/KERNEL/6.6.8-tinycore}"
        
        if [ ! -f "$DEST/$subdep" ]; then
            echo " -> Downloading sub-dependency $subdep..."
            curl -s --connect-timeout 10 --retry 3 -o "$DEST/$subdep" "$REPO_15/$subdep" || {
                echo " [WARN] Sub-dependency $subdep not found on 15.x repo"
                rm -f "$DEST/$subdep"
            }
        fi
    done < "$depfile"
done

# 4. Update onboot.lst
echo "[4/4] Updating onboot.lst with essential startup extensions..."
ONBOOT="$DEST/onboot.lst"

# Base standard apps
cat <<'LIST' > "$ONBOOT"
dillo.tcz
leafpad.tcz
gpicview.tcz
flaxpdf.tcz
lxtask.tcz
htop.tcz
lxterminal.tcz
lxappearance.tcz
lxrandr.tcz
fluff.tcz
flcalc.tcz
flviewer.tcz
flburn.tcz
kmaps.tcz
wifi.tcz
wireless-6.6.8-tinycore.tcz
wireless_tools.tcz
wpa_supplicant-dbus.tcz
iw.tcz
pci-utils.tcz
ezremaster.tcz
ndiswrapper.tcz
firmware-atheros.tcz
firmware-broadcom_bcm43xx.tcz
firmware-intel.tcz
firmware-intel_e100.tcz
firmware-ipw2100.tcz
firmware-ipw2200.tcz
firmware-iwimax.tcz
firmware-iwl8000.tcz
firmware-iwl9000.tcz
firmware-iwlwifi.tcz
firmware-marvel.tcz
firmware-myri10ge.tcz
firmware-netxen.tcz
firmware-openfwwf.tcz
firmware-ralinkwifi.tcz
firmware-rtl_nic.tcz
firmware-rtlwifi.tcz
firmware-ti-connectivity.tcz
firmware-ueagle-atm.tcz
firmware-vxge.tcz
firmware-zd1211.tcz
firmware-chelsio.tcz
firmware-tigon.tcz
firmware-amd-ucode.tcz
LIST

chmod +x "$0" 2>/dev/null || true

echo "=========================================================="
echo "    [DOWNLOAD] CorePlus Extension Ingestion Completed!"
echo "    Total packages in $DEST: $(ls -1 "$DEST"/*.tcz | wc -l)"
echo "    Total size: $(du -sh "$DEST" | cut -f1)"
echo "=========================================================="
