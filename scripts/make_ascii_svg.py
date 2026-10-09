"""Turn data/portrait.png into an animated ASCII-art SVG -> ascii-portrait.svg."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAMP = " .`:-=+*cs#%@"   # sparse -> dense; dense = bright on the dark card
COLS = 76
FONT, CHAR_W, LINE_H = 9, 5.4, 9.4
PAD_X, PAD_Y = 18, 50
COLOR = "#39d353"
STATIC = os.environ.get("STATIC") == "1"


def main():
    img = Image.open(ROOT / "data" / "portrait.png").convert("RGBA")
    img = img.crop(img.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox())
    rows = round(COLS * img.height / img.width * CHAR_W / LINE_H)
    a = np.asarray(img.resize((COLS, rows), Image.LANCZOS)).astype(float)
    lum, alpha = a[:, :, 0] / 255, a[:, :, 3] / 255

    lines = []
    for y in range(rows):
        line = ""
        for x in range(COLS):
            if alpha[y, x] < 0.5:
                line += " "
            else:  # never blank inside the silhouette so dark hair still shows
                line += RAMP[1 + int(lum[y, x] * (len(RAMP) - 2) + 0.5)]
        lines.append(line.rstrip())

    width = int(COLS * CHAR_W + 2 * PAD_X)
    height = int(rows * LINE_H + PAD_Y + 20)
    defs, body = [], []
    for y, line in enumerate(lines):
        if not line:
            continue
        ty = PAD_Y + y * LINE_H
        w = len(line) * CHAR_W
        text = f'<text x="{PAD_X}" y="{ty:.1f}" textLength="{w:.1f}"'
        if STATIC:
            body.append(f"{text}>{escape(line)}</text>")
            continue
        begin = 0.3 + y * 0.045  # rows wipe in top to bottom
        defs.append(
            f'<clipPath id="r{y}"><rect x="{PAD_X}" y="{ty - FONT:.1f}" width="0" height="{LINE_H + 1}">'
            f'<animate attributeName="width" from="0" to="{w:.1f}" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        body.append(
            f'{text} clip-path="url(#r{y})">{escape(line)}</text>'
            f'<rect x="{PAD_X}" y="{ty - FONT + 1:.1f}" width="{CHAR_W}" height="{FONT}" fill="{COLOR}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin:.2f}s"/>'
            f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X + w:.1f}" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + 0.35:.2f}s"/></rect>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>text {{ font: {FONT}px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: {COLOR}; white-space: pre; }}</style>
<rect width="100%" height="100%" rx="12" fill="#0d1117" stroke="#30363d"/>
<rect width="100%" height="34" rx="12" fill="#161b22"/><rect y="22" width="100%" height="12" fill="#161b22"/>
<circle cx="20" cy="17" r="6" fill="#ff5f56"/><circle cx="40" cy="17" r="6" fill="#ffbd2e"/><circle cx="60" cy="17" r="6" fill="#27c93f"/>
<text x="{width / 2}" y="21" text-anchor="middle" style="font-size:12px;fill:#8b949e">cat portrait.txt</text>
<defs>{"".join(defs)}</defs>
<g xml:space="preserve">{"".join(body)}</g>
</svg>'''
    (ROOT / "ascii-portrait.svg").write_text(svg, encoding="utf-8")
    print(f"wrote ascii-portrait.svg ({COLS}x{rows})")


if __name__ == "__main__":
    main()
