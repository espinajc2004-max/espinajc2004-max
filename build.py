"""Builds the profile images in assets/ (light + dark) from the portfolio's palette.

Edit STACK below, then run:  py build.py
Logos come from simple-icons; VS Code has no simple-icons logo, so it gets a code glyph.
"""
import math, pathlib, re, urllib.request
from html import escape

OUT = pathlib.Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

# Same values as the portfolio: Lagoon (light) and Deep sea (dark) themes, plus its six-hue palette.
THEMES = {
    "light": dict(bg="#e4efec", fg="#173f57", muted="#2e5a70", border="#b7d0cb", accent="#2a8c8c"),
    "dark": dict(bg="#0b2a45", fg="#dceae6", muted="#9dbcc8", border="#24506f", accent="#4fb3b0"),
}
PALETTE = ["#F05032", "#61DAFB", "#3FCF8E", "#F7DF1E", "#A78BFA", "#5FA04E"]
FONT = "Archivo, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"

STACK = [
    ("Languages", [("JavaScript", "javascript"), ("TypeScript", "typescript"), ("HTML", "html5"), ("CSS", "css")]),
    ("Frontend", [("Next.js", "nextdotjs"), ("React", "react"), ("Tailwind CSS", "tailwindcss"), ("shadcn/ui", "shadcnui"),
                  ("styled-components", "styledcomponents"), ("GSAP", "gsap"), ("Three.js", "threedotjs")]),
    ("Backend", [("Node.js", "nodedotjs"), ("Express", "express"), ("Hono", "hono"), ("Prisma", "prisma"),
                 ("Drizzle ORM", "drizzle"), ("Zod", "zod")]),
    ("Database", [("PostgreSQL", "postgresql"), ("Neon", "neon"), ("Supabase", "supabase"), ("MongoDB", "mongodb")]),
    ("AI", [("Claude", "claude"), ("OpenAI", "openai")]),
    ("Cloud", [("Vercel", "vercel"), ("Cloudflare", "cloudflare")]),
    ("Tools", [("Git", "git"), ("GitHub", "github"), ("VS Code", None), ("Cursor", "cursor"), ("Postman", "postman"), ("npm", "npm")]),
    ("Services", [("Better Auth", "betterauth"), ("Stripe", "stripe"), ("Resend", "resend")]),
]

SHARE_ROW = {"Cloud"}  # sits beside AI instead of taking its own short row

_cache = {}
def logo(slug):
    if slug not in _cache:
        req = urllib.request.Request(f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg",
                                     headers={"User-Agent": "profile-build"})
        _cache[slug] = re.search(r'<path d="([^"]+)"', urllib.request.urlopen(req).read().decode()).group(1)
    return _cache[slug]


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{escape(title)}</title>{body}</svg>')


def hero(t):
    W, H = 900, 300
    b = [f'<rect width="{W}" height="{H}" rx="18" fill="{t["bg"]}"/>']
    # Depth contours on the right: a nod to the Lagoon / Deep sea theme names.
    for k in range(11):
        y0, amp = 70 + k * 19, 10 + k * 1.4
        pts = " ".join(f"{x},{y0 + amp * math.sin(x / (38 + k * 3) + k * .7):.1f}" for x in range(560, W + 1, 8))
        color, op = (t["accent"], .9) if k == 6 else (t["border"], .35 + k * .05)
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{2 if k == 6 else 1.2}" opacity="{op:.2f}"/>')
    b.append(f'<rect x="540" width="120" height="{H}" fill="url(#fade)"/>')
    b.insert(0, f'<defs><linearGradient id="fade"><stop offset="0" stop-color="{t["bg"]}"/>'
                f'<stop offset="1" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient></defs>')
    b.append(f'<text x="48" y="112" font-family="{FONT}" font-size="46" font-weight="700" fill="{t["fg"]}" letter-spacing="-1">John Carlo Espina</text>')
    b.append(f'<text x="48" y="152" font-family="{FONT}" font-size="20" fill="{t["fg"]}">Full-stack developer, from the interface down to the database.</text>')
    b.append(f'<text x="48" y="184" font-family="{FONT}" font-size="15" fill="{t["muted"]}">Computer Science student in San Jose del Monte, Bulacan.</text>')
    b.append(f'<text x="48" y="206" font-family="{FONT}" font-size="15" fill="{t["muted"]}">Interning now, still upskilling, and open to work.</text>')
    for i, c in enumerate(PALETTE):
        b.append(f'<rect x="{48 + i * 30}" y="240" width="22" height="22" rx="6" fill="{c}"/>')
    return svg(W, H, "".join(b), "John Carlo Espina, full-stack developer")


def stack(t):
    W, PAD, ROW, LABEL_W, SLOT = 900, 36, 84, 170, 92
    rows = []  # groups in SHARE_ROW sit beside the group before them
    for group in STACK:
        if group[0] in SHARE_ROW:
            rows[-1].append(group)
        else:
            rows.append([group])
    H = PAD * 2 + ROW * len(rows)
    b = [f'<rect width="{W}" height="{H}" rx="18" fill="{t["bg"]}"/>']
    for r, row in enumerate(rows):
        top = PAD + r * ROW
        if r:
            b.append(f'<line x1="{PAD}" x2="{W - PAD}" y1="{top}" y2="{top}" stroke="{t["border"]}"/>')
        mid, x = top + ROW / 2, PAD
        for g, (group, items) in enumerate(row):
            lw = LABEL_W if g == 0 else LABEL_W - 60  # a group sharing a row needs less label room
            dot = PALETTE[[n for n, _ in STACK].index(group) % len(PALETTE)]
            b.append(f'<circle cx="{x + 5}" cy="{mid}" r="5" fill="{dot}"/>')
            b.append(f'<text x="{x + 20}" y="{mid + 5}" font-family="{FONT}" font-size="15" font-weight="600" fill="{t["fg"]}">{group}</text>')
            assert x + lw + len(items) * SLOT <= W - PAD + 10, f"{group} row too wide"
            for i, (name, slug) in enumerate(items):
                cx, iy = x + lw + i * SLOT + SLOT / 2, mid - 24
                if slug:
                    b.append(f'<path transform="translate({cx - 13} {iy}) scale({26 / 24})" fill="{t["fg"]}" d="{logo(slug)}"/>')
                else:  # code glyph
                    b.append(f'<path transform="translate({cx - 13} {iy}) scale({26 / 24})" fill="none" stroke="{t["fg"]}" '
                             f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M8 5 2 12l6 7M16 5l6 7-6 7"/>')
                b.append(f'<text x="{cx}" y="{mid + 22}" text-anchor="middle" font-family="{FONT}" font-size="11.5" fill="{t["muted"]}">{escape(name)}</text>')
            x += lw + len(items) * SLOT + 50
    names = ", ".join(n for _, items in STACK for n, _ in items)
    return svg(W, H, "".join(b), f"Tech stack: {names}")


for mode, t in THEMES.items():
    (OUT / f"hero-{mode}.svg").write_text(hero(t), encoding="utf-8")
    (OUT / f"stack-{mode}.svg").write_text(stack(t), encoding="utf-8")
    print("built", mode)
