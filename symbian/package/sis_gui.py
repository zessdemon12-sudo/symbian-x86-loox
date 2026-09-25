#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Graphical Package Installer (sis-installer-gui)
Symbian Belle styled lightweight installer for .sis and .sisx packages.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from symbian.package.sis_parser import SisParser
from symbian.package.sis_installer import SymbianPackageManager

class SymbianInstallerGui:
    def __init__(self, root, initial_package=None):
        self.root = root
        self.root.title("Symbian Application Installer")
        self.root.geometry("520x460")
        self.root.resizable(False, False)
        self.root.configure(bg="#F4F6F8")

        self.pkg_manager = SymbianPackageManager()
        self.current_pkg = None
        self.current_path = initial_package
        self.installed_app = None

        self._setup_ui()

        if self.current_path and os.path.exists(self.current_path):
            self.load_package(self.current_path)

    def _setup_ui(self):
        # Header Banner (Symbian Blue Gradient)
        header = tk.Frame(self.root, bg="#008BE3", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        
        lbl_title = tk.Label(header, text="Symbian Package Installer", font=("DejaVu Sans", 13, "bold"), fg="#FFFFFF", bg="#008BE3")
        lbl_title.pack(side=tk.LEFT, padx=16, pady=12)

        lbl_sub = tk.Label(header, text="Symbian-X86 LOOX OS", font=("DejaVu Sans", 9), fg="#D0ECFC", bg="#008BE3")
        lbl_sub.pack(side=tk.RIGHT, padx=16, pady=14)

        # Main Content Frame
        self.content = tk.Frame(self.root, bg="#F4F6F8", padx=20, pady=15)
        self.content.pack(fill=tk.BOTH, expand=True)

        # File Selection Frame
        file_frame = tk.Frame(self.content, bg="#F4F6F8")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_path = tk.Label(file_frame, text="No package selected", font=("DejaVu Sans", 9, "italic"), fg="#555", bg="#FFFFFF", relief=tk.SUNKEN, anchor=tk.W, padx=6, height=1)
        self.lbl_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        btn_browse = tk.Button(file_frame, text="Browse...", command=self.browse_file, bg="#E2E6EA", font=("DejaVu Sans", 9))
        btn_browse.pack(side=tk.RIGHT)

        # Package Details Frame
        self.card = tk.LabelFrame(self.content, text=" Application Details ", font=("DejaVu Sans", 9, "bold"), bg="#FFFFFF", fg="#222", padx=12, pady=8)
        self.card.pack(fill=tk.BOTH, expand=True, pady=5)

        self.lbl_name = tk.Label(self.card, text="Name: -", font=("DejaVu Sans", 10, "bold"), bg="#FFFFFF", anchor=tk.W)
        self.lbl_name.pack(fill=tk.X, pady=2)

        self.lbl_vendor = tk.Label(self.card, text="Vendor: -", font=("DejaVu Sans", 9), bg="#FFFFFF", anchor=tk.W)
        self.lbl_vendor.pack(fill=tk.X, pady=1)

        self.lbl_version = tk.Label(self.card, text="Version: -", font=("DejaVu Sans", 9), bg="#FFFFFF", anchor=tk.W)
        self.lbl_version.pack(fill=tk.X, pady=1)

        self.lbl_uid = tk.Label(self.card, text="UID3 / SecureID: -", font=("DejaVu Sans", 9), bg="#FFFFFF", anchor=tk.W)
        self.lbl_uid.pack(fill=tk.X, pady=1)

        self.lbl_caps = tk.Label(self.card, text="Requested Permissions: -", font=("DejaVu Sans", 9), bg="#FFFFFF", anchor=tk.W, fg="#006699")
        self.lbl_caps.pack(fill=tk.X, pady=2)

        # Target Drive Selection
        drive_frame = tk.LabelFrame(self.content, text=" Target Drive ", font=("DejaVu Sans", 9, "bold"), bg="#F4F6F8", fg="#222", padx=10, pady=5)
        drive_frame.pack(fill=tk.X, pady=5)

        self.drive_var = tk.StringVar(value="C:")
        rb_c = tk.Radiobutton(drive_frame, text="C: Phone Memory (Internal Storage)", variable=self.drive_var, value="C:", bg="#F4F6F8", font=("DejaVu Sans", 9))
        rb_c.pack(anchor=tk.W)
        rb_e = tk.Radiobutton(drive_frame, text="E: Memory Card / Removable USB", variable=self.drive_var, value="E:", bg="#F4F6F8", font=("DejaVu Sans", 9))
        rb_e.pack(anchor=tk.W)

        # Progress & Status
        self.progress = ttk.Progressbar(self.content, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(8, 2))

        self.lbl_status = tk.Label(self.content, text="Ready to install.", font=("DejaVu Sans", 8), bg="#F4F6F8", fg="#666")
        self.lbl_status.pack(anchor=tk.W)

        # Bottom Action Bar
        bottom = tk.Frame(self.root, bg="#E8ECEF", height=45)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_install = tk.Button(bottom, text="Install Application", font=("DejaVu Sans", 10, "bold"), bg="#008BE3", fg="#FFFFFF", padx=14, pady=4, state=tk.DISABLED, command=self.do_install)
        self.btn_install.pack(side=tk.RIGHT, padx=14, pady=8)

        btn_cancel = tk.Button(bottom, text="Close", font=("DejaVu Sans", 9), bg="#D4D8DC", padx=10, pady=4, command=self.root.quit)
        btn_cancel.pack(side=tk.RIGHT, padx=4, pady=8)

    def browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("Symbian Packages", "*.sisx *.sis"), ("All Files", "*.*")])
        if f:
            self.load_package(f)

    def load_package(self, path):
        try:
            self.current_path = path
            self.lbl_path.config(text=os.path.basename(path), fg="#111")
            self.current_pkg = SisParser.parse(path)

            self.lbl_name.config(text=f"Name: {self.current_pkg.app_name}")
            self.lbl_vendor.config(text=f"Vendor: {self.current_pkg.vendor_name}")
            self.lbl_version.config(text=f"Version: {self.current_pkg.version_string()}")
            self.lbl_uid.config(text=f"UID3 / SecureID: 0x{self.current_pkg.uid3:08X} ({self.current_pkg.target_type})")
            
            caps = self.current_pkg.capability_list()
            self.lbl_caps.config(text=f"Requested Permissions: {', '.join(caps) if caps else 'Basic (Safe)'}")

            self.btn_install.config(state=tk.NORMAL)
            self.lbl_status.config(text="Package validated. Click 'Install Application' to proceed.", fg="#006600")
        except Exception as e:
            messagebox.showerror("Invalid Package", f"Failed to parse Symbian package:\n{e}")
            self.lbl_status.config(text="Error parsing package.", fg="#CC0000")

    def do_install(self):
        if not self.current_pkg or not self.current_path:
            return

        self.btn_install.config(state=tk.DISABLED)
        self.lbl_status.config(text="Extracting and registering files...", fg="#006699")
        self.progress["value"] = 50
        self.root.update_idletasks()

        target = self.drive_var.get()
        try:
            res = self.pkg_manager.install(self.current_path, target_drive=target)
            self.progress["value"] = 100
            self.lbl_status.config(text="Installation successful!", fg="#008800")
            
            answer = messagebox.askyesno("Installation Complete", f"{self.current_pkg.app_name} has been installed successfully!\n\nWould you like to launch it now?")
            if answer:
                # Launch via desktop shortcut
                desk = self.pkg_manager.registry.get(f"0x{self.current_pkg.uid3:08X}").get("desktop_file")
                if desk:
                    os.system(f"gtk-launch {os.path.basename(desk)} &")
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Installation Error", f"Installation failed:\n{e}")
            self.lbl_status.config(text=f"Installation failed: {e}", fg="#CC0000")
            self.btn_install.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    initial_pkg = sys.argv[1] if len(sys.argv) > 1 else None
    app = SymbianInstallerGui(root, initial_pkg)
    root.mainloop()

if __name__ == "__main__":
    main()
