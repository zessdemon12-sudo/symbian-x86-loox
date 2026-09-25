#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Native Symbian File Manager
Displays drives C:, D:, E:, Z: with Symbian hierarchy and capacity status.
UID3: 0x2000E004
"""

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from symbian.api.symbian_core import SymbianDriveManager

class SymbianFileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Symbian File Manager")
        self.root.geometry("640x440")
        self.root.configure(bg="#F4F6F8")

        self.drives = {
            "C: Phone Memory": SymbianDriveManager.resolve_path("C:\\"),
            "D: Internal Storage": SymbianDriveManager.resolve_path("D:\\"),
            "E: Memory Card / USB": SymbianDriveManager.resolve_path("E:\\"),
            "Z: ROM (Symbian Core)": SymbianDriveManager.resolve_path("Z:\\")
        }
        self.current_path = self.drives["C: Phone Memory"]

        self._setup_ui()
        self.refresh_drives()
        self.browse_path(self.current_path)

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#37474F", height=45)
        header.pack(fill=tk.X)
        lbl = tk.Label(header, text="Symbian File Manager", font=("DejaVu Sans", 11, "bold"), fg="#FFFFFF", bg="#37474F")
        lbl.pack(side=tk.LEFT, padx=12, pady=10)

        # Path bar
        path_frame = tk.Frame(self.root, bg="#E8ECEF")
        path_frame.pack(fill=tk.X, padx=4, pady=2)
        btn_up = tk.Button(path_frame, text="▲ Up", command=self.go_up, bg="#FFFFFF")
        btn_up.pack(side=tk.LEFT, padx=2)
        self.lbl_current_path = tk.Label(path_frame, text="", font=("DejaVu Sans", 9), anchor=tk.W, bg="#FFFFFF", relief=tk.SUNKEN)
        self.lbl_current_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # Main splitter
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#CCD1D6")
        paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Left Pane: Drives list
        left_frame = tk.Frame(paned, bg="#FFFFFF", width=180)
        paned.add(left_frame, minsize=140)

        lbl_drives = tk.Label(left_frame, text="Drives", font=("DejaVu Sans", 9, "bold"), bg="#E8ECEF", anchor=tk.W, padx=6)
        lbl_drives.pack(fill=tk.X)

        self.tree_drives = ttk.Treeview(left_frame, show="tree", selectmode="browse")
        self.tree_drives.pack(fill=tk.BOTH, expand=True)
        self.tree_drives.bind("<<TreeviewSelect>>", self.on_drive_selected)

        # Right Pane: File list
        right_frame = tk.Frame(paned, bg="#FFFFFF")
        paned.add(right_frame, minsize=280)

        columns = ("name", "size", "type")
        self.tree_files = ttk.Treeview(right_frame, columns=columns, show="headings", selectmode="browse")
        self.tree_files.heading("name", text="Name")
        self.tree_files.heading("size", text="Size")
        self.tree_files.heading("type", text="Type")
        self.tree_files.column("name", width=220)
        self.tree_files.column("size", width=80, anchor=tk.E)
        self.tree_files.column("type", width=80)
        self.tree_files.pack(fill=tk.BOTH, expand=True)
        self.tree_files.bind("<Double-1>", self.on_file_double_click)

        # Status Bar
        self.lbl_status = tk.Label(self.root, text="Ready", font=("DejaVu Sans", 8), bg="#F4F6F8", fg="#666", anchor=tk.W)
        self.lbl_status.pack(fill=tk.X, padx=6, pady=2)

    def refresh_drives(self):
        self.tree_drives.delete(*self.tree_drives.get_children())
        for dname, dpath in self.drives.items():
            os.makedirs(dpath, exist_ok=True)
            self.tree_drives.insert("", tk.END, text=dname, values=(dpath,))

    def on_drive_selected(self, event):
        sel = self.tree_drives.selection()
        if sel:
            path = self.tree_drives.item(sel[0])["values"][0]
            self.browse_path(path)

    def browse_path(self, path):
        if not os.path.exists(path):
            return
        self.current_path = os.path.abspath(path)
        self.lbl_current_path.config(text=self.current_path)

        self.tree_files.delete(*self.tree_files.get_children())
        try:
            entries = os.listdir(self.current_path)
            entries.sort(key=lambda s: (not os.path.isdir(os.path.join(self.current_path, s)), s.lower()))
            
            for e in entries:
                full = os.path.join(self.current_path, e)
                if os.path.isdir(full):
                    self.tree_files.insert("", tk.END, values=(f"📁 {e}", "-", "Folder"))
                else:
                    sz = os.path.getsize(full)
                    sz_str = f"{sz/1024:.1f} KB" if sz < 1048576 else f"{sz/1048576:.1f} MB"
                    self.tree_files.insert("", tk.END, values=(f"📄 {e}", sz_str, "File"))
            
            self.lbl_status.config(text=f"Total items: {len(entries)}")
        except Exception as ex:
            self.lbl_status.config(text=f"Error accessing directory: {ex}")

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.browse_path(parent)

    def on_file_double_click(self, event):
        sel = self.tree_files.selection()
        if not sel:
            return
        item = self.tree_files.item(sel[0])
        name = item["values"][0][2:].strip() # Strip folder/file emoji
        target = os.path.join(self.current_path, name)

        if os.path.isdir(target):
            self.browse_path(target)
        else:
            # Check if .sis or .sisx
            if target.endswith(".sis") or target.endswith(".sisx"):
                subprocess.Popen(["python3", "-m", "symbian.package.sis_gui", target])
            elif target.endswith(".exe") or target.endswith(".bin"):
                subprocess.Popen(["python3", "-m", "symbian.package.symbian_run", target])
            else:
                try:
                    subprocess.Popen(["xdg-open", target])
                except Exception:
                    pass

def main():
    root = tk.Tk()
    app = SymbianFileManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
