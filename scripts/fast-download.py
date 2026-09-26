import urllib.request
import os
import concurrent.futures

REPO_15 = "http://repo.tinycorelinux.net/15.x/x86/tcz/"
REPO_10 = "http://repo.tinycorelinux.net/10.x/x86/tcz/"
DEST = "kernel/tinycore/tcz_apps"
os.makedirs(DEST, exist_ok=True)

PACKAGES = [
    # Non-US Keymaps
    ("kmaps.tcz", REPO_15),
    
    # Remaster Tools
    ("ezremaster.tcz", REPO_15),
    ("advcomp.tcz", REPO_15),
    ("mkisofs-tools.tcz", REPO_15),
    ("syslinux.tcz", REPO_15),
    
    # Wireless & Tools
    ("wifi.tcz", REPO_15),
    ("wireless-6.6.8-tinycore.tcz", REPO_15),
    ("wireless_tools.tcz", REPO_15),
    ("libiw.tcz", REPO_15),
    ("wpa_supplicant-dbus.tcz", REPO_15),
    ("iw.tcz", REPO_15),
    ("libnl.tcz", REPO_15),
    ("pci-utils.tcz", REPO_15),
    ("libpci.tcz", REPO_15),
    
    # Firmware Collection
    ("firmware-atheros.tcz", REPO_15),
    ("firmware-broadcom_bcm43xx.tcz", REPO_15),
    ("firmware-intel.tcz", REPO_15),
    ("firmware-intel_e100.tcz", REPO_15),
    ("firmware-ipw2100.tcz", REPO_15),
    ("firmware-ipw2200.tcz", REPO_15),
    ("firmware-iwimax.tcz", REPO_15),
    ("firmware-iwl8000.tcz", REPO_15),
    ("firmware-iwl9000.tcz", REPO_15),
    ("firmware-iwlwifi.tcz", REPO_15),
    ("firmware-marvel.tcz", REPO_15),
    ("firmware-myri10ge.tcz", REPO_15),
    ("firmware-netxen.tcz", REPO_15),
    ("firmware-openfwwf.tcz", REPO_15),
    ("firmware-ralinkwifi.tcz", REPO_15),
    ("firmware-rtl_nic.tcz", REPO_15),
    ("firmware-rtlwifi.tcz", REPO_15),
    ("firmware-ti-connectivity.tcz", REPO_15),
    ("firmware-ueagle-atm.tcz", REPO_15),
    ("firmware-vxge.tcz", REPO_15),
    ("firmware-zd1211.tcz", REPO_15),
    ("firmware-chelsio.tcz", REPO_15),
    ("firmware-tigon.tcz", REPO_15),
    ("firmware-amd-ucode.tcz", REPO_15),
    
    # Ndiswrapper
    ("ndiswrapper.tcz", REPO_10),
]

def download_file(item):
    pkg, repo = item
    target = os.path.join(DEST, pkg)
    dep_target = os.path.join(DEST, pkg + ".dep")
    url = repo + pkg
    dep_url = repo + pkg + ".dep"
    
    # Download main package if not present or incomplete
    if not os.path.exists(target):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp, open(target + ".tmp", "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
            os.rename(target + ".tmp", target)
            size_mb = os.path.getsize(target) / (1024 * 1024)
            print(f" [OK] {pkg} ({size_mb:.2f} MB)")
        except Exception as e:
            if os.path.exists(target + ".tmp"):
                os.remove(target + ".tmp")
            print(f" [ERR] {pkg}: {e}")
            return
    else:
        print(f" [CACHED] {pkg}")
        
    # Download .dep file
    if not os.path.exists(dep_target):
        try:
            req = urllib.request.Request(dep_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read()
                if content.strip():
                    with open(dep_target, "wb") as f:
                        f.write(content)
        except Exception:
            pass

print("Starting parallel download with 8 threads...")
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    list(executor.map(download_file, PACKAGES))

print("All downloads finished!")
