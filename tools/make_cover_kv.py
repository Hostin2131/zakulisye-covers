#!/usr/bin/env python3
"""Generate a per-story cover for the «Коридоры власти» politics channel
(dark red / black, gritty — matches the channel avatar).

Usage:
  python3 make_cover_kv.py out.jpg --rubric ЗАКОН --title "Госдума приняла закон о ..." \
      [--quote "Реальная цитата"] [--quote-by "Кто — где сказал"] [--big "120 млрд ₽"]

Rubrics: СВО, ЗАКОН, ОТСТАВКА, ЗАЯВЛЕНИЕ, СКАНДАЛ, СУД, ВЫБОРЫ, МИР, САНКЦИИ, СРОЧНО, ГОРЯЧЕЕ.
In --title, the word VS (or "против") is highlighted automatically.
"""
import argparse
import html
import os
import re
import sys

from playwright.sync_api import sync_playwright

RED = "#e0161c"
RUBRICS = {
    "СВО": "🎖", "ЗАКОН": "📜", "ОТСТАВКА": "🚪", "ЗАЯВЛЕНИЕ": "🎙",
    "СКАНДАЛ": "💥", "СУД": "⚖️", "ВЫБОРЫ": "🗳", "МИР": "🌍",
    "САНКЦИИ": "⛔", "СРОЧНО": "⚡", "ГОРЯЧЕЕ": "🔥",
}

FONT = "'Noto Sans CJK JP','Noto Sans CJK SC','DejaVu Sans',sans-serif"

# SVG grunge texture (noise + scratches), inlined so no network is needed
GRAIN = ("data:image/svg+xml;utf8,"
         "<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='720'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1.4 -0.55'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>")


def esc(s):
    return html.escape(s or "", quote=False)


def build(rubric, title, quote, quote_by, big):
    icon = RUBRICS[rubric]
    t = esc(title)
    t = re.sub(r"\b(VS|vs|против)\b",
               lambda m: f'<span style="color:{RED}">{m.group(1)}</span>', t)
    n = len(title)
    tsize = 74 if n <= 28 else 64 if n <= 45 else 54 if n <= 70 else 46
    parts = [f'<div><span style="background:{RED};color:#fff;font-weight:900;font-size:30px;'
             f'letter-spacing:6px;padding:10px 22px;clip-path:polygon(0 0,100% 0,97% 100%,0 100%)">'
             f'{icon} {rubric}</span></div>',
             f'<div style="font-size:{tsize}px;font-weight:900;line-height:1.1;text-transform:none;'
             f'text-shadow:0 4px 0 #000,0 0 30px #000">{t}</div>']
    if big:
        parts.append(f'<div style="font-size:100px;font-weight:900;color:{RED};line-height:1;'
                     f'text-shadow:0 4px 0 #000">{esc(big)}</div>')
    if quote:
        q = quote if len(quote) <= 90 else quote[:87].rstrip() + "…"
        qsize = 46 if len(q) <= 40 else 38 if len(q) <= 70 else 32
        by = (f'<div style="font-size:26px;color:#a99;margin-top:12px">{esc(quote_by)}</div>'
              if quote_by else "")
        parts.append(f'<div style="border-left:10px solid {RED};padding-left:28px">'
                     f'<div style="font-size:{qsize}px;color:#f3ecec;font-weight:700">«{esc(q)}»</div>{by}</div>')
    body = '<div style="margin:auto 0;display:flex;flex-direction:column;gap:28px">' + "".join(parts) + "</div>"
    footer = ('<div style="display:flex;justify-content:space-between;align-items:center;'
              'border-top:3px solid #3a1416;padding-top:18px">'
              '<span style="font-size:32px;font-weight:900;letter-spacing:6px">КОРИДОРЫ '
              f'<span style="color:{RED}">ВЛАСТИ</span></span>'
              '<span style="font-size:24px;color:#9a8a8a;letter-spacing:4px">ВЛАСТЬ ЛЮБИТ ТИШИНУ</span></div>')
    return f"""<html><body style="margin:0">
<div style="width:1280px;height:720px;position:relative;overflow:hidden;font-family:{FONT};color:#fff;
background:#08070a">
  <!-- corridor with red light from a half-open door on the right -->
  <div style="position:absolute;right:120px;top:120px;width:150px;height:300px;background:#ff2a1e;
       box-shadow:0 0 120px 40px rgba(220,0,0,.55)"></div>
  <div style="position:absolute;right:170px;top:128px;width:100px;height:286px;background:#0a0606;
       transform:skewY(4deg)"></div>
  <div style="position:absolute;inset:0;background:
       linear-gradient(90deg,#08070a 0%,#08070a 45%,rgba(8,7,10,.55) 70%,rgba(8,7,10,.2) 100%)"></div>
  <div style="position:absolute;inset:0;background:radial-gradient(ellipse at 85% 110%,rgba(170,0,0,.45),transparent 55%)"></div>
  <div style="position:absolute;inset:0;background-image:url(&quot;{GRAIN}&quot;);opacity:.55;mix-blend-mode:multiply"></div>
  <div style="position:absolute;left:0;top:0;bottom:0;width:14px;background:{RED}"></div>
  <div style="position:absolute;left:80px;right:80px;top:70px;bottom:50px;display:flex;flex-direction:column;gap:26px">
    {body}
    {footer}
  </div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--rubric", required=True, choices=list(RUBRICS))
    ap.add_argument("--title", required=True)
    ap.add_argument("--quote")
    ap.add_argument("--quote-by")
    ap.add_argument("--big")
    a = ap.parse_args()
    page_html = build(a.rubric, a.title, a.quote, a.quote_by, a.big)
    with sync_playwright() as p:
        kw = {}
        if os.path.exists("/opt/pw-browsers/chromium"):
            kw["executable_path"] = "/opt/pw-browsers/chromium"
        b = p.chromium.launch(**kw)
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.set_content(page_html)
        pg.screenshot(path=a.out, type="jpeg", quality=88)
        b.close()
    print(a.out)


if __name__ == "__main__":
    sys.exit(main())
