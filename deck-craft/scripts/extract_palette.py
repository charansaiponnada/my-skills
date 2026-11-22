#!/usr/bin/env python3
"""Pull a palette from a reference image (screenshot, slide render, logo) or a .pptx theme.

Usage:
  python extract_palette.py reference.png
  python extract_palette.py old_deck.pptx      # reads theme colors + fonts exactly

Prints JSON: colors with share, plus guessed roles (background / text / accent).
Fonts cannot be read from an image: map to the closest safe font and say so.
"""
import json
import re
import sys
import zipfile


def from_pptx(path):
    z = zipfile.ZipFile(path)
    theme = next((n for n in z.namelist() if re.match(r"ppt/theme/theme\d+\.xml", n)), None)
    if not theme:
        return {"error": "no theme found"}
    x = z.read(theme).decode("utf8", "ignore")
    out = {}
    for name in ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6"]:
        m = re.search(rf"<a:{name}>.*?(?:srgbClr val|lastClr)=\"([0-9A-Fa-f]{{6}})\"", x, re.S)
        if m:
            out[name] = m.group(1).upper()
    maj = re.search(r"<a:majorFont>\s*<a:latin typeface=\"([^\"]+)\"", x)
    mnr = re.search(r"<a:minorFont>\s*<a:latin typeface=\"([^\"]+)\"", x)
    return {"source": "pptx-theme", "colors": out,
            "fonts": {"heading": maj.group(1) if maj else None, "body": mnr.group(1) if mnr else None}}


def lum(rgb):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def sat(rgb):
    mx, mn = max(rgb), min(rgb)
    return 0 if mx == 0 else (mx - mn) / mx


def from_image(path, k=8):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((240, 240))
    q = im.quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[: k * 3]
    counts = sorted(q.getcolors(), reverse=True)
    total = sum(c for c, _ in counts)
    cols = []
    for c, idx in counts:
        rgb = tuple(pal[idx * 3: idx * 3 + 3])
        cols.append({"hex": "%02X%02X%02X" % rgb, "share": round(c / total, 3),
                     "rgb": rgb, "lum": round(lum(rgb), 3), "sat": round(sat(rgb), 2)})
    # merge near-duplicate shades (gradients quantize into many close colors)
    merged = []
    for c in cols:
        for m in merged:
            if sum((a - b) ** 2 for a, b in zip(c["rgb"], m["rgb"])) < 30 ** 2 * 3 / 3:
                m["share"] = round(m["share"] + c["share"], 3)
                break
        else:
            merged.append(c)
    cols = sorted(merged, key=lambda c: -c["share"])
    bg = cols[0]
    text = max(cols, key=lambda c: abs(c["lum"] - bg["lum"]))
    accents = [c for c in cols if c["sat"] > 0.35 and c["share"] > 0.01 and c is not bg]
    accent = max(accents, key=lambda c: c["sat"] * (c["share"] ** 0.3)) if accents else None
    for c in cols:
        c.pop("rgb")
    return {"source": "image", "colors": cols,
            "roles": {"background": bg["hex"], "text": text["hex"], "accent": accent["hex"] if accent else None},
            "mode": "dark" if bg["lum"] < 0.25 else "light"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    p = sys.argv[1]
    print(json.dumps(from_pptx(p) if p.lower().endswith((".pptx", ".potx")) else from_image(p), indent=2))
