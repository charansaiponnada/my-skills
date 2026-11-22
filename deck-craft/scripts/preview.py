#!/usr/bin/env python3
"""Render a .pptx to ONE contact-sheet image (cheap to look at: one image instead of N).

Usage:
  python preview.py deck.pptx sheet.png [--cols 3] [--dpi 80]
  python preview.py deck.pptx slide3.png --slide 3 --dpi 130     # single slide, larger

Needs LibreOffice (via the pptx skill's soffice.py wrapper) and pdftoppm.
"""
import argparse
import glob
import os
import subprocess
import sys
import tempfile

from PIL import Image

SOFFICE = os.environ.get("PPTX_SKILL_DIR", "/mnt/skills/public/pptx") + "/scripts/office/soffice.py"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("out")
    ap.add_argument("--cols", type=int, default=0)
    ap.add_argument("--dpi", type=int, default=80)
    ap.add_argument("--slide", type=int, default=0, help="render only this slide (1-based)")
    ap.add_argument("--max-width", type=int, default=2000)
    a = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="dcprev-")
    subprocess.run([sys.executable, SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", tmp, a.deck],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = glob.glob(os.path.join(tmp, "*.pdf"))[0]
    cmd = ["pdftoppm", "-png", "-r", str(a.dpi)]
    if a.slide:
        cmd += ["-f", str(a.slide), "-l", str(a.slide)]
    subprocess.run(cmd + [pdf, os.path.join(tmp, "s")], check=True)
    pages = sorted(glob.glob(os.path.join(tmp, "s-*.png")))
    ims = [Image.open(p).convert("RGB") for p in pages]
    if len(ims) == 1:
        ims[0].save(a.out)
        print(f"wrote {a.out}")
        return
    cols = a.cols or (2 if len(ims) <= 4 else 3)
    rows = -(-len(ims) // cols)
    w, h = ims[0].size
    gap = 12
    sheet = Image.new("RGB", (cols * w + (cols + 1) * gap, rows * h + (rows + 1) * gap), (60, 60, 64))
    for i, im in enumerate(ims):
        sheet.paste(im, (gap + (i % cols) * (w + gap), gap + (i // cols) * (h + gap)))
    if sheet.width > a.max_width:
        r = a.max_width / sheet.width
        sheet = sheet.resize((a.max_width, int(sheet.height * r)))
    sheet.save(a.out)
    print(f"wrote {a.out} ({len(ims)} slides)")


if __name__ == "__main__":
    main()
