#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Native Symbian Task & Application Manager (appmanager)
Combines package management with low-overhead process monitoring.
UID3: 0x2000E005
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from symbian.package.sis_installer import SymbianPackageManager

class SymbianAppManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Symbian Task & Application Manager")
        self.root.geometry("580x440")
        self.root.configure(bg="#F4F6F8")

        self.pkg_mgr = SymbianPackageManager()
        self._setup_ui()
        self.refresh_apps()
        self.refresh_tasks()
        self.refresh_sysinfo()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#5E35B1", height=45)
        header.pack(fill=tk.X)
        lbl = tk.Label(header, text="Symbian Application & Task Manager", font=("DejaVu Sans", 11, "bold"), fg="#FFFFFF", bg="#5E35B1")
        lbl.pack(side=tk.LEFT, padx=12, pady=10)

        # Notebook Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Tab 1: Installed Packages
        self.tab_apps = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_apps, text=" Installed Packages ")
        self._setup_apps_tab()

        # Tab 2: Running Tasks
        self.tab_tasks = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_tasks, text=" Running Tasks ")
        self._setup_tasks_tab()

        # Tab 3: System & Memory
        self.tab_sys = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_sys, text=" Hardware & Memory ")
        self._setup_sys_tab()

    def _setup_apps_tab(self):
        cols = ("name", "version", "uid3", "vendor")
        self.tree_apps = ttk.Treeview(self.tab_apps, columns=cols, show="headings", selectmode="browse")
        self.tree_apps.heading("name", text="Application")
        self.tree_apps.heading("version", text="Version")
        self.tree_apps.heading("uid3", text="UID3")
        self.tree_apps.heading("vendor", text="Vendor")
        self.tree_apps.column("name", width=180)
        self.tree_apps.column("version", width=70)
        self.tree_apps.column("uid3", width=110)
        self.tree_apps.column("vendor", width=140)
        self.tree_apps.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        bar = tk.Frame(self.tab_apps, bg="#E8ECEF")
        bar.pack(fill=tk.X)
        btn_launch = tk.Button(bar, text="Launch", command=self.launch_selected_app, bg="#FFFFFF")
        btn_launch.pack(side=tk.LEFT, padx=6, pady=4)
        btn_uninstall = tk.Button(bar, text="Uninstall", command=self.uninstall_selected_app, bg="#FFCDD2")
        btn_uninstall.pack(side=tk.LEFT, padx=6, pady=4)
        btn_refresh = tk.Button(bar, text="Refresh", command=self.refresh_apps, bg="#FFFFFF")
        btn_refresh.pack(side=tk.RIGHT, padx=6, pady=4)

    def _setup_tasks_tab(self):
        cols = ("pid", "name", "mem")
        self.tree_tasks = ttk.Treeview(self.tab_tasks, columns=cols, show="headings", selectmode="browse")
        self.tree_tasks.heading("pid", text="PID")
        self.tree_tasks.heading("name", text="Process Name")
        self.tree_tasks.heading("mem", text="Memory")
        self.tree_tasks.column("pid", width=70)
        self.tree_tasks.column("name", width=320)
        self.tree_tasks.column("mem", width=110, anchor=tk.E)
        self.tree_tasks.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        bar = tk.Frame(self.tab_tasks, bg="#E8ECEF")
        bar.pack(fill=tk.X)
        btn_end = tk.Button(bar, text="End Task", command=self.end_selected_task, bg="#FFCDD2")
        btn_end.pack(side=tk.LEFT, padx=6, pady=4)
        btn_refresh = tk.Button(bar, text="Refresh", command=self.refresh_tasks, bg="#FFFFFF")
        btn_refresh.pack(side=tk.RIGHT, padx=6, pady=4)

    def _setup_sys_tab(self):
        self.lbl_cpu = tk.Label(self.tab_sys, text="CPU: Intel Atom N450 @ 1.66 GHz", font=("DejaVu Sans", 10, "bold"), bg="#FFFFFF", anchor=tk.W)
        self.lbl_cpu.pack(fill=tk.X, padx=14, pady=6)

        self.lbl_mem = tk.Label(self.tab_sys, text="Memory: Calculating...", font=("DejaVu Sans", 9), bg="#FFFFFF", anchor=tk.W)
        self.lbl_mem.pack(fill=tk.X, padx=14, pady=2)

        self.lbl_zram = tk.Label(self.tab_sys, text="zram Swap: Calculating...", font=("DejaVu Sans", 9), bg="#FFFFFF", anchor=tk.W)
        self.lbl_zram.pack(fill=tk.X, padx=14, pady=2)

        self.lbl_batt = tk.Label(self.tab_sys, text="Battery: Calculating...", font=("DejaVu Sans", 9), bg="#FFFFFF", anchor=tk.W)
        self.lbl_batt.pack(fill=tk.X, padx=14, pady=2)

        btn_refresh = tk.Button(self.tab_sys, text="Refresh Hardware Status", command=self.refresh_sysinfo, bg="#FFFFFF")
        btn_refresh.pack(anchor=tk.W, padx=14, pady=10)

    def refresh_apps(self):
        self.tree_apps.delete(*self.tree_apps.get_children())
        self.pkg_mgr.registry.load()
        for uid, rec in self.pkg_mgr.registry.data.items():
            self.tree_apps.insert("", tk.END, values=(rec.get("name"), rec.get("version"), uid, rec.get("vendor")))

    def launch_selected_app(self):
        sel = self.tree_apps.selection()
        if not sel: return
        uid = self.tree_apps.item(sel[0])["values"][2]
        rec = self.pkg_mgr.registry.get(uid)
        if rec and rec.get("desktop_file"):
            os.system(f"gtk-launch {os.path.basename(rec['desktop_file'])} &")

    def uninstall_selected_app(self):
        sel = self.tree_apps.selection()
        if not sel: return
        uid = self.tree_apps.item(sel[0])["values"][2]
        name = self.tree_apps.item(sel[0])["values"][0]
        if messagebox.askyesno("Uninstall", f"Are you sure you want to uninstall {name}?"):
            self.pkg_mgr.uninstall(uid)
            self.refresh_apps()

    def refresh_tasks(self):
        self.tree_tasks.delete(*self.tree_tasks.get_children())
        try:
            out = subprocess.check_output(["ps", "-eo", "pid,rss,comm", "--sort=-rss"], text=True)
            lines = out.strip().split("\n")[1:25] # top 25 processes
            for line in lines:
                parts = line.split(None, 2)
                if len(parts) == 3:
                    pid, rss, comm = parts
                    mem_mb = f"{int(rss)/1024:.1f} MB"
                    self.tree_tasks.insert("", tk.END, values=(pid, comm, mem_mb))
        except Exception:
            pass

    def end_selected_task(self):
        sel = self.tree_tasks.selection()
        if not sel: return
        pid = self.tree_tasks.item(sel[0])["values"][0]
        name = self.tree_tasks.item(sel[0])["values"][1]
        if messagebox.askyesno("End Task", f"Terminate process '{name}' (PID {pid})?"):
            os.system(f"kill -9 {pid}")
            self.refresh_tasks()

    def refresh_sysinfo(self):
        # RAM & zram
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            mem_dict = {}
            for line in lines:
                parts = line.split(":")
                if len(parts) == 2:
                    mem_dict[parts[0].strip()] = int(parts[1].strip().split()[0])
            total_mb = mem_dict.get("MemTotal", 0) / 1024
            avail_mb = mem_dict.get("MemAvailable", 0) / 1024
            used_mb = total_mb - avail_mb
            self.lbl_mem.config(text=f"RAM: {used_mb:.1f} MB used / {total_mb:.1f} MB total (Available: {avail_mb:.1f} MB)")
            
            swap_total_mb = mem_dict.get("SwapTotal", 0) / 1024
            swap_free_mb = mem_dict.get("SwapFree", 0) / 1024
            self.lbl_zram.config(text=f"Compressed Swap (zram): {swap_total_mb - swap_free_mb:.1f} MB used / {swap_total_mb:.1f} MB total")
        except Exception:
            pass

def main():
    root = tk.Tk()
    app = SymbianAppManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
