"""Shared theme for the profile panels: light/dark aware, window chrome, helpers."""
import json
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Helvetica,Arial,sans-serif"

# char advance of the monospace font, per px of font size
CH = 0.6

THEME = f"""
svg{{--bg:#0d1117;--panel:#161b22;--chrome:#11161d;--line:#30363d;--fg:#e6edf3;--soft:#c9d1d9;--muted:#8b949e;
--purple:#a78bfa;--cyan:#22d3ee;--amber:#fbbf24;--green:#4ade80;--pink:#f472b6}}
@media (prefers-color-scheme:light){{svg{{--bg:#ffffff;--panel:#f6f8fa;--chrome:#f3f4f6;--line:#d0d7de;--fg:#1f2328;
--soft:#32383f;--muted:#59636e;--purple:#7c3aed;--cyan:#0e7490;--amber:#b45309;--green:#15803d;--pink:#be185d}}}}
.mono{{font-family:{MONO}}}.sans{{font-family:{SANS}}}
.fg{{fill:var(--fg)}}.soft{{fill:var(--soft)}}.mu{{fill:var(--muted)}}.pu{{fill:var(--purple)}}.cy{{fill:var(--cyan)}}
.am{{fill:var(--amber)}}.gr{{fill:var(--green)}}.pk{{fill:var(--pink)}}.b{{font-weight:700}}
.ty{{clip-path:inset(0 100% 0 0);animation:ty var(--t) steps(var(--n),end) var(--d) forwards}}
@keyframes ty{{to{{clip-path:inset(0 0 0 0)}}}}
.cur{{fill:var(--fg);opacity:0;animation:on 0s var(--d) forwards,blink 1s steps(1) var(--d) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.in{{opacity:0;animation:on .35s ease-out var(--d) forwards}}
@keyframes on{{to{{opacity:1}}}}
.up{{opacity:0;animation:up .5s cubic-bezier(.2,.8,.2,1) var(--d) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.sl{{opacity:0;animation:sl .55s cubic-bezier(.2,.8,.2,1) var(--d) forwards}}
@keyframes sl{{from{{opacity:0;transform:translateX(-14px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.ty{{animation:none;clip-path:none}}.in,.up,.sl{{animation:none;opacity:1}}}}
"""


def esc(text):
    return escape(str(text), quote=True)


def icons():
    return json.load(open(os.path.join(ROOT, "data", "icons.json"), encoding="utf-8"))


def luminance(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def icon(key, x, y, size, ic=None):
    """Brand glyph from Simple Icons; near-black brands follow the text color."""
    ic = ic or icons()
    if key == "aws":
        return (f'<g transform="translate({x},{y})"><text x="{size / 2}" y="{size * .62}" text-anchor="middle" class="am mono b" '
                f'style="font-size:{size * .5:.1f}px">aws</text><path d="M{size * .2:.1f} {size * .78:.1f} q{size * .3:.1f} {size * .16:.1f} {size * .6:.1f} 0" '
                f'fill="none" stroke="var(--amber)" stroke-width="{size * .07:.2f}" stroke-linecap="round"/></g>')
    if key not in ic:
        return f'<circle cx="{x + size / 2}" cy="{y + size / 2}" r="{size * .22:.1f}" class="pu"/>'
    data = ic[key]
    fill = f'#{data["hex"]}' if luminance(data["hex"]) > 0.22 else "var(--fg)"
    return f'<g transform="translate({x},{y}) scale({size / 24:.4f})"><path d="{data["path"]}" fill="{fill}"/></g>'


def window(width, height, title, label, body, css="", pad=0.5):
    """A rounded editor window with a title bar showing a file name."""
    w, h = width - 2 * pad, height - 2 * pad
    chrome = (
        f'<path d="M{pad} {pad + 12} a12 12 0 0 1 12 -12 h{w - 24} a12 12 0 0 1 12 12 v22 h-{w} z" fill="var(--chrome)"/>'
        f'<line x1="{pad}" x2="{pad + w}" y1="{pad + 34}" y2="{pad + 34}" stroke="var(--line)"/>'
        + "".join(f'<circle cx="{pad + 20 + i * 18}" cy="{pad + 17}" r="5.5" fill="{c}"/>'
                  for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")))
        + f'<text x="{width / 2}" y="{pad + 22}" text-anchor="middle" class="mu mono" style="font-size:12px">{esc(title)}</text>'
    ) if title else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" aria-label="{esc(label)}">\n<title>{esc(label)}</title>\n<style>{THEME}{css}</style>\n'
        f'<rect x="{pad}" y="{pad}" width="{w}" height="{h}" rx="12" fill="var(--bg)" stroke="var(--line)"/>\n'
        f"{chrome}\n{body}\n</svg>\n"
    )


def typed(x, y, text, delay, size=15, cls="fg", per_char=0.045):
    """Text that types itself. Returns (svg, end_time)."""
    dur = max(len(text) * per_char, 0.15)
    return (f'<text x="{x}" y="{y}" class="{cls} mono ty" style="font-size:{size}px;--d:{delay:.2f}s;'
            f'--t:{dur:.2f}s;--n:{max(len(text), 1)}">{esc(text)}</text>'), delay + dur


def write(name, svg):
    path = os.path.join(ROOT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("wrote", name)
