# Hardware Specification: Fujitsu FMV-BIBLO LOOX M/G30

This document defines the hardware platform, device identifiers, Linux kernel modules, and power optimization profiles for the Fujitsu FMV-BIBLO LOOX M/G30 netbook.

---

## 1. System Specifications

| Component | Hardware Specification | Linux Driver / Subsystem | Status & Configuration |
| :--- | :--- | :--- | :--- |
| **Processor (CPU)** | Intel Atom N450 @ 1.66 GHz (Pineview-M, 1 Core, 2 Threads, 512KB L2, 64-bit capable) | `intel_idle`, `acpi-cpufreq`, `intel_pstate` (passive) | Target: 32-bit i686 for minimal RAM overhead; SSSE3 optimized |
| **Chipset** | Intel NM10 Express (Tiger Point) | `lpc_ich`, `i2c_i801` | Core southbridge controller |
| **Graphics (GPU)** | Intel Graphics Media Accelerator 3150 (GMA 3150, Gen 3.5) | `i915` (Direct Rendering Manager / KMS) | 1024x600 native WSVGA TFT; OpenGL 1.4/1.5 via Mesa `crocus` / `i915` |
| **Memory (RAM)** | 1 GB or 2 GB DDR2-667/800 SO-DIMM (Single channel) | Linux Memory Management + `zram` | Compressed RAM swap (1.5x physical RAM) mandatory for smooth multitasking |
| **Storage** | 160 GB / 250 GB 2.5" SATA-II 5400 RPM HDD | `ahci`, `libata`, `sd_mod` | `ext4` filesystem with `noatime`, `barrier=0` (optional), writeback cache |
| **Display Panel** | 10.1-inch WSVGA TFT Color LCD (1024 x 600, 16:9) | `drm_kms_helper`, `i915` | Native mode 1024x600 @ 60Hz; brightness via `intel_backlight` |
| **Audio** | Realtek High Definition Audio (ALC269 codec) | `snd_hda_intel`, `snd_hda_codec_realtek` | Stereo speakers, internal mic, headphone/mic combo jack |
| **Ethernet** | Realtek RTL8102E / RTL8103E 10/100 Mbps PCI-E Fast Ethernet | `r8169` | Standard auto-negotiation, power saving enabled |
| **Wireless LAN** | Atheros AR9285 802.11b/g/n Wireless Network Adapter | `ath9k` | Full open-source mac80211 driver; power saving `ps_mode=1` |
| **Bluetooth** | Integrated USB Bluetooth (optional model variants) | `btusb`, `bluetooth` | Standard BlueZ stack |
| **Webcam** | Fujitsu Integrated 1.3MP USB Webcam | `uvcvideo`, `videodev` | V4L2 interface, compatible with Cheese, VLC, browser WebRTC |
| **Input: Keyboard** | Japanese 84-key or US layout notebook keyboard | `atkbd`, `i8042` | PS/2 interface |
| **Input: Touchpad** | Synaptics / Alps PS/2 Touchpad with 2 physical buttons | `psmouse` | Multi-touch vertical edge scrolling, tapping enabled |
| **Power & Battery** | 3-cell or 6-cell Lithium-ion battery pack, AC adapter (19V) | `battery`, `ac`, `thermal` | ACPI battery status `/sys/class/power_supply/BAT0`, S3 sleep |

---

## 2. Kernel Boot Parameters for LOOX M/G30

To achieve fast boot, ultra-low idle RAM, and optimal power consumption on the Atom N450, the kernel command line is configured as:

```text
quiet splash loglevel=3 elevator=deadline intel_idle.max_cstate=4 pcie_aspm=force mitigations=auto,nosmt zswap.enabled=0
```

### Parameter Rationale:
- `elevator=deadline`: Minimizes I/O latency on slow 5400 RPM 2.5" mechanical laptop drives.
- `intel_idle.max_cstate=4`: Enables deep C-states (C1, C2, C4) on Pineview Atom processors, extending battery life significantly.
- `pcie_aspm=force`: Forces Active State Power Management on PCIe links (Atheros Wi-Fi and Realtek NIC).
- `mitigations=auto,nosmt`: Disables hyperthreading-dependent speculative mitigations that severely degrade performance on single-core Atom CPUs without hardware vulnerability.
- `zswap.enabled=0`: Disables zswap in favor of dedicated `zram` swap devices configured with zstd compression.

---

## 3. Power & Thermal Management

The LOOX M/G30 relies on a single small fan and passive copper heat-pipe:
1. **CPU Frequency Scaling**: Handled by the `acpi-cpufreq` or `intel_pstate` driver with the `ondemand` governor.
   - Frequency steps: 1000 MHz, 1333 MHz, 1666 MHz.
2. **Thermal Trip Points**:
   - Passive cooling at 75°C (CPU throttling).
   - Active cooling (fan high) at 85°C.
   - Critical shutdown at 100°C.
3. **Display Backlight**:
   - Controlled via `/sys/class/backlight/intel_backlight/`.
   - ACPI hotkeys (`Fn + F6`, `Fn + F7`) mapped to `xbacklight` or `brightnessctl`.
