"""Build the static profile panels. Edit PROFILE below, then run:

    python scripts/build_profile.py

Writes terminal.svg, stack.svg, now.svg, links/*.svg and projects/*.svg.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from term import (BLUE, BORDER, CW13, CW15, CW16, MONO, MUTED, TEXT,  # noqa: E402
                  command, cursor, esc, frame, write)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Everything personal lives here.
# ---------------------------------------------------------------------------
PROFILE = {
    "prompt": "omar@github ~ $",
    "name": "Omar Iván Quintanilla",
    "login": "Ivanok1990",
    "role": "Full Stack Developer",
    "focus": "Cloud & DevOps",
    "location": "Managua, Nicaragua · UTC-6 · open to remote",
    "doing": "Building internal platforms @ Colibrí with NestJS, React, AWS & Terraform",
    "status": "available for remote full stack roles",
    "links": [
        # (file name, command shown, value shown)
        ("portfolio", "open portfolio", "omarquintanilla.netlify.app"),
        ("linkedin", "open linkedin", "in/omar-quintanilla-09950420b"),
        ("email", "mail me", "omarrayo988@gmail.com"),
    ],
    # icon keys from data/icons.json, plus "aws" (drawn as text, no logo)
    "stack": [
        ["typescript", "javascript", "react", "nextdotjs", "vite", "tailwindcss",
         "shadcnui", "nodedotjs", "nestjs", "express"],
        ["postgresql", "mysql", "prisma", "sequelize", "aws", "terraform",
         "docker", "githubactions", "jest", "k6", "git"],
    ],
    "projects": [
        {
            "file": "quintanilla-airlines",
            "path": "~/projects/quintanilla-airlines",
            "title": "Quintanilla Airlines",
            "desc": ["Full stack airline reservation platform:",
                     "flight search, bookings and admin."],
            "tags": "React · Node.js · Express · MySQL · Sequelize",
        },
        {
            "file": "attira-ai",
            "path": "~/projects/attira-ai",
            "title": "Attira AI",
            "desc": ["AI-powered app that generates outfit",
                     "ideas from photos of your clothes."],
            "tags": "AI · Computer vision · Web",
        },
    ],
    "now": [
        ("working", "Full Stack Dev @ Colibrí · REST APIs, workers, SQS, Terraform"),
        ("studying", "Postgrad in Management & Leadership · Keiser University"),
        ("learning", "AWS Cloud Practitioner · cloud architecture · CI/CD"),
        ("certs", "GitHub Foundations · ISTQB CTFL · Terraform Associate"),
        ("degree", "B.S. Software Engineering · Keiser University (2025)"),
        ("looking", "remote Full Stack roles · cloud · devops"),
    ],
}


# ---------------------------------------------------------------------------
def terminal():
    p = PROFILE
    x, w = 28, 860
    parts = []
    svg, t, _ = command(x, 40, p["prompt"], "whoami", 0.2)
    parts.append(svg)
    t += 0.25
    lines = [
        f'<tspan class="hi">{esc(p["name"])}</tspan><tspan class="m"> (@{esc(p["login"])})</tspan>',
        f'<tspan class="a">{esc(p["role"])}</tspan><tspan class="m"> · </tspan>{esc(p["focus"])}',
        f'<tspan class="m">{esc(p["location"])}</tspan>',
        esc(p["doing"]),
    ]
    for i, line in enumerate(lines):
        parts.append(f'<text x="{x}" y="{74 + i * 27}" class="o up" style="--d:{t + i * 0.12:.2f}s">{line}</text>')
    t += len(lines) * 0.12 + 0.4

    svg, t, _ = command(x, 204, p["prompt"], "./status", t)
    parts.append(svg)
    t += 0.2
    parts.append(
        f'<g class="up" style="--d:{t:.2f}s">'
        f'<circle cx="{x + 6}" cy="233" r="5" class="g dot"/>'
        f'<text x="{x + 20}" y="238" class="o">{esc(p["status"])}</text></g>'
    )
    t += 0.5
    cx = x + (len(p["prompt"]) + 1) * CW16
    parts.append(f'<text x="{x}" y="276" class="p in" style="--d:{t:.2f}s">{esc(p["prompt"])}</text>')
    parts.append(cursor(cx, 276, t))
    css = ".dot{transform-box:fill-box;transform-origin:center;animation:pulse 2s ease-in-out infinite}" \
          "@keyframes pulse{50%{opacity:.35;transform:scale(.7)}}"
    label = f'{p["name"]} (@{p["login"]}) — {p["role"]}, {p["focus"]}. {p["location"]}. {p["doing"]}.'
    write(os.path.join(ROOT, "terminal.svg"), frame(w, 296, label, "\n".join(parts), css))


def link_card(name, cmd, value):
    w, h, pad = 286, 104, 4
    svg, t, _ = command(22, 40, "~ $", cmd, 0.3)
    size = 15 if len(value) * CW15 < w - 50 else 13
    body = svg + (
        f'<text x="22" y="74" class="up" style="--d:{t + 0.15:.2f}s;fill:{BLUE};font:700 {size}px {MONO}">'
        f'{esc(value)}</text>'
    )
    write(os.path.join(ROOT, "links", f"{name}.svg"), frame(w, h, f"{name}: {value}", body, pad=pad))


def luminance(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def stack():
    icons = json.load(open(os.path.join(ROOT, "data", "icons.json"), encoding="utf-8"))
    w, h = 860, 246
    pitch, tile = 72, 50
    parts = []
    svg, t, end_x = command(28, 36, PROFILE["prompt"], "./stack.sh --list", 0.2)
    parts.append(svg)
    t += 0.2
    names = []
    k = 0
    for r, row in enumerate(PROFILE["stack"]):
        x0 = (w - len(row) * pitch) / 2 + (pitch - tile) / 2
        y = 62 + r * 88
        for c, key in enumerate(row):
            x = x0 + c * pitch
            delay = t + k * 0.05
            wave = t + 1.2 + k * 0.12
            k += 1
            if key == "aws":
                label, glyph = "AWS", (
                    f'<text x="25" y="30" text-anchor="middle" style="fill:#FF9900;font:800 17px {MONO}">aws</text>'
                    f'<path d="M13 35 q12 6 24 0" fill="none" stroke="#FF9900" stroke-width="2.4" stroke-linecap="round"/>'
                )
            else:
                ic = icons[key]
                label = ic["label"]
                color = "#" + ic["hex"] if luminance(ic["hex"]) > 0.22 else TEXT
                glyph = f'<g transform="translate(11,11) scale(1.1667)"><path d="{ic["path"]}" fill="{color}"/></g>'
            names.append(label)
            parts.append(
                f'<g transform="translate({x:.1f},{y})"><g class="i" style="animation-delay:{delay:.2f}s,{wave:.2f}s">'
                f'<title>{esc(label)}</title>'
                f'<rect x=".5" y=".5" width="{tile - 1}" height="{tile - 1}" rx="12" fill="#161b22" stroke="{BORDER}"/>'
                f'{glyph}</g>'
                f'<text x="{tile / 2}" y="{tile + 17}" class="n in" style="--d:{delay + 0.2:.2f}s">{esc(label)}</text></g>'
            )
    css = (
        ".i{opacity:0;transform-box:fill-box;transform-origin:center;"
        "animation:pop .45s cubic-bezier(.2,.8,.2,1.3) forwards,bob 5s ease-in-out infinite}"
        "@keyframes pop{from{opacity:0;transform:translateY(10px) scale(.6)}to{opacity:1;transform:none}}"
        "@keyframes bob{0%,14%,100%{transform:none}7%{transform:translateY(-5px)}}"
        f".n{{fill:{MUTED};font:11px {MONO};text-anchor:middle}}"
        "@media (prefers-reduced-motion:reduce){.i{animation:none;opacity:1}}"
    )
    write(os.path.join(ROOT, "stack.svg"), frame(w, h, "Tech stack: " + ", ".join(names), "\n".join(parts), css))


def project_card(pr):
    w, h, pad = 430, 172, 4
    parts = []
    svg, t, _ = command(22, 38, "~ $", f"cd {pr['path']}", 0.3)
    parts.append(svg)
    t += 0.2
    parts.append(f'<text x="22" y="72" class="up" style="--d:{t:.2f}s;fill:{TEXT};font:700 18px {MONO}">{esc(pr["title"])}</text>')
    for i, line in enumerate(pr["desc"]):
        parts.append(f'<text x="22" y="{100 + i * 20}" class="s up" style="--d:{t + 0.1 + i * 0.08:.2f}s">{esc(line)}</text>')
    parts.append(f'<text x="22" y="152" class="up" style="--d:{t + 0.35:.2f}s;fill:{BLUE};font:12px {MONO}">{esc(pr["tags"])}</text>')
    parts.append(f'<text x="{w - 22}" y="72" class="m in" text-anchor="end" style="--d:{t:.2f}s;font:12px {MONO}">view repo →</text>')
    label = f'{pr["title"]}: {" ".join(pr["desc"])} ({pr["tags"]})'
    write(os.path.join(ROOT, "projects", f"{pr['file']}.svg"), frame(w, h, label, "\n".join(parts), pad=pad))


def now():
    rows = PROFILE["now"]
    w = 860
    h = 76 + len(rows) * 28 + 40
    parts = []
    svg, t, _ = command(28, 38, PROFILE["prompt"], "tail -f now.log", 0.2)
    parts.append(svg)
    t += 0.25
    key_w = max(len(k) for k, _ in rows) + 1
    for i, (key, value) in enumerate(rows):
        y = 76 + i * 28
        parts.append(
            f'<g class="up" style="--d:{t + i * 0.15:.2f}s">'
            f'<text x="28" y="{y}" class="o m">[{i + 1:02d}]</text>'
            f'<text x="{28 + 5.5 * CW15:.1f}" y="{y}" class="o a">{esc(key)}</text>'
            f'<text x="{28 + (5.5 + key_w) * CW15:.1f}" y="{y}" class="o"><tspan class="m">→ </tspan>{esc(value)}</text></g>'
        )
    t += len(rows) * 0.15 + 0.3
    yc = 76 + len(rows) * 28 + 6
    cx = 28 + (len(PROFILE["prompt"]) + 1) * CW16
    parts.append(f'<text x="28" y="{yc}" class="p in" style="--d:{t:.2f}s">{esc(PROFILE["prompt"])}</text>')
    parts.append(cursor(cx, yc, t))
    label = "now.log: " + "; ".join(f"{k}: {v}" for k, v in rows)
    write(os.path.join(ROOT, "now.svg"), frame(w, h, label, "\n".join(parts)))


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "links"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "projects"), exist_ok=True)
    terminal()
    for link in PROFILE["links"]:
        link_card(*link)
    stack()
    for pr in PROFILE["projects"]:
        project_card(pr)
    now()
