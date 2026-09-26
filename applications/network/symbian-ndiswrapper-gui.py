#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Windows Wireless Driver Assistant (ndiswrapper)
Provides a visual interface to install and manage Windows XP/2000/Vista NDIS
wireless network drivers (.INF and .SYS files) on Linux.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

BG_DARK = "#1c222b"
BG_CARD = "#252e3b"
BG_PANEL = "#2d3748"
FG_LIGHT = "#f7fafc"
FG_MUTED = "#a0aec0"
ACCENT_BLUE = "#0088cc"
ACCENT_GREEN = "#38a169"
ACCENT_RED = "#e53e3e"
FONT_TITLE = ("DejaVu Sans", 12, "bold")
FONT_BOLD = ("DejaVu Sans", 10, "bold")
FONT_REGULAR = ("DejaVu Sans", 9)
FONT_MONO = ("Monospace", 9)

class NdiswrapperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Windows Wireless Drivers (ndiswrapper)")
        self.geometry("600x440")
        self.minsize(540, 380)
        self.configure(bg=BG_DARK)
        
        self._build_ui()
        self.refresh_drivers()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG_CARD, height=52)
        hdr.pack(fill="x")
        lbl = tk.Label(hdr, text="🪟 Windows Wireless Driver Manager (ndiswrapper)", font=FONT_TITLE, bg=BG_CARD, fg=FG_LIGHT)
        lbl.pack(side="left", padx=14, pady=10)
        
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=14, pady=10)
        
        desc = (
            "If your Wi-Fi card does not have a native Linux driver, ndiswrapper allows\n"
            "you to load original 32-bit Windows XP/2000/Vista (.INF and .SYS) drivers."
        )
        tk.Label(content, text=desc, font=FONT_REGULAR, bg=BG_DARK, fg=FG_MUTED, justify="left").pack(anchor="w", pady=(0, 10))
        
        # Action Bar
        act_bar = tk.Frame(content, bg=BG_DARK)
        act_bar.pack(fill="x", pady=4)
        
        tk.Button(act_bar, text="📂 Install Windows Driver (.INF)...", font=FONT_BOLD, bg=ACCENT_BLUE, fg="#ffffff", command=self.install_inf, bd=0, padx=12, pady=6).pack(side="left", padx=(0, 6))
        tk.Button(act_bar, text="🔄 Refresh List", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=self.refresh_drivers, bd=0, padx=10, pady=6).pack(side="left")
        tk.Button(act_bar, text="❌ Remove Driver", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=self.remove_driver, bd=0, padx=10, pady=6).pack(side="right")
        
        # Installed Drivers Card
        tk.Label(content, text="Installed Windows Wireless Drivers:", font=FONT_BOLD, bg=BG_DARK, fg=FG_LIGHT).pack(anchor="w", pady=(8, 4))
        
        self.txt_drivers = tk.Text(content, bg=BG_CARD, fg=FG_LIGHT, font=FONT_MONO, height=8, wrap="word", bd=1, relief="ridge")
        self.txt_drivers.pack(fill="both", expand=True, pady=4)
        
        # Load Module Bar
        mod_bar = tk.Frame(content, bg=BG_CARD, bd=1, relief="ridge", padx=10, pady=8)
        mod_bar.pack(fill="x", pady=8)
        
        tk.Label(mod_bar, text="Activate Windows Driver Kernel Module:", font=FONT_BOLD, bg=BG_CARD, fg=FG_LIGHT).pack(side="left")
        tk.Button(mod_bar, text="🚀 Load ndiswrapper", font=FONT_BOLD, bg=ACCENT_GREEN, fg="#ffffff", command=self.load_ndis_module, bd=0, padx=12, pady=4).pack(side="right")

    def refresh_drivers(self):
        self.txt_drivers.delete("1.0", "end")
        cmd = ["sudo", "ndiswrapper", "-l"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            out = res.stdout.strip()
            if out:
                self.txt_drivers.insert("end", out)
            else:
                self.txt_drivers.insert("end", "No Windows drivers currently installed with ndiswrapper.\nClick 'Install Windows Driver (.INF)' to add a driver.")
        except FileNotFoundError:
            self.txt_drivers.insert("end", "Notice: 'ndiswrapper' command not found in PATH.\nEnsure ndiswrapper.tcz extension is loaded.")
        except Exception as e:
            self.txt_drivers.insert("end", f"Error checking ndiswrapper: {e}")

    def install_inf(self):
        fpath = filedialog.askopenfilename(
            title="Select Windows Driver INF File",
            filetypes=[("Windows Driver Setup Information", "*.inf *.INF"), ("All Files", "*.*")]
        )
        if not fpath:
            return
        
        try:
            cmd = ["sudo", "ndiswrapper", "-i", fpath]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            messagebox.showinfo("ndiswrapper", f"Installation Output:\n{res.stdout or res.stderr or 'Driver installed successfully.'}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install driver: {e}")
            
        self.refresh_drivers()

    def remove_driver(self):
        sel_drv = self.txt_drivers.get("1.0", "end").strip().splitlines()
        if not sel_drv or "No Windows drivers" in sel_drv[0] or "not found" in sel_drv[0]:
            messagebox.showwarning("Remove", "No installed driver to remove.")
            return
            
        drv_name = sel_drv[0].split()[0]
        if messagebox.askyesno("Confirm", f"Remove Windows driver '{drv_name}'?"):
            subprocess.run(["sudo", "ndiswrapper", "-r", drv_name], check=False)
            self.refresh_drivers()

    def load_ndis_module(self):
        try:
            subprocess.run(["sudo", "ndiswrapper", "-m"], check=False)
            res = subprocess.run(["sudo", "modprobe", "ndiswrapper"], capture_output=True, text=True)
            if res.returncode == 0:
                messagebox.showinfo("Success", "ndiswrapper driver module loaded successfully!\nWireless interface should now appear in Network Manager.")
            else:
                messagebox.showwarning("Module Load", f"Result:\n{res.stderr or 'Check dmesg for module details.'}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = NdiswrapperApp()
    app.mainloop()
