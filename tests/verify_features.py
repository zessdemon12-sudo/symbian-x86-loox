import subprocess
import time
import socket
import json
import os
import sys

ISO = "output/symbian-x86-loox.iso"
QMP_SOCK = "/tmp/qemu_qmp.sock"
SERIAL_SOCK = "/tmp/qemu_serial.sock"
SCREENSHOT = "docs/screenshots/screenshot_coreplus_features.png"

for s in (QMP_SOCK, SERIAL_SOCK):
    if os.path.exists(s):
        os.remove(s)

cmd = [
    "qemu-system-i386",
    "-name", "Symbian-X86 Feature Verification",
    "-enable-kvm",
    "-cpu", "host",
    "-smp", "2",
    "-m", "512M",
    "-cdrom", ISO,
    "-boot", "d",
    "-netdev", "user,id=net0",
    "-device", "e1000,netdev=net0",
    "-vga", "std",
    "-display", "none",
    "-qmp", f"unix:{QMP_SOCK},server,nowait",
    "-serial", f"unix:{SERIAL_SOCK},server,nowait"
]

print("Launching QEMU...")
proc = subprocess.Popen(cmd)

try:
    # Connect QMP
    time.sleep(1)
    qmp = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    for _ in range(10):
        try:
            qmp.connect(QMP_SOCK)
            break
        except Exception:
            time.sleep(0.5)
            
    qmp_data = qmp.recv(1024)
    qmp.sendall(json.dumps({"execute": "qmp_capabilities"}).encode() + b"\n")
    qmp.recv(1024)
    print("QMP connected successfully.")

    # Connect Serial
    ser = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    for _ in range(10):
        try:
            ser.connect(SERIAL_SOCK)
            break
        except Exception:
            time.sleep(0.5)
            
    ser.setblocking(False)
    print("Serial console connected.")
    
    # Press Enter on bootloader menu immediately
    time.sleep(0.5)
    ser.sendall(b"\r\n")
    time.sleep(0.5)
    ser.sendall(b"\r\n")
    
    print("Waiting for Tiny Core system boot and user login...")
    boot_log = b""
    t0 = time.time()
    logged_in = False
    
    while time.time() - t0 < 45:
        try:
            chunk = ser.recv(4096)
            if chunk:
                boot_log += chunk
                sys.stdout.write(chunk.decode("utf-8", "ignore"))
                sys.stdout.flush()
                if b"tc@loox:" in boot_log or b"Drives: C:" in boot_log:
                    logged_in = True
                    break
        except Exception:
            pass
        time.sleep(0.5)
            
    print("\n\n=== Boot completed! Sending diagnostics ===")
    time.sleep(2)
    ser.sendall(b"\n")
    time.sleep(1)
    
    diag_cmds = [
        "echo '=== NETWORK CHECK ==='",
        "ifconfig eth0",
        "route -n",
        "echo '=== KMAPS CHECK ==='",
        "ls -d /usr/share/kmap/* | head -n 8",
        "echo '=== WIRELESS TOOLS CHECK ==='",
        "iwconfig --version || true",
        "wpa_supplicant -v || true",
        "echo '=== NDISWRAPPER CHECK ==='",
        "ndiswrapper -v || true",
        "echo '=== EZREMASTER CHECK ==='",
        "which ezremaster || true",
        "echo '=== FIRMWARE CHECK ==='",
        "ls /usr/local/lib/firmware | head -n 12",
        "echo '=== SYMBIAN APPS CHECK ==='",
        "which symbian-network symbian-keyboard symbian-remaster symbian-ndiswrapper",
        "echo '=== LAUNCHING APPS FOR SCREENSHOT ==='",
        "DISPLAY=:0.0 /usr/bin/symbian-network &",
        "sleep 1",
        "DISPLAY=:0.0 /usr/bin/symbian-keyboard &",
        "sleep 1",
        "DISPLAY=:0.0 /usr/bin/symbian-remaster &",
        "sleep 3"
    ]
    
    for c in diag_cmds:
        ser.sendall(c.encode() + b"\n")
        time.sleep(1.0)
        try:
            resp = ser.recv(8192)
            sys.stdout.write(resp.decode("utf-8", "ignore"))
            sys.stdout.flush()
        except Exception:
            pass

    # Wait for windows to render
    time.sleep(3)
    
    # Capture Screenshot via QMP
    print(f"\nCapturing live desktop screenshot to {SCREENSHOT}...")
    ppm_path = "/tmp/qemu_screen.ppm"
    qmp_req = {"execute": "screendump", "arguments": {"filename": ppm_path}}
    qmp.sendall(json.dumps(qmp_req).encode() + b"\n")
    time.sleep(1)
    
    if os.path.exists(ppm_path):
        from PIL import Image
        img = Image.open(ppm_path)
        img.save(SCREENSHOT, "PNG")
        print(f"Screenshot successfully saved: {SCREENSHOT} ({img.size[0]}x{img.size[1]})")
        os.remove(ppm_path)
    else:
        print("Warning: Screendump file not created.")

finally:
    print("Terminating QEMU...")
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
