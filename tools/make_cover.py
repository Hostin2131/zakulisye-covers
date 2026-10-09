#!/usr/bin/env python3
"""Generate a per-story neon cover for the «Закулисье» channel.

Usage:
  python3 make_cover.py out.jpg --rubric СКАНДАЛ --title "Клава Кока VS Виктор Дробыш" \
      [--quote "Это хайп стопроцентный"] [--quote-by "Дробыш — в ответ на слова Клавы Коки"] \
      [--big "16,6 млн ₽"]

Rubrics: СКАНДАЛ, СУД, ЛИЧНОЕ, ДЕНЬГИ, ЭФИР, СРОЧНО, ГОРЯЧЕЕ.
In --title, the word VS (or "против") is highlighted automatically.
"""
import argparse
import html
import re
import sys

from playwright.sync_api import sync_playwright

RUBRICS = {
    "СКАНДАЛ": ("💥", "#ff2bd6", "#2bf0ff"),
    "СУД": ("⚖️", "#2bf0ff", "#ffd23b"),
    "ЛИЧНОЕ": ("💔", "#ff6bb5", "#ffd23b"),
    "ДЕНЬГИ": ("💰", "#3bff8a", "#ffd23b"),
    "ЭФИР": ("📺", "#a35bff", "#2bf0ff"),
    "СРОЧНО": ("⚡", "#ff3b3b", "#ffffff"),
    "ГОРЯЧЕЕ": ("🔥", "#ff3b3b", "#ffd23b"),
}


def esc(s):
    return html.escape(s or "", quote=False)


def build(rubric, title, quote, quote_by, big):
    icon, main, second = RUBRICS[rubric]
    t = esc(title)
    t = re.sub(r"\b(VS|vs|против)\b",
               lambda m: f'<span style="color:{second};text-shadow:0 0 18px {second}">{m.group(1)}</span>', t)
    # auto-size title by length
    n = len(title)
    tsize = 72 if n <= 28 else 62 if n <= 45 else 52 if n <= 70 else 44
    parts = [f'<div><span style="background:{main};color:#0a0410;font-weight:bold;font-size:30px;'
             f'letter-spacing:5px;padding:10px 22px;border-radius:8px">{icon} {rubric}</span></div>',
             f'<div style="font-size:{tsize}px;font-weight:bold;line-height:1.12;'
             f'text-shadow:0 0 18px {main}">{t}</div>']
    if big:
        parts.append(f'<div style="font-size:96px;font-weight:bold;color:{second};'
                     f'text-shadow:0 0 22px {second};line-height:1">{esc(big)}</div>')
    if quote:
        q = quote if len(quote) <= 90 else quote[:87].rstrip() + "…"
        qsize = 48 if len(q) <= 40 else 38 if len(q) <= 70 else 32
        by = (f'<div style="font-size:28px;color:#b9a7c9;margin-top:12px">{esc(quote_by)}</div>'
              if quote_by else "")
        parts.append(f'<div style="border-left:8px solid {second};padding-left:28px">'
                     f'<div style="font-size:{qsize}px;color:#ffe9fb">«{esc(q)}»</div>{by}</div>')
    parts = ['<div style="margin:auto 0;display:flex;flex-direction:column;gap:30px">' + "".join(parts) + "</div>"]
    parts.append('<div style="display:flex;justify-content:space-between;align-items:center">'
                 '<span style="font-size:30px;font-weight:bold;letter-spacing:8px;opacity:.85">ЗАКУЛИСЬЕ</span>'
                 f'<span style="font-size:26px;color:{second};letter-spacing:3px">ШОУБИЗ БЕЗ ГРИМА</span></div>')
    return f"""<html><body style="margin:0">
<div style="width:1280px;height:720px;position:relative;overflow:hidden;font-family:'DejaVu Sans';
background:radial-gradient(ellipse at 30% 40%,#2a0b3d 0%,#07030c 70%);color:#fff">
  <div style="position:absolute;inset:30px;border:6px solid {main};border-radius:30px;
       box-shadow:0 0 30px {main},inset 0 0 30px {main}55"></div>
  <div style="position:absolute;left:80px;right:80px;top:80px;bottom:70px;display:flex;flex-direction:column;gap:30px">
    {''.join(parts)}
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
        import os
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
