"""Build the 7-slide defense deck: docs/presentation.pptx and docs/presentation.pdf.

Run from the repo root:
    .venv/bin/python docs/build_slides.py [--url https://your-live-url]

What it does in plain words:
- Every slide is described once, as boxes in inches.
- Each box is written twice: into the .pptx (python-pptx) and into an HTML twin
  (docs/slides-assets/slides.html).
- Headless Chrome prints the HTML twin to docs/presentation.pdf and takes one PNG
  per slide (docs/slides-assets/preview-N.png) so the layout can be checked by eye.
- Charts, the green title band and the QR code are rendered to PNG first and used by both.

Fonts (see docs/slides-assets/FONTS.md):
- Geologica / Onest / JetBrains Mono (the website fonts) are not installed on the Mac,
  and Keynote would swap them for something random. So the deck uses fonts every Mac has:
  display and body = "Helvetica Neue", mono = "Menlo". On Windows PowerPoint they fall
  back to Arial / Courier-like fonts. The PDF embeds Helvetica Neue and Menlo: it is the safe copy.

Style: the website palette (public/styles.css). Light background, dark green ink, leaf green
as the only strong accent, no shadows, no gradients, a plain green band on the title slide, no emoji.
All numbers come from the real program output (greenhouse/*.py).
"""

from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path

import qrcode
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

LIVE_URL = "https://greenhouse-ai-blue.vercel.app"  # pass --url to change
REPO_URL = "https://github.com/lordwateroff/greenhouse-ai"
if "--url" in sys.argv:
    LIVE_URL = sys.argv[sys.argv.index("--url") + 1].rstrip("/")

DOCS = Path(__file__).resolve().parent
ASSETS = DOCS / "slides-assets"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Fonts (safe stack, see header)
DISPLAY = "Helvetica Neue"
BODY = "Helvetica Neue"
MONO = "Menlo"

# Website tokens (public/styles.css :root)
BG = "f5f8f0"
CARD = "fcfdf9"
TRACK = "e2f0e1"  # leaf-soft: console / bar track
BORDER = "dfe7d8"
TEXT = "1b2a1e"
TEXT_3 = "3f5243"
TEXT_4 = "3f5243"
TEXT_5 = "66776a"
TEXT_6 = "66776a"
LEAF = "2e7d45"
LEAF_DARK = "1f5e32"
LEAF_MID = "9fcca5"
ON_LEAF = "f8fcf5"
SOIL = "a8743f"
INV_BG = LEAF  # the green answer card
INV_FG = ON_LEAF
INV_MUTED = "e2f0e1"

W, H = 13.333, 7.5  # 16:9, inches
M = 0.6  # side margin


# ---------------------------------------------------------------- rendering helpers


def chrome(*args: str) -> None:
    """Run headless Chrome once."""
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--no-pdf-header-footer", "--allow-file-access-from-files", *args],
        check=True, capture_output=True, timeout=120,
    )


def shot(svg: str, out: Path, w_in: float, h_in: float) -> Path:
    """Render an SVG (sized in CSS px, 96 per inch) to a 2x PNG."""
    w, h = round(w_in * 96), round(h_in * 96)
    page = ASSETS / f"_{out.stem}.html"
    page.write_text(
        f"<html><body style='margin:0;background:#{BG}'>{svg}</body></html>", encoding="utf-8"
    )
    chrome(f"--screenshot={out}", f"--window-size={w},{h}", "--force-device-scale-factor=2",
           page.as_uri())
    page.unlink()
    return out


# ---------------------------------------------------------------- assets


def green_band(w_in: float, h_in: float) -> Path:
    """Brand band: a plain leaf-green band with the sprout logo from public/index.html."""
    w, h = round(w_in * 96), round(h_in * 96)
    # the 32x32 logo, drawn twice: small tile next to the name, big faint sprout on the right
    leaves = ("<path d='M16 25v-9' stroke='#{c}' stroke-width='2' stroke-linecap='round' fill='none'/>"
              "<path d='M16 17c-4.5 0-7-2.6-7-6.5 4.5 0 7 2.6 7 6.5z' fill='#{c}'/>"
              "<path d='M16 15c0-4 2.6-6.5 7-6.5 0 4-2.6 6.5-7 6.5z' fill='#{c}'/>")
    tile = (f"<g transform='translate(34 30) scale(1.5)'><rect width='32' height='32' rx='10' fill='#{LEAF_DARK}'/>"
            f"{leaves.format(c=ON_LEAF)}</g>")
    big = f"<g transform='translate({w - 330} {h / 2 - 190}) scale(11)' opacity='.22'>{leaves.format(c=LEAF_MID)}</g>"
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>
<clipPath id='c'><rect width='{w}' height='{h}' rx='22'/></clipPath>
<g clip-path='url(#c)'><rect width='{w}' height='{h}' fill='#{LEAF}'/>{big}{tile}</g></svg>"""
    return shot(svg, ASSETS / "green-band.png", w_in, h_in)


def axes(w, h, pad, xs, ys, fx, fy, xfmt, yfmt, xlabel, ylabel) -> str:
    """Grid lines and mono labels, shared by both charts."""
    l, r, t, b = pad
    out = []
    for y in ys:
        out.append(f"<line x1='{l}' x2='{w - r}' y1='{fy(y):.1f}' y2='{fy(y):.1f}' stroke='#{BORDER}'/>"
                   f"<text x='{l - 10}' y='{fy(y) + 4:.1f}' text-anchor='end'>{yfmt(y)}</text>")
    for x in xs:
        out.append(f"<text x='{fx(x):.1f}' y='{h - b + 22}' text-anchor='middle'>{xfmt(x)}</text>")
    out.append(f"<text x='{(l + w - r) / 2}' y='{h - 6}' text-anchor='middle'>{xlabel}</text>")
    out.append(f"<text x='{l - 10}' y='{t - 14}' text-anchor='end'>{ylabel}</text>" if ys else "")
    return "".join(out)


STYLE = f"<style>text{{font:12px Menlo;fill:#{TEXT_6}}} .hi{{fill:#{TEXT}}}</style>"


def mdp_chart(w_in: float, h_in: float) -> Path:
    """Score(Water) and Score(Wait) against P(Dry), with the 0.376 threshold."""
    w, h = round(w_in * 96), round(h_in * 96)
    pad = (52, 74, 34, 50)
    fx = lambda p: pad[0] + p * (w - pad[0] - pad[1])  # noqa: E731
    fy = lambda v: pad[2] + (56 - v) / 20 * (h - pad[2] - pad[3])  # noqa: E731
    qdw, qdt, qnw, qnt = 53.1356, 37.8220, 43.0593, 52.2881  # Q* from greenhouse/mdp.py
    water = lambda b: b * qdw + (1 - b) * qnw  # noqa: E731
    wait = lambda b: b * qdt + (1 - b) * qnt  # noqa: E731
    th, alert, quiet = 0.376, 0.6585, 0.0508
    g = axes(w, h, pad, [0, .2, .4, .6, .8, 1], [36, 40, 44, 48, 52, 56], fx, fy,
             lambda x: f"{x:.1f}", lambda y: f"{y}", "P(Dry)", "score")
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>{STYLE}
<rect width='{w}' height='{h}' fill='#{CARD}'/>{g}
<line x1='{fx(th):.1f}' x2='{fx(th):.1f}' y1='{pad[2]}' y2='{h - pad[3]}' stroke='#{TEXT_6}' stroke-dasharray='2 4'/>
<text x='{fx(th) + 8:.1f}' y='{pad[2] + 12}' class='hi'>threshold 0.376</text>
<line x1='{fx(0)}' y1='{fy(water(0)):.1f}' x2='{fx(1)}' y2='{fy(water(1)):.1f}' stroke='#{LEAF}' stroke-width='2.5'/>
<line x1='{fx(0)}' y1='{fy(wait(0)):.1f}' x2='{fx(1)}' y2='{fy(wait(1)):.1f}' stroke='#{SOIL}' stroke-width='2.5' stroke-dasharray='8 6'/>
<text x='{fx(1) + 10}' y='{fy(water(1)) + 4:.1f}' class='hi'>Water</text>
<text x='{fx(1) + 10}' y='{fy(wait(1)) + 4:.1f}'>Wait</text>
<circle cx='{fx(quiet):.1f}' cy='{fy(wait(quiet)):.1f}' r='6' fill='#{CARD}' stroke='#{TEXT_3}' stroke-width='2'/>
<text x='{fx(quiet) + 12:.1f}' y='{fy(wait(quiet)) - 28:.1f}'>no alert, 5%<tspan x='{fx(quiet) + 12:.1f}' dy='15'>Wait 51.55</tspan></text>
<circle cx='{fx(alert):.1f}' cy='{fy(water(alert)):.1f}' r='8' fill='#{INV_BG}'/>
<text x='{fx(alert) + 10:.1f}' y='{fy(water(alert)) + 26:.1f}' class='hi'>alert, 66%: Water ≈ 49.7</text>
</svg>"""
    return shot(svg, ASSETS / "mdp-chart.png", w_in, h_in)


def hill_chart(name: str, scores: list[int], path: list[int], best: int, stuck: int | None,
               w_in: float, h_in: float, small: bool = False) -> Path:
    """Five doses, their scores, the climb path and the best point (inverted)."""
    w, h = round(w_in * 96), round(h_in * 96)
    doses = [10, 20, 30, 40, 50]
    pad = (52, 24, 34, 46) if not small else (20, 20, 26, 42)
    lo, hi = 50, 95
    fx = lambda d: pad[0] + (d - 10) / 40 * (w - pad[0] - pad[1])  # noqa: E731
    fy = lambda v: pad[2] + (hi - v) / (hi - lo) * (h - pad[2] - pad[3])  # noqa: E731
    sc = dict(zip(doses, scores))
    yt = [50, 60, 70, 80, 90] if not small else []  # small chart: scores sit above the points
    g = axes(w, h, pad, doses, yt, fx, fy, lambda x: f"{x}", lambda y: f"{y}", "dose, ml", "score")
    pts = "".join(f"<circle cx='{fx(d):.1f}' cy='{fy(s):.1f}' r='5' fill='#{LEAF_MID}'/>"
                  f"<text x='{fx(d):.1f}' y='{fy(s) + (-12 if small else 22):.1f}' text-anchor='middle'>{s}</text>"
                  for d, s in sc.items() if d != best and d != stuck)
    arrows = "".join(
        f"<line x1='{fx(a):.1f}' y1='{fy(sc[a]):.1f}' x2='{fx(b):.1f}' y2='{fy(sc[b]):.1f}' "
        f"stroke='#{LEAF}' stroke-width='2.5' marker-end='url(#ah)' "
        f"stroke-dasharray='{0 if b != path[-1] else 0}'/>" for a, b in zip(path, path[1:]))
    marks = ""
    if stuck is not None:
        marks += (f"<circle cx='{fx(stuck):.1f}' cy='{fy(sc[stuck]):.1f}' r='8' fill='#{CARD}' stroke='#{TEXT_3}' stroke-width='2'/>"
                  f"<text x='{fx(stuck):.1f}' y='{fy(sc[stuck]) - 16:.1f}' text-anchor='middle' class='hi'>stuck {sc[stuck]}</text>")
    marks += (f"<circle cx='{fx(best):.1f}' cy='{fy(sc[best]):.1f}' r='9' fill='#{INV_BG}'/>"
              f"<text x='{fx(best):.1f}' y='{fy(sc[best]) - 18:.1f}' text-anchor='middle' class='hi'>best {sc[best]}</text>")
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}'>{STYLE}
<defs><marker id='ah' viewBox='0 0 10 10' refX='14' refY='5' markerWidth='7' markerHeight='7' orient='auto'>
<path d='M0,0 L10,5 L0,10z' fill='#{LEAF}'/></marker></defs>
<rect width='{w}' height='{h}' fill='#{CARD if not small else TRACK}'/>{g}{arrows}{pts}{marks}</svg>"""
    return shot(svg, ASSETS / f"{name}.png", w_in, h_in)


def qr_png() -> Path:
    """QR code to the live demo, dark ink on white (it sits on a white tile in the green card)."""
    out = ASSETS / "qr.png"
    q = qrcode.QRCode(border=0, box_size=20, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(LIVE_URL)
    q.make_image(fill_color=f"#{TEXT}", back_color=f"#{CARD}").save(out)
    return out


# ---------------------------------------------------------------- deck builder (pptx + html twin)


def rgb(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr)


class Deck:
    """Writes every element into the pptx and into the HTML twin at the same position."""

    def __init__(self) -> None:
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(W), Inches(H)
        self.html: list[list[str]] = []

    def slide(self, notes: str):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])  # blank
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = rgb(BG)
        s.notes_slide.notes_text_frame.text = notes
        self.html.append([])
        self.s = s
        return s

    @staticmethod
    def _box(x, y, w, h, extra=""):
        return f"left:{x}in;top:{y}in;width:{w}in;height:{h}in;{extra}"

    def rect(self, x, y, w, h, fill=CARD, r=0.25, line: str | None = BORDER, oval=False):
        kind = MSO_SHAPE.OVAL if oval else (MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE)
        sp = self.s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
        style = sp._element.find(qn("p:style"))
        if style is not None:  # drop theme style: no shadow, no theme line
            sp._element.remove(style)
        if r and not oval:
            sp.adjustments[0] = min(0.5, r / min(w, h))
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(fill)
        if line:
            sp.line.color.rgb = rgb(line)
            sp.line.width = Pt(0.75)
        else:
            sp.line.fill.background()
        rad = "50%" if oval else f"{r}in"
        bd = f"border:0.75pt solid #{line};" if line else ""
        self.html[-1].append(
            f"<div style='{self._box(x, y, w, h)}background:#{fill};border-radius:{rad};{bd}box-sizing:border-box'></div>")

    def image(self, path: Path, x, y, w, h):
        self.s.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w), Inches(h))
        self.html[-1].append(f"<img src='{path.name}' style='{self._box(x, y, w, h)}'>")

    def text(self, x, y, w, h, paras, size=16, font=BODY, color=TEXT, align="l", anchor="t",
             lh=1.2, after=0):
        """paras: list of paragraphs; a paragraph is a str or a list of (text, {size,font,color}) runs."""
        tb = self.s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
        hp = []
        for i, para in enumerate(paras):
            runs = [(para, {})] if isinstance(para, str) else para
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
            p.line_spacing = lh / 1.2  # pptx 'single' is ~1.2 em for Helvetica Neue / Menlo; CSS lh is in em
            if i < len(paras) - 1:
                p.space_after = Pt(after)
            spans = []
            for t, o in runs:
                r = p.add_run()
                r.text = t
                f = r.font
                f.name, f.size = o.get("font", font), Pt(o.get("size", size))
                f.color.rgb = rgb(o.get("color", color))
                spans.append(
                    f"<span style=\"font-family:'{o.get('font', font)}';font-size:{o.get('size', size)}pt;"
                    f"color:#{o.get('color', color)}\">{html.escape(t)}</span>")
            mb = f"margin:0 0 {after}pt 0" if i < len(paras) - 1 else "margin:0"
            hp.append(f"<p style='{mb};line-height:{lh}'>{''.join(spans)}</p>")
        jc = {"t": "flex-start", "m": "center", "b": "flex-end"}[anchor]
        ta = {"l": "left", "c": "center", "r": "right"}[align]
        self.html[-1].append(
            f"<div style='{self._box(x, y, w, h)}display:flex;flex-direction:column;justify-content:{jc};"
            f"text-align:{ta}'>{''.join(hp)}</div>")

    # common pieces
    def title(self, t: str, sub: str):
        self.text(M, 0.5, W - 2 * M, 0.6, [t], size=32, font=DISPLAY)
        self.text(M, 1.15, W - 2 * M, 0.4, [sub], size=16, color=TEXT_5)

    def badge(self, x, y, n: str, inverted=False, d=0.42):
        self.rect(x, y, d, d, fill=INV_BG if inverted else TRACK, line=None if inverted else BORDER, oval=True)
        self.text(x, y, d, d, [n], size=13, font=MONO, color=INV_FG if inverted else TEXT, align="c", anchor="m")

    def save(self):
        self.prs.save(DOCS / "presentation.pptx")
        sections = "".join(f"<section id='s{i + 1}'>{''.join(els)}</section>" for i, els in enumerate(self.html))
        page = f"""<!doctype html><html><head><meta charset='utf-8'><title>Slides twin</title><style>
@page {{size:{W}in {H}in;margin:0}}
html,body{{margin:0;background:#{BG}}}
section{{position:relative;width:{W}in;height:{H}in;background:#{BG};overflow:hidden;page-break-after:always}}
section>*{{position:absolute}} p{{white-space:pre-wrap}}
body.one section{{display:none}} body.one section:target{{display:block}}
</style></head><body><script>if(location.hash)document.body.className='one'</script>{sections}</body></html>"""
        twin = ASSETS / "slides.html"
        twin.write_text(page, encoding="utf-8")
        chrome(f"--print-to-pdf={DOCS / 'presentation.pdf'}", twin.as_uri())
        for i in range(len(self.html)):
            chrome(f"--screenshot={ASSETS / f'preview-{i + 1}.png'}", "--window-size=1280,720",
                   f"{twin.as_uri()}#s{i + 1}")


# ---------------------------------------------------------------- slides

S_BAYES = "The sensor says 'dry', but it sometimes lies. Bayes tells us how much to trust it."
S_MDP = ("For each action we ask: what do I get now, plus what can I expect later? "
         "We pick the bigger number.")
S_HILL = ("Try a bit more or a bit less water. If the plant gets better, keep going that way. "
          "If it gets worse, stop.")


def build() -> None:
    ASSETS.mkdir(exist_ok=True)
    d = Deck()
    short_url = LIVE_URL.removeprefix("https://")

    # 1 Title ---------------------------------------------------------------
    d.slide(
        'Part 1, about 25 seconds. Hello. My name is Miras Yessenaly. My project is the Mini Greenhouse Assistant. It decides when to water a plant and how much, even when the soil sensor is unreliable. It uses three AI methods in a chain: Bayes, an MDP and hill climbing.'
    )
    band_h = 3.2
    d.image(green_band(W - 2 * M, band_h), M, M, W - 2 * M, band_h)
    d.text(M + 0.95, M + 0.34, 4, 0.5, ["greenhouse"], size=22, font=BODY, color=ON_LEAF, anchor="m")
    d.text(M, 4.3, W - 2 * M, 0.8, ["Mini Greenhouse Assistant"], size=44, font=DISPLAY)
    d.text(M, 5.2, W - 2 * M, 0.5,
           ["Cheap soil sensors are noisy, so we weigh the reading before we water."],
           size=20, color=TEXT_3)
    d.text(M, 6.35, W - 2 * M, 0.4, ["Miras Yessenaly · AI Fundamentals · Final project"],
           size=14, color=TEXT_6)

    # 2 Problem and objectives ----------------------------------------------
    d.slide(
        'Part 1, about 40 seconds. Soil moisture sensors are cheap and noisy. Sometimes they say dry when the soil is fine. If we trust the sensor blindly, false alarms make us water too often. The roots rot and water is wasted. If we ignore it, we miss real dryness and the plant suffers. So I set three objectives. Estimate how likely the soil is really dry. Decide to water now or wait. Pick the best dose. All numbers are hypothetical assumptions. The course allows this.'
    )
    d.title("Noisy sensors lead to bad watering", "A cheap sensor can be wrong in both directions.")
    for i, (head, body) in enumerate([
        ("Trust it blindly", "False alarms lead to overwatering. Roots rot and water is wasted."),
        ("Ignore it", "Real dryness gets missed. The plant dries out and suffers."),
    ]):
        y = 1.95 + i * 2.25
        d.rect(M, y, 5.5, 1.95)
        d.text(M + 0.35, y + 0.3, 4.8, 0.45, [head], size=20, font=DISPLAY)
        d.text(M + 0.35, y + 0.85, 4.8, 0.9, [body], size=16, color=TEXT_4)
    ox = 6.5
    d.text(ox, 1.95, 6, 0.35, ["Objectives"], size=14, color=TEXT_6)
    for i, (head, tag) in enumerate([
        ("Estimate how likely the soil is really dry", "Bayesian inference"),
        ("Decide to water now or wait", "MDP, value iteration"),
        ("Pick the best water dose", "Hill climbing"),
    ]):
        y = 2.4 + i * 1.33
        d.rect(ox, y, W - M - ox, 1.13, r=0.22)
        d.badge(ox + 0.3, y + 0.355, str(i + 1))
        d.text(ox + 0.95, y + 0.2, 5.0, 0.42, [head], size=17)
        d.text(ox + 0.95, y + 0.65, 5.0, 0.32, [tag], size=12, font=MONO, color=TEXT_6)
    d.text(M, 6.75, W - 2 * M, 0.3,
           ["All probabilities, rewards and scores are hypothetical assumptions."],
           size=12, color=TEXT_6)

    # 3 Pipeline -------------------------------------------------------------
    d.slide(
        "Part 1, about 55 seconds. "
        "This is the whole system in one picture. It is a chain. "
        "The sensor gives a reading: alert or no alert. "
        "Step one, Bayes, turns the reading into a belief: with an alert, the soil is dry with 66% probability. "
        "Step two, the MDP, takes that belief and decides: water or wait. With 66% it says water. "
        "Step three, hill climbing, picks the dose: 30 ml. "
        "So the final answer is: water 30 ml now. "
        "If there is no alert, the belief is only 5%, the MDP says wait, and we still show the best dose for later."
    )
    d.title("One chain: belief, decision, dose", "The output of each step is the input of the next.")
    cards = [
        ("", "Soil sensor", "Gives a cheap, noisy reading.", "alert"),
        ("1", "Bayes", "Is the soil really dry?", "P(Dry) = 66%"),
        ("2", "MDP", "Water now or wait? Uses P(Dry) as the belief.", "Water"),
        ("3", "Hill climbing", "How much water is best?", "30 ml"),
    ]
    widths = [2.35, 2.78, 2.78, 2.78]
    gap, x, y, ch = 0.48, M, 1.95, 2.75
    for i, ((n, head, q, out), cw) in enumerate(zip(cards, widths)):
        d.rect(x, y, cw, ch)
        if n:
            d.badge(x + 0.3, y + 0.3, n)
        else:
            d.text(x + 0.3, y + 0.3, cw - 0.6, 0.42, ["input"], size=12, font=MONO, color=TEXT_6, anchor="m")
        d.text(x + 0.3, y + 0.92, cw - 0.6, 0.42, [head], size=20, font=DISPLAY)
        d.text(x + 0.3, y + 1.38, cw - 0.6, 0.7, [q], size=13, color=TEXT_4)
        d.text(x + 0.3, y + 2.05, cw - 0.6, 0.45, [out], size=20, font=MONO)
        if i < 3:
            d.text(x + cw, y, gap, ch, ["→"], size=20, color=TEXT_6, align="c", anchor="m")
        x += cw + gap
    d.rect(M, 5.0, W - 2 * M, 1.75, fill=INV_BG, line=None)
    d.text(M + 0.4, 5.25, 8, 0.6, ["Water 30 ml now."], size=30, font=DISPLAY, color=INV_FG)
    d.text(M + 0.4, 5.95, W - 2 * M - 0.8, 0.6,
           ["We are 66% sure the soil is dry, so watering pays off. "
            "With no alert we wait, and the best dose for later stays 30 ml."],
           size=14, color=INV_MUTED)

    # 4 Bayes ----------------------------------------------------------------
    d.slide(
        "Part 3, about 30 seconds. Topic one is Bayes. The sensor says 'dry', but it sometimes lies. Bayes tells us how much to trust it. Before any reading, the soil is dry 30% of the time. That is the prior. After an alert it is 0.27 divided by 0.41, about 66%. Not 90%, because dry soil is rare and false alarms are common. With no alert it drops to about 5%."
    )
    d.title("Bayes: how much to trust the sensor", "Before the reading 30%. After an alert 66%.")
    d.rect(M, 1.95, 7.2, 4.8)
    bx, bw = M + 0.4, 6.4
    for i, (lab, p, val, inv) in enumerate([
        ("Before the reading (prior)", 0.30, "30%", False),
        ("After an alert", 0.6585, "66%", True),
        ("After no alert", 0.0508, "5%", False),
    ]):
        y = 2.3 + i * 1.45
        d.text(bx, y, 4.8, 0.35, [lab], size=14, color=TEXT_4)
        d.text(bx + bw - 1.4, y - 0.05, 1.4, 0.4, [val], size=18, font=MONO,
               color=TEXT, align="r")
        d.rect(bx, y + 0.5, bw, 0.38, fill=TRACK, r=0.19)
        d.rect(bx, y + 0.5, max(bw * p, 0.38), 0.38, fill=LEAF if inv else LEAF_MID, r=0.19, line=None)
    rx = 8.2
    rw = W - M - rx
    d.text(rx, 1.95, rw, 2.4, [S_BAYES], size=24, font=DISPLAY, lh=1.25)
    d.rect(rx, 4.65, rw, 2.1, fill=TRACK)
    d.text(rx + 0.3, 4.9, rw - 0.6, 1.7, [
        "P(alert) = 0.90·0.30 + 0.20·0.70",
        "         = 0.41",
        "P(Dry|alert) = 0.27 / 0.41 = 0.6585",
        [("Sensor model: catches dry soil 90%, false alarm 20%.", {"font": BODY, "size": 12, "color": TEXT_6})],
    ], size=12, font=MONO, color=TEXT_3, after=6, lh=1.3)

    # 5 MDP ------------------------------------------------------------------
    d.slide(
        'Part 3, about 40 seconds. Topic two is the MDP. For each action we ask: what do I get now, plus what can I expect later? We pick the bigger number. Gamma 0.9 means the future counts a bit less than now. Value iteration stops after 148 iterations. We only have a belief, so we weigh the Q values by P(Dry). The lines cross at 0.376: we water when we are more than 38% sure. With an alert, Water wins, about 49.7 against 42.8.'
    )
    d.title("MDP: water now or wait", "Q values weighted by the belief from Bayes.")
    d.rect(M, 1.95, 7.4, 4.8)
    d.image(mdp_chart(6.9, 4.3), M + 0.25, 2.2, 6.9, 4.3)
    rx = 8.4
    rw = W - M - rx
    d.text(rx, 1.95, rw, 1.75, [S_MDP], size=19, font=DISPLAY, lh=1.25)
    rows = [("Policy", "Dry → Water"), ("", "Normal → Wait"), ("Converged", "148 iterations"),
            ("Discount", "γ = 0.9"), ("Alert", "Water ≈ 49.7"), ("", "Wait ≈ 42.8")]
    for i, (k, v) in enumerate(rows):
        y = 3.85 + i * 0.36
        d.text(rx, y, 1.6, 0.32, [k], size=13, color=TEXT_6)
        d.text(rx + 1.6, y, rw - 1.6, 0.32, [v], size=13, font=MONO, align="r")
    d.text(rx, 6.15, rw, 0.6, ["We water when we are more than 38% sure the soil is dry."],
           size=14, color=TEXT_3, anchor="b")

    # 6 Hill climbing --------------------------------------------------------
    d.slide(
        'Part 3, about 35 seconds. Topic three is hill climbing. Try a bit more or a bit less water. If the plant gets better, keep going that way. If it gets worse, stop. From 10 ml it goes to 20, then 30 ml, score 88, in two steps. With the tricky plant it gets stuck at 20 ml. That is a local maximum. Our restart tries every one of the five doses, which is cheap here, and finds 40 ml.'
    )
    d.title("Hill climbing: how much water", "Five candidate doses, one health score each.")
    d.rect(M, 1.95, 7.4, 4.8)
    d.image(hill_chart("hill-chart", [55, 72, 88, 80, 60], [10, 20, 30], 30, None, 6.9, 4.3),
            M + 0.25, 2.2, 6.9, 4.3)
    rx = 8.4
    rw = W - M - rx
    d.text(rx, 1.95, rw, 1.3, [S_HILL], size=16, font=DISPLAY, lh=1.25)
    d.text(rx, 3.3, rw, 0.35, ["10 → 20 → 30 ml · score 88 · 2 steps"], size=12, font=MONO)
    d.rect(rx, 3.85, rw, 2.9, fill=TRACK)
    d.text(rx + 0.25, 4.0, rw - 0.5, 0.3, ["Tricky plant: 60, 70, 65, 85, 75"], size=12, font=MONO, color=TEXT_3)
    d.image(hill_chart("hill-tricky", [60, 70, 65, 85, 75], [10, 20], 40, 20, 3.85, 1.6, small=True),
            rx + 0.2, 4.35, 3.85, 1.6)
    d.text(rx + 0.25, 6.0, rw - 0.5, 0.65,
           ["From 10 ml it gets stuck at 20 ml (70). Restarting from all 5 doses finds 40 ml (85)."],
           size=12, color=TEXT_4)

    # 7 Results and next steps ----------------------------------------------
    d.slide(
        "Part 3, about 30 seconds. There are 41 automated tests, and they check the hand-calculated numbers. One experiment: when dry soil is rare, prior 0.1 with 20% false alarms, P(Dry) is only 0.33, so the assistant waits even on an alert. Next steps: real sensors, probabilities learned from data, a full POMDP, several plants. The QR code opens the live demo. Thank you. I'm ready for questions."
    )
    d.title("Results and next steps", "Every number from the hand calculation is checked by a test.")
    lw = 8.0
    tw = (lw - 2 * 0.3) / 3
    for i, (val, lab, unit) in enumerate([("41", "tests passing", "pytest -q"),
                                          ("148", "iterations to converge", "value iteration"),
                                          ("38%", "water threshold", "P(Dry) > 0.376")]):
        x = M + i * (tw + 0.3)
        d.rect(x, 1.95, tw, 1.5, r=0.2)
        d.text(x + 0.25, 2.1, tw - 0.5, 0.3, [lab], size=12, color=TEXT_6)
        d.text(x + 0.25, 2.4, tw - 0.5, 0.6, [val], size=30, font=DISPLAY)
        d.text(x + 0.25, 3.03, tw - 0.5, 0.3, [unit], size=11, font=MONO, color=TEXT_6)
    d.rect(M, 3.7, lw, 1.5)
    d.text(M + 0.3, 3.85, lw - 0.6, 0.3, ["Experiments"], size=12, color=TEXT_6)
    d.text(M + 0.3, 4.2, lw - 0.6, 0.95, [
        "Rare drought plus a noisy sensor can turn an alert into Wait (prior 0.1, false alarm 0.2: P(Dry) 0.33).",
        "Normal table: every start reaches 30 ml. Tricky table: restarts always find 40 ml.",
    ], size=13, color=TEXT_3, after=6)
    d.rect(M, 5.45, lw, 1.3)
    d.text(M + 0.3, 5.6, lw - 0.6, 0.3, ["Next steps"], size=12, color=TEXT_6)
    d.text(M + 0.3, 5.95, lw - 0.6, 0.7, [
        "Real sensors on Arduino or ESP32. Learn the probabilities from data. "
        "A full POMDP instead of weighing Q by the belief. Several plants."],
        size=13, color=TEXT_3)
    qx = M + lw + 0.35
    qw = W - M - qx
    d.rect(qx, 1.95, qw, 4.8, fill=INV_BG, line=None)
    d.text(qx + 0.35, 2.15, qw - 0.7, 0.35, ["Live demo"], size=14, color=INV_MUTED)
    qs = 2.7
    d.rect(qx + (qw - qs) / 2 - 0.15, 2.5, qs + 0.3, qs + 0.3, fill=CARD, r=0.15, line=None)
    d.image(qr_png(), qx + (qw - qs) / 2, 2.65, qs, qs)
    d.text(qx + 0.3, 5.55, qw - 0.6, 0.35, [short_url], size=13, font=MONO, color=INV_FG, align="c")
    d.text(qx + 0.15, 5.95, qw - 0.3, 0.35, [REPO_URL.removeprefix("https://")], size=10, font=MONO,
           color=INV_MUTED, align="c")

    d.save()


if __name__ == "__main__":
    build()
    print("wrote", DOCS / "presentation.pptx", "and", DOCS / "presentation.pdf")
