"""Render data/profile.json as an animated neofetch-style card -> info-card.svg.

Add, remove or reorder lines in data/profile.json, then run this script.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
WIDTH, ROW_H, TOP = 520, 24, 118
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#58a6ff"]


def main():
    profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    rows = profile["rows"]
    key_w = max(len(k) for k, _ in rows) + 2  # align values in one column
    height = TOP + len(rows) * ROW_H + 70

    def row(i, delay, content):
        return f'<g class="row" style="animation-delay:{delay:.2f}s">{content}</g>'

    user, host = escape(profile["user"]), escape(profile["host"])
    parts = [
        row(0, 0.2, f'<text x="24" y="70"><tspan class="k">{user}</tspan>@<tspan class="k">{host}</tspan></text>'),
        row(0, 0.35, f'<text x="24" y="90" class="dim">{"-" * (len(user) + len(host) + 1)}</text>'),
    ]
    for i, (key, value) in enumerate(rows):
        y = TOP + i * ROW_H
        label = escape(f"{key}:".ljust(key_w)).replace(" ", "&#160;")
        parts.append(row(i, 0.5 + i * 0.15,
                         f'<text x="24" y="{y}"><tspan class="k">{label}</tspan>{escape(value)}</text>'))

    t = 0.5 + len(rows) * 0.15
    y = TOP + len(rows) * ROW_H
    swatches = "".join(f'<rect x="{24 + i * 24}" y="{y - 6}" width="22" height="14" fill="{c}"/>'
                       for i, c in enumerate(PALETTE))
    parts.append(row(0, t, swatches))
    parts.append(row(0, t + 0.15, f'<text x="24" y="{y + 40}"><tspan class="k">$</tspan> <tspan class="cur">█</tspan></text>'))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
<style>
  text {{ font: 13px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #c9d1d9; }}
  .k {{ fill: #39d353; font-weight: bold; }}
  .dim {{ fill: #8b949e; }}
  .row {{ opacity: 0; animation: in .45s ease-out forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateX(-12px); }} to {{ opacity: 1; transform: none; }} }}
  .cur {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
<rect width="{WIDTH}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d"/>
<rect width="{WIDTH}" height="34" rx="12" fill="#161b22"/><rect y="22" width="{WIDTH}" height="12" fill="#161b22"/>
<circle cx="20" cy="17" r="6" fill="#ff5f56"/><circle cx="40" cy="17" r="6" fill="#ffbd2e"/><circle cx="60" cy="17" r="6" fill="#27c93f"/>
<text x="{WIDTH / 2}" y="22" text-anchor="middle" class="dim">{user}@{host}: ~</text>
{chr(10).join(parts)}
</svg>'''
    (ROOT / "info-card.svg").write_text(svg, encoding="utf-8")
    print(f"wrote info-card.svg ({len(rows)} rows)")


if __name__ == "__main__":
    main()
