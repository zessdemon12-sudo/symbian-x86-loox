#!/usr/bin/env python3
"""
Symbian-X86 LOOX OS - Native Symbian Calculator Application
UID3: 0x2000E003
"""

import os
import sys
import tkinter as tk

if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0.0"

class SymbianCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("280x360+580+60")
        self.root.resizable(False, False)
        self.root.configure(bg="#263238")
        self.root.deiconify()
        self.root.lift()

        self.expression = ""
        self._setup_ui()

    def _setup_ui(self):
        # Display
        self.display_var = tk.StringVar(value="0")
        display = tk.Label(self.root, textvariable=self.display_var, font=("DejaVu Sans", 18, "bold"), anchor=tk.E, bg="#37474F", fg="#80CBC4", padx=12, pady=16)
        display.pack(fill=tk.X, padx=8, pady=8)

        # Buttons Grid
        btn_frame = tk.Frame(self.root, bg="#263238")
        btn_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        buttons = [
            ('C', '#EF5350', self.clear), ('±', '#546E7A', self.negate), ('%', '#546E7A', self.percent), ('/', '#FFA726', lambda: self.press('/')),
            ('7', '#455A64', lambda: self.press('7')), ('8', '#455A64', lambda: self.press('8')), ('9', '#455A64', lambda: self.press('9')), ('*', '#FFA726', lambda: self.press('*')),
            ('4', '#455A64', lambda: self.press('4')), ('5', '#455A64', lambda: self.press('5')), ('6', '#455A64', lambda: self.press('6')), ('-', '#FFA726', lambda: self.press('-')),
            ('1', '#455A64', lambda: self.press('1')), ('2', '#455A64', lambda: self.press('2')), ('3', '#455A64', lambda: self.press('3')), ('+', '#FFA726', lambda: self.press('+')),
            ('0', '#455A64', lambda: self.press('0')), ('.', '#455A64', lambda: self.press('.')), ('=', '#26A69A', self.evaluate)
        ]

        for i in range(4):
            btn_frame.columnconfigure(i, weight=1)
        for i in range(5):
            btn_frame.rowconfigure(i, weight=1)

        idx = 0
        for r in range(4):
            for c in range(4):
                text, color, cmd = buttons[idx]
                btn = tk.Button(btn_frame, text=text, font=("DejaVu Sans", 11, "bold"), bg=color, fg="#FFFFFF", relief=tk.FLAT, command=cmd)
                btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                idx += 1

        # Last row: 0 spans 2 columns
        btn_zero = tk.Button(btn_frame, text='0', font=("DejaVu Sans", 11, "bold"), bg="#455A64", fg="#FFFFFF", relief=tk.FLAT, command=lambda: self.press('0'))
        btn_zero.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=2, pady=2)

        btn_dot = tk.Button(btn_frame, text='.', font=("DejaVu Sans", 11, "bold"), bg="#455A64", fg="#FFFFFF", relief=tk.FLAT, command=lambda: self.press('.'))
        btn_dot.grid(row=4, column=2, sticky="nsew", padx=2, pady=2)

        btn_eq = tk.Button(btn_frame, text='=', font=("DejaVu Sans", 11, "bold"), bg="#26A69A", fg="#FFFFFF", relief=tk.FLAT, command=self.evaluate)
        btn_eq.grid(row=4, column=3, sticky="nsew", padx=2, pady=2)

    def press(self, val):
        if self.expression == "0" and val != '.':
            self.expression = ""
        self.expression += str(val)
        self.display_var.set(self.expression)

    def clear(self):
        self.expression = ""
        self.display_var.set("0")

    def negate(self):
        if self.expression:
            if self.expression.startswith('-'):
                self.expression = self.expression[1:]
            else:
                self.expression = '-' + self.expression
            self.display_var.set(self.expression)

    def percent(self):
        try:
            val = float(self.expression) / 100.0
            self.expression = str(val)
            self.display_var.set(self.expression)
        except Exception:
            self.clear()

    def evaluate(self):
        try:
            res = str(eval(self.expression))
            self.display_var.set(res)
            self.expression = res
        except Exception:
            self.display_var.set("Error")
            self.expression = ""

def main():
    root = tk.Tk()
    app = SymbianCalculatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
