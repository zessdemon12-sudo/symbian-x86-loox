#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Unified Network Manager (Wired & Wireless)
Provides comprehensive configuration for:
- Wired Ethernet interfaces (DHCP, Static IP, link status)
- Wireless 802.11 Wi-Fi (SSID scanning, WPA/WPA2 association, signal quality)
- Network diagnostics (Ping, Route, DNS status)
Designed for Fujitsu LOOX M/G30 Netbook (1024x600 TFT).
"""

import os
import sys
import subprocess
import re
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

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

class NetworkManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Symbian Network Manager")
        self.geometry("640x480")
        self.minsize(580, 420)
        self.configure(bg=BG_DARK)
        
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure(".", background=BG_DARK, foreground=FG_LIGHT, font=FONT_REGULAR)
        self.style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=BG_CARD, foreground=FG_LIGHT, padding=[12, 6], font=FONT_BOLD)
        self.style.map("TNotebook.Tab", background=[("selected", ACCENT_BLUE)], foreground=[("selected", "#ffffff")])
        self.style.configure("TButton", background=BG_PANEL, foreground=FG_LIGHT, padding=6, font=FONT_BOLD)
        self.style.map("TButton", background=[("active", ACCENT_BLUE)])
        self.style.configure("Treeview", background=BG_CARD, foreground=FG_LIGHT, fieldbackground=BG_CARD, font=FONT_REGULAR)
        self.style.configure("Treeview.Heading", background=BG_PANEL, foreground=FG_LIGHT, font=FONT_BOLD)
        self.style.map("Treeview", background=[("selected", ACCENT_BLUE)])

        self._build_header()
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=8)
        
        self.tab_wired = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_wifi = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_diag = tk.Frame(self.notebook, bg=BG_DARK)
        
        self.notebook.add(self.tab_wired, text=" Wired Ethernet ")
        self.notebook.add(self.tab_wifi, text=" Wi-Fi Wireless ")
        self.notebook.add(self.tab_diag, text=" Diagnostics ")
        
        self._init_wired_tab()
        self._init_wifi_tab()
        self._init_diag_tab()
        
        self.refresh_all()

    def _build_header(self):
        hdr = tk.Frame(self, bg=BG_CARD, height=52)
        hdr.pack(fill="x", padx=0, pady=0)
        
        lbl_title = tk.Label(hdr, text="🌐 Symbian Connectivity & Networks", font=FONT_TITLE, bg=BG_CARD, fg=FG_LIGHT)
        lbl_title.pack(side="left", padx=14, pady=10)
        
        self.lbl_status = tk.Label(hdr, text="Checking...", font=FONT_BOLD, bg=BG_CARD, fg=ACCENT_BLUE)
        self.lbl_status.pack(side="right", padx=14, pady=10)

    # ---------------------------------------------------------
    # 1. Wired Ethernet Tab
    # ---------------------------------------------------------
    def _init_wired_tab(self):
        frame = tk.Frame(self.tab_wired, bg=BG_DARK)
        frame.pack(fill="both", expand=True, padx=12, pady=10)
        
        top_bar = tk.Frame(frame, bg=BG_DARK)
        top_bar.pack(fill="x", pady=4)
        tk.Label(top_bar, text="Select Ethernet Interface:", font=FONT_BOLD, bg=BG_DARK, fg=FG_LIGHT).pack(side="left")
        
        self.wired_iface_var = tk.StringVar()
        self.cb_wired_ifaces = ttk.Combobox(top_bar, textvariable=self.wired_iface_var, state="readonly", width=16)
        self.cb_wired_ifaces.pack(side="left", padx=10)
        self.cb_wired_ifaces.bind("<<ComboboxSelected>>", lambda e: self.update_wired_details())
        
        btn_refresh = tk.Button(top_bar, text="🔄 Refresh", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=self.refresh_wired, bd=0, padx=10)
        btn_refresh.pack(side="right")
        
        # Details Card
        self.card_wired = tk.Frame(frame, bg=BG_CARD, bd=1, relief="ridge")
        self.card_wired.pack(fill="x", pady=10, ipady=8, ipadx=10)
        
        self.lbl_wired_info = tk.Label(self.card_wired, text="Detecting ethernet devices...", font=FONT_MONO, bg=BG_CARD, fg=FG_LIGHT, justify="left", anchor="w")
        self.lbl_wired_info.pack(fill="both", expand=True, padx=12, pady=8)
        
        # Actions
        btn_box = tk.Frame(frame, bg=BG_DARK)
        btn_box.pack(fill="x", pady=10)
        
        tk.Button(btn_box, text="⚡ Renew DHCP Lease", font=FONT_BOLD, bg=ACCENT_BLUE, fg="#ffffff", command=self.renew_dhcp, bd=0, padx=14, pady=6).pack(side="left", padx=4)
        tk.Button(btn_box, text="⚙️ Static IP Configuration", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=self.config_static_ip, bd=0, padx=12, pady=6).pack(side="left", padx=4)
        tk.Button(btn_box, text="🔴 Disable Interface", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=self.disable_wired, bd=0, padx=10, pady=6).pack(side="right", padx=4)

    def refresh_wired(self):
        ifaces = self.get_ethernet_interfaces()
        self.cb_wired_ifaces["values"] = ifaces
        if ifaces:
            if not self.wired_iface_var.get() or self.wired_iface_var.get() not in ifaces:
                self.wired_iface_var.set(ifaces[0])
            self.update_wired_details()
        else:
            self.lbl_wired_info.config(text="No wired ethernet interfaces (eth*, en*) found.\nPlease verify network hardware cable or PCI drivers.")

    def update_wired_details(self):
        iface = self.wired_iface_var.get()
        if not iface:
            return
        info = self.get_interface_info(iface)
        text = (
            f"Interface:       {iface} (Wired Network)\n"
            f"Status:          {'CONNECTED (UP)' if info['up'] else 'DISCONNECTED / DOWN'}\n"
            f"IP Address:      {info['ip'] or 'Not assigned (DHCP required)'}\n"
            f"Netmask:         {info['mask'] or 'N/A'}\n"
            f"Broadcast:       {info['bcast'] or 'N/A'}\n"
            f"MAC Address:     {info['mac'] or 'N/A'}\n"
            f"Gateway:         {self.get_default_gateway() or 'N/A'}\n"
            f"DNS Servers:     {self.get_dns_servers()}"
        )
        self.lbl_wired_info.config(text=text)
        if info['ip']:
            self.lbl_status.config(text=f"Online: {iface} ({info['ip']})", fg=ACCENT_GREEN)
        else:
            self.lbl_status.config(text=f"{iface}: No IP Address", fg=ACCENT_RED)

    def renew_dhcp(self):
        iface = self.wired_iface_var.get()
        if not iface:
            return
        self.lbl_wired_info.config(text=f"Broadcasting DHCP request on {iface}...\nPlease wait...")
        self.update()
        try:
            subprocess.run(["sudo", "pkill", "-f", f"udhcpc.*{iface}"], check=False)
            subprocess.run(["sudo", "ifconfig", iface, "up"], check=False)
            res = subprocess.run(["sudo", "/sbin/udhcpc", "-b", "-i", iface, "-x", "hostname:loox-symbian", "-n", "-q"], capture_output=True, text=True, timeout=8)
            messagebox.showinfo("DHCP", f"DHCP lease request sent on {iface}.\n{res.stdout}")
        except Exception as e:
            messagebox.showerror("DHCP Error", str(e))
        self.refresh_wired()

    def config_static_ip(self):
        iface = self.wired_iface_var.get()
        if not iface:
            return
        ip = simpledialog.askstring("Static IP", f"Enter IP Address for {iface} (e.g. 192.168.1.50):")
        if not ip:
            return
        mask = simpledialog.askstring("Netmask", "Enter Netmask (e.g. 255.255.255.0):", initialvalue="255.255.255.0")
        gw = simpledialog.askstring("Gateway", "Enter Default Gateway (e.g. 192.168.1.1):")
        dns = simpledialog.askstring("DNS", "Enter Primary DNS (e.g. 8.8.8.8):", initialvalue="8.8.8.8")
        
        try:
            subprocess.run(["sudo", "ifconfig", iface, ip, "netmask", mask, "up"], check=True)
            if gw:
                subprocess.run(["sudo", "route", "add", "default", "gw", gw], check=False)
            if dns:
                with open("/tmp/resolv_tmp.conf", "w") as f:
                    f.write(f"nameserver {dns}\n")
                subprocess.run(["sudo", "cp", "/tmp/resolv_tmp.conf", "/etc/resolv.conf"], check=False)
            messagebox.showinfo("Success", f"{iface} configured with Static IP: {ip}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set static IP: {e}")
        self.refresh_wired()

    def disable_wired(self):
        iface = self.wired_iface_var.get()
        if not iface:
            return
        subprocess.run(["sudo", "ifconfig", iface, "down"], check=False)
        messagebox.showinfo("Disabled", f"Interface {iface} disabled.")
        self.refresh_wired()

    # ---------------------------------------------------------
    # 2. Wireless Wi-Fi Tab
    # ---------------------------------------------------------
    def _init_wifi_tab(self):
        frame = tk.Frame(self.tab_wifi, bg=BG_DARK)
        frame.pack(fill="both", expand=True, padx=12, pady=10)
        
        ctrl_bar = tk.Frame(frame, bg=BG_DARK)
        ctrl_bar.pack(fill="x", pady=4)
        
        tk.Label(ctrl_bar, text="Wi-Fi Interface:", font=FONT_BOLD, bg=BG_DARK, fg=FG_LIGHT).pack(side="left")
        self.wifi_iface_var = tk.StringVar()
        self.cb_wifi_ifaces = ttk.Combobox(ctrl_bar, textvariable=self.wifi_iface_var, state="readonly", width=14)
        self.cb_wifi_ifaces.pack(side="left", padx=8)
        
        btn_scan = tk.Button(ctrl_bar, text="🔍 Scan Networks", font=FONT_BOLD, bg=ACCENT_BLUE, fg="#ffffff", command=self.scan_wifi, bd=0, padx=12)
        btn_scan.pack(side="left", padx=8)
        
        btn_fltk_wifi = tk.Button(ctrl_bar, text="📶 WiFi Wizard", font=FONT_REGULAR, bg=BG_PANEL, fg=FG_LIGHT, command=self.launch_tc_wifi, bd=0, padx=8)
        btn_fltk_wifi.pack(side="right", padx=(4, 0))

        btn_wm = tk.Button(ctrl_bar, text="⚡ wifi-manager", font=FONT_REGULAR, bg=BG_PANEL, fg=FG_LIGHT, command=self.launch_wifi_manager, bd=0, padx=8)
        btn_wm.pack(side="right")
        
        # Treeview for Networks
        columns = ("ssid", "signal", "security")
        self.tree_wifi = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        self.tree_wifi.heading("ssid", text="Network Name (SSID)")
        self.tree_wifi.heading("signal", text="Signal Quality")
        self.tree_wifi.heading("security", text="Encryption")
        self.tree_wifi.column("ssid", width=260)
        self.tree_wifi.column("signal", width=120, anchor="center")
        self.tree_wifi.column("security", width=150, anchor="center")
        self.tree_wifi.pack(fill="both", expand=True, pady=10)
        
        act_box = tk.Frame(frame, bg=BG_DARK)
        act_box.pack(fill="x", pady=4)
        
        tk.Button(act_box, text="🔑 Connect to Selected Network", font=FONT_BOLD, bg=ACCENT_GREEN, fg="#ffffff", command=self.connect_wifi, bd=0, padx=14, pady=6).pack(side="left")
        tk.Button(act_box, text="Disconnect Wi-Fi", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=self.disconnect_wifi, bd=0, padx=10, pady=6).pack(side="right")

    def refresh_wifi_ifaces(self):
        ifaces = self.get_wireless_interfaces()
        self.cb_wifi_ifaces["values"] = ifaces
        if ifaces and not self.wifi_iface_var.get():
            self.wifi_iface_var.set(ifaces[0])

    def scan_wifi(self):
        self.refresh_wifi_ifaces()
        iface = self.wifi_iface_var.get()
        if not iface:
            messagebox.showwarning("Wi-Fi", "No wireless network adapter detected.\nEnsure firmware extensions (firmware-*.tcz) are loaded.")
            return
        
        self.tree_wifi.delete(*self.tree_wifi.get_children())
        subprocess.run(["sudo", "ifconfig", iface, "up"], check=False)
        
        try:
            res = subprocess.run(["sudo", "iwlist", iface, "scan"], capture_output=True, text=True, timeout=10)
            output = res.stdout
        except Exception as e:
            messagebox.showerror("Scan Error", f"Failed to scan on {iface}: {e}")
            return
        
        cells = output.split("Cell ")
        networks = []
        for cell in cells[1:]:
            ssid_m = re.search(r'ESSID:"([^"]+)"', cell)
            ssid = ssid_m.group(1) if ssid_m else "<Hidden SSID>"
            
            sig_m = re.search(r'Quality=([0-9/]+)', cell)
            sig = sig_m.group(1) if sig_m else "N/A"
            
            sec = "Open (None)"
            if "WPA2" in cell:
                sec = "WPA2-PSK"
            elif "WPA" in cell:
                sec = "WPA-PSK"
            elif "Encryption key:on" in cell:
                sec = "WEP"
                
            networks.append((ssid, sig, sec))
            
        for n in networks:
            self.tree_wifi.insert("", "end", values=n)
            
        if not networks:
            messagebox.showinfo("Wi-Fi", f"No wireless networks found in range of {iface}.")

    def connect_wifi(self):
        sel = self.tree_wifi.selection()
        if not sel:
            messagebox.showwarning("Wi-Fi", "Please select a Wi-Fi network from the list first.")
            return
        vals = self.tree_wifi.item(sel[0])["values"]
        ssid = vals[0]
        sec = vals[2]
        iface = self.wifi_iface_var.get()
        
        passwd = ""
        if "WPA" in sec or "WEP" in sec:
            passwd = simpledialog.askstring("Passphrase", f"Enter Wi-Fi password for '{ssid}':", show="*")
            if passwd is None:
                return
        
        # Connect using wpa_supplicant or wifi.sh
        wpa_conf = f"/tmp/wpa_{iface}.conf"
        with open(wpa_conf, "w") as f:
            if passwd:
                f.write(f'network={{\n    ssid="{ssid}"\n    psk="{passwd}"\n}}\n')
            else:
                f.write(f'network={{\n    ssid="{ssid}"\n    key_mgmt=NONE\n}}\n')
                
        subprocess.run(["sudo", "pkill", "-f", f"wpa_supplicant.*{iface}"], check=False)
        cmd = ["sudo", "wpa_supplicant", "-B", "-i", iface, "-c", wpa_conf, "-D", "nl80211,wext"]
        subprocess.run(cmd, check=False)
        
        # Acquire DHCP
        subprocess.run(["sudo", "/sbin/udhcpc", "-b", "-i", iface, "-x", "hostname:loox-symbian", "-n", "-q"], check=False)
        messagebox.showinfo("Connected", f"Attempted connection to '{ssid}' on {iface}.\nCheck status tab for acquired IP.")
        self.refresh_all()

    def disconnect_wifi(self):
        iface = self.wifi_iface_var.get()
        if iface:
            subprocess.run(["sudo", "pkill", "-f", f"wpa_supplicant.*{iface}"], check=False)
            subprocess.run(["sudo", "ifconfig", iface, "down"], check=False)
            messagebox.showinfo("Disconnected", f"Disconnected {iface}.")
            self.refresh_all()

    def launch_tc_wifi(self):
        term = shutil.which("lxterminal") or shutil.which("aterm") or "/usr/local/bin/lxterminal"
        if os.path.exists("/usr/local/bin/wifi.sh") or os.path.exists("/usr/bin/wifi.sh"):
            subprocess.Popen([term, "-e", "sudo wifi.sh"])
        else:
            messagebox.showinfo("Info", "wifi.sh script is provided by wifi.tcz.")

    def launch_wifi_manager(self):
        term = shutil.which("lxterminal") or shutil.which("aterm") or "/usr/local/bin/lxterminal"
        if os.path.exists("/usr/local/bin/wifi-connect") or os.path.exists("/usr/bin/wifi-connect"):
            subprocess.Popen([term, "-e", "sudo wifi-connect"])
        else:
            messagebox.showinfo("Info", "wifi-connect is provided by wifi-manager.tcz.")

    # ---------------------------------------------------------
    # 3. Diagnostics Tab
    # ---------------------------------------------------------
    def _init_diag_tab(self):
        frame = tk.Frame(self.tab_diag, bg=BG_DARK)
        frame.pack(fill="both", expand=True, padx=12, pady=10)
        
        btn_bar = tk.Frame(frame, bg=BG_DARK)
        btn_bar.pack(fill="x", pady=4)
        
        tk.Button(btn_bar, text="🌐 Ping Test (Google DNS)", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=lambda: self.run_diag(["ping", "-c", "3", "8.8.8.8"]), bd=0, padx=8).pack(side="left", padx=4)
        tk.Button(btn_bar, text="🧭 Routing Table", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=lambda: self.run_diag(["route", "-n"]), bd=0, padx=8).pack(side="left", padx=4)
        tk.Button(btn_bar, text="📋 DNS Servers", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=lambda: self.run_diag(["cat", "/etc/resolv.conf"]), bd=0, padx=8).pack(side="left", padx=4)
        tk.Button(btn_bar, text="🔍 Hardware Adapters", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=lambda: self.run_diag(["lspci"]), bd=0, padx=8).pack(side="left", padx=4)
        
        self.txt_diag = tk.Text(frame, bg=BG_CARD, fg=FG_LIGHT, font=FONT_MONO, height=12, wrap="word", bd=1, relief="ridge")
        self.txt_diag.pack(fill="both", expand=True, pady=8)

    def run_diag(self, cmd):
        self.txt_diag.delete("1.0", "end")
        self.txt_diag.insert("end", f"$ {' '.join(cmd)}\nRunning diagnostic command...\n\n")
        self.update()
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            out = res.stdout + res.stderr
            self.txt_diag.insert("end", out if out else "(No output received)")
        except Exception as e:
            self.txt_diag.insert("end", f"Error executing command: {e}")

    # ---------------------------------------------------------
    # Helper Network Methods
    # ---------------------------------------------------------
    def refresh_all(self):
        self.refresh_wired()
        self.refresh_wifi_ifaces()

    def get_ethernet_interfaces(self):
        ifaces = []
        try:
            with open("/proc/net/dev", "r") as f:
                for line in f.readlines()[2:]:
                    name = line.split(":")[0].strip()
                    if name.startswith(("eth", "en", "usb")) and not name.startswith("wlan"):
                        ifaces.append(name)
        except Exception:
            pass
        return ifaces or ["eth0"]

    def get_wireless_interfaces(self):
        ifaces = []
        try:
            with open("/proc/net/wireless", "r") as f:
                for line in f.readlines()[2:]:
                    name = line.split(":")[0].strip()
                    ifaces.append(name)
        except Exception:
            pass
        if not ifaces:
            try:
                for d in os.listdir("/sys/class/net"):
                    if os.path.exists(f"/sys/class/net/{d}/wireless") or d.startswith("wlan") or d.startswith("ath"):
                        ifaces.append(d)
            except Exception:
                pass
        return ifaces

    def get_interface_info(self, iface):
        info = {"up": False, "ip": None, "mask": None, "bcast": None, "mac": None}
        try:
            res = subprocess.run(["ifconfig", iface], capture_output=True, text=True)
            out = res.stdout
            info["up"] = "UP" in out and "RUNNING" in out
            ip_m = re.search(r'inet (?:addr:)?([0-9.]+)', out)
            if ip_m:
                info["ip"] = ip_m.group(1)
            mask_m = re.search(r'Mask:([0-9.]+)', out)
            if mask_m:
                info["mask"] = mask_m.group(1)
            bcast_m = re.search(r'Bcast:([0-9.]+)', out)
            if bcast_m:
                info["bcast"] = bcast_m.group(1)
            mac_m = re.search(r'HWaddr ([0-9a-fA-F:]{17})', out) or re.search(r'ether ([0-9a-fA-F:]{17})', out)
            if mac_m:
                info["mac"] = mac_m.group(1)
        except Exception:
            pass
        return info

    def get_default_gateway(self):
        try:
            res = subprocess.run(["route", "-n"], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[0] == "0.0.0.0":
                    return parts[1]
        except Exception:
            pass
        return None

    def get_dns_servers(self):
        dns = []
        try:
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        dns.append(line.split()[1])
        except Exception:
            pass
        return ", ".join(dns) if dns else "None"

if __name__ == "__main__":
    app = NetworkManagerApp()
    app.mainloop()
