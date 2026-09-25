#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Native Symbian Notes Application
UID3: 0x2000E002
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from symbian.api.symbian_core import SymbianDriveManager, CenRep

if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0.0"

APP_UID = 0x2000E002

class SymbianNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Symbian Notes")
        self.root.geometry("480x400+60+60")
        self.root.configure(bg="#F4F6F8")
        self.root.deiconify()
        self.root.lift()

        self.cenrep = CenRep(APP_UID)
        self.notes_dir = SymbianDriveManager.resolve_path("D:\\Notes")
        os.makedirs(self.notes_dir, exist_ok=True)
        self.current_file = None

        self._setup_ui()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#2E7D32", height=45)
        header.pack(fill=tk.X)
        lbl = tk.Label(header, text="Symbian Notes", font=("DejaVu Sans", 11, "bold"), fg="#FFFFFF", bg="#2E7D32")
        lbl.pack(side=tk.LEFT, padx=12, pady=10)

        # Toolbar
        toolbar = tk.Frame(self.root, bg="#E8ECEF")
        toolbar.pack(fill=tk.X, pady=2)
        btn_new = tk.Button(toolbar, text="New", command=self.new_note, bg="#FFFFFF")
        btn_new.pack(side=tk.LEFT, padx=4, pady=2)
        btn_open = tk.Button(toolbar, text="Open...", command=self.open_note, bg="#FFFFFF")
        btn_open.pack(side=tk.LEFT, padx=4, pady=2)
        btn_save = tk.Button(toolbar, text="Save", command=self.save_note, bg="#FFFFFF")
        btn_save.pack(side=tk.LEFT, padx=4, pady=2)

        # Text Area
        self.text_area = tk.Text(self.root, font=("DejaVu Sans", 10), wrap=tk.WORD, bg="#FFFFFF", fg="#222")
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        welcome_note = (
            "Symbian-X86 LOOX OS\n"
            "========================================\n"
            "Platform: Fujitsu FMV-BIBLO LOOX M/G30\n"
            "Processor: Intel Atom N450 @ 1.66 GHz\n"
            "Display: 1024x600 Netbook Screen\n"
            "Base: Tiny Core Linux 15.x x86 (RAM-based)\n"
            "Theme: Symbian Belle UI + Wbar Dock\n\n"
            "Drive Mappings:\n"
            "  C: -> /home/tc (User Home)\n"
            "  D: -> /media (Removable Media)\n"
            "  Z: -> /opt/symbian/rom (Symbian ROM)\n\n"
            "Status: System operational. Zero-panic OK!"
        )
        self.text_area.insert("1.0", welcome_note)

        # Status
        self.status = tk.Label(self.root, text=f"Storage: {self.notes_dir}", font=("DejaVu Sans", 8), bg="#F4F6F8", fg="#666", anchor=tk.W)
        self.status.pack(fill=tk.X, padx=8, pady=2)

    def new_note(self):
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.status.config(text="New note created.")

    def open_note(self):
        f = filedialog.askopenfilename(initialdir=self.notes_dir, filetypes=[("Text Notes", "*.txt"), ("All Files", "*.*")])
        if f:
            with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", fp.read())
            self.current_file = f
            self.status.config(text=f"Loaded: {os.path.basename(f)}")

    def save_note(self):
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(initialdir=self.notes_dir, defaultextension=".txt", filetypes=[("Text Notes", "*.txt")])
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as fp:
                fp.write(self.text_area.get("1.0", tk.END).strip())
            self.status.config(text=f"Saved: {os.path.basename(self.current_file)}")

def main():
    root = tk.Tk()
    app = SymbianNotesApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
