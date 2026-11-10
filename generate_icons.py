from PIL import Image, ImageDraw
import os

icons_dir = "/workspace/mioads/static/images/icons"
os.makedirs(icons_dir, exist_ok=True)

NAVY = (11, 25, 44, 255)       # #0B192C
WHITE = (255, 255, 255, 255)   # #FFFFFF
ACCENT = (0, 180, 216, 255)    # #00B4D8 (electric cyan/blue)
MUTED = (148, 163, 184, 255)   # #94A3B8

def create_home(active=False):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = ACCENT if active else MUTED
    d.polygon([(32, 12), (14, 28), (50, 28)], fill=color)
    d.rectangle([18, 28, 46, 50], fill=color)
    d.rectangle([27, 36, 37, 50], fill=(0, 0, 0, 0) if active else NAVY)
    return img

def create_channels(active=False):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = ACCENT if active else MUTED
    d.polygon([(14, 24), (26, 16), (26, 48), (14, 40)], fill=color)
    d.rectangle([26, 20, 36, 44], fill=color)
    d.arc([36, 18, 48, 46], -60, 60, fill=color, width=3)
    d.arc([42, 12, 56, 52], -60, 60, fill=color, width=3)
    d.polygon([(20, 40), (24, 40), (22, 54), (18, 52)], fill=color)
    return img

def create_wallet(active=False):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = ACCENT if active else MUTED
    d.rounded_rectangle([10, 18, 54, 50], radius=6, fill=color)
    d.rounded_rectangle([36, 28, 54, 40], radius=4, fill=(11, 25, 44, 255) if active else (255, 255, 255, 220))
    d.ellipse([42, 32, 48, 36], fill=color)
    return img

def create_stats(active=False):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = ACCENT if active else MUTED
    d.rounded_rectangle([12, 38, 20, 52], radius=2, fill=color)
    d.rounded_rectangle([24, 26, 32, 52], radius=2, fill=color)
    d.rounded_rectangle([36, 14, 44, 52], radius=2, fill=color)
    d.rounded_rectangle([48, 20, 56, 52], radius=2, fill=color)
    return img

def create_support(active=False):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = ACCENT if active else MUTED
    d.rounded_rectangle([12, 14, 52, 44], radius=8, fill=color)
    d.polygon([(20, 44), (32, 44), (16, 54)], fill=color)
    dot_color = (11, 25, 44, 255) if active else (255, 255, 255, 220)
    d.ellipse([22, 26, 26, 30], fill=dot_color)
    d.ellipse([30, 26, 34, 30], fill=dot_color)
    d.ellipse([38, 26, 42, 30], fill=dot_color)
    return img

def create_admin(active=False):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = ACCENT if active else MUTED
    d.polygon([(32, 10), (52, 18), (52, 36), (32, 54), (12, 36), (12, 18)], fill=color)
    shield_inner = (11, 25, 44, 255) if active else (255, 255, 255, 220)
    d.polygon([(32, 20), (35, 28), (44, 28), (37, 33), (40, 42), (32, 37), (24, 42), (27, 33), (20, 28), (29, 28)], fill=shield_inner)
    return img

def create_settings(active=False):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = ACCENT if active else MUTED
    d.ellipse([18, 18, 46, 46], fill=color)
    d.ellipse([26, 26, 38, 38], fill=(0, 0, 0, 0))
    for coord in [(30, 10, 34, 20), (30, 44, 34, 54), (10, 30, 20, 34), (44, 30, 54, 34)]:
        d.rectangle(coord, fill=color)
    return img

for name, fn in [
    ("home", create_home),
    ("channels", create_channels),
    ("wallet", create_wallet),
    ("stats", create_stats),
    ("support", create_support),
    ("admin", create_admin),
    ("settings", create_settings),
]:
    fn(False).save(f"{icons_dir}/{name}.png")
    fn(True).save(f"{icons_dir}/{name}_active.png")

print("All navigation PNG icons generated successfully in", icons_dir)
