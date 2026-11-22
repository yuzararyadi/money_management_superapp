#!/usr/bin/env python3
"""Draw the dashboard's app icons (home-screen icon on Android) into icons/.

If money/app-icon-source/ contains a photo (jpg/png/webp), the icons are made
from that photo; otherwise a wallet logo is drawn. To change the photo, put a
new one there (remove the old one) and re-run.

Run once (or after changing the design):  python money/make_app_icons.py
Makes icon-192.png, icon-512.png (rounded) and icon-maskable-512.png
(full-bleed with safe padding, for Android's adaptive icon shapes),
plus apple-touch-icon.png (180).
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "icons")
os.makedirs(OUT, exist_ok=True)

C1, C2, C3 = (49, 46, 129), (79, 70, 229), (14, 165, 233)  # indigo -> sky (header gradient)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(n):
    img = Image.new("RGB", (n, n))
    px = img.load()
    for y in range(n):
        for x in range(n):
            t = (x * 0.62 + y * 0.38) / n  # diagonal, like the 125deg CSS gradient
            px[x, y] = lerp(C1, C2, t / 0.42) if t < 0.42 else lerp(C2, C3, min(1, (t - 0.42) / 0.58))
    return img


def wallet(draw, n, scale):
    """White wallet glyph centred; scale = glyph width as a fraction of n."""
    w = n * scale
    h = w * 0.74
    x0, y0 = (n - w) / 2, (n - h) / 2 + n * 0.02
    sw = max(2, round(n * 0.045))
    r = w * 0.14
    # body
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=r, outline="white", width=sw)
    # band across the top of the wallet
    by = y0 + h * 0.30
    draw.line([x0 + sw / 2, by, x0 + w - sw / 2, by], fill="white", width=sw)
    # clasp pocket on the right edge, with a dot
    ph = h * 0.30
    py0 = y0 + h * 0.48
    px0 = x0 + w * 0.60
    draw.rounded_rectangle([px0, py0, x0 + w, py0 + ph], radius=ph / 2, fill="white")
    cr = ph * 0.20
    cx, cy = px0 + ph / 2, py0 + ph / 2
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=lerp(C2, C3, 0.55))


def make(n, rounded, glyph_scale):
    big = n * 4  # draw large, scale down for smooth edges
    img = gradient(big).convert("RGBA")
    # soft light in the top-right corner
    glow = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([big * 0.55, -big * 0.35, big * 1.25, big * 0.35], fill=(255, 255, 255, 38))
    img = Image.alpha_composite(img, glow)
    wallet(ImageDraw.Draw(img), big, glyph_scale)
    if rounded:
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, big - 1, big - 1], radius=big * 0.22, fill=255)
        img.putalpha(mask)
    return img.resize((n, n), Image.LANCZOS)


# ---------- photo icon (used when money/app-icon-source/ has a photo) ----------
from PIL import ImageFilter

SRC_DIR = os.path.join(ROOT, "money", "app-icon-source")
# square crop of the source photo (left, top, right, bottom as fractions) that
# keeps all the faces; tweak if a new photo is used
PHOTO_CROP = (0.02, 0.0, 0.96, 0.94)
MASKABLE_SCALE = 0.86  # photo size inside the maskable icon; faces stay in Android's 80% safe circle


def find_photo():
    if os.path.isdir(SRC_DIR):
        for fn in sorted(os.listdir(SRC_DIR)):
            if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                return os.path.join(SRC_DIR, fn)
    return None


def photo_square(im):
    w, h = im.size
    l, t, r, b = PHOTO_CROP
    box = [l * w, t * h, r * w, b * h]
    side = min(box[2] - box[0], box[3] - box[1])
    return im.crop((int(box[0]), int(box[1]), int(box[0] + side), int(box[1] + side)))


def photo_icon(im, n, rounded):
    img = photo_square(im).resize((n, n), Image.LANCZOS).convert("RGBA")
    if rounded:
        big = n * 4
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, big - 1, big - 1], radius=big * 0.22, fill=255)
        img.putalpha(mask.resize((n, n), Image.LANCZOS))
    return img


def photo_maskable(im, n):
    # blurred, slightly darkened copy of the photo fills the edges Android may cut off
    bg = im.resize((n, n), Image.LANCZOS).filter(ImageFilter.GaussianBlur(n * 0.06)).convert("RGBA")
    bg = Image.alpha_composite(bg, Image.new("RGBA", (n, n), (15, 23, 42, 40)))
    inner = int(n * MASKABLE_SCALE)
    fg = im.resize((inner, inner), Image.LANCZOS).convert("RGBA")
    # feather the photo's edge into the blurred background
    m = Image.new("L", (inner, inner), 0)
    pad = int(inner * 0.04)
    ImageDraw.Draw(m).rounded_rectangle([pad, pad, inner - pad, inner - pad], radius=inner * 0.18, fill=255)
    fg.putalpha(m.filter(ImageFilter.GaussianBlur(pad * 0.8)))
    off = (n - inner) // 2
    bg.alpha_composite(fg, (off, off))
    return bg


photo = find_photo()
if photo:
    im = Image.open(photo).convert("RGB")
    photo_icon(im, 192, True).save(os.path.join(OUT, "icon-192.png"))
    photo_icon(im, 512, True).save(os.path.join(OUT, "icon-512.png"))
    photo_maskable(im, 512).save(os.path.join(OUT, "icon-maskable-512.png"))
    photo_icon(im, 180, False).convert("RGB").save(os.path.join(OUT, "apple-touch-icon.png"))
    photo_icon(im, 64, True).save(os.path.join(OUT, "favicon-64.png"))
    print("photo icons from", os.path.basename(photo), "written to", OUT)
else:
    make(192, True, 0.56).save(os.path.join(OUT, "icon-192.png"))
    make(512, True, 0.56).save(os.path.join(OUT, "icon-512.png"))
    make(512, False, 0.44).save(os.path.join(OUT, "icon-maskable-512.png"))  # glyph inside the 80% safe zone
    make(180, False, 0.54).save(os.path.join(OUT, "apple-touch-icon.png"))
    make(64, True, 0.56).save(os.path.join(OUT, "favicon-64.png"))
    print("wallet icons written to", OUT)
