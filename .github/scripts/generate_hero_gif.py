#!/usr/bin/env python3
"""Generate an animated hero GIF that works reliably on GitHub READMEs."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 340
FRAMES = 20
OUT = Path(__file__).resolve().parents[2] / "assets" / "hero-parallax.gif"


def make_background() -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(11 + (26 - 11) * t)
        g = int(16 + (16 - 16) * t)
        b = int(32 + (48 - 32) * t)
        # slight horizontal shift
        for x in range(0, W, 8):
            tx = x / W
            rr = min(255, r + int(8 * tx))
            bb = min(255, b + int(10 * (1 - tx)))
            draw.rectangle((x, y, x + 7, y), fill=(rr, g, bb))
    return img.convert("RGBA")


BG = None


def make_frame(i: int) -> Image.Image:
    global BG
    if BG is None:
        BG = make_background()

    t = i / FRAMES
    img = BG.copy()
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    gx = int(220 + math.sin(t * math.tau) * 24)
    draw.ellipse((gx - 130, -40, gx + 130, 220), fill=(124, 58, 237, 80))
    gx2 = int(980 + math.cos(t * math.tau) * 20)
    draw.ellipse((gx2 - 110, -50, gx2 + 110, 170), fill=(34, 211, 238, 50))

    stars = [
        (80, 50), (160, 120), (300, 40), (420, 150), (560, 35),
        (700, 110), (820, 55), (940, 140), (1080, 48), (1140, 170),
        (240, 90), (480, 70), (760, 160), (900, 30),
    ]
    for si, (sx, sy) in enumerate(stars):
        phase = (t + si * 0.07) % 1.0
        a = int(50 + 200 * (0.5 + 0.5 * math.sin(phase * math.tau)))
        r = 2 if si % 3 == 0 else 1
        sx2 = int(sx + math.sin(t * math.tau) * 8)
        draw.ellipse((sx2 - r, sy - r, sx2 + r, sy + r), fill=(226, 232, 240, a))

    oy1 = int(210 + math.sin(t * math.tau) * 12)
    oy2 = int(200 - math.sin(t * math.tau) * 10)
    oy3 = int(250 + math.cos(t * math.tau) * 10)
    draw.ellipse((162, oy1 - 18, 198, oy1 + 18), fill=(124, 58, 237, 110))
    draw.ellipse((956, oy2 - 24, 1004, oy2 + 24), fill=(34, 211, 238, 90))
    draw.ellipse((628, oy3 - 12, 652, oy3 + 12), fill=(167, 139, 250, 120))

    img = Image.alpha_composite(img, overlay.filter(ImageFilter.GaussianBlur(10)))

    wave = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(wave)
    shift_a = math.sin(t * math.tau) * 30
    shift_b = math.cos(t * math.tau) * 22
    pts_a, pts_b = [], []
    for x in range(0, W + 1, 16):
        y1 = 275 + math.sin((x + shift_a) / 140) * 18
        y2 = 295 + math.cos((x + shift_b) / 160) * 12
        pts_a.append((x, y1))
        pts_b.append((x, y2))
    wdraw.polygon(pts_a + [(W, H), (0, H)], fill=(124, 58, 237, 75))
    wdraw.polygon(pts_b + [(W, H), (0, H)], fill=(34, 211, 238, 50))
    img = Image.alpha_composite(img, wave)

    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(text_layer)
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 46)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
    except OSError:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_small = font_title

    for text, y, font, fill in (
        ("Mohsen Jabbarehasl", 125, font_title, (255, 255, 255, 255)),
        ("Senior Software Developer  ·  AI & Machine Learning", 170, font_sub, (196, 181, 253, 255)),
        ("Building production platforms that ship", 205, font_small, (148, 163, 184, 255)),
    ):
        bbox = tdraw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        tdraw.text(((W - tw) / 2, y), text, font=font, fill=fill)

    img = Image.alpha_composite(img, text_layer)
    return img.convert("P", palette=Image.ADAPTIVE, colors=128)


def main() -> None:
    frames = [make_frame(i) for i in range(FRAMES)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
