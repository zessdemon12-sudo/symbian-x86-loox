#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Operating System Remastering Assistant
Provides quick access to:
- Official Tiny Core ezremaster graphical remastering engine
- Symbian-X86 custom ISO and USB disk image remastering
- System state backup (filetool.sh -b)
- Extension inspection & persistence management
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

BG_DARK = "#1c222b"
BG_CARD = "#252e3b"
BG_PANEL = "#2d3748"
FG_LIGHT = "#f7fafc"
FG_MUTED = "#a0aec0"
ACCENT_BLUE = "#0088cc"
ACCENT_GREEN = "#38a169"
FONT_TITLE = ("DejaVu Sans", 12, "bold")
FONT_BOLD = ("DejaVu Sans", 10, "bold")
FONT_REGULAR = ("DejaVu Sans", 9)
FONT_MONO = ("Monospace", 9)

class RemasterAssistantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Symbian OS Remastering Assistant")
        self.geometry("620x460")
        self.minsize(560, 400)
        self.configure(bg=BG_DARK)
        
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG_CARD, height=52)
        hdr.pack(fill="x")
        lbl = tk.Label(hdr, text="🛠️ Symbian-X86 OS Remastering & Backup", font=FONT_TITLE, bg=BG_CARD, fg=FG_LIGHT)
        lbl.pack(side="left", padx=14, pady=10)
        
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=14, pady=10)
        
        desc = (
            "Customize, backup, and build custom Symbian-X86 LOOX OS images.\n"
            "Create bootable ISOs, configure onboot extensions, and backup user data."
        )
        tk.Label(content, text=desc, font=FONT_REGULAR, bg=BG_DARK, fg=FG_MUTED, justify="left").pack(anchor="w", pady=(0, 10))
        
        # Action Grid Cards
        cards_frame = tk.Frame(content, bg=BG_DARK)
        cards_frame.pack(fill="x", pady=6)
        
        # Card 1: ezremaster
        c1 = tk.Frame(cards_frame, bg=BG_CARD, bd=1, relief="ridge", padx=10, pady=8)
        c1.pack(fill="x", pady=4)
        tk.Label(c1, text="💿 ezremaster GUI Engine", font=FONT_BOLD, bg=BG_CARD, fg=FG_LIGHT).pack(side="left")
        tk.Label(c1, text="Visual Tiny Core ISO Remastering Tool", font=FONT_REGULAR, bg=BG_CARD, fg=FG_MUTED).pack(side="left", padx=10)
        tk.Button(c1, text="🚀 Launch ezremaster", font=FONT_BOLD, bg=ACCENT_BLUE, fg="#ffffff", command=self.launch_ezremaster, bd=0, padx=12, pady=4).pack(side="right")
        
        # Card 2: Backup User State
        c2 = tk.Frame(cards_frame, bg=BG_CARD, bd=1, relief="ridge", padx=10, pady=8)
        c2.pack(fill="x", pady=4)
        tk.Label(c2, text="💾 Backup User State (mydata.tgz)", font=FONT_BOLD, bg=BG_CARD, fg=FG_LIGHT).pack(side="left")
        tk.Label(c2, text="Persist /home/tc and /opt customizations", font=FONT_REGULAR, bg=BG_CARD, fg=FG_MUTED).pack(side="left", padx=10)
        tk.Button(c2, text="⚡ Run Backup", font=FONT_BOLD, bg=ACCENT_GREEN, fg="#ffffff", command=self.run_backup, bd=0, padx=12, pady=4).pack(side="right")
        
        # Card 3: Inspect Loaded Extensions
        c3 = tk.Frame(cards_frame, bg=BG_CARD, bd=1, relief="ridge", padx=10, pady=8)
        c3.pack(fill="x", pady=4)
        tk.Label(c3, text="📦 Loaded Extensions (TCZ)", font=FONT_BOLD, bg=BG_CARD, fg=FG_LIGHT).pack(side="left")
        tk.Button(c3, text="📋 View Loaded Apps", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=self.view_extensions, bd=0, padx=10, pady=4).pack(side="right")
        tk.Button(c3, text="📝 View onboot.lst", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=self.view_onboot, bd=0, padx=10, pady=4).pack(side="right", padx=6)
        
        # Terminal / Output Area
        tk.Label(content, text="Activity Log / Output:", font=FONT_BOLD, bg=BG_DARK, fg=FG_LIGHT).pack(anchor="w", pady=(8, 4))
        self.txt_log = tk.Text(content, bg=BG_CARD, fg=FG_LIGHT, font=FONT_MONO, height=7, wrap="word", bd=1, relief="ridge")
        self.txt_log.pack(fill="both", expand=True, pady=4)
        self.txt_log.insert("end", "Symbian OS Remastering Assistant initialized.\nReady to customize and package live system.\n")

    def log(self, text):
        self.txt_log.insert("end", text + "\n")
        self.txt_log.see("end")

    def launch_ezremaster(self):
        self.log("Launching ezremaster GUI...")
        ez_path = "/usr/local/bin/ezremaster"
        if os.path.exists(ez_path):
            subprocess.Popen(["sudo", ez_path])
        else:
            self.log("Notice: ezremaster binary not found at /usr/local/bin/ezremaster. Loading extension...")
            subprocess.run(["tce-load", "-i", "ezremaster.tcz"], check=False)
            if os.path.exists(ez_path):
                subprocess.Popen(["sudo", ez_path])
            else:
                messagebox.showinfo("ezremaster", "ezremaster is included in the live image extensions.\nRun 'ezremaster' in terminal or check onboot packages.")

    def run_backup(self):
        self.log("Executing filetool.sh -b to create backup archive...")
        self.update()
        try:
            res = subprocess.run(["filetool.sh", "-b"], capture_output=True, text=True, timeout=15)
            self.log(res.stdout or res.stderr or "Backup completed.")
            messagebox.showinfo("Backup", f"Backup process completed.\n{res.stdout}")
        except Exception as e:
            self.log(f"Error during backup: {e}")
            messagebox.showerror("Error", str(e))

    def view_extensions(self):
        self.log("Checking mounted loop extensions in /tmp/tcloop/...")
        try:
            exts = os.listdir("/tmp/tcloop") if os.path.exists("/tmp/tcloop") else []
            self.log(f"Active Loop Mounted Packages ({len(exts)} total):")
            for e in sorted(exts):
                self.log(f"  * {e}")
        except Exception as e:
            self.log(f"Error reading extensions: {e}")

    def view_onboot(self):
        paths = ["/etc/sysconfig/tcedir/onboot.lst", "/mnt/sda1/tce/onboot.lst", "/cde/onboot.lst", "/kernel/tinycore/tcz_apps/onboot.lst"]
        found = False
        for p in paths:
            if os.path.exists(p):
                with open(p) as f:
                    self.log(f"=== {p} ===")
                    self.log(f.read())
                found = True
                break
        if not found:
            self.log("Could not locate onboot.lst in standard TCE directories.")

if __name__ == "__main__":
    app = RemasterAssistantApp()
    app.mainloop()
