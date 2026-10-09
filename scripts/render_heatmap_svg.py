"""Render data/contributions.json as an animated SVG heatmap."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP = 13, 3
LEFT, TOP = 40, 50
STEP_S, PAUSE_S = 0.035, 0.35  # runner: seconds per cell moved, seconds resting on a day
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def steps(a, b):
    """Cell indexes walked going from a to b, excluding a."""
    d = 1 if b > a else -1
    return list(range(a + d, b + d, d)) if a != b else []


def runner_svg(stops, start_delay):
    """A glowing square that walks the grid (row first, then column) from one
    contribution day to the next, pinging each day it lands on, then loops."""
    if len(stops) < 2:
        return ""
    pos = lambda c, r: (LEFT + c * (CELL + GAP), TOP + r * (CELL + GAP))
    frames, arrivals, t = [(*stops[0], 0.0)], [(*stops[0], 0.0)], 0.0
    for (c0, r0), (c1, r1) in zip(stops, stops[1:]):
        t += PAUSE_S
        frames.append((c0, r0, t))
        for c in steps(c0, c1):  # along the row...
            t += STEP_S
            frames.append((c, r0, t))
        for r in steps(r0, r1):  # ...then up/down the column
            t += STEP_S
            frames.append((c1, r, t))
        arrivals.append((c1, r1, t))
    t += PAUSE_S * 3
    frames.append((*stops[-1], t))
    total = t

    kt = ";".join(f"{f[2] / total:.5f}" for f in frames)
    xs = ";".join(str(pos(f[0], f[1])[0]) for f in frames)
    ys = ";".join(str(pos(f[0], f[1])[1]) for f in frames)

    def square(delay, opacity, glow):
        filt = ' filter="url(#glow)"' if glow else ""
        fill = "#ffffff" if glow else "#69f0a0"  # white head, green trail
        return (
            f'<rect width="{CELL}" height="{CELL}" rx="3" fill="{fill}" opacity="0"{filt}>'
            # fade in/out at the loop seam so the jump back to the start isn't visible
            f'<animate attributeName="opacity" values="0;{opacity};{opacity};0" keyTimes="0;0.02;0.97;1" '
            f'dur="{total:.2f}s" begin="{start_delay + delay:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="x" values="{xs}" keyTimes="{kt}" dur="{total:.2f}s" '
            f'begin="{start_delay + delay:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{ys}" keyTimes="{kt}" dur="{total:.2f}s" '
            f'begin="{start_delay + delay:.2f}s" repeatCount="indefinite"/></rect>'
        )

    pings = []
    for c, r, at in arrivals:
        x, y = pos(c, r)
        a, e = at / total, 0.5 / total
        b = min(a + e, 1)
        pings.append(
            f'<rect x="{x - 2}" y="{y - 2}" width="{CELL + 4}" height="{CELL + 4}" rx="4" fill="none" '
            f'stroke="#69f0a0" stroke-width="1.5" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{a:.5f};{a:.5f};{b:.5f};1" '
            f'dur="{total:.2f}s" begin="{start_delay:.2f}s" repeatCount="indefinite"/></rect>'
        )
    trail = "".join(square(d, o, False) for d, o in [(0.18, 0.15), (0.12, 0.3), (0.06, 0.5)])
    return "".join(pings) + trail + square(0, 1, True)


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days, stats = data["days"], data["stats"]

    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    cells, month_labels, last_month, stops = [], [], None, []
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
        if d["count"] > 0:
            stops.append((col, row))
        m = date.fromisoformat(d["date"]).month
        if row == 0 and m != last_month:
            month_labels.append(f'<text x="{x}" y="{TOP - 10}">{MONTHS[m - 1]}</text>')
            last_month = m

    runner = runner_svg(stops, start_delay=(len(days) + offset) // 7 * 0.025 + 0.8)
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
<defs><filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
  <feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter></defs>
<rect width="100%" height="100%" rx="12" fill="#0d1117" stroke="#30363d"/>
{"".join(month_labels)}
<text x="8" y="{TOP + 1 * (CELL + GAP) + 10}">Mon</text>
<text x="8" y="{TOP + 3 * (CELL + GAP) + 10}">Wed</text>
<text x="8" y="{TOP + 5 * (CELL + GAP) + 10}">Fri</text>
{"".join(cells)}
{runner}
<text x="{legend_x}" y="{height - 38}">Less</text>{legend}
<text x="{legend_x + 42 + 5 * (CELL + GAP)}" y="{height - 38}">More</text>
<text x="{LEFT}" y="{height - 16}" style="fill:#39d353">{footer}</text>
</svg>'''
    (ROOT / "contrib-heatmap.svg").write_text(svg, encoding="utf-8")
    print("wrote contrib-heatmap.svg")


if __name__ == "__main__":
    main()
