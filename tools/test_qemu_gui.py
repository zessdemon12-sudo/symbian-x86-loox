#!/usr/bin/env python3
import subprocess
import time
import os
import socket
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
USB_IMG = os.path.join(BASE_DIR, "output", "symbian-x86-loox-usb.img")
SCREEN_PPM = "/tmp/qemu_screen.ppm"
SCREEN_PNG = os.path.join(BASE_DIR, "output", "screenshot_desktop.png")
DOC_PNG = os.path.join(BASE_DIR, "docs", "screenshots", "screenshot_desktop.png")
MONITOR_SOCK = "/tmp/qemu_monitor.sock"
SERIAL_LOG = "/tmp/qemu_serial.log"

if os.path.exists(MONITOR_SOCK):
    os.remove(MONITOR_SOCK)
if os.path.exists(SCREEN_PPM):
    os.remove(SCREEN_PPM)
if os.path.exists(SERIAL_LOG):
    os.remove(SERIAL_LOG)

qemu_cmd = [
    "qemu-system-i386",
    "-name", "Symbian-X86 LOOX OS",
    "-m", "512M",
    "-smp", "2",
    "-kernel", os.path.join(BASE_DIR, "output", "boot", "vmlinuz"),
    "-initrd", os.path.join(BASE_DIR, "output", "boot", "core.gz"),
    "-append", "loglevel=3 quiet waitusb=5 cde console=ttyS0,115200 console=tty0",
    "-drive", f"file={USB_IMG},format=raw",
    "-vga", "std",
    "-display", "none",
    "-monitor", f"unix:{MONITOR_SOCK},server,nowait",
    "-serial", f"file:{SERIAL_LOG}",
]

print(f"[TEST] Launching QEMU with image: {USB_IMG}")
proc = subprocess.Popen(qemu_cmd)

try:
    for _ in range(30):
        if os.path.exists(MONITOR_SOCK):
            break
        time.sleep(0.5)

    if not os.path.exists(MONITOR_SOCK):
        raise RuntimeError("QEMU monitor socket not created!")

    print("[TEST] QEMU started. Waiting 35 seconds for kernel decompression & desktop init...")
    time.sleep(35)

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(MONITOR_SOCK)
    time.sleep(0.5)
    _ = s.recv(1024)

    print("[TEST] Sending screendump command to QEMU monitor...")
    s.sendall(f"screendump {SCREEN_PPM}\n".encode('utf-8'))
    time.sleep(2)
    s.close()

    if os.path.exists(SCREEN_PPM):
        print(f"[TEST] Screendump captured: {SCREEN_PPM}")
        img = Image.open(SCREEN_PPM)
        os.makedirs(os.path.dirname(SCREEN_PNG), exist_ok=True)
        os.makedirs(os.path.dirname(DOC_PNG), exist_ok=True)
        img.save(SCREEN_PNG, "PNG")
        img.save(DOC_PNG, "PNG")
        print(f"[TEST] Saved screenshot to {SCREEN_PNG} and {DOC_PNG} ({img.size[0]}x{img.size[1]})")
    else:
        print("[ERROR] Screendump file was not created!")

    if os.path.exists(SERIAL_LOG):
        print("\n--- Serial Console Log (Last 30 lines) ---")
        with open(SERIAL_LOG, "r", errors="ignore") as f:
            lines = f.readlines()
            for line in lines[-30:]:
                print(line.rstrip())
        print("------------------------------------------\n")

finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    if os.path.exists(MONITOR_SOCK):
        os.remove(MONITOR_SOCK)
