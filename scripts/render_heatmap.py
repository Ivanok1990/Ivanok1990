"""Render the animated contribution heatmap from data/contributions.json.

    python scripts/render_heatmap.py data/contributions.json contrib-heatmap.svg
"""
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from term import BLUE, MONO, MUTED, TEXT, command, esc, frame, write  # noqa: E402

PROMPT = "omar@github ~ $"
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
CELL, GAP = 11, 3
STEP = CELL + GAP
LEFT, TOP = 62, 80
W = 860


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    tail = days[:-1] if days and not days[-1]["count"] else days  # today may still be empty
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1
    return longest, current


def plural(n, word):
    return f"{n:,} {word}" + ("" if n == 1 else "s")


def main(src, out):
    data = json.load(open(src, encoding="utf-8"))
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday = row 0
    parts = []
    svg, t, _ = command(28, 36, PROMPT, "./contributions.sh --last-year", 0.2)
    parts.append(svg)
    t += 0.2

    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="28" y="{TOP + row * STEP + 10}" class="lbl in" style="--d:{t:.2f}s">{name}</text>')

    last_month, last_col = None, -9
    cells = []
    best = max(days, key=lambda d: d["count"])
    for i, d in enumerate(days):
        idx = i + offset
        col, row = idx // 7, idx % 7
        x, y = LEFT + col * STEP, TOP + row * STEP
        dt = date.fromisoformat(d["date"])
        if row == 0 and dt.month != last_month:
            # label a month at its first full column, if there is room for the text
            if col - last_col >= 3 and col <= 51:
                parts.append(f'<text x="{x}" y="{TOP - 10}" class="lbl in" style="--d:{t:.2f}s">{MONTHS[dt.month - 1]}</text>')
                last_col = col
            last_month = dt.month
        delay = t + col * 0.022 + row * 0.03
        cls = "hc best" if d is best and d["count"] else "hc"
        tip = f'{plural(d["count"], "contribution")} on {dt.strftime("%b %d, %Y")}'
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[d["level"]]}" '
            f'class="{cls}" style="animation-delay:{delay:.2f}s{",0s" if "best" in cls else ""}"><title>{esc(tip)}</title></rect>'
        )
    parts.extend(cells)
    cols = (len(days) + offset + 6) // 7
    grid_w = cols * STEP - GAP
    grid_h = 7 * STEP - GAP
    scan_start = t + cols * 0.022 + 0.6
    parts.append(
        f'<g clip-path="url(#grid)"><rect x="{LEFT - 40}" y="{TOP - 2}" width="40" height="{grid_h + 4}" '
        f'fill="url(#beam)" class="scan" style="animation-delay:{scan_start:.2f}s"/></g>'
    )

    longest, current = streaks(days)
    yb = TOP + grid_h + 34
    stats = (
        f'<tspan class="hi">{data["total"]:,}</tspan> contributions in the last year'
        f'<tspan class="m">  ·  </tspan>longest streak <tspan class="hi">{plural(longest, "day")}</tspan>'
        f'<tspan class="m">  ·  </tspan>current <tspan class="hi">{plural(current, "day")}</tspan>'
    )
    parts.append(f'<text x="28" y="{yb}" class="s up" style="--d:{scan_start - 0.3:.2f}s">{stats}</text>')
    lx = LEFT + grid_w - 5 * STEP - 34
    legend = [f'<text x="{lx - 8}" y="{yb}" class="lbl" text-anchor="end">Less</text>']
    for k, color in enumerate(PALETTE):
        legend.append(f'<rect x="{lx + k * STEP}" y="{yb - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
    legend.append(f'<text x="{lx + 5 * STEP + 4}" y="{yb}" class="lbl">More</text>')
    parts.append(f'<g class="up" style="--d:{scan_start - 0.3:.2f}s">{"".join(legend)}</g>')

    h = yb + 26
    defs = (
        f'<defs><clipPath id="grid"><rect x="{LEFT}" y="{TOP - 2}" width="{grid_w}" height="{grid_h + 4}"/></clipPath>'
        f'<linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}" stop-opacity="0"/>'
        f'<stop offset=".85" stop-color="{BLUE}" stop-opacity=".22"/><stop offset="1" stop-color="{BLUE}" stop-opacity=".5"/>'
        f'</linearGradient></defs>'
    )
    css = (
        f".lbl{{fill:{MUTED};font:11px {MONO}}}"
        ".hc{opacity:0;transform-box:fill-box;transform-origin:center;animation:cell .4s cubic-bezier(.2,.8,.2,1.4) forwards}"
        "@keyframes cell{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:none}}"
        ".best{animation:cell .4s cubic-bezier(.2,.8,.2,1.4) forwards,glow 1.6s ease-in-out infinite;"
        f"stroke:{TEXT};stroke-opacity:.0}}"
        "@keyframes glow{50%{stroke-opacity:.9;transform:scale(1.25)}}"
        f".scan{{opacity:0;animation:sweep 6s linear infinite}}"
        f"@keyframes sweep{{0%{{opacity:1;transform:translateX(0)}}90%{{opacity:1;transform:translateX({grid_w + 40}px)}}"
        f"100%{{opacity:0;transform:translateX({grid_w + 40}px)}}}}"
        "@media (prefers-reduced-motion:reduce){.hc,.best{animation:none;opacity:1}.scan{display:none}}"
    )
    label = (f'GitHub contributions of @{data["login"]}: {data["total"]} in the last year, '
             f'longest streak {longest} days, current streak {current} days')
    write(out, frame(W, h, label, defs + "\n".join(parts), css))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
