"""Shared helpers for the terminal-style profile panels (GitHub dark palette)."""
from html import escape

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
CW16 = 9.6   # advance width of one monospace char at 16px
CW15 = 9.0
CW13 = 7.8

BG = "#0d1117"
BORDER = "#30363d"
GREEN = "#3fb950"
BLUE = "#58a6ff"
TEXT = "#e6edf3"
SOFT = "#c9d1d9"
MUTED = "#8b949e"

BASE_CSS = f"""
.p{{fill:{GREEN};font:16px {MONO}}}
.c{{fill:{TEXT};font:16px {MONO}}}
.o{{fill:{SOFT};font:15px {MONO}}}
.s{{fill:{SOFT};font:13px {MONO}}}
.hi{{fill:{TEXT};font-weight:700}}
.a{{fill:{BLUE}}}
.g{{fill:{GREEN}}}
.m{{fill:{MUTED}}}
.ty{{clip-path:inset(0 100% 0 0);animation:ty var(--t) steps(var(--n),end) var(--d) forwards}}
@keyframes ty{{to{{clip-path:inset(0 0 0 0)}}}}
.cur{{fill:{TEXT};opacity:0;animation:on 0s var(--d) forwards,blink 1s steps(1) var(--d) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.in{{opacity:0;animation:on .3s ease-out var(--d) forwards}}
@keyframes on{{to{{opacity:1}}}}
.up{{opacity:0;animation:up .5s cubic-bezier(.2,.8,.2,1) var(--d) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.ty{{animation:none;clip-path:none}}.in,.up{{animation:none;opacity:1}}}}
"""

TYPE_PER_CHAR = 0.055


def esc(text):
    return escape(str(text), quote=True)


def frame(width, height, label, body, css="", pad=0.5):
    """Wrap body in a rounded terminal window. pad>0.5 leaves transparent margin."""
    w, h = width - 2 * pad, height - 2 * pad
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{esc(label)}">\n'
        f"<title>{esc(label)}</title>\n"
        f"<style>{BASE_CSS}{css}</style>\n"
        f'<rect x="{pad}" y="{pad}" width="{w}" height="{h}" rx="12" fill="{BG}" stroke="{BORDER}"/>\n'
        f"{body}\n</svg>\n"
    )


def command(x, y, prompt, cmd, delay, cls_prompt="p", cls_cmd="c", cw=CW16):
    """A prompt that fades in followed by a command that types itself.
    Returns (svg, time_when_typing_ends, x_after_command)."""
    cx = x + (len(prompt) + 1) * cw
    dur = max(len(cmd) * TYPE_PER_CHAR, 0.15)
    svg = (
        f'<text x="{x}" y="{y}" class="{cls_prompt} in" style="--d:{delay:.2f}s">{esc(prompt)}</text>'
        f'<text x="{cx:.1f}" y="{y}" class="{cls_cmd} ty" '
        f'style="--d:{delay:.2f}s;--t:{dur:.2f}s;--n:{max(len(cmd), 1)}">{esc(cmd)}</text>'
    )
    return svg, delay + dur, cx + len(cmd) * cw


def cursor(x, y, delay, h=16):
    return f'<rect x="{x:.1f}" y="{y - h + 3}" width="8" height="{h}" class="cur" style="--d:{delay:.2f}s"/>'


def write(path, svg):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("wrote", path)
