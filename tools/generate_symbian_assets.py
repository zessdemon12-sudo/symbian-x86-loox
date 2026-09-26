#!/usr/bin/env python3
import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(BASE_DIR, "desktop", "lxde", "icons", "Symbian-Belle")
APPS_DIR = os.path.join(ICON_DIR, "apps")
WP_DIR = os.path.join(BASE_DIR, "desktop", "lxde", "wallpaper")
BOOT_DIR = os.path.join(BASE_DIR, "boot")

os.makedirs(APPS_DIR, exist_ok=True)
os.makedirs(WP_DIR, exist_ok=True)
os.makedirs(BOOT_DIR, exist_ok=True)

def draw_squircle(draw, bounds, fill_color, outline_color=None, radius=12):
    x0, y0, x1, y1 = bounds
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill_color, outline=outline_color, width=1)

def create_symbian_menu_icon(path, size=48):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_squircle(d, [2, 2, size-3, size-3], "#008BE3", "#006FA8", radius=int(size*0.25))
    grid_size = int(size * 0.22)
    gap = int(size * 0.12)
    start = int(size * 0.22)
    for row in range(2):
        for col in range(2):
            x = start + col * (grid_size + gap)
            y = start + row * (grid_size + gap)
            d.rounded_rectangle([x, y, x + grid_size, y + grid_size], radius=2, fill="#FFFFFF")
    im.save(path)

def create_app_icon(path, name, bg_gradient_colors, symbol=""):
    size = 48
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c1, c2 = bg_gradient_colors
    draw_squircle(d, [2, 2, size-3, size-3], c1, c2, radius=10)
    
    if symbol == "pkg":
        d.polygon([(24, 10), (38, 17), (38, 33), (24, 40), (10, 33), (10, 17)], fill="#FFFFFF", outline="#004D80")
        d.line([(24, 10), (24, 40)], fill="#004D80", width=1)
        d.line([(10, 17), (24, 25), (38, 17)], fill="#004D80", width=1)
    elif symbol == "folder":
        d.polygon([(10, 15), (20, 15), (24, 18), (38, 18), (38, 34), (10, 34)], fill="#FFE082", outline="#FFA000")
        d.rectangle([10, 20, 38, 36], fill="#FFD54F", outline="#FF8F00")
    elif symbol == "notes":
        d.rectangle([14, 10, 34, 38], fill="#FFFFFF", outline="#78909C")
        d.line([(18, 16), (30, 16)], fill="#0288D1", width=2)
        d.line([(18, 22), (30, 22)], fill="#546E7A", width=2)
        d.line([(18, 28), (28, 28)], fill="#546E7A", width=2)
    elif symbol == "calc":
        d.rounded_rectangle([12, 10, 36, 38], radius=4, fill="#37474F", outline="#263238")
        d.rectangle([16, 14, 32, 20], fill="#80CBC4")
        d.rectangle([16, 24, 22, 28], fill="#90A4AE")
        d.rectangle([26, 24, 32, 28], fill="#FF7043")
        d.rectangle([16, 30, 22, 34], fill="#90A4AE")
        d.rectangle([26, 30, 32, 34], fill="#42A5F5")
    elif symbol == "sys":
        d.ellipse([14, 14, 34, 34], fill="#78909C", outline="#455A64")
        d.ellipse([20, 20, 28, 28], fill=c1)
    elif symbol == "browser":
        # Globe
        d.ellipse([12, 12, 36, 36], fill="#FFFFFF", outline="#0277BD", width=2)
        d.ellipse([18, 12, 30, 36], outline="#0277BD", width=1)
        d.line([(12, 24), (36, 24)], fill="#0277BD", width=1)
        d.line([(14, 18), (34, 18)], fill="#0277BD", width=1)
        d.line([(14, 30), (34, 30)], fill="#0277BD", width=1)
    elif symbol == "editor":
        d.rectangle([13, 10, 31, 38], fill="#FFFFFF", outline="#37474F")
        d.line([(17, 16), (27, 16)], fill="#00897B", width=2)
        d.line([(17, 22), (27, 22)], fill="#78909C", width=2)
        d.line([(17, 28), (27, 28)], fill="#78909C", width=2)
        # Pencil
        d.polygon([(26, 34), (36, 18), (38, 20), (28, 36)], fill="#FFB300", outline="#E65100")
    elif symbol == "image":
        # Photo Frame
        d.rectangle([10, 12, 38, 36], fill="#FFFFFF", outline="#546E7A", width=2)
        d.ellipse([15, 16, 20, 21], fill="#FFB300")
        d.polygon([(12, 34), (20, 23), (28, 34)], fill="#43A047")
        d.polygon([(24, 34), (30, 27), (36, 34)], fill="#2E7D32")
    elif symbol == "pdf":
        d.rectangle([13, 10, 35, 38], fill="#D32F2F", outline="#B71C1C")
        d.polygon([(27, 10), (35, 18), (27, 18)], fill="#FFFFFF")
        d.text((17, 22), "PDF", fill="#FFFFFF")
    elif symbol == "terminal":
        d.rounded_rectangle([10, 12, 38, 36], radius=4, fill="#212121", outline="#424242")
        d.line([(15, 18), (20, 24)], fill="#00E676", width=2)
        d.line([(20, 24), (15, 30)], fill="#00E676", width=2)
        d.line([(22, 30), (30, 30)], fill="#00E676", width=2)
    elif symbol == "task":
        # Activity pulse / monitor
        d.rounded_rectangle([10, 12, 38, 36], radius=4, fill="#1A237E", outline="#303F9F")
        d.line([(12, 24), (18, 24), (22, 16), (26, 32), (30, 20), (34, 24), (36, 24)], fill="#00E5FF", width=2)
    elif symbol == "settings":
        d.ellipse([12, 12, 36, 36], fill="#455A64", outline="#263238")
        d.ellipse([18, 18, 30, 30], fill="#ECEFF1")

    im.save(path)

def create_wallpaper(path, width=1024, height=600):
    im = Image.new("RGB", (width, height), (16, 24, 36))
    d = ImageDraw.Draw(im)
    for y in range(height):
        r = int(12 + (y / height) * 20)
        g = int(24 + (y / height) * 45)
        b = int(48 + (y / height) * 85)
        d.line([(0, y), (width, y)], fill=(r, g, b))
    
    for x in range(width):
        y_wave1 = int(350 + math.sin(x * 0.006) * 70 + math.cos(x * 0.003) * 40)
        y_wave2 = int(420 + math.cos(x * 0.005) * 60)
        d.line([(x, y_wave1), (x, height)], fill=(0, 110, 180, 50))
        d.line([(x, y_wave2), (x, height)], fill=(0, 140, 220, 60))

    im.save(path)

def create_boot_splash(path, width=640, height=480):
    im = Image.new("RGB", (width, height), (10, 18, 30))
    d = ImageDraw.Draw(im)
    for y in range(height):
        ratio = y / height
        d.line([(0, y), (width, y)], fill=(int(8 + ratio * 15), int(15 + ratio * 30), int(28 + ratio * 60)))
    
    cx, cy = width // 2, height // 2 - 30
    draw_squircle(d, [cx - 40, cy - 40, cx + 40, cy + 40], "#008BE3", "#00A6FF", radius=18)
    
    for r in range(2):
        for c in range(2):
            x = cx - 22 + c * 24
            y = cy - 22 + r * 24
            d.rounded_rectangle([x, y, x + 18, y + 18], radius=3, fill="#FFFFFF")
    
    im.save(path)

print("[ASSETS] Generating Symbian-Belle icons, wallpaper, and splash...")
create_symbian_menu_icon(os.path.join(ICON_DIR, "symbian-menu.png"))
create_app_icon(os.path.join(APPS_DIR, "symbian-pkg.png"), "Software Center", ("#008BE3", "#006FA8"), "pkg")
create_app_icon(os.path.join(APPS_DIR, "filemanager.png"), "File Manager", ("#37474F", "#263238"), "folder")
create_app_icon(os.path.join(APPS_DIR, "notes.png"), "Notes", ("#43A047", "#2E7D32"), "notes")
create_app_icon(os.path.join(APPS_DIR, "calculator.png"), "Calculator", ("#FB8C00", "#EF6C00"), "calc")
create_app_icon(os.path.join(APPS_DIR, "sysmanager.png"), "Installer", ("#5E35B1", "#4527A0"), "sys")

# Additional regular application icons
create_app_icon(os.path.join(APPS_DIR, "browser.png"), "Web Browser", ("#0288D1", "#01579B"), "browser")
create_app_icon(os.path.join(APPS_DIR, "leafpad.png"), "Leafpad Text Editor", ("#00897B", "#004D40"), "editor")
create_app_icon(os.path.join(APPS_DIR, "gpicview.png"), "Image Viewer", ("#7CB342", "#558B2F"), "image")
create_app_icon(os.path.join(APPS_DIR, "pdf.png"), "PDF Viewer", ("#E53935", "#C62828"), "pdf")
create_app_icon(os.path.join(APPS_DIR, "terminal.png"), "Terminal", ("#424242", "#212121"), "terminal")
create_app_icon(os.path.join(APPS_DIR, "taskmanager.png"), "Task Manager", ("#3949AB", "#1A237E"), "task")
create_app_icon(os.path.join(APPS_DIR, "settings.png"), "Display & Themes", ("#546E7A", "#37474F"), "settings")

create_wallpaper(os.path.join(WP_DIR, "symbian-loox-bg.png"))
create_boot_splash(os.path.join(BOOT_DIR, "splash.png"))

print("[ASSETS] Generated all assets successfully.")
