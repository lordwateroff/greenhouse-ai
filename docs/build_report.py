"""Build the technical report: figures, report.pdf and report.docx from report.md.

Run from the repo root:  .venv/bin/python docs/build_report.py
Needs: markdown, python-docx (pip install into .venv), Google Chrome and public/fonts/*.woff2.
Re-runnable: edit report.md (for example the live demo URL) and run again.
All numbers in the figures come from the greenhouse package itself.
"""

import base64
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DOCS = Path(__file__).resolve().parent
ROOT = DOCS.parent
FIG = DOCS / "figures"
sys.path.insert(0, str(ROOT))

import itertools

from greenhouse import config
from greenhouse.hill_climbing import hill_climb, random_restart
from greenhouse.pipeline import run_pipeline

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# The site's own fonts (public/fonts), embedded as data URIs: works offline, and Chrome
# does not load fonts across file:// URLs.
def _face(family: str, file: str, weight: str) -> str:
    data = base64.b64encode((ROOT / "public" / "fonts" / file).read_bytes()).decode()
    return (f'@font-face{{font-family:"{family}";font-weight:{weight};'
            f'src:url(data:font/woff2;base64,{data}) format("woff2")}}')


FACES = (_face("Geologica", "geologica-500.woff2", "500") + _face("Onest", "onest.woff2", "400 500")
         + _face("JetBrains Mono", "jetbrains-mono.woff2", "400 500"))
INK, MID, LIGHT, PAPER = "#0c0e10", "#6f747c", "#c4c9d0", "#ffffff"


def chrome(*args: str) -> None:
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--virtual-time-budget=8000", *args], check=True, capture_output=True)


# ---------- figures ----------

def svg_doc(w: int, h: int, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<style>{FACES}'
            f'text{{font-family:Onest,Helvetica,Arial,sans-serif;fill:{INK}}}'
            f'.m{{font-family:"JetBrains Mono",Menlo,monospace}}.mid{{fill:{MID}}}.inv{{fill:{PAPER}}}</style>'
            f'<rect width="{w}" height="{h}" fill="{PAPER}"/>{body}</svg>')


def arrow(x1, y1, x2, y2, label=""):
    s = (f'<line x1="{x1}" y1="{y1}" x2="{x2 - 6}" y2="{y2}" stroke="{INK}" stroke-width="1.5"/>'
         f'<path d="M{x2 - 8},{y2 - 5} L{x2},{y2} L{x2 - 8},{y2 + 5}" fill="none" stroke="{INK}" stroke-width="1.5"/>')
    if label:
        s += f'<text class="m mid" x="{(x1 + x2) / 2}" y="{y1 - 10}" font-size="11" text-anchor="middle">{label}</text>'
    return s


def fig_pipeline(r: dict) -> str:
    p = r["bayes"]["p_dry"]
    boxes = [("Sensor reading", "alert", "noisy soil sensor", False),
             ("1 · Bayes", f"P(Dry) = {p:.4f}", "is it really dry?", False),
             ("2 · MDP", r["decision"]["action"], "water now or wait?", False),
             ("3 · Hill climbing", f'{r["hill_climbing"]["best_dose"]} ml', "how much water?", False),
             ("Recommendation", r["recommendation"]["headline"], "final advice", True)]
    w, bw, gap, y, bh = 1120, 180, 44, 30, 110
    body = ""
    for i, (title, value, q, inverted) in enumerate(boxes):
        x = 20 + i * (bw + gap)
        fill, cls = (INK, "inv") if inverted else (PAPER, "")
        body += (f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="18" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>'
                 f'<text class="{cls}" x="{x + 16}" y="{y + 30}" font-size="13" font-weight="500">{title}</text>'
                 f'<text class="m {cls}" x="{x + 16}" y="{y + 64}" font-size="{13 if inverted else 16}" font-weight="500">{value}</text>'
                 f'<text class="{cls or "mid"}" x="{x + 16}" y="{y + 92}" font-size="12">{q}</text>')
        if i < len(boxes) - 1:
            body += arrow(x + bw + 4, y + bh / 2, x + bw + gap - 2, y + bh / 2)
    return svg_doc(w, 170, body)


def fig_scores(r: dict) -> str:
    Q, t = r["mdp"]["Q"], r["decision"]["threshold"]
    W, H, x0, x1, y0, y1, lo, hi = 760, 430, 70, 720, 30, 360, 35.0, 55.0
    X = lambda b: x0 + b * (x1 - x0)
    Y = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)
    score = lambda b, a: b * Q["Dry"][a] + (1 - b) * Q["Normal"][a]
    body = ""
    for v in range(35, 56, 5):
        body += (f'<line x1="{x0}" x2="{x1}" y1="{Y(v)}" y2="{Y(v)}" stroke="#e4e6ea"/>'
                 f'<text class="m mid" x="{x0 - 10}" y="{Y(v) + 4}" font-size="11" text-anchor="end">{v}</text>')
    for i in range(11):
        b = i / 10
        body += f'<text class="m mid" x="{X(b)}" y="{y1 + 20}" font-size="11" text-anchor="middle">{b:.1f}</text>'
    body += (f'<line x1="{x0}" x2="{x1}" y1="{y1}" y2="{y1}" stroke="{INK}"/>'
             f'<text x="{(x0 + x1) / 2}" y="{y1 + 46}" font-size="13" text-anchor="middle">P(Dry), belief from Bayes</text>'
             f'<text x="18" y="{(y0 + y1) / 2}" font-size="13" text-anchor="middle" transform="rotate(-90 18 {(y0 + y1) / 2})">Score</text>')
    for a, dash in (("Water", ""), ("Wait", 'stroke-dasharray="7 5"')):
        body += (f'<line x1="{X(0)}" y1="{Y(score(0, a))}" x2="{X(1)}" y2="{Y(score(1, a))}" '
                 f'stroke="{INK if a == "Water" else MID}" stroke-width="2.2" {dash}/>')
    body += (f'<text x="{X(1) - 4}" y="{Y(score(1, "Water")) - 10}" font-size="13" text-anchor="end">Score(Water)</text>'
             f'<text class="mid" x="{X(1) - 4}" y="{Y(score(1, "Wait")) + 20}" font-size="13" text-anchor="end">Score(Wait)</text>'
             f'<line x1="{X(t)}" x2="{X(t)}" y1="{y0}" y2="{y1}" stroke="{INK}" stroke-dasharray="2 4"/>'
             f'<text class="m" x="{X(t) + 8}" y="{y0 + 14}" font-size="12">threshold {t:.3f}</text>'
             f'<text x="{X(t) + 8}" y="{y0 + 32}" font-size="12">Water above this line</text>')
    for obs in ("no_alert", "alert"):
        b = run_pipeline(observation=obs)["bayes"]["p_dry"]
        a = "Water" if score(b, "Water") > score(b, "Wait") else "Wait"
        v = score(b, a)
        body += (f'<circle cx="{X(b)}" cy="{Y(v)}" r="6" fill="{INK}"/>'
                 f'<text class="m" x="{X(b) + 10}" y="{Y(v) + (22 if a == 'Water' else -14)}" font-size="11">{obs.replace("_", " ")}: {a} {v:.2f}</text>')
    return svg_doc(W, H, body)


def hill_panel(ox: int, title: str, scores: list, note: str, restart_dose=None) -> str:
    doses = config.DOSES
    run = hill_climb(doses, scores, config.START_DOSE)
    x0, x1, y0, y1, lo, hi = ox + 50, ox + 440, 60, 300, 50, 95
    X = lambda d: x0 + (d - doses[0]) / (doses[-1] - doses[0]) * (x1 - x0)
    Y = lambda s: y1 - (s - lo) / (hi - lo) * (y1 - y0)
    s = f'<text x="{ox + 20}" y="28" font-size="15" font-weight="500">{title}</text>'
    s += f'<line x1="{x0 - 20}" x2="{x1 + 20}" y1="{y1 + 20}" y2="{y1 + 20}" stroke="{INK}"/>'
    pts = " ".join(f"{X(d)},{Y(v)}" for d, v in zip(doses, scores))
    s += f'<polyline points="{pts}" fill="none" stroke="{LIGHT}" stroke-width="1.5"/>'
    path = [(X(d), Y(scores[doses.index(d)])) for d in run["path"]]
    for (ax, ay), (bx, by) in itertools.pairwise(path):
        s += f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="{INK}" stroke-width="3"/>'
    for d, v in zip(doses, scores):
        end = d == run["best_dose"]
        s += (f'<circle cx="{X(d)}" cy="{Y(v)}" r="{8 if end else 5}" fill="{INK if end else PAPER}" stroke="{INK}" stroke-width="1.5"/>'
              f'<text class="m" x="{X(d)}" y="{Y(v) - 16}" font-size="12" text-anchor="middle">{v}</text>'
              f'<text class="m mid" x="{X(d)}" y="{y1 + 40}" font-size="11" text-anchor="middle">{d} ml</text>')
    if restart_dose is not None:
        v = scores[doses.index(restart_dose)]
        s += (f'<circle cx="{X(restart_dose)}" cy="{Y(v)}" r="13" fill="none" stroke="{INK}" stroke-width="1.5" stroke-dasharray="3 3"/>'
              f'<text x="{X(restart_dose)}" y="{Y(v) - 34}" font-size="12" text-anchor="middle">restarts find {restart_dose} ml</text>')
    path_txt = " → ".join(map(str, run["path"]))
    s += (f'<text class="m" x="{ox + 20}" y="{y1 + 72}" font-size="12">path {path_txt}, stops at {run["best_dose"]} ml</text>'
          f'<text class="mid" x="{ox + 20}" y="{y1 + 92}" font-size="12">{note}</text>')
    return s


def fig_hill() -> str:
    best = random_restart(config.DOSES, config.TRICKY_SCORES)["best_dose"]
    body = (hill_panel(0, "Normal table", config.SCORES, "reaches the best dose") +
            '<line x1="480" x2="480" y1="20" y2="380" stroke="#e4e6ea"/>' +
            hill_panel(490, "Tricky table", config.TRICKY_SCORES, "stuck on a local maximum", best))
    return svg_doc(980, 400, body)


def build_figures() -> None:
    FIG.mkdir(exist_ok=True)
    r = run_pipeline()
    for name, svg in (("pipeline", fig_pipeline(r)), ("score_vs_pdry", fig_scores(r)), ("hill_climbing", fig_hill())):
        src = FIG / f"{name}.svg"
        src.write_text(svg, encoding="utf-8")
        w, h = re.search(r'width="(\d+)" height="(\d+)"', svg).groups()
        chrome(f"--screenshot={FIG / f'{name}.png'}", f"--window-size={w},{h}",
               "--force-device-scale-factor=2", src.as_uri())


# ---------- PDF ----------

CSS = """
@page { size: A4; margin: 16mm 17mm 17mm 17mm;
        @bottom-right { content: counter(page); font: 9pt 'JetBrains Mono', Menlo, monospace; color: #6f747c; } }
@page :first { @bottom-right { content: none; } }
html { color: #0c0e10; font: 10pt/1.45 Onest, Helvetica, Arial, sans-serif; }
body { margin: 0; }
h1, h2 { font-family: Geologica, Onest, Helvetica, sans-serif; font-weight: 500;
         font-variation-settings: "CRSV" 0, "SHRP" 0; break-after: avoid; }
h2 { font-size: 14pt; margin: 14pt 0 5pt; padding-top: 6pt; border-top: 1px solid #d5d8dd; }
p { margin: 0 0 7pt; }
ul, ol { margin: 0 0 7pt; padding-left: 18pt; } li { margin-bottom: 2pt; }
code, pre { font-family: 'JetBrains Mono', Menlo, monospace; font-size: 8.6pt; }
code { background: #f1f2f4; padding: 0 3px; border-radius: 4px; }
pre { background: #f4f5f7; border: 1px solid #e1e3e7; border-radius: 10px; padding: 9pt 11pt;
      margin: 0 0 9pt; break-inside: avoid; white-space: pre-wrap; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 0 0 9pt; font-size: 8.8pt; }
tr { break-inside: avoid; }
th, td { border-bottom: 1px solid #e1e3e7; padding: 3.5pt 6pt; text-align: left; vertical-align: top; }
th { font-weight: 500; border-bottom: 1px solid #0c0e10; }
td { font-variant-numeric: tabular-nums; }
figure { margin: 6pt 0 12pt; break-inside: avoid; }
figure img { width: 100%; display: block; }
figure.narrow img { width: 78%; }
figcaption { font-size: 9pt; color: #3c424c; margin-top: 5pt; }
a { color: inherit; }
.title-page { height: 250mm; display: flex; flex-direction: column; justify-content: center; break-after: page; }
.title-page h1 { font-size: 34pt; margin: 0 0 6pt; }
.title-page p { font-size: 12pt; margin: 0 0 4pt; color: #3c424c; }
.title-page p:nth-of-type(1) { font-size: 16pt; color: #0c0e10; margin-bottom: 28pt; }
.title-page p:nth-of-type(n+5) { font-family: 'JetBrains Mono', Menlo, monospace; font-size: 10pt; }
"""


def split_title(md_text: str) -> tuple[str, str]:
    i = md_text.index("\n## ")
    return md_text[:i], md_text[i + 1:]


def build_pdf(md_text: str) -> None:
    title, rest = split_title(md_text)
    conv = lambda t: markdown.markdown(t, extensions=["tables", "fenced_code"])
    body = conv(rest)
    body = re.sub(r'<p><img alt="([^"]*)" src="([^"]*)" /></p>',
                  r'<figure><img src="\2" alt="\1"><figcaption>\1</figcaption></figure>', body)
    body = body.replace('<figure><img src="figures/score_vs_pdry', '<figure class="narrow"><img src="figures/score_vs_pdry')
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><base href="{DOCS.as_uri()}/">'
            f'<title>Mini Greenhouse Assistant, technical report</title>'
            f'<style>{FACES}{CSS}</style></head>'
            f'<body><section class="title-page">{conv(title)}</section>{body}</body></html>')
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "report.html"
        page.write_text(html, encoding="utf-8")
        chrome("--no-pdf-header-footer", f"--print-to-pdf={DOCS / 'report.pdf'}", page.as_uri())


# ---------- DOCX ----------

INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*\s][^*]*\*|\[[^\]]+\]\([^)]+\))")


def add_link(par, text: str, url: str) -> None:
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), par.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True))
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    props.append(u)
    run.append(props)
    t = OxmlElement("w:t")
    t.text = text
    run.append(t)
    link.append(run)
    par._p.append(link)


def add_inline(par, text: str, bold: bool = False) -> None:
    text = text.replace("\\|", "|")
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**"):
            par.add_run(part[2:-2]).bold = True
        elif part.startswith("`"):
            r = par.add_run(part[1:-1])
            r.font.name = "Courier New"
            r.font.size = Pt(9)
        elif part.startswith("[") and "](" in part:
            label, url = re.match(r"\[([^\]]+)\]\(([^)]+)\)", part).groups()
            add_link(par, label, url) if url.startswith("http") else par.add_run(label)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            par.add_run(part[1:-1]).italic = True
        else:
            par.add_run(part).bold = bold


def build_docx(md_text: str) -> None:
    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = "Arial", Pt(10.5)
    for name in ("Title", "Heading 1"):
        st = doc.styles[name]
        st.font.name, st.font.color.rgb = "Arial", RGBColor(0x0C, 0x0E, 0x10)

    title, rest = split_title(md_text)
    for line in title.splitlines():
        if line.startswith("# "):
            doc.add_paragraph(line[2:], style="Title")
        elif line.strip():
            add_inline(doc.add_paragraph(), line)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    lines, i = rest.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            doc.add_heading(line[3:], level=1)
        elif line.startswith("```"):
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            p = doc.add_paragraph()
            r = p.add_run("\n".join(lines[i + 1:j]))
            r.font.name, r.font.size = "Courier New", Pt(8.5)
            p.paragraph_format.left_indent = Cm(0.4)
            i = j
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", lines[i].strip())[1:-1]]
                if not all(set(c) <= set("-:") for c in cells):
                    rows.append(cells)
                i += 1
            i -= 1
            table = doc.add_table(rows=len(rows), cols=len(rows[0]))
            table.style = "Table Grid"
            for ri, row in enumerate(rows):
                for ci, cell in enumerate(row):
                    par = table.cell(ri, ci).paragraphs[0]
                    add_inline(par, cell, bold=ri == 0)
                    for run in par.runs:
                        run.font.size = Pt(8.5)
            doc.add_paragraph()
        elif m := re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line):
            doc.add_picture(str(DOCS / m.group(2)), width=Cm(17))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap = doc.add_paragraph()
            cap.add_run(m.group(1)).italic = True
        elif line.startswith("- "):
            add_inline(doc.add_paragraph(style="List Bullet"), line[2:])
        elif m := re.match(r"(\d+)\. (.*)", line):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            add_inline(p, f"{m.group(1)}. {m.group(2)}")
        elif line.strip():
            add_inline(doc.add_paragraph(), line)
        i += 1
    doc.save(DOCS / "report.docx")


def main() -> None:
    md_text = (DOCS / "report.md").read_text(encoding="utf-8")
    build_figures()
    build_pdf(md_text)
    build_docx(md_text)
    print("built", *(DOCS / n for n in ("report.pdf", "report.docx")), sep="\n  ")


if __name__ == "__main__":
    main()
