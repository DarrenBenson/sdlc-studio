#!/usr/bin/env python3
"""Render docs/whitepaper.md as a designed, distributable PDF (repo-only tool).

Usage:
    <venv-python> tools/whitepaper_pdf.py [--out docs/whitepaper.pdf]

Needs `markdown` and `weasyprint` (not repo dependencies - use a venv). The layout
is deliberately self-contained: system fonts (Liberation family), inline SVG
exhibits, no network fetches, so the render is reproducible anywhere.
"""
from __future__ import annotations

import argparse
import datetime
import re
from pathlib import Path

import markdown  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "whitepaper.md"

INK = "#1b2735"       # deep navy - body headings, cover
ACCENT = "#0e7c66"    # teal - rules, links, table headers
AMBER = "#c47f17"     # highlight - callouts, chart emphasis
FAINT = "#eef1f4"     # panel background
GOOD = "#1e8e5a"
BAD = "#c0392b"
MID = "#d9a441"

CSS = f"""
@page {{
  size: A4; margin: 22mm 18mm 20mm 18mm;
  @bottom-left {{ content: "SDLC Studio · The Mill, Not the Engine";
    font: 7.5pt 'Liberation Sans'; color: #8a93a0; }}
  @bottom-right {{ content: counter(page);
    font: 8pt 'Liberation Sans'; color: #8a93a0; }}
}}
@page cover {{ margin: 0; @bottom-left {{ content: none }} @bottom-right {{ content: none }} }}
* {{ box-sizing: border-box; }}
html {{ font-size: 10pt; }}
body {{ font-family: 'Liberation Serif', serif; color: #232a33; line-height: 1.5; margin: 0; }}
h1, h2, h3, h4 {{ font-family: 'Liberation Sans', sans-serif; color: {INK}; line-height: 1.25; }}
h2 {{ font-size: 15pt; margin: 1.6em 0 .5em; padding-bottom: .25em;
     border-bottom: 2.2pt solid {ACCENT}; page-break-after: avoid; }}
h3 {{ font-size: 11.5pt; margin: 1.2em 0 .35em; page-break-after: avoid; }}
p {{ margin: .45em 0 .75em; text-align: justify; }}
a {{ color: {ACCENT}; text-decoration: none; }}
strong {{ color: {INK}; }}
code {{ font-family: 'Liberation Mono', monospace; font-size: 8.6pt;
       background: {FAINT}; padding: 0 2.5pt; border-radius: 2pt; }}
ul, ol {{ margin: .4em 0 .8em; padding-left: 1.35em; }}
li {{ margin: .28em 0; }}
table {{ border-collapse: collapse; width: 100%; margin: .8em 0 1.1em;
        font-family: 'Liberation Sans', sans-serif; font-size: 8.6pt;
        page-break-inside: avoid; }}
th {{ background: {INK}; color: #fff; text-align: left; padding: 5pt 7pt;
     font-weight: 700; font-size: 8.3pt; }}
td {{ padding: 4.5pt 7pt; border-bottom: .6pt solid #d5dbe2; vertical-align: top; }}
tr:nth-child(even) td {{ background: #f7f9fb; }}
hr {{ border: none; border-top: .8pt solid #d5dbe2; margin: 1.4em 0; }}
blockquote {{ margin: .9em 0; padding: .55em .9em; background: {FAINT};
             border-left: 3pt solid {ACCENT}; font-style: italic; }}

.cover {{ page: cover; width: 210mm; height: 296mm; background: {INK};
         color: #fff; position: relative; page-break-after: always; }}
.cover .band {{ position: absolute; top: 0; left: 0; width: 8mm; height: 100%;
               background: {ACCENT}; }}
.cover .inner {{ position: absolute; left: 24mm; right: 20mm; top: 52mm; }}
.cover h1 {{ font-size: 34pt; color: #fff; margin: 0 0 6mm; line-height: 1.12; }}
.cover .sub {{ font-family: 'Liberation Sans'; font-size: 13.5pt; color: #bcd6cf;
              margin-bottom: 14mm; line-height: 1.4; }}
.cover .meta {{ font-family: 'Liberation Sans'; font-size: 10pt; color: #8fa3b8;
               border-top: .8pt solid #3b4a5e; padding-top: 5mm; }}
.cover .art {{ position: absolute; right: 16mm; bottom: 30mm; }}
.cover .thesis {{ position: absolute; left: 24mm; right: 60mm; bottom: 30mm;
                 font-size: 10.5pt; color: #d8e2ec; font-style: italic; line-height: 1.5; }}

.findings {{ counter-reset: fnd; margin: 1em 0; }}
.finding {{ display: flex; gap: 8pt; background: {FAINT}; border-left: 3pt solid {ACCENT};
           padding: 7pt 10pt; margin: 6pt 0; page-break-inside: avoid; }}
.finding .n {{ counter-increment: fnd; font-family: 'Liberation Sans';
              font-size: 17pt; font-weight: 700; color: {ACCENT}; min-width: 16pt; }}
.finding .n::before {{ content: counter(fnd); }}
.finding p {{ margin: 0; text-align: left; font-size: 9.3pt; }}

.exhibit {{ margin: 1em 0 1.2em; page-break-inside: avoid; }}
.exhibit .cap {{ font-family: 'Liberation Sans'; font-size: 8pt; color: #5c6672;
                margin-top: 3pt; }}
.exhibit .cap b {{ color: {ACCENT}; }}
.callout {{ background: {FAINT}; border-left: 3pt solid {AMBER};
           padding: .6em .9em; margin: .9em 0; page-break-inside: avoid; }}
.callout p {{ margin: .2em 0; text-align: left; }}
.footer-note {{ font-size: 8.4pt; color: #5c6672; font-style: italic;
               border-top: .8pt solid #d5dbe2; margin-top: 1.6em; padding-top: .7em; }}
.toc {{ font-family: 'Liberation Sans'; font-size: 9pt; column-count: 2;
       column-gap: 8mm; margin: .8em 0 1.2em; }}
.toc div {{ margin: 2.2pt 0; }}
.toc .tn {{ color: {ACCENT}; font-weight: 700; margin-right: 4pt; }}
"""


def gear(cx, cy, r, colour, label):
    """One cockpit instrument: a ring with a label."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" '
            f'stroke-width="7" opacity="0.9"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r-14}" fill="none" stroke="{colour}" '
            f'stroke-width="1.5" opacity="0.45"/>'
            f'<text x="{cx}" y="{cy+4}" text-anchor="middle" '
            f'font-family="Liberation Sans" font-size="11" font-weight="bold" '
            f'fill="{colour}">{label}</text>')


def cover_art():
    """Five interlocking instrument rings - the cockpit motif."""
    cols = ["#0e7c66", "#2a9d8f", "#c47f17", "#5b8bb2", "#88a8c3"]
    labels = ["SPEC", "GOV", "MEAS", "EVID", "ID"]
    pos = [(55, 55), (135, 40), (205, 70), (95, 130), (180, 145)]
    rings = "".join(gear(x, y, 34, c, l) for (x, y), c, l in zip(pos, cols, labels))
    return (f'<svg width="66mm" height="50mm" viewBox="0 0 250 190" '
            f'xmlns="http://www.w3.org/2000/svg">{rings}</svg>')


def quadrant_svg():
    """The centrepiece: escapes by model x engagement mode, as a heat grid."""
    rows = [("Mid-tier (Sonnet 5)", [("5/5", BAD), ("2/5", MID), ("1/5", GOOD)]),
            ("Premium (Opus 4.8)", [("3/3", BAD), ("3/3", BAD), ("0/5", GOOD)]),
            ("Frontier (Fable 5)", [("0/5", GOOD), ("0/5", GOOD), ("not run", "#9aa4af")])]
    cols = ["Judgement-gated", "No process", "Mandated"]
    cw, ch, lx, ty = 118, 44, 150, 34
    out = [f'<svg width="170mm" height="52mm" viewBox="0 0 {lx+3*cw+8} {ty+3*ch+10}" '
           'xmlns="http://www.w3.org/2000/svg" font-family="Liberation Sans">']
    for i, c in enumerate(cols):
        out.append(f'<text x="{lx+i*cw+cw/2}" y="{ty-12}" text-anchor="middle" '
                   f'font-size="12.5" font-weight="bold" fill="{INK}">{c}</text>')
    for r, (label, cells) in enumerate(rows):
        y = ty + r * ch
        out.append(f'<text x="{lx-8}" y="{y+ch/2+4}" text-anchor="end" font-size="12" '
                   f'fill="{INK}">{label}</text>')
        for i, (val, col) in enumerate(cells):
            x = lx + i * cw
            out.append(f'<rect x="{x+3}" y="{y+3}" width="{cw-6}" height="{ch-6}" '
                       f'rx="4" fill="{col}" opacity="0.88"/>')
            out.append(f'<text x="{x+cw/2}" y="{y+ch/2+5}" text-anchor="middle" '
                       f'font-size="14" font-weight="bold" fill="#fff">{val}</text>')
    out.append("</svg>")
    return "".join(out)


def cost_svg():
    """Cost per delivered ticket - horizontal bars, escapes annotated."""
    data = [("Frontier · pipeline", 1.39, "0/5", ACCENT, True),
            ("Frontier · no process", 0.98, "0/5", "#9aa4af", False),
            ("Premium · mandated", 0.52, "0/5", ACCENT, True),
            ("Premium · no process", 0.49, "3/3", BAD, False),
            ("Mid-tier · mandated", 0.43, "1/5", ACCENT, True),
            ("Mid-tier · no process", 0.36, "2/5", MID, False)]
    w, bh, lx = 560, 30, 168
    scale = 330 / 1.39
    out = [f'<svg width="170mm" height="62mm" viewBox="0 0 {w} {len(data)*bh+34}" '
           'xmlns="http://www.w3.org/2000/svg" font-family="Liberation Sans">']
    for i, (label, cost, esc, col, trail) in enumerate(data):
        y = 8 + i * bh
        bw = cost * scale
        out.append(f'<text x="{lx-6}" y="{y+15}" text-anchor="end" font-size="10.5" '
                   f'fill="{INK}">{label}</text>')
        out.append(f'<rect x="{lx}" y="{y+2}" width="{bw}" height="{bh-9}" rx="3" '
                   f'fill="{col}" opacity="{0.92 if trail else 0.55}"/>')
        badge = "evidence trail" if trail else "no trail"
        out.append(f'<text x="{lx+bw+7}" y="{y+15}" font-size="10.5" fill="{INK}">'
                   f'<tspan font-weight="bold">${cost:.2f}</tspan>'
                   f'<tspan fill="#5c6672">  · {esc} escapes · {badge}</tspan></text>')
    out.append(f'<text x="{lx}" y="{len(data)*bh+26}" font-size="9" fill="#5c6672">'
               'Cost per delivered ticket, trap fixture, July 2026 list rates '
               '(mid-tier shown at post-August pricing; the intro rate is lower).</text>')
    out.append("</svg>")
    return "".join(out)


def trail_svg():
    """The worked-example delivery trail."""
    steps = ["Finding\nfiled", "Failing test\nfirst", "Fix", "Gated close\n(depth + verdict)",
             "Reconcile\n+ gate", "Attestation\nledger"]
    n, bw, bh, gap = len(steps), 116, 52, 26
    w = n * bw + (n - 1) * gap + 8
    out = [f'<svg width="170mm" height="22mm" viewBox="0 0 {w} 66" '
           'xmlns="http://www.w3.org/2000/svg" font-family="Liberation Sans">']
    for i, s in enumerate(steps):
        x = 4 + i * (bw + gap)
        fill = ACCENT if i in (1, 3, 5) else INK
        out.append(f'<rect x="{x}" y="6" width="{bw}" height="{bh}" rx="6" '
                   f'fill="{fill}" opacity="0.92"/>')
        lines = s.split("\n")
        for j, ln in enumerate(lines):
            dy = 32 + (j - (len(lines) - 1) / 2) * 13
            out.append(f'<text x="{x+bw/2}" y="{dy}" text-anchor="middle" '
                       f'font-size="10" font-weight="bold" fill="#fff">{ln}</text>')
        if i < n - 1:
            ax = x + bw
            out.append(f'<path d="M {ax+4} 32 L {ax+gap-4} 32" stroke="{AMBER}" '
                       f'stroke-width="2.5"/><path d="M {ax+gap-9} 27 L {ax+gap-4} 32 '
                       f'L {ax+gap-9} 37" fill="none" stroke="{AMBER}" stroke-width="2.5"/>')
    out.append("</svg>")
    return "".join(out)


def build(out_path: Path) -> None:
    md = SRC.read_text(encoding="utf-8")

    # Split off the title block (rendered as the cover) from the body.
    body_md = md.split("---", 2)[2] if md.count("---") >= 2 else md
    html_body = markdown.markdown(
        body_md, extensions=["tables", "attr_list", "smarty"],
        output_format="html")

    # Findings list on the At-a-glance page -> numbered cards.
    def cardify(m):
        items = re.findall(r"<li>(.*?)</li>", m.group(1), re.S)
        cards = "".join(
            f'<div class="finding"><div class="n"></div><p>{i}</p></div>' for i in items)
        return f'<div class="findings">{cards}</div>'
    html_body = re.sub(r"<ol>\s*(<li>.*?</li>)\s*</ol>", cardify, html_body,
                       count=1, flags=re.S)

    # Inject exhibits after their anchor tables/paragraphs.
    quad_anchor = "<p><strong>The quadrant.</strong>"
    html_body = html_body.replace(
        quad_anchor,
        f'<div class="exhibit">{quadrant_svg()}<div class="cap"><b>Exhibit 1.</b> '
        'Defect escapes on the hidden-requirement fixture, by model tier and '
        'engagement mode. Green cells passed the held-back suite.</div></div>'
        + quad_anchor, 1)
    price_anchor = "<p><strong>The prices.</strong>"
    html_body = html_body.replace(
        price_anchor,
        f'<div class="exhibit">{cost_svg()}<div class="cap"><b>Exhibit 2.</b> '
        'What a governed base model costs against ungoverned alternatives. Teal '
        'bars produce the full audit trail.</div></div>' + price_anchor, 1)
    trail_heading = re.search(r"<h2[^>]*>7\..*?</h2>", html_body)
    if trail_heading:
        ins = (f'<div class="exhibit">{trail_svg()}<div class="cap"><b>Exhibit 3.</b> '
               'One unit of work, end to end: teal stages are the mechanically '
               'gated ones.</div></div>')
        first_para_end = html_body.find("</p>", trail_heading.end()) + 4
        # place after the section's second paragraph for flow
        second_para_end = html_body.find("</p>", first_para_end) + 4
        html_body = html_body[:second_para_end] + ins + html_body[second_para_end:]

    # Page breaks before each numbered section and the register.
    html_body = re.sub(r'<h2', '<h2 style="page-break-before: always"', html_body)
    # ...but not the very first h2 (At a glance follows the cover naturally)
    html_body = html_body.replace('<h2 style="page-break-before: always"', "<h2", 1)

    today = datetime.date(2026, 7, 10).strftime("%-d %B %Y")
    cover = f"""
<div class="cover"><div class="band"></div>
  <div class="inner">
    <h1>The Mill,<br/>Not the Engine</h1>
    <div class="sub">Running a full engineering discipline through<br/>
    the AI coding agent you already have</div>
    <div class="meta">SDLC Studio white paper · v4.0 · {today}<br/>
    Open source · every claim traceable to shipped behaviour or published measurement</div>
  </div>
  <div class="thesis">"The code is the cloth. The organisation around it is
  where the money is."</div>
  <div class="art">{cover_art()}</div>
</div>"""

    html = (f"<html><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body>{cover}{html_body}</body></html>")
    from weasyprint import HTML  # deferred: import cost only when rendering
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(out_path))
    print(f"wrote {out_path} ({out_path.stat().st_size//1024} KB)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "docs" / "whitepaper.pdf"))
    build(Path(ap.parse_args().out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
