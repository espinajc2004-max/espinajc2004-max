"""Builds the profile images in assets/ (light + dark) from the portfolio's palette.

Edit STACK below, then run:  py build.py
Logos come from simple-icons; VS Code has no simple-icons logo, so it gets a code glyph.
"""
import json, math, pathlib, re, urllib.request
from html import escape

OUT = pathlib.Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

# Same values as the portfolio: Lagoon (light) and Deep sea (dark) themes.
THEMES = {
    "light": dict(bg="#e4efec", fg="#173f57", muted="#2e5a70", border="#b7d0cb", accent="#2a8c8c"),
    "dark": dict(bg="#0b2a45", fg="#dceae6", muted="#9dbcc8", border="#24506f", accent="#4fb3b0"),
}
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
SI = "https://cdn.jsdelivr.net/npm/simple-icons@latest"
def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "profile-build"})).read().decode()

def _slug(title):  # simple-icons derives most slugs from the title
    for a, b in (("+", "plus"), (".", "dot"), ("&", "and")):
        title = title.replace(a, b)
    return re.sub("[^a-z0-9]", "", title.lower())

HEX = {i.get("slug") or _slug(i["title"]): "#" + i["hex"] for i in json.loads(fetch(f"{SI}/data/simple-icons.json"))}

def logo(slug):
    """(path, brand hex) for a simple-icons slug."""
    if slug not in _cache:
        _cache[slug] = (re.search(r'<path d="([^"]+)"', fetch(f"{SI}/icons/{slug}.svg")).group(1), HEX.get(slug, "#000000"))  # OpenAI has no colour entry; its logo is black
    return _cache[slug]


def _lum(hex_):
    c = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + .05) / (lo + .05)


def readable(brand, bg):
    """Brand colour, nudged toward black (light bg) or white (dark bg) until it reaches 3:1 against bg."""
    target = 0 if _lum(bg) > .5 else 255
    rgb = [int(brand[i:i + 2], 16) for i in (1, 3, 5)]
    for step in range(21):
        mixed = "#" + "".join(f"{round(v + (target - v) * step / 20):02x}" for v in rgb)
        if contrast(mixed, bg) >= 3:
            return mixed
    return mixed



def mono(hex_):
    """Black, white and grey brands follow the theme's text colour instead of turning grey."""
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return max(r, g, b) - min(r, g, b) < 40  # 40 also catches near-grey slates like Prisma

assert contrast("#000000", "#ffffff") > 20 and contrast(readable("#F7DF1E", "#e4efec"), "#e4efec") >= 3
assert contrast(readable("#000000", "#0b2a45"), "#0b2a45") >= 3


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{escape(title)}</title>{body}</svg>')


def hero(t):
    W, H = 900, 240
    b = [f'<rect width="{W}" height="{H}" rx="18" fill="{t["bg"]}"/>']
    # Depth contours on the right: a nod to the Lagoon / Deep sea theme names.
    for k in range(11):
        y0, amp = 36 + k * 18, 10 + k * 1.4
        pts = " ".join(f"{x},{y0 + amp * math.sin(x / (38 + k * 3) + k * .7):.1f}" for x in range(560, W + 1, 8))
        color, op = (t["accent"], .9) if k == 6 else (t["border"], .35 + k * .05)
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{2 if k == 6 else 1.2}" opacity="{op:.2f}"/>')
    b.append(f'<rect x="540" width="120" height="{H}" fill="url(#fade)"/>')
    b.insert(0, f'<defs><linearGradient id="fade"><stop offset="0" stop-color="{t["bg"]}"/>'
                f'<stop offset="1" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient></defs>')
    b.append(f'<text x="48" y="92" font-family="{FONT}" font-size="46" font-weight="700" fill="{t["fg"]}" letter-spacing="-1">John Carlo Espina</text>')
    b.append(f'<text x="48" y="132" font-family="{FONT}" font-size="20" fill="{t["fg"]}">Full-stack developer, from the interface down to the database.</text>')
    b.append(f'<text x="48" y="166" font-family="{FONT}" font-size="15" fill="{t["muted"]}">Computer Science student in San Jose del Monte, Bulacan.</text>')
    b.append(f'<text x="48" y="188" font-family="{FONT}" font-size="15" fill="{t["muted"]}">Interning now, still upskilling, and open to work.</text>')
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
            b.append(f'<text x="{x}" y="{mid + 5}" font-family="{FONT}" font-size="15" font-weight="600" fill="{t["fg"]}">{group}</text>')
            assert x + lw + len(items) * SLOT <= W - PAD + 10, f"{group} row too wide"
            for i, (name, slug) in enumerate(items):
                cx, iy = x + lw + i * SLOT + SLOT / 2, mid - 24
                if slug:
                    path, brand = logo(slug)
                    b.append(f'<path transform="translate({cx - 13} {iy}) scale({26 / 24})" fill="{t["fg"] if mono(brand) else readable(brand, t["bg"])}" d="{path}"/>')
                else:  # code glyph in VS Code blue
                    b.append(f'<path transform="translate({cx - 13} {iy}) scale({26 / 24})" fill="none" stroke="{readable("#007ACC", t["bg"])}" '
                             f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M8 5 2 12l6 7M16 5l6 7-6 7"/>')
                b.append(f'<text x="{cx}" y="{mid + 22}" text-anchor="middle" font-family="{FONT}" font-size="11.5" fill="{t["muted"]}">{escape(name)}</text>')
            x += lw + len(items) * SLOT + 50
    names = ", ".join(n for _, items in STACK for n, _ in items)
    return svg(W, H, "".join(b), f"Tech stack: {names}")


for mode, t in THEMES.items():
    (OUT / f"hero-{mode}.svg").write_text(hero(t), encoding="utf-8")
    (OUT / f"stack-{mode}.svg").write_text(stack(t), encoding="utf-8")
    print("built", mode)
