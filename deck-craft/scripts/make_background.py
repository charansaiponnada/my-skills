#!/usr/bin/env python3
"""Generate a gradient (+ optional glow and grain) background PNG for slides.

pptxgenjs cannot write gradient fills, so use a PNG as the slide/layout background.

Usage:
  python make_background.py --colors 0B1020 182044 --out bg_dark.png
  python make_background.py --colors FFFFFF EEF1F8 --angle 160 --grain 0.02 --out bg_light.png
  python make_background.py --colors 0B1020 182044 --glow 0.85,0.15,3DDCFF,0.45,0.35 --out bg.png

--glow x,y,hex,radius,strength   (x,y,radius are fractions of the image; strength 0..1)
"""
import argparse
import numpy as np
from PIL import Image


def hex_to_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--colors", nargs="+", required=True, help="2+ hex colors, no #")
    ap.add_argument("--angle", type=float, default=135.0, help="gradient angle in degrees")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--grain", type=float, default=0.0, help="0..0.08 film-grain amount")
    ap.add_argument("--glow", action="append", default=[], help="x,y,hex,radius,strength (repeatable)")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    w, h = (int(v) for v in a.size.lower().split("x"))
    cols = [hex_to_rgb(c) for c in a.colors]
    if len(cols) < 2:
        cols = cols * 2

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xn, yn = xx / w - 0.5, yy / h - 0.5
    th = np.deg2rad(a.angle)
    t = xn * np.cos(th) + yn * np.sin(th)
    t = (t - t.min()) / (t.max() - t.min() + 1e-9)

    stops = np.linspace(0, 1, len(cols))
    img = np.zeros((h, w, 3), dtype=np.float32)
    for ch in range(3):
        img[..., ch] = np.interp(t, stops, [c[ch] for c in cols])

    for g in a.glow:
        gx, gy, gc, gr, gs = g.split(",")
        gx, gy, gr, gs = float(gx), float(gy), float(gr), float(gs)
        d = np.sqrt(((xx / w - gx) * (w / h)) ** 2 + (yy / h - gy) ** 2)
        m = np.clip(1 - d / gr, 0, 1) ** 2 * gs
        gcol = hex_to_rgb(gc)
        for ch in range(3):
            img[..., ch] = img[..., ch] * (1 - m) + gcol[ch] * m

    if a.grain > 0:
        rng = np.random.default_rng(a.seed)
        n = rng.normal(0, 255 * a.grain, (h, w, 1)).astype(np.float32)
        img = img + n

    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(a.out, optimize=True)
    print(f"wrote {a.out} ({w}x{h})")


if __name__ == "__main__":
    main()
