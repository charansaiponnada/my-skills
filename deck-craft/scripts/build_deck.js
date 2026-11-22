#!/usr/bin/env node
/**
 * deck-craft builder: tokens.json + content.json -> native, editable .pptx
 *
 *   node build_deck.js tokens.json content.json out.pptx [--preview]
 *
 * --preview builds only the cover + the first content slide, with the exact same
 * code path as the full deck, so what the user approves is what they get.
 *
 * Slide types: title, statement, stat, split, compare, steps, quote, chart, closing
 * (schema: references/builder.md). Everything is a native PowerPoint object except
 * the two background PNGs. Colors are hex without "#".
 */
const fs = require("fs");
const path = require("path");
const os = require("os");
const { execFileSync } = require("child_process");
const pptxgen = require("pptxgenjs");

const PPTX_DIR = process.env.PPTX_SKILL_DIR || "/mnt/skills/public/pptx";
const { applyTheme } = require(path.join(PPTX_DIR, "scripts/apply_theme.js"));

const [tokensPath, contentPath, outPath] = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const PREVIEW = process.argv.includes("--preview");
if (!tokensPath || !contentPath || !outPath) {
  console.error("usage: node build_deck.js tokens.json content.json out.pptx [--preview]");
  process.exit(2);
}

const T = JSON.parse(fs.readFileSync(tokensPath, "utf8"));
const D = JSON.parse(fs.readFileSync(contentPath, "utf8"));
const F = Object.assign({ heading: "Cambria", body: "Calibri" }, T.fonts);
const C = Object.assign(
  {
    ink: "111827", paper: "FFFFFF", muted: "5B6480", accent: "3DDCFF", accent2: "FFB454",
    on_dark: "F1F4FB", on_dark_muted: "9AA4C7", card_light: "EEF1F8", card_dark: "1B2347",
    dark_bg: ["0B1020", "182044"], light_bg: ["FFFFFF", "EEF1F8"],
  },
  T.colors
);
C.accent_on_light = C.accent_on_light || C.accent;
const S = Object.assign({ title: 36, cover: 46, statement: 40, quote: 32, perLine: 32 }, T.sizes);
const W = 10, H = 5.625, M = 0.6, CW = W - 2 * M;

// ---------- backgrounds (gradient PNGs: pptxgenjs cannot write gradient fills)
const bgDir = fs.mkdtempSync(path.join(os.tmpdir(), "deckbg-"));
function makeBg(name, colors, extra = []) {
  const out = path.join(bgDir, name + ".png");
  const args = [path.join(__dirname, "make_background.py"), "--colors", ...colors, "--out", out,
    "--angle", String(T.angle || 135), "--grain", String(T.grain ?? 0.02), ...extra];
  execFileSync("python3", args, { stdio: "pipe" });
  return out;
}
const glow = T.glow
  ? ["--glow", `${T.glow.x ?? 0.85},${T.glow.y ?? 0.1},${T.glow.color || C.accent},${T.glow.radius ?? 0.5},${T.glow.strength ?? 0.25}`]
  : [];
const bgDark = makeBg("dark", C.dark_bg, glow);
const bgLight = makeBg("light", C.light_bg, T.light_glow ? ["--glow", T.light_glow] : []);

// ---------- presentation + layouts
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.title = D.title || "Presentation";
if (D.author) pres.author = D.author;
pres.theme = { headFontFace: F.heading, bodyFontFace: F.body };

function titleBox(color, size, y, h) {
  return {
    placeholder: {
      options: { name: "title", type: "title", x: M, y, w: CW, h, fontFace: F.heading, fontSize: size, bold: true,
        color, align: "left", valign: "top", margin: 0 },
      text: "",
    },
  };
}
const slideNum = (color) => ({ x: W - M - 0.5, y: H - 0.42, w: 0.5, h: 0.25, fontFace: F.body, fontSize: 10, color, align: "right" });
const LAYOUTS = {
  DARK_T: { background: { path: bgDark }, objects: [titleBox(C.on_dark, S.title, 0.45, 1.3)], slideNumber: slideNum(C.on_dark_muted) },
  LIGHT_T: { background: { path: bgLight }, objects: [titleBox(C.ink, S.title, 0.45, 1.3)], slideNumber: slideNum(C.muted) },
  COVER: { background: { path: bgDark }, objects: [titleBox(C.on_dark, S.cover, 1.25, 2.0)] },
  DARK_BLANK: { background: { path: bgDark }, objects: [], slideNumber: slideNum(C.on_dark_muted) },
  LIGHT_BLANK: { background: { path: bgLight }, objects: [], slideNumber: slideNum(C.muted) },
};
for (const [title, def] of Object.entries(LAYOUTS)) pres.defineSlideMaster({ title, ...def });
pres.addSection({ title: D.title || "Deck" });

// ---------- helpers
const tone = (dark) => (dark
  ? { text: C.on_dark, muted: C.on_dark_muted, card: C.card_dark, accent: C.accent }
  : { text: C.ink, muted: C.muted, card: C.card_light, accent: C.accent_on_light });
const clean = (t) => String(t || "").trim().replace(/\.$/, "");
const txt = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, margin: 0, fontFace: F.body, valign: "top" }, o));
function bullets(items, size, color) {
  return items.map((t, i) => ({
    text: String(t),
    options: { bullet: true, breakLine: i < items.length - 1, fontSize: size, color, paraSpaceAfter: 10 },
  }));
}
function emphasised(text, emph, base, hi) {
  if (!emph || !text.includes(emph)) return [{ text, options: Object.assign({}, base) }];
  const [a, b] = text.split(emph);
  const runs = [];
  if (a) runs.push({ text: a, options: Object.assign({}, base) });
  runs.push({ text: emph, options: Object.assign({}, base, hi) });
  if (b) runs.push({ text: b, options: Object.assign({}, base) });
  return runs;
}
function fitWarn(i, title, perLine) {
  const lines = Math.ceil(title.length / perLine);
  if (lines > 3) console.warn(`[fit] slide ${i}: title is ${title.length} chars (~${lines} lines); shorten it`);
}

// ---------- slide builders
const BUILD = {
  title(s, c) {
    const t = tone(true);
    if (c.kicker) txt(s, c.kicker.toUpperCase(), { x: M, y: 0.9, w: CW, h: 0.3, fontSize: 12, bold: true, color: t.accent, charSpacing: 3 });
    s.addText(clean(c.title), { placeholder: "title" });
    if (c.subtitle) txt(s, c.subtitle, { x: M, y: 3.5, w: 7.6, h: 0.9, fontSize: 18, color: t.muted });
    if (c.meta) txt(s, c.meta, { x: M, y: 4.75, w: CW, h: 0.3, fontSize: 12, color: t.accent });
  },
  statement(s, c, dark) {
    const t = tone(dark);
    const base = { fontFace: F.heading, fontSize: S.statement, bold: true, color: t.text };
    txt(s, emphasised(clean(c.title), c.emphasis, base, { color: t.accent }), { x: M, y: 1.0, w: 8.4, h: 2.7, fontFace: F.heading });
    if (c.support) txt(s, c.support, { x: M, y: 3.95, w: 7.4, h: 0.9, fontSize: 16, color: t.muted });
  },
  stat(s, c, dark) {
    const t = tone(dark);
    s.addText(clean(c.title), { placeholder: "title" });
    const st = (c.stats || []).slice(0, 3);
    const w = CW / st.length;
    st.forEach((x, i) => {
      const left = M + i * w;
      txt(s, String(x.value), { x: left, y: 2.15, w: w - 0.25, h: 1.3, fontFace: F.heading, fontSize: st.length > 2 ? 52 : 66, bold: true, color: t.accent, valign: "bottom" });
      txt(s, x.label, { x: left, y: 3.55, w: w - 0.25, h: 0.5, fontSize: 16, bold: true, color: t.text });
      if (x.note) txt(s, x.note, { x: left, y: 4.1, w: w - 0.25, h: 0.9, fontSize: 14, color: t.muted });
    });
  },
  split(s, c, dark) {
    const t = tone(dark);
    s.addText(clean(c.title), { placeholder: "title" });
    const hasCard = !!c.callout;
    txt(s, bullets(c.bullets || [], 16, t.text), { x: M, y: 2.1, w: hasCard ? 4.9 : CW, h: 2.9 });
    if (hasCard) {
      s.addShape(pres.shapes.RECTANGLE, { x: 5.9, y: 2.1, w: 3.5, h: 2.9, fill: { color: t.card }, line: { type: "none" } });
      if (c.callout_label) txt(s, c.callout_label.toUpperCase(), { x: 6.2, y: 2.4, w: 2.9, h: 0.3, fontSize: 11, bold: true, color: t.accent, charSpacing: 2 });
      txt(s, c.callout, { x: 6.2, y: 2.8, w: 2.9, h: 2.0, fontFace: F.heading, fontSize: 20, color: t.text });
    }
  },
  compare(s, c, dark) {
    const t = tone(dark);
    s.addText(clean(c.title), { placeholder: "title" });
    s.addShape(pres.shapes.RECTANGLE, { x: M + 4.35, y: 1.95, w: 4.45, h: 3.1, fill: { color: t.card }, line: { type: "none" } });
    (c.columns || []).slice(0, 2).forEach((col, i) => {
      const left = M + i * 4.6;
      txt(s, col.heading, { x: left, y: 2.1, w: 4.2, h: 0.5, fontFace: F.heading, fontSize: 22, bold: true, color: i === 0 ? t.muted : t.accent });
      txt(s, bullets(col.bullets || [], 16, t.text), { x: left, y: 2.8, w: 4.2, h: 2.2 });
    });
  },
  steps(s, c, dark) {
    const t = tone(dark);
    s.addText(clean(c.title), { placeholder: "title" });
    const st = (c.steps || []).slice(0, 4);
    const w = CW / st.length;
    st.forEach((x, i) => {
      const left = M + i * w;
      txt(s, String(i + 1).padStart(2, "0"), { x: left, y: 2.05, w: w - 0.25, h: 0.7, fontFace: F.heading, fontSize: 40, bold: true, color: t.accent });
      txt(s, x.title, { x: left, y: 2.85, w: w - 0.25, h: 0.8, fontSize: 18, bold: true, color: t.text });
      if (x.text) txt(s, x.text, { x: left, y: 3.7, w: w - 0.25, h: 1.3, fontSize: 14, color: t.muted });
    });
  },
  quote(s, c, dark) {
    const t = tone(dark);
    txt(s, clean(c.title), { x: M, y: 1.1, w: 8.2, h: 2.7, fontFace: F.heading, fontSize: S.quote, italic: true, color: t.text });
    if (c.attribution) txt(s, c.attribution, { x: M, y: 4.1, w: 7, h: 0.4, fontSize: 14, color: t.accent });
  },
  chart(s, c, dark) {
    const t = tone(dark);
    s.addText(clean(c.title), { placeholder: "title" });
    const ch = c.chart || {};
    const data = (ch.series || []).map((se) => ({ name: se.name, labels: ch.labels, values: se.values }));
    const multi = data.length > 1;
    const common = {
      x: M, y: 2.0, w: 5.7, h: 3.1, showTitle: false, showLegend: multi, legendPos: "b", legendFontFace: "+mn-lt", legendColor: t.muted,
      showValue: true, dataLabelFontSize: 12, dataLabelColor: t.text, dataLabelFontFace: "+mn-lt",
      catAxisLabelFontSize: 12, catAxisLabelColor: t.muted, catAxisLabelFontFace: "+mn-lt",
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      chartColors: [t.accent, C.accent2, C.muted].slice(0, multi ? data.length : 1),
    };
    if (ch.type === "line") {
      s.addChart(pres.charts.LINE, data, Object.assign({ lineSize: 3, lineDataSymbolSize: 8, dataLabelPosition: "t" }, common));
    } else {
      s.addChart(pres.charts.BAR, data, Object.assign({ barDir: "col", barGapWidthPct: 60, dataLabelPosition: "outEnd" }, common));
    }
    if (c.takeaway) txt(s, c.takeaway, { x: 6.8, y: 2.2, w: 2.6, h: 2.2, fontFace: F.heading, fontSize: 18, color: t.text });
    if (c.source) txt(s, c.source, { x: 6.8, y: 4.6, w: 2.6, h: 0.4, fontSize: 11, color: t.muted });
  },
  closing(s, c) {
    const t = tone(true);
    s.addText(clean(c.title), { placeholder: "title" });
    if (c.points && c.points.length) txt(s, bullets(c.points.slice(0, 3), 16, t.text), { x: M, y: 3.5, w: 7.6, h: 1.2 });
    if (c.contact) txt(s, c.contact, { x: M, y: 4.8, w: CW, h: 0.3, fontSize: 14, color: t.accent });
  },
};
const DEFAULT_DARK = new Set(["title", "statement", "quote", "closing"]);
const LAYOUT_FOR = (type, dark) =>
  type === "title" || type === "closing" ? "COVER"
    : type === "statement" || type === "quote" ? (dark ? "DARK_BLANK" : "LIGHT_BLANK")
      : dark ? "DARK_T" : "LIGHT_T";

// ---------- assemble
let list = D.slides || [];
if (PREVIEW) {
  const first = list.find((x) => x.type === "title") || list[0];
  // show a real content slide (light layout, data/steps/split), not a second type-led dark slide
  const body = list.find((x) => !["title", "closing", "statement", "quote"].includes(x.type)) || list.find((x) => x !== first);
  list = [first, body].filter(Boolean);
}
list.forEach((c, idx) => {
  const type = c.type;
  if (!BUILD[type]) throw new Error(`slide ${idx + 1}: unknown type '${type}'`);
  const dark = c.theme ? c.theme === "dark" : DEFAULT_DARK.has(type);
  const s = pres.addSlide({ masterName: LAYOUT_FOR(type, dark), sectionTitle: D.title || "Deck" });
  if (type === "closing" && c.title) fitWarn(idx + 1, c.title, Math.round(S.perLine * 0.75));
  else if (c.title) fitWarn(idx + 1, c.title, type === "statement" ? Math.round(S.perLine * 0.8) : S.perLine);
  BUILD[type](s, c, dark);
  if (c.notes) s.addNotes(c.notes);
});

const THEME = {
  name: T.name || "deck-craft",
  headFontFace: F.heading,
  bodyFontFace: F.body,
  colors: {
    dk1: C.ink, lt1: C.paper, dk2: C.dark_bg[0], lt2: C.light_bg[C.light_bg.length - 1],
    accent1: C.accent_on_light, accent2: C.accent2, accent3: C.muted, accent4: C.accent,
    accent5: C.on_dark_muted, accent6: C.card_dark, hlink: C.accent_on_light, folHlink: C.muted,
  },
};
(async () => {
  await pres.writeFile({ fileName: outPath });
  await applyTheme(outPath, THEME);
  console.log(`wrote ${outPath} (${list.length} slide${list.length === 1 ? "" : "s"}${PREVIEW ? ", preview" : ""})`);
})().catch((e) => { console.error(e); process.exit(1); });
