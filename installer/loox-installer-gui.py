#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Live Desktop Graphical Installer
Target: Fujitsu FMV-BIBLO LOOX M/G30
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

class LooxInstallerGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Install Symbian-X86 LOOX OS")
        self.root.geometry("540x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#F4F6F8")

        self.disks = self.detect_disks()
        self._setup_ui()

    def detect_disks(self):
        disks = []
        try:
            out = subprocess.check_output(["lsblk", "-d", "-n", "-o", "NAME,SIZE,MODEL"], text=True)
            for line in out.strip().split("\n"):
                parts = line.split(None, 2)
                if len(parts) >= 2:
                    name = parts[0]
                    size = parts[1]
                    model = parts[2] if len(parts) > 2 else "Drive"
                    if name.startswith("sd") or name.startswith("vd"):
                        disks.append((f"/dev/{name}", f"/dev/{name} ({size} - {model})"))
        except Exception:
            disks.append(("/dev/sda", "/dev/sda (Internal SATA Hard Disk)"))
        return disks

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#008BE3", height=60)
        header.pack(fill=tk.X)
        lbl_title = tk.Label(header, text="Install Symbian-X86 LOOX OS", font=("DejaVu Sans", 13, "bold"), fg="#FFFFFF", bg="#008BE3")
        lbl_title.pack(side=tk.LEFT, padx=16, pady=12)

        content = tk.Frame(self.root, bg="#F4F6F8", padx=20, pady=15)
        content.pack(fill=tk.BOTH, expand=True)

        lbl_desc = tk.Label(content, text="This installer will install Symbian-X86 LOOX OS directly onto the internal hard disk of your Fujitsu FMV-BIBLO LOOX M/G30.", wraplength=480, justify=tk.LEFT, bg="#F4F6F8", font=("DejaVu Sans", 9))
        lbl_desc.pack(anchor=tk.W, pady=(0, 15))

        # Target Disk Selection
        frame_disk = tk.LabelFrame(content, text=" Target Hard Disk ", font=("DejaVu Sans", 9, "bold"), bg="#FFFFFF", padx=12, pady=10)
        frame_disk.pack(fill=tk.X, pady=5)

        self.disk_var = tk.StringVar()
        if self.disks:
            self.disk_var.set(self.disks[0][0])
            for dev, label in self.disks:
                rb = tk.Radiobutton(frame_disk, text=label, variable=self.disk_var, value=dev, bg="#FFFFFF", font=("DejaVu Sans", 9))
                rb.pack(anchor=tk.W, pady=2)
        else:
            lbl_nodisk = tk.Label(frame_disk, text="No suitable disks detected.", bg="#FFFFFF", fg="#C00")
            lbl_nodisk.pack()

        # Warning
        lbl_warn = tk.Label(content, text="⚠️ Warning: All existing partitions and data on the selected drive will be permanently erased and replaced with Symbian-X86 LOOX OS.", wraplength=480, justify=tk.LEFT, bg="#F4F6F8", fg="#C00", font=("DejaVu Sans", 8, "bold"))
        lbl_warn.pack(anchor=tk.W, pady=10)

        # Progress
        self.progress = ttk.Progressbar(content, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=5)

        self.lbl_status = tk.Label(content, text="Ready to install.", font=("DejaVu Sans", 8), bg="#F4F6F8", fg="#666")
        self.lbl_status.pack(anchor=tk.W)

        # Bottom
        bottom = tk.Frame(self.root, bg="#E8ECEF", height=45)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_install = tk.Button(bottom, text="Erase & Install OS", font=("DejaVu Sans", 10, "bold"), bg="#008BE3", fg="#FFFFFF", padx=14, pady=4, command=self.do_install)
        self.btn_install.pack(side=tk.RIGHT, padx=14, pady=8)

        btn_cancel = tk.Button(bottom, text="Cancel", font=("DejaVu Sans", 9), bg="#D4D8DC", padx=10, pady=4, command=self.root.quit)
        btn_cancel.pack(side=tk.RIGHT, padx=4, pady=8)

    def do_install(self):
        target = self.disk_var.get()
        if not target:
            messagebox.showerror("Error", "Please select a target hard disk.")
            return

        confirm = messagebox.askyesno("Confirm Disk Erase", f"Are you sure you want to completely format and install Symbian-X86 LOOX OS on {target}?\n\nALL EXISTING DATA WILL BE LOST!")
        if not confirm:
            return

        self.btn_install.config(state=tk.DISABLED)
        self.progress.start(10)
        self.lbl_status.config(text=f"Partitioning and installing to {target}...", fg="#006699")
        self.root.update_idletasks()

        # Call install.sh
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sh_path = os.path.join(script_dir, "install.sh")
        try:
            cmd = ["sudo", sh_path, target] if os.getuid() != 0 else [sh_path, target]
            # If in simulation or test environment
            res = subprocess.call(cmd)
            self.progress.stop()
            if res == 0:
                self.lbl_status.config(text="Installation completed successfully!", fg="#008800")
                if messagebox.askyesno("Success", "Installation Complete!\n\nWould you like to reboot the computer now?"):
                    os.system("reboot")
                self.root.quit()
            else:
                self.lbl_status.config(text="Installation encountered an error.", fg="#CC0000")
                self.btn_install.config(state=tk.NORMAL)
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Installation Error", f"Installation failed: {e}")
            self.lbl_status.config(text=f"Error: {e}", fg="#CC0000")
            self.btn_install.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = LooxInstallerGui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
