"""Render data/contributions.json as an animated SVG heatmap."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP = 13, 3
LEFT, TOP = 40, 50
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days, stats = data["days"], data["stats"]

    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    cells, month_labels, last_month = [], [], None
    for i, d in enumerate(days):
        idx = i + offset
        col, row = idx // 7, idx % 7
        x, y = LEFT + col * (CELL + GAP), TOP + row * (CELL + GAP)
        delay = (col + row) * 0.025  # diagonal wave
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{PALETTE[d["level"]]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{d["count"]} on {d["date"]}</title></rect>'
        )
        m = date.fromisoformat(d["date"]).month
        if row == 0 and m != last_month:
            month_labels.append(f'<text x="{x}" y="{TOP - 10}">{MONTHS[m - 1]}</text>')
            last_month = m

    cols = (len(days) + offset + 6) // 7
    width = LEFT + cols * (CELL + GAP) + 20
    height = TOP + 7 * (CELL + GAP) + 70
    legend_x = width - 20 - 5 * (CELL + GAP) - 70
    legend = "".join(
        f'<rect x="{legend_x + 38 + i * (CELL + GAP)}" y="{height - 48}" width="{CELL}" '
        f'height="{CELL}" rx="3" fill="{c}"/>' for i, c in enumerate(PALETTE)
    )
    best = stats["best_day"]
    footer = (
        f'{stats["total"]} contributions · current streak {stats["current_streak"]}d · '
        f'longest streak {stats["longest_streak"]}d · best day {best["count"]} ({best["date"]})'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  text {{ font: 11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #8b949e; }}
  .c {{ opacity: 0; animation: drop .5s ease-out forwards; }}
  @keyframes drop {{ from {{ opacity: 0; transform: translateY(-8px); }} to {{ opacity: 1; transform: none; }} }}
</style>
<rect width="100%" height="100%" rx="12" fill="#0d1117" stroke="#30363d"/>
{"".join(month_labels)}
<text x="8" y="{TOP + 1 * (CELL + GAP) + 10}">Mon</text>
<text x="8" y="{TOP + 3 * (CELL + GAP) + 10}">Wed</text>
<text x="8" y="{TOP + 5 * (CELL + GAP) + 10}">Fri</text>
{"".join(cells)}
<text x="{legend_x}" y="{height - 38}">Less</text>{legend}
<text x="{legend_x + 42 + 5 * (CELL + GAP)}" y="{height - 38}">More</text>
<text x="{LEFT}" y="{height - 16}" style="fill:#39d353">{footer}</text>
</svg>'''
    (ROOT / "contrib-heatmap.svg").write_text(svg, encoding="utf-8")
    print("wrote contrib-heatmap.svg")


if __name__ == "__main__":
    main()
