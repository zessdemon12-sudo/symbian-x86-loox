#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Non-US International Keyboard Selector
Provides an intuitive GUI to select, test, and instantly apply international
keyboard layouts (AZERTY French, QWERTZ German/Swiss, UK, Spanish, Japanese, etc.)
using Tiny Core's kmaps infrastructure.
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

# Popular non-US and standard keymaps
POPULAR_MAPS = [
    ("🇺🇸 US English (Standard QWERTY)", "qwerty/us"),
    ("🇬🇧 UK English (QWERTY)", "qwerty/uk"),
    ("🇫🇷 French (AZERTY)", "azerty/fr"),
    ("🇫🇷 French Latin-9 (AZERTY)", "azerty/fr-latin9"),
    ("🇧🇪 Belgian (AZERTY)", "azerty/be-latin1"),
    ("🇩🇪 German (QWERTZ)", "qwertz/de"),
    ("🇩🇪 German Latin-1 (QWERTZ)", "qwertz/de-latin1"),
    ("🇨🇭 Swiss German (QWERTZ)", "qwertz/sg-latin1"),
    ("🇨🇭 Swiss French (QWERTZ)", "qwertz/fr_CH-latin1"),
    ("🇪🇸 Spanish (QWERTY)", "qwerty/es"),
    ("🇮🇹 Italian (QWERTY)", "qwerty/it"),
    ("🇵🇹 Portuguese (QWERTY)", "qwerty/pt"),
    ("🇧🇷 Brazilian ABNT2", "qwerty/br-abnt2"),
    ("🇯🇵 Japanese 106-key", "qwerty/jp106"),
    ("🇷🇺 Russian (Cyrillic)", "qwerty/ru"),
    ("🇨🇿 Czech (QWERTZ)", "qwertz/cz"),
    ("🇸🇰 Slovak (QWERTZ)", "qwertz/sk-qwertz"),
    ("🇭🇺 Hungarian (QWERTZ)", "qwertz/hu"),
    ("🇳🇱 Dutch (QWERTY)", "qwerty/nl"),
    ("🇸🇪 Swedish (QWERTY)", "qwerty/se-latin1"),
    ("🇳🇴 Norwegian (QWERTY)", "qwerty/no-latin1"),
    ("🇩🇰 Danish (QWERTY)", "qwerty/dk-latin1"),
    ("🇹🇷 Turkish (QWERTY)", "qwerty/trq"),
]

class KeyboardSettingsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Keyboard Layout Settings")
        self.geometry("540x440")
        self.minsize(500, 400)
        self.configure(bg=BG_DARK)
        
        self._build_ui()
        self.load_current_keymap()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG_CARD, height=52)
        hdr.pack(fill="x")
        lbl = tk.Label(hdr, text="⌨️ International Keyboard Settings", font=FONT_TITLE, bg=BG_CARD, fg=FG_LIGHT)
        lbl.pack(side="left", padx=14, pady=10)
        
        self.lbl_current = tk.Label(hdr, text="Current: US", font=FONT_BOLD, bg=BG_CARD, fg=ACCENT_BLUE)
        self.lbl_current.pack(side="right", padx=14, pady=10)
        
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=14, pady=10)
        
        tk.Label(content, text="Select your keyboard layout (Non-US supported):", font=FONT_BOLD, bg=BG_DARK, fg=FG_LIGHT).pack(anchor="w", pady=(0, 6))
        
        # Keymap Listbox
        list_frame = tk.Frame(content, bg=BG_DARK)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(list_frame, bg=BG_CARD, fg=FG_LIGHT, font=FONT_REGULAR, selectbackground=ACCENT_BLUE, selectforeground="#ffffff", bd=1, relief="ridge", yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Populate list
        self.keymap_data = []
        for name, kpath in POPULAR_MAPS:
            self.listbox.insert("end", f"  {name}")
            self.keymap_data.append((name, kpath))
            
        # Discover any additional keymaps installed in /usr/share/kmap
        if os.path.exists("/usr/share/kmap"):
            for root, _, files in os.walk("/usr/share/kmap"):
                for f in sorted(files):
                    if f.endswith(".kmap"):
                        rel = os.path.relpath(os.path.join(root, f), "/usr/share/kmap")
                        base = rel[:-5]
                        if not any(k[1] == base for k in self.keymap_data):
                            self.listbox.insert("end", f"  [Other] {base}")
                            self.keymap_data.append((base, base))
                            
        self.listbox.bind("<Double-1>", lambda e: self.apply_keymap())
        
        # Test Input Card
        test_frame = tk.Frame(content, bg=BG_CARD, bd=1, relief="ridge", padx=10, pady=8)
        test_frame.pack(fill="x", pady=10)
        
        tk.Label(test_frame, text="Test Typing Here:", font=FONT_BOLD, bg=BG_CARD, fg=FG_LIGHT).pack(anchor="w")
        self.entry_test = tk.Entry(test_frame, bg=BG_PANEL, fg=FG_LIGHT, font=FONT_REGULAR, insertbackground="#ffffff", bd=1)
        self.entry_test.pack(fill="x", pady=4)
        
        # Button Bar
        btn_bar = tk.Frame(content, bg=BG_DARK)
        btn_bar.pack(fill="x", pady=4)
        
        tk.Button(btn_bar, text="✔️ Apply Keyboard Layout", font=FONT_BOLD, bg=ACCENT_GREEN, fg="#ffffff", command=self.apply_keymap, bd=0, padx=14, pady=6).pack(side="left")
        tk.Button(btn_bar, text="Close", font=FONT_BOLD, bg=BG_PANEL, fg=FG_LIGHT, command=self.destroy, bd=0, padx=12, pady=6).pack(side="right")

    def load_current_keymap(self):
        k = "us"
        if os.path.exists("/etc/sysconfig/keymap"):
            try:
                with open("/etc/sysconfig/keymap") as f:
                    line = f.read().strip()
                    if "KEYMAP=" in line:
                        k = line.split("KEYMAP=")[1].strip()
                    else:
                        k = line
            except Exception:
                pass
        self.lbl_current.config(text=f"Current: {k}")
        
        # Select in listbox
        for idx, item in enumerate(self.keymap_data):
            if item[1] == k or item[1].endswith(k):
                self.listbox.selection_clear(0, "end")
                self.listbox.selection_set(idx)
                self.listbox.see(idx)
                break

    def apply_keymap(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Select Layout", "Please select a keyboard layout from the list.")
            return
        
        name, kpath = self.keymap_data[sel[0]]
        kfile = f"/usr/share/kmap/{kpath}.kmap"
        
        # Check if file exists, or search in /usr/share/kmap
        if not os.path.exists(kfile):
            # Try finding by basename
            base = os.path.basename(kpath)
            found = False
            if os.path.exists("/usr/share/kmap"):
                for root, _, files in os.walk("/usr/share/kmap"):
                    if f"{base}.kmap" in files:
                        kfile = os.path.join(root, f"{base}.kmap")
                        found = True
                        break
            if not found:
                messagebox.showerror("Error", f"Keymap file '{kfile}' not found.\nPlease ensure kmaps.tcz is installed.")
                return

        try:
            # Run loadkmap with sudo
            with open(kfile, "rb") as kf:
                p = subprocess.run(["sudo", "/sbin/loadkmap"], stdin=kf, capture_output=True)
                if p.returncode == 0:
                    with open("/tmp/cur_kmap", "w") as out:
                        out.write(f"KEYMAP={kpath}\n")
                    subprocess.run(["sudo", "mv", "/tmp/cur_kmap", "/etc/sysconfig/keymap"], check=False)
                    self.lbl_current.config(text=f"Current: {kpath}")
                    messagebox.showinfo("Keyboard Layout", f"Keyboard layout successfully set to:\n{name} ({kpath})\n\nYou can test typing in the input box below.")
                    self.entry_test.focus_set()
                else:
                    messagebox.showwarning("Notice", f"loadkmap output: {p.stderr.decode('utf-8', 'ignore')}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply keymap: {e}")

if __name__ == "__main__":
    app = KeyboardSettingsApp()
    app.mainloop()
