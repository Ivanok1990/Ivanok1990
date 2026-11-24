"""Build the bento profile. Every row is an SVG in img/; the README stacks them.

    python scripts/bento.py [data/contributions.json]

Edit PROFILE below. The GitHub Action re-runs this daily so the contribution tile stays fresh.
"""
import json
import math
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from theme import MONO, ROOT, SANS, esc, icon, icons, write  # noqa: E402

PROFILE = {
    "login": "Ivanok1990",
    "name": "Omar Iván Quintanilla",
    "host": "omar@ivanok1990",
    "initials": "OQ",
    # neofetch-style facts: (key, value)
    "facts": [
        ("role", "Full Stack Dev @ Colibrí"),
        ("project", "Colibrí Searcher"),
        ("location", "Nicaragua · UTC−6"),
        ("stack", "NestJS · React · Postgres"),
        ("cloud", "AWS · Terraform · SQS"),
        ("edu", "B.S. Software Engineering '26"),
    ],
    "headline": "Full Stack Developer · Cloud & DevOps",
    "about": ["I build and maintain the portal our sales team", "uses to track leads, deals, and projects."],
    "status": "open to remote",
    "stack": [
        ["typescript", "javascript", "react", "nextdotjs", "vite", "tailwindcss",
         "shadcnui", "nodedotjs", "nestjs", "express"],
        ["postgresql", "mysql", "prisma", "sequelize", "aws", "terraform",
         "docker", "githubactions", "jest", "k6", "git"],
    ],
    "projects": [
        {"file": "quintanilla-airlines", "title": "Quintanilla Airlines",
         "desc": ["Full stack airline reservation platform:", "flight search, bookings and admin."],
         "tags": "React · Node.js · Express · MySQL · Sequelize", "glow": "#6d5dfc"},
        {"file": "attira-ai", "title": "Attira AI",
         "desc": ["AI-powered app that generates outfit", "ideas from photos of your clothes."],
         "tags": "AI · Computer vision · Web", "glow": "#e24bb0"},
    ],
    "journey": [
        ("Next", "Remote Full Stack role"),
        ("Aug 2026", "Full Stack Dev @ Colibrí"),
        ("Jun 2026", "Postgrad · Management & Leadership"),
        ("2026", "B.S. Software Engineering · Keiser"),
        ("Before", "AI Engineer @ OneClick · AI QA @ Outlier"),
    ],
    "certs": ["GitHub Foundations"],
    "learning": "AWS Cloud Practitioner",
    "awards": [("3×", "Outstanding Club"), ("1×", "Outstanding Activity")],
    "awards_from": "Keiser Software Club",
    "contacts": [
        ("portfolio", "Portfolio", "omarquintanilla.com", "#6d5dfc"),
        ("linkedin", "LinkedIn", "omar-quintanilla", "#0a66c2"),
        ("email", "Email", "omarrayo988@gmail.com", "#18a3b8"),
    ],
}

M, G = 6, 12            # outer margin, gap between tiles
W = 860
COL = (W - 2 * M - 3 * G) / 4   # 203

CSS = f"""
svg{{--tile:#11151c;--edge:#232a35;--chip:#171c25;--fg:#f0f3f6;--soft:#c4cad3;--muted:#7d8794;--accent:#8f9bff;
--green:#3ee07c;--cyan:#18c2d8;--violet:#6d5dfc;--pink:#e24bb0;--amber:#fbbf24;
--h0:#1a2029;--h1:#2e2a6e;--h2:#4b40c9;--h3:#6d5dfc;--h4:#18c2d8;--blob:.55}}
@media (prefers-color-scheme:light){{svg{{--tile:#f6f8fa;--edge:#d0d7de;--chip:#ffffff;--fg:#1f2328;--soft:#3d444d;
--muted:#59636e;--accent:#5b4bdb;--green:#1a7f37;--cyan:#0e8ea3;--amber:#b45309;
--h0:#e9ecf0;--h1:#d6d1fe;--h2:#a79bfb;--h3:#6d5dfc;--h4:#0e9fb5;--blob:.28}}}}
.t{{fill:var(--tile);stroke:var(--edge)}}
.fg{{fill:var(--fg)}}.soft{{fill:var(--soft)}}.mu{{fill:var(--muted)}}.ac{{fill:var(--accent)}}.gr{{fill:var(--green)}}
.cy{{fill:var(--cyan)}}.vi{{fill:var(--violet)}}.pk{{fill:var(--pink)}}.am{{fill:var(--amber)}}
.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}.b{{font-weight:700}}.xb{{font-weight:800}}
.lbl{{fill:var(--muted);font:600 11px {SANS};letter-spacing:1.6px}}
.up{{opacity:0;animation:up .6s cubic-bezier(.2,.8,.2,1) var(--d) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
.in{{opacity:0;animation:in .4s ease-out var(--d) forwards}}@keyframes in{{to{{opacity:1}}}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.4;transform:scale(.7)}}}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 2s ease-out infinite}}
@keyframes ping{{from{{opacity:.9;transform:scale(.5)}}to{{opacity:0;transform:scale(2.2)}}}}
@media (prefers-reduced-motion:reduce){{.up,.in{{animation:none;opacity:1}}}}
"""


def svg(width, height, label, body, css="", defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
            f'role="img" aria-label="{esc(label)}">\n<title>{esc(label)}</title>\n<style>{CSS}{css}</style>\n'
            f'{defs}\n{body}\n</svg>\n')


def tile(x, y, w, h, delay=0.0, inner=""):
    return (f'<g class="up" style="--d:{delay:.2f}s"><rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" '
            f'rx="20" class="t"/>{inner}</g>')


def label(x, y, text):
    return f'<text x="{x}" y="{y}" class="lbl">{esc(text.upper())}</text>'


def T(x, y, text, cls, size, extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" style="font-size:{size}px{extra}">{esc(text)}</text>'


# --------------------------------------------------------------------------- contributions helpers
def load_days(path):
    data = json.load(open(path, encoding="utf-8"))
    return data, data["days"]


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    tail = days[:-1] if days and not days[-1]["count"] else days
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1
    return longest, current


# --------------------------------------------------------------------------- row 1: neofetch + contributions
PIXEL_FONT = {  # 5x7
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
}


def pixel_logo(x, y, text, px=8):
    cols = []
    for ch in text:
        cols.extend(zip(*PIXEL_FONT[ch]))
        cols.append(("0",) * 7)
    cols = cols[:-1]
    n = len(cols)
    out = []
    for c, col in enumerate(cols):
        for r, bit in enumerate(col):
            if bit == "1":
                out.append(f'<rect x="{x + c * px}" y="{y + r * px}" width="{px - 1}" height="{px - 1}" rx="1.5" '
                           f'fill="url(#logo)" class="px" style="animation-delay:{.5 + (c + r) * .035:.2f}s"/>')
    return "".join(out), n * px, 7 * px


def row_top(data, days):
    p = PROFILE
    th = 328
    H = M * 2 + th
    tw = 2 * COL + G
    out = []

    # ---- neofetch terminal
    x, y = M, M
    out.append(tile(x, y, tw, th, .05))
    prompt = p["host"] + " ~ $"
    out.append(f'<text x="{x + 24}" y="{y + 40}" class="gr mono" style="font-size:14px">{esc(prompt)}</text>')
    cx = x + 24 + (len(prompt) + 1) * 8.4
    out.append(f'<text x="{cx:.1f}" y="{y + 40}" class="fg mono ty" style="font-size:14px;--d:.2s;--t:.4s;--n:8">neofetch</text>')
    logo, lw, lh = pixel_logo(x + 24, y + 74, p["initials"], px=6)
    out.append(logo)
    out.append(f'<text x="{x + 24 + lw / 2}" y="{y + 74 + lh + 22}" text-anchor="middle" class="mu mono in" '
               f'style="font-size:11px;--d:1s">{esc("@" + p["login"])}</text>')
    ix = x + 24 + lw + 26
    fs, lh2, kw = 12, 21, 10 * 7.2
    rows = [f'<text x="{ix}" y="{y + 80}" class="ac mono b" style="font-size:13.5px">{esc(p["host"])}</text>',
            f'<line x1="{ix}" x2="{ix + len(p["host"]) * 8.1:.0f}" y1="{y + 89}" y2="{y + 89}" stroke="var(--edge)" stroke-width="1.5"/>']
    for i, (k, v) in enumerate(p["facts"]):
        yy = y + 110 + i * lh2
        rows.append(f'<text x="{ix}" y="{yy}" class="ac mono" style="font-size:{fs}px">{esc(k)}</text>'
                    f'<text x="{ix + kw:.0f}" y="{yy}" class="fg mono" style="font-size:{fs}px">{esc(v)}</text>')
    yy = y + 110 + len(p["facts"]) * lh2
    rows.append(f'<text x="{ix}" y="{yy}" class="ac mono" style="font-size:{fs}px">status</text>'
                f'<circle cx="{ix + kw + 5:.0f}" cy="{yy - 4}" r="8" fill="var(--green)" opacity=".3" class="ping"/>'
                f'<circle cx="{ix + kw + 5:.0f}" cy="{yy - 4}" r="4" fill="var(--green)"/>'
                f'<text x="{ix + kw + 16:.0f}" y="{yy}" class="gr mono b" style="font-size:{fs}px">{esc(p["status"])}</text>')
    out.append(f'<g class="up" style="--d:.7s">{"".join(rows)}</g>')
    palette = ["#1a2029", "#e5534b", "#3ee07c", "#fbbf24", "#6d5dfc", "#e24bb0", "#18c2d8", "#f0f3f6"]
    by = y + 74 + lh + 38
    out.append("".join(f'<rect x="{x + 24 + (i % 4) * (lw / 4):.1f}" y="{by + (i // 4) * 12}" width="{lw / 4 - 3:.1f}" '
                       f'height="9" rx="2" fill="{c}" class="in" style="--d:{1.3 + i * .06:.2f}s"/>'
                       for i, c in enumerate(palette)))
    out.append(f'<line x1="{x + 24}" x2="{x + tw - 24}" y1="{yy + 20}" y2="{yy + 20}" stroke="var(--edge)" class="in" style="--d:1.4s"/>')
    out.append(f'<g class="up" style="--d:1.5s">' + "".join(
        T(x + 24, yy + 50 + i * 22, line, "fg sans", 15) for i, line in enumerate(p["about"])) + "</g>")

    # ---- contributions
    hx = M + tw + G
    nh = 92
    out.append(tile(hx, M, tw, nh, .1,
                    f'<text x="{hx + 24}" y="{M + 44}" class="fg sans xb" style="font-size:27px;letter-spacing:-.6px">{esc(p["name"])}</text>'
                    + T(hx + 24, M + 68, p["headline"], "ac mono", 13)))
    hy = M + nh + G
    ch = th - nh - G
    out.append(tile(hx, hy, tw, ch, .15))
    total = data["total"]
    longest, current = streaks(days)
    best = max(days, key=lambda d: d["count"])
    first = date.fromisoformat(days[0]["date"])
    off = (first.weekday() + 1) % 7
    cols = (len(days) + off + 6) // 7
    step = (tw - 48) / cols
    cell = step * .78
    gx, gy = hx + 24, hy + 94
    cells = []
    for i, d in enumerate(days):
        idx = i + off
        c, r = idx // 7, idx % 7
        cls = f"h{d['level']} cell" + (" best" if d is best and d["count"] else "")
        cells.append(f'<rect x="{gx + c * step:.2f}" y="{gy + r * step:.2f}" width="{cell:.2f}" height="{cell:.2f}" rx="1.6" '
                     f'class="{cls}" style="animation-delay:{.5 + c * .018 + r * .03:.2f}s"><title>{d["count"]} on {d["date"]}</title></rect>')
    grid_w, grid_h = cols * step, 7 * step
    out.append(label(hx + 24, hy + 34, "Contributions · last 12 months"))
    num = f"{total:,}"
    out.append(f'<text x="{hx + 24}" y="{hy + 76}" class="fg sans xb up" style="font-size:38px;--d:.3s">{num}</text>')
    out.append(T(hx + 24 + sum(11 if ch == "," else 24 for ch in num) + 10, hy + 74, "contributions", "mu sans up", 14, ";--d:.4s"))
    out += cells
    out.append(f'<g clip-path="url(#gridclip)"><rect x="{gx - 50}" y="{gy - 2}" width="50" height="{grid_h + 4}" '
               f'fill="url(#beam)" class="scan"/></g>')
    # three stats
    best_txt = date.fromisoformat(best["date"]).strftime("%b %d") if best["count"] else "—"
    stats = [(f"{longest}d", "longest streak"), (f"{current}d", "current streak"),
             (f"{best['count']}", f"best day · {best_txt}")]
    sy = gy + grid_h + 36
    sw = (tw - 48) / 3
    for i, (v, k) in enumerate(stats):
        out.append(f'<g class="up" style="--d:{1.2 + i * .1:.2f}s">'
                   + T(hx + 24 + i * sw, sy, v, "fg sans xb", 22) + T(hx + 24 + i * sw, sy + 19, k, "mu sans", 12) + "</g>")
    defs = (
        f'<defs><clipPath id="gridclip"><rect x="{gx}" y="{gy - 2}" width="{grid_w}" height="{grid_h + 4}"/></clipPath>'
        '<linearGradient id="logo" gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="80" y2="140">'
        '<stop offset="0" stop-color="#8f9bff"/><stop offset="1" stop-color="#18c2d8"/></linearGradient>'
        '<linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="#8f9bff" stop-opacity="0"/>'
        '<stop offset=".8" stop-color="#8f9bff" stop-opacity=".18"/><stop offset="1" stop-color="#18c2d8" stop-opacity=".55"/></linearGradient>'
        '</defs>')
    css = (
        "".join(f".h{i}{{fill:var(--h{i})}}" for i in range(5))
        + ".ty{clip-path:inset(0 100% 0 0);animation:ty var(--t) steps(var(--n),end) var(--d) forwards}"
          "@keyframes ty{to{clip-path:inset(0 0 0 0)}}"
          ".cur{fill:var(--fg);opacity:0;animation:in 0s var(--d) forwards,blink 1s steps(1) var(--d) infinite}"
          "@keyframes blink{50%{opacity:0}}"
          ".px{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .35s cubic-bezier(.2,.8,.2,1.5) forwards}"
          ".cell{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.2,.8,.2,1.5) forwards}"
          "@keyframes pop{from{opacity:0;transform:scale(.1)}to{opacity:1;transform:none}}"
          ".best{animation:pop .45s cubic-bezier(.2,.8,.2,1.5) forwards,beat 1.6s ease-in-out 2.4s infinite;stroke:var(--fg);stroke-opacity:0}"
          "@keyframes beat{50%{transform:scale(1.5);stroke-opacity:.9}}"
        f".scan{{opacity:0;animation:sweep 5s linear 1.8s infinite}}"
        f"@keyframes sweep{{0%{{opacity:1;transform:translateX(0)}}92%{{opacity:1;transform:translateX({grid_w + 50:.0f}px)}}"
        f"100%{{opacity:0;transform:translateX({grid_w + 50:.0f}px)}}}}"
          ".bar{fill:var(--h2);opacity:0;transform-box:fill-box;transform-origin:bottom;animation:grow .6s cubic-bezier(.2,.8,.2,1) forwards}"
          ".bar.hi{fill:var(--h4)}"
          "@keyframes grow{from{opacity:0;transform:scaleY(0)}to{opacity:1;transform:none}}"
          "@media (prefers-reduced-motion:reduce){.cell,.best,.px,.bar{animation:none;opacity:1}.scan{display:none}"
          ".ty{animation:none;clip-path:none}}"
    )
    lab = (f'neofetch: {p["name"]} (@{p["login"]}); ' + "; ".join(f"{k}: {v}" for k, v in p["facts"])
           + f'; status: {p["status"]}. {total} contributions in the last 12 months, longest streak {longest} days, '
             f'current streak {current} days. {" ".join(p["about"])}')
    write("img/top.svg", svg(W, H, lab, "\n".join(out), css, defs))


# --------------------------------------------------------------------------- row 2: stack (icon tiles)
def row_stack():
    ic = icons()
    pitch, sz = 72, 50
    H = M * 2 + 236
    out = [f'<rect x="{M + .5}" y="{M + .5}" width="{W - 2 * M - 1}" height="{H - 2 * M - 1}" rx="20" class="t"/>',
           label(M + 24, M + 34, "Stack")]
    names, k = [], 0
    for r, row in enumerate(PROFILE["stack"]):
        x0 = (W - len(row) * pitch) / 2 + (pitch - sz) / 2
        y = M + 58 + r * 88
        for c, key in enumerate(row):
            x = x0 + c * pitch
            d1, d2 = .3 + k * .05, 1.6 + k * .12
            k += 1
            name = "AWS" if key == "aws" else ("Actions" if key == "githubactions" else ic[key]["label"])
            names.append("GitHub Actions" if key == "githubactions" else name)
            out.append(
                f'<g transform="translate({x:.1f},{y})"><g class="ic" style="animation-delay:{d1:.2f}s,{d2:.2f}s">'
                f'<title>{esc(names[-1])}</title>'
                f'<rect x=".5" y=".5" width="{sz - 1}" height="{sz - 1}" rx="13" fill="var(--chip)" stroke="var(--edge)"/>'
                f'{icon(key, 11, 11, 28, ic)}</g>'
                f'<text x="{sz / 2}" y="{sz + 17}" text-anchor="middle" class="mu mono in" style="font-size:11px;--d:{d1 + .2:.2f}s">{esc(name)}</text></g>')
    css = (".ic{opacity:0;transform-box:fill-box;transform-origin:center;"
           "animation:icpop .45s cubic-bezier(.2,.8,.2,1.3) forwards,bob 5s ease-in-out infinite}"
           "@keyframes icpop{from{opacity:0;transform:translateY(10px) scale(.6)}to{opacity:1;transform:none}}"
           "@keyframes bob{0%,14%,100%{transform:none}7%{transform:translateY(-6px)}}"
           "@media (prefers-reduced-motion:reduce){.ic{animation:none;opacity:1}}")
    write("img/stack.svg", svg(W, H, "Stack: " + ", ".join(names), "\n".join(out), css))


# --------------------------------------------------------------------------- row 3: architecture
def node(x, y, w, h, title, sub, glyph, delay):
    return (f'<g class="up" style="--d:{delay:.2f}s">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="var(--chip)" stroke="var(--edge)"/>{glyph}'
            f'<text x="{x + 38}" y="{y + 24}" class="fg sans b" style="font-size:12.5px">{esc(title)}</text>'
            f'<text x="{x + 38}" y="{y + 42}" class="mu mono" style="font-size:11px">{esc(sub)}</text></g>')


def row_architecture():
    ic = icons()
    H = M * 2 + 330
    out = [f'<rect x="{M + .5}" y="{M + .5}" width="{W - 2 * M - 1}" height="{H - 2 * M - 1}" rx="20" class="t"/>',
           label(M + 24, M + 34, "How I ship")]
    rx, ry, rw, rh = 196, 60, 636, 232
    out.append(f'<g class="in" style="--d:.1s"><rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="14" fill="none" '
               f'stroke="var(--amber)" stroke-opacity=".75" stroke-dasharray="6 6"/>'
               f'{icon("aws", rx + 12, ry + 6, 30, ic)}'
               f'<text x="{rx + 48}" y="{ry + 26}" class="am mono" style="font-size:12px">region · vpc</text>'
               f'{icon("terraform", rx + rw - 196, ry + 12, 16, ic)}'
               f'<text x="{rx + rw - 174}" y="{ry + 25}" class="mu mono" style="font-size:12px">managed by terraform</text></g>')
    nw, nh, row_y, db_y = 132, 56, 108, 218
    xs = {"client": 30, "lb": 212, "api": 370, "sqs": 528, "wk": 684}
    queue = "".join(f'<rect x="{xs["sqs"] + 12 + i * 6}" y="{row_y + 18}" width="4" height="20" rx="1.5" class="pk" '
                    f'opacity="{.45 + i * .18:.2f}"/>' for i in range(4))
    lb = (f'<g fill="none" stroke="var(--cyan)" stroke-width="2" stroke-linecap="round"><path d="M{xs["lb"] + 12} {row_y + 28} h6 '
          f'M{xs["lb"] + 18} {row_y + 28} l10 -8 M{xs["lb"] + 18} {row_y + 28} l10 8 M{xs["lb"] + 18} {row_y + 28} h10"/></g>')
    gear = (f'<g transform="translate({xs["wk"] + 22},{row_y + 28})"><g class="spin"><circle r="7" fill="none" '
            f'stroke="var(--violet)" stroke-width="3" stroke-dasharray="3.2 2.3"/><circle r="3" class="vi"/></g></g>')
    out.append('<g fill="none" stroke="var(--edge)" stroke-width="2">'
               f'<path id="e1" d="M{xs["client"] + nw} {row_y + 28} H{xs["lb"]}"/>'
               f'<path id="e2" d="M{xs["lb"] + nw} {row_y + 28} H{xs["api"]}"/>'
               f'<path id="e3" d="M{xs["api"] + nw} {row_y + 28} H{xs["sqs"]}"/>'
               f'<path id="e4" d="M{xs["sqs"] + nw} {row_y + 28} H{xs["wk"]}"/>'
               f'<path id="e5" d="M{xs["api"] + nw / 2} {row_y + nh} V{db_y}"/>'
               f'<path id="e6" d="M{xs["wk"] + nw / 2} {row_y + nh + 8} V{db_y + 28} H{xs["api"] + nw}"/></g>')
    t = .3
    out.append(node(xs["client"], row_y, nw, nh, "Web app", "react/next", icon("react", xs["client"] + 10, row_y + 16, 22, ic), t))
    out.append(node(xs["lb"], row_y, nw, nh, "Load balancer", "rate limit", lb, t + .15))
    out.append(node(xs["api"], row_y, nw, nh, "REST API", "nestjs/prisma", icon("nestjs", xs["api"] + 10, row_y + 16, 22, ic), t + .3))
    out.append(node(xs["sqs"], row_y, nw, nh, "SQS queue", "jobs/retries", queue, t + .45))
    for k in (2, 1):
        out.append(f'<rect x="{xs["wk"] + k * 5}" y="{row_y + k * 5}" width="{nw}" height="{nh}" rx="12" fill="var(--chip)" '
                   f'stroke="var(--edge)" class="up" style="--d:{t + .6:.2f}s"/>')
    out.append(node(xs["wk"], row_y, nw, nh, "Workers", "autoscaled", gear, t + .6))
    out.append(node(xs["api"], db_y, nw, nh, "PostgreSQL", "primary db", icon("postgresql", xs["api"] + 10, db_y + 16, 22, ic), t + .75))
    for path, cls, begin in [("e1", "cy", 0), ("e2", "cy", .5), ("e3", "pk", 1), ("e4", "pk", 1.5), ("e5", "cy", .8),
                             ("e6", "vi", 2.1), ("e1", "cy", 1.6), ("e3", "pk", 2.6)]:
        out.append(f'<circle r="4.5" class="{cls}" opacity="0"><animateMotion dur="1.6s" begin="{1.6 + begin:.1f}s" '
                   f'repeatCount="indefinite"><mpath href="#{path}"/></animateMotion>'
                   f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="1.6s" '
                   f'begin="{1.6 + begin:.1f}s" repeatCount="indefinite"/></circle>')
    out.append(f'<g class="up" style="--d:1.2s">{icon("githubactions", 30, db_y + 14, 22, ic)}'
               f'<text x="60" y="{db_y + 24}" class="fg sans b" style="font-size:13px">CI/CD</text>'
               f'<text x="60" y="{db_y + 42}" class="mu mono" style="font-size:11px">github actions</text>'
               f'<path d="M150 {db_y + 28} H{rx - 6}" stroke="var(--green)" stroke-width="2" stroke-dasharray="4 5" '
               f'fill="none" class="flow"/></g>')
    out.append(f'<text x="{M + 24}" y="{H - M - 20}" class="sans up" style="font-size:13px;--d:1.4s">'
               f'<tspan class="fg b">Event-driven backends on AWS</tspan><tspan class="mu"> — provisioned with Terraform, '
               f'shipped with GitHub Actions, tested with Jest &amp; k6.</tspan></text>')
    css = (".spin{animation:spin 3s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}"
           ".flow{animation:flow 1s linear infinite}@keyframes flow{to{stroke-dashoffset:-18}}")
    lab = ("How I ship: web app (React, Next.js) to a rate-limited load balancer, NestJS REST API with Prisma and "
           "PostgreSQL, SQS queue and autoscaled workers on AWS, managed by Terraform, CI/CD with GitHub Actions")
    write("img/architecture.svg", svg(W, H, lab, "\n".join(out), css))


# --------------------------------------------------------------------------- row 4: projects
def project(pr, delay):
    w, h = W / 2, 176
    first = pr is PROFILE["projects"][0]
    x, y = (M if first else G / 2), M
    tw, th = w - x - (G / 2 if first else M), h - 2 * M
    gid = "g" + pr["file"].replace("-", "")
    out = [f'<defs><clipPath id="c{gid}"><rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="20"/></clipPath>'
           f'<radialGradient id="{gid}"><stop offset="0" stop-color="{pr["glow"]}"/><stop offset="1" stop-color="{pr["glow"]}" stop-opacity="0"/></radialGradient></defs>',
           f'<g class="up" style="--d:{delay:.2f}s"><rect x="{x + .5}" y="{y + .5}" width="{tw - 1}" height="{th - 1}" rx="20" class="t"/>'
           f'<g clip-path="url(#c{gid})" style="opacity:var(--blob)"><circle cx="{x + tw - 30}" cy="{y + 20}" r="110" fill="url(#{gid})" class="glow"/></g>',
           label(x + 24, y + 34, "Project"),
           T(x + 24, y + 64, pr["title"], "fg sans xb", 20),
           f'<path d="M{x + tw - 38} {y + 38} l12 -12 M{x + tw - 35} {y + 26} h9 v9" fill="none" stroke="var(--muted)" '
           f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="nudge"/>',
           *(T(x + 24, y + 92 + i * 20, l, "soft sans", 13.5) for i, l in enumerate(pr["desc"])),
           T(x + 24, y + 146, pr["tags"], "ac mono", 12),
           "</g>"]
    css = ".nudge{animation:nudge 2.4s ease-in-out infinite}@keyframes nudge{50%{transform:translate(2px,-2px)}}" \
          ".glow{transform-box:fill-box;transform-origin:center;animation:glow 6s ease-in-out infinite alternate}" \
          "@keyframes glow{to{transform:scale(1.25) translate(-20px,10px)}}"
    write(f"img/project-{pr['file']}.svg", svg(w, h, f'{pr["title"]}: {" ".join(pr["desc"])} ({pr["tags"]})', "\n".join(out), css))


# --------------------------------------------------------------------------- row 5: journey, certs, awards
def row_bottom():
    p = PROFILE
    H = M * 2 + 236
    xs = [M + i * (COL + G) for i in range(4)]
    th = H - 2 * M
    out = []
    jw = 2 * COL + G
    rows = []
    for i, (when, what) in enumerate(p["journey"]):
        y = M + 66 + i * 34
        nxt = i == 0
        rows.append(f'<g class="sl" style="--d:{.4 + i * .1:.2f}s">'
                    + T(xs[0] + 24, y, when, ("gr b" if nxt else "mu") + " sans", 13)
                    + T(xs[0] + 100, y, what, "fg sans" + (" b" if nxt else ""), 13.5)
                    + (f'<line x1="{xs[0] + 24}" x2="{xs[0] + jw - 24}" y1="{y + 13}" y2="{y + 13}" stroke="var(--edge)"/>'
                       if i < len(p["journey"]) - 1 else "")
                    + "</g>")
    out.append(tile(xs[0], M, jw, th, .1, label(xs[0] + 24, M + 34, "Journey") + "".join(rows)))

    cx = xs[2]
    # GitHub Foundations badge: hexagon emblem + name
    bx, by, r = cx + 56, M + 100, 34
    hexagon = " ".join(f"{bx + r * math.cos(math.radians(a)):.1f},{by + r * math.sin(math.radians(a)):.1f}"
                       for a in range(-90, 270, 60))
    inner = " ".join(f"{bx + (r - 5) * math.cos(math.radians(a)):.1f},{by + (r - 5) * math.sin(math.radians(a)):.1f}"
                     for a in range(-90, 270, 60))
    badge = (f'<g class="badge" style="--d:.5s"><polygon points="{hexagon}" fill="url(#bdg)"/>'
             f'<polygon points="{inner}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="1.2"/>'
             f'{icon("github", bx - 14, by - 18, 28)}'.replace('fill="var(--fg)"', 'fill="#fff"')
             + f'<text x="{bx}" y="{by + 24}" text-anchor="middle" class="mono b" style="font-size:6px;fill:#fff;letter-spacing:.5px">FOUNDATIONS</text>'
             f'<g clip-path="url(#bclip)"><rect x="{bx - r - 30}" y="{by - r}" width="18" height="{2 * r}" fill="#fff" '
             f'opacity=".35" transform="skewX(-20)" class="shine"/></g></g>')
    ly = M + 162
    out.append(tile(cx, M, COL, th, .2,
                    label(cx + 24, M + 34, "Certifications") + badge
                    + f'<g class="up" style="--d:.7s">'
                    + T(bx + r + 14, by - 8, "GitHub", "fg sans b", 14)
                    + T(bx + r + 14, by + 10, "Foundations", "fg sans b", 14)
                    + f'<path d="M{bx + r + 15} {by + 25} l3 3 l6 -7" fill="none" stroke="var(--green)" stroke-width="2" '
                      f'stroke-linecap="round" stroke-linejoin="round"/>'
                    + T(bx + r + 28, by + 29, "certified", "gr sans b", 11.5) + "</g>"
                    + T(cx + 24, ly, "Learning:", "mu sans", 12)
                    + T(cx + 24, ly + 18, p["learning"], "soft sans b", 12.5)
                    + f'<rect x="{cx + 24}" y="{ly + 30}" width="{COL - 48}" height="6" rx="3" fill="var(--edge)"/>'
                    + f'<rect x="{cx + 24}" y="{ly + 30}" width="{(COL - 48) * .35:.0f}" height="6" rx="3" fill="url(#prog)" class="prog"/>'))
    ax = xs[3]
    awards = "".join(
        f'<g class="up" style="--d:{.5 + i * .2:.2f}s">'
        f'<text x="{ax + 24}" y="{M + 88 + i * 64}" class="fg sans xb" style="font-size:34px">{esc(n)}</text>'
        + T(ax + 24, M + 110 + i * 64, what, "soft sans b", 13.5) + "</g>"
        for i, (n, what) in enumerate(p["awards"]))
    out.append(tile(ax, M, COL, th, .3,
                    label(ax + 24, M + 34, "Awards") + awards
                    + T(ax + 24, M + th - 22, p["awards_from"], "mu sans", 12)
                    + "".join(f'<path d="M{ax + 128 + dx} {M + 50 + dy} l3 7 l7 3 l-7 3 l-3 7 l-3 -7 l-7 -3 l7 -3 z" '
                              f'class="am spark" style="animation-delay:{.8 + j * .5:.1f}s"/>'
                              for j, (dx, dy) in enumerate(((0, 0), (24, 14), (4, 26))))))
    defs = ('<defs><linearGradient id="prog" x1="0" x2="1"><stop offset="0" stop-color="#6d5dfc"/>'
            '<stop offset="1" stop-color="#18c2d8"/></linearGradient>'
            '<linearGradient id="bdg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b3137"/>'
            '<stop offset=".55" stop-color="#6e40c9"/><stop offset="1" stop-color="#2f81f7"/></linearGradient>'
            f'<clipPath id="bclip"><polygon points="{hexagon}"/></clipPath></defs>')
    css = (".sl{opacity:0;animation:sl .55s cubic-bezier(.2,.8,.2,1) var(--d) forwards}"
           "@keyframes sl{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:none}}"
           f".prog{{animation:prog 2.4s ease-in-out infinite alternate}}"
           f"@keyframes prog{{from{{transform:translateX(0)}}to{{transform:translateX({(COL - 48) * .65:.0f}px)}}}}"
           ".pop{transform-box:fill-box;transform-origin:left bottom;animation:apop .6s cubic-bezier(.2,.8,.2,1.6) .5s both}"
           "@keyframes apop{from{transform:scale(.3);opacity:0}to{transform:none;opacity:1}}"
           ".spark{opacity:0;transform-box:fill-box;transform-origin:center;animation:spark 2.4s ease-in-out infinite}"
           "@keyframes spark{0%,100%{opacity:0;transform:scale(.3)}50%{opacity:1;transform:scale(1) rotate(45deg)}}"
           ".badge{opacity:0;transform-box:fill-box;transform-origin:center;animation:bpop .7s cubic-bezier(.2,.8,.2,1.4) var(--d) forwards}"
           "@keyframes bpop{from{opacity:0;transform:scale(.4) rotate(-30deg)}to{opacity:1;transform:none}}"
           ".shine{animation:shine 3.5s ease-in-out 1.4s infinite}"
           "@keyframes shine{0%{transform:skewX(-20deg) translateX(0)}40%,100%{transform:skewX(-20deg) translateX(110px)}}"
           "@media (prefers-reduced-motion:reduce){.sl,.pop,.badge{animation:none;opacity:1}.prog,.spark,.shine{animation:none}}")
    lab = ("Journey: " + "; ".join(f"{a}: {b}" for a, b in p["journey"]) + ". Certifications: " + ", ".join(p["certs"])
           + f". Learning {p['learning']}. Awards ({p['awards_from']}): " + ", ".join(f"{n} {w}" for n, w in p["awards"]) + ".")
    write("img/bottom.svg", svg(W, H, lab, "\n".join(out), css, defs))


# --------------------------------------------------------------------------- row 6: contacts
def contact(i, file, name, value, color):
    w, h = round(W / 3, 2), 96
    x = M if i == 0 else G / 2
    tw = w - x - (M if i == 2 else G / 2)
    th = h - 2 * M
    size = 14 if len(value) * 7.6 < tw - 80 else 12.5
    out = [tile(x, M, tw, th, .1 + i * .1,
                label(x + 22, M + 33, name)
                + T(x + 22, M + 60, value, "fg sans b", size)
                + f'<circle cx="{x + tw - 32}" cy="{M + th / 2}" r="15" fill="{color}"/>'
                + f'<path d="M{x + tw - 37} {M + th / 2 + 5} l10 -10 M{x + tw - 35} {M + th / 2 - 5} h8 v8" fill="none" '
                  f'stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="nudge"/>')]
    css = ".nudge{animation:nudge 2.4s ease-in-out infinite}@keyframes nudge{50%{transform:translate(2px,-2px)}}"
    write(f"img/contact-{file}.svg", svg(w, h, f"{name}: {value}", "\n".join(out), css))


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "contributions.json")
    data, days = load_days(src)
    row_top(data, days)
    row_stack()
    row_architecture()
    for i, pr in enumerate(PROFILE["projects"]):
        project(pr, .1 + i * .1)
    row_bottom()
    for i, c in enumerate(PROFILE["contacts"]):
        contact(i, *c)
