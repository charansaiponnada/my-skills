#!/usr/bin/env python3
"""Design lint for .pptx decks. Cheap, mechanical, no model tokens.

Checks things validate.py does not: slop tells, readability, variety, and invented numbers.

Usage:
  python lint_deck.py deck.pptx [--facts facts.json] [--brand] [--json]

  --facts facts.json  fact ledger: {"facts": ["Beat baseline by 12 points", ...], "numbers": ["12","94.2"]}
                      numbers on slides that appear nowhere in the ledger are flagged
  --brand             a brand template/guide mandates the look: skip style bans
                      (lines, bars, stripes, banned fonts, flat backgrounds)
  --json              machine-readable output

Exit code 1 when there are errors. Warnings never fail the run.
"""
import argparse
import json
import re
import sys
import zipfile
from collections import Counter

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
from pptx.util import Emu

EMU_IN = 914400
BANNED_FONTS = {"inter", "roboto", "aptos", "aptos display", "open sans", "segoe ui"}
KNOWN_FONTS = {"cambria", "calibri", "calibri light", "bookman old style", "century schoolbook",
               "times new roman", "courier new", "georgia", "consolas", "palatino linotype",
               "trebuchet ms", "arial", "arial black", "impact", "garamond", "verdana", "tahoma"}
PLACEHOLDER_RE = re.compile(r"\b(lorem|ipsum|xxx+|todo|insert (text|title|image)|click to (add|edit))\b", re.I)
NUM_RE = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, slide, rule, msg):
        self.items.append({"level": level, "slide": slide, "rule": rule, "msg": msg})


def inches(v):
    return (v or 0) / EMU_IN


def shape_text(sh):
    return sh.text_frame.text.strip() if sh.has_text_frame else ""


def runs_of(sh):
    if not sh.has_text_frame:
        return
    for p in sh.text_frame.paragraphs:
        for r in p.runs:
            yield r


def max_size(sh):
    sizes = [r.font.size.pt for r in runs_of(sh) if r.font.size]
    return max(sizes) if sizes else None


def is_title_ph(sh):
    try:
        return sh.is_placeholder and sh.placeholder_format.type in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE)
    except Exception:
        return False


def find_title(slide, sw, sh_):
    for sh in slide.shapes:
        if is_title_ph(sh) and shape_text(sh):
            return sh
    best, best_sz = None, 0
    for sh in slide.shapes:
        if sh.has_text_frame and shape_text(sh) and inches(sh.top) < 0.4 * sh_ / EMU_IN:
            sz = max_size(sh) or 0
            if sz > best_sz:
                best, best_sz = sh, sz
    return best


def bg_kind(slide):
    """Return 'solid' | 'gradient' | 'picture' | 'unknown' for the effective slide background."""
    try:
        node = slide
        if slide.follow_master_background:
            node = slide.slide_layout
            if node.follow_master_background:
                node = node.slide_master
        t = node.background.fill.type
        return {1: "solid", 3: "gradient", 6: "picture"}.get(int(t) if t is not None else -1, "unknown")
    except Exception:
        return "unknown"


def theme_fonts(path):
    z = zipfile.ZipFile(path)
    out = set()
    for n in z.namelist():
        if re.match(r"ppt/theme/theme\d+\.xml", n):
            x = z.read(n).decode("utf8", "ignore")
            for m in re.finditer(r"<a:(?:major|minor)Font>\s*<a:latin typeface=\"([^\"]*)\"", x):
                if m.group(1):
                    out.add(m.group(1))
    return out


def signature(slide, sw, sh_):
    parts = []
    for sh in slide.shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.PICTURE and sh.width >= 0.9 * sw and sh.height >= 0.9 * sh_:
            continue  # full-bleed background
        kind = "chart" if getattr(sh, "has_chart", False) and sh.has_chart else \
               "table" if getattr(sh, "has_table", False) and sh.has_table else \
               "pic" if sh.shape_type == MSO_SHAPE_TYPE.PICTURE else \
               "txt" if shape_text(sh) else "shape"
        parts.append((kind, round(4 * (sh.left or 0) / sw), round(4 * (sh.top or 0) / sh_), round(4 * (sh.width or 0) / sw)))
    return tuple(sorted(parts))


def norm_num(s):
    s = s.replace(",", "")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def load_ledger(path):
    d = json.load(open(path))
    nums = set()
    texts = list(d.get("facts", [])) + [str(n) for n in d.get("numbers", [])]
    for t in texts:
        for m in NUM_RE.findall(str(t)):
            nums.add(norm_num(m))
    return nums


def lint(path, facts=None, brand=False):
    prs = Presentation(path)
    sw, sh_ = prs.slide_width, prs.slide_height
    rep = Report()
    slides = list(prs.slides)
    n = len(slides)
    ledger = load_ledger(facts) if facts else None

    # --- theme / font choices
    tfonts = {f.lower() for f in theme_fonts(path)}
    used = Counter()
    for i, s in enumerate(slides, 1):
        for sh in s.shapes:
            for r in runs_of(sh):
                if r.font.name:
                    used[r.font.name.lower()] += 1
    all_fonts = set(used) | tfonts
    if not brand:
        for f in sorted(all_fonts & BANNED_FONTS):
            rep.add("error", 0, "banned-font", f"font '{f}' is a no-choice default; use a pairing from references/design-systems.md")
        if all_fonts and all_fonts <= {"arial", "calibri"}:
            rep.add("warn", 0, "default-fonts", "only Arial/Calibri used: no typographic choice made; pair a safe serif heading (Cambria, Bookman Old Style, Century Schoolbook)")
    for f in sorted(all_fonts - KNOWN_FONTS - BANNED_FONTS):
        if not f.startswith("+"):
            rep.add("info", 0, "unlisted-font", f"font '{f}' is outside the known list: it may fall back on other machines and the QA preview may mis-fit it")

    # --- per-slide checks
    bg_kinds, sigs, title_pos = [], [], []
    for i, s in enumerate(slides, 1):
        texts = [shape_text(sh) for sh in s.shapes if sh.has_text_frame]
        words = sum(len(t.split()) for t in texts)
        alltext = " ".join(texts)

        if PLACEHOLDER_RE.search(alltext):
            rep.add("error", i, "placeholder-text", "leftover placeholder text")
        if re.search(r"\[TBD[^\]]*\]", alltext):
            rep.add("warn", i, "tbd", "contains a [TBD] marker: the user must fill this in before presenting")

        title = find_title(s, sw, sh_)
        content_slide = 1 < i < n or n <= 2
        if title is not None:
            t = shape_text(title)
            if t.endswith("."):
                rep.add("error", i, "title-period", "title ends with a period")
            if content_slide and len(t.split()) < 4:
                rep.add("warn", i, "label-title", f"title '{t[:40]}' reads as a topic label; write the takeaway as a sentence")
            sz = max_size(title)
            if content_slide and sz and sz < 28:
                rep.add("warn", i, "small-title", f"title is {sz:.0f}pt; titles need clear size contrast with body")
            if content_slide:
                title_pos.append((i, round(inches(title.left), 1), round(inches(title.top), 1), round(sz or 0)))
        elif content_slide:
            rep.add("warn", i, "no-title", "no title found")

        if words > 110:
            rep.add("error", i, "too-much-text", f"{words} words on one slide")
        elif words > 60:
            rep.add("warn", i, "dense-slide", f"{words} words: cut or split")

        has_visual, big_type = False, False
        for sh in s.shapes:
            st = sh.shape_type
            w_in, h_in = inches(sh.width), inches(sh.height)
            l_in, t_in = inches(sh.left), inches(sh.top)
            has_text = bool(shape_text(sh))
            sz = max_size(sh)
            if sz and sz >= 36 and not is_title_ph(sh):
                big_type = True
            if has_text:
                wc = len(shape_text(sh).split())
                if sz is not None and sz < 10:
                    rep.add("error", i, "tiny-text", f"{sz:.0f}pt text ('{shape_text(sh)[:30]}...')")
                else:
                    small = [r for r in runs_of(sh) if r.font.size and r.font.size.pt < 14]
                    if wc > 15 and small and not is_title_ph(sh):
                        rep.add("warn", i, "small-body", f"body text under 14pt in a {wc}-word block")
            if st == MSO_SHAPE_TYPE.PICTURE and not (sh.width >= 0.9 * sw and sh.height >= 0.9 * sh_):
                has_visual = True
            elif getattr(sh, "has_chart", False) and sh.has_chart:
                has_visual = True
            elif getattr(sh, "has_table", False) and sh.has_table:
                has_visual = True
            elif st in (MSO_SHAPE_TYPE.AUTO_SHAPE, MSO_SHAPE_TYPE.FREEFORM, MSO_SHAPE_TYPE.GROUP) and not has_text:
                has_visual = True

            if brand or has_text or st == MSO_SHAPE_TYPE.PICTURE or getattr(sh, "has_chart", False) or getattr(sh, "has_table", False):
                continue
            thin = min(w_in, h_in) < 0.08 and max(w_in, h_in) > 0.8
            if thin and w_in >= h_in:
                where = "under/near the title" if t_in < 0.4 * sh_ / EMU_IN else "across the slide"
                rep.add("error", i, "rule-line", f"thin horizontal line {where}: use whitespace or a tint change")
            elif thin:
                rep.add("error", i, "stripe", "thin vertical line/stripe: use whitespace or a background tint")
            elif w_in < 0.15 and h_in >= 0.5:
                rep.add("error", i, "stripe", "narrow accent stripe on an edge/card: use a tint or whitespace")
            elif sh.width >= 0.9 * sw and h_in <= 0.7 and (t_in < 0.8 or t_in + h_in > sh_ / EMU_IN - 0.8):
                rep.add("error", i, "color-bar", "full-width header/footer bar")

        if not has_visual and not big_type and 1 < i < n:
            rep.add("warn", i, "no-visual", "text-only slide: add a chart, shape, or oversized number")

        k = bg_kind(s)
        full_pic = any(sh.shape_type == MSO_SHAPE_TYPE.PICTURE and sh.width >= 0.9 * sw and sh.height >= 0.9 * sh_ for sh in s.shapes)
        bg_kinds.append("picture" if full_pic else k)
        sigs.append(signature(s, sw, sh_))

    if not brand and n >= 3:
        flat = sum(1 for k in bg_kinds if k == "solid")
        if flat / n > 0.7:
            rep.add("warn", 0, "flat-backgrounds", f"{flat}/{n} slides have flat solid backgrounds: use gradient/grain PNGs (make_background.py)")

    for i in range(1, n):
        if sigs[i] == sigs[i - 1] and sigs[i]:
            rep.add("warn", i + 1, "repeat-layout", "same layout as the previous slide")
    if n >= 6 and len(set(sigs)) < max(3, n // 3):
        rep.add("warn", 0, "low-variety", f"only {len(set(sigs))} distinct layouts in {n} slides")

    pos = Counter((x, y, sz) for _, x, y, sz in title_pos)
    if len(pos) > 2:
        rep.add("warn", 0, "title-drift", f"title position/size varies across content slides ({len(pos)} variants)")

    if ledger is not None:
        for i, s in enumerate(slides, 1):
            for sh in s.shapes:
                if not sh.has_text_frame:
                    continue
                for m in NUM_RE.findall(shape_text(sh)):
                    v = norm_num(m)
                    if v in ledger:
                        continue
                    try:
                        f = float(v)
                    except ValueError:
                        continue
                    if f == int(f) and (0 <= f <= 10 or 1900 <= f <= 2100):
                        continue  # small counts and years
                    rep.add("warn", i, "unverified-number", f"'{m}' is not in the fact ledger: source it or remove it")
    return rep, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--facts")
    ap.add_argument("--brand", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rep, n = lint(a.deck, a.facts, a.brand)
    errs = sum(1 for x in rep.items if x["level"] == "error")
    warns = sum(1 for x in rep.items if x["level"] == "warn")
    if a.json:
        print(json.dumps({"slides": n, "errors": errs, "warnings": warns, "findings": rep.items}, indent=2))
    else:
        for x in sorted(rep.items, key=lambda x: ({"error": 0, "warn": 1, "info": 2}[x["level"]], x["slide"])):
            loc = f"slide {x['slide']}" if x["slide"] else "deck"
            print(f"[{x['level'].upper():5}] {loc:9} {x['rule']}: {x['msg']}")
        print(f"\n{n} slides · {errs} errors · {warns} warnings" + ("  (brand mode: style bans off)" if a.brand else ""))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
