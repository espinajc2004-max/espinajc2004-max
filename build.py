"""Builds the profile images in assets/ (light + dark) from the portfolio's palette.

Edit STACK below, then run:  py build.py
Logos come from simple-icons; VS Code has no simple-icons logo, so it gets a code glyph.
"""
import json, math, pathlib, re, subprocess, urllib.request
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
                  ("styled-components", "styledcomponents")]),
    ("Backend", [("Node.js", "nodedotjs"), ("Express", "express"), ("Hono", "hono"), ("Prisma", "prisma"),
                 ("Drizzle ORM", "drizzle"), ("Zod", "zod")]),
    ("Database", [("PostgreSQL", "postgresql"), ("Neon", "neon"), ("Supabase", "supabase"), ("MongoDB", "mongodb")]),
    ("AI", [("OpenAI", "openai")]),
    ("Cloud", [("Vercel", "vercel"), ("Cloudflare", "cloudflare")]),
    ("Tools", [("Git", "git"), ("GitHub", "github"), ("VS Code", None), ("Cursor", "cursor"), ("Postman", "postman"), ("npm", "npm")]),
    ("Services", [("Better Auth", "betterauth"), ("Resend", "resend")]),
]

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


def svg(w, h, body, title, css=""):
    style = f"<style>{css}@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}</style>" if css else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{escape(title)}</title>{style}{body}</svg>')


def hero(t):
    W, H = 900, 240
    css = []
    b = [f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
         f'<linearGradient id="fade"><stop offset="0" stop-color="{t["bg"]}"/>'
         f'<stop offset="1" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient></defs>',
         f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>']
    # Depth contours that drift sideways, each at its own speed: a nod to the Lagoon / Deep sea themes.
    for k in range(11):
        y0, amp, s = 36 + k * 18, 10 + k * 1.4, 38 + k * 3
        period = 2 * math.pi * s  # sin(x/s) repeats every 2*pi*s, so sliding by one period loops seamlessly
        pts = " ".join(f"{x},{y0 + amp * math.sin(x / s + k * .7):.1f}" for x in range(500, int(W + period) + 9, 8))
        color, op = (t["accent"], .9) if k == 6 else (t["border"], .35 + k * .05)
        css.append(f"@keyframes w{k}{{to{{transform:translateX(-{period:.1f}px)}}}}"
                   f".w{k}{{animation:w{k} {18 + k * 3}s linear infinite}}")
        b.append(f'<polyline class="w{k}" points="{pts}" fill="none" stroke="{color}" '
                 f'stroke-width="{2 if k == 6 else 1.2}" opacity="{op:.2f}"/>')
    b.append(f'<rect width="560" height="{H}" fill="{t["bg"]}"/><rect x="560" width="140" height="{H}" fill="url(#fade)"/></g>')
    b.append(f'<text x="48" y="92" font-family="{FONT}" font-size="46" font-weight="700" fill="{t["fg"]}" letter-spacing="-1">John Carlo Espina</text>')
    b.append(f'<text x="48" y="132" font-family="{FONT}" font-size="20" fill="{t["fg"]}">Full-stack developer, from the interface down to the database.</text>')
    b.append(f'<text x="48" y="166" font-family="{FONT}" font-size="15" fill="{t["muted"]}">Computer Science student in San Jose del Monte, Bulacan.</text>')
    b.append(f'<text x="48" y="188" font-family="{FONT}" font-size="15" fill="{t["muted"]}">Interning now, still upskilling, and open to work.</text>')
    return svg(W, H, "".join(b), "John Carlo Espina, full-stack developer", "".join(css))


def stack(t):
    items = [it for _, group in STACK for it in group]
    COLS, TILE = 10, 90
    rows = math.ceil(len(items) / COLS)
    W, H = COLS * TILE, rows * TILE
    # A soft light crosses the tiles on a diagonal, echoing the hero's drifting waves.
    css = (f"@keyframes glow{{0%,100%{{opacity:0}}8%{{opacity:.18}}20%{{opacity:0}}}}"
           f".g{{opacity:0;animation:glow 7s ease-in-out infinite}}")
    b = [f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>',
         f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{t["bg"]}"/>']
    for i, (name, slug) in enumerate(items):
        r, c = divmod(i, COLS)
        x, y = c * TILE, r * TILE
        cx = x + TILE / 2
        b.append(f'<rect class="g" style="animation-delay:{(r + c) * .14:.2f}s" x="{x}" y="{y}" width="{TILE}" height="{TILE}" fill="{t["accent"]}"/>')
        if slug:
            path, brand = logo(slug)
            b.append(f'<path transform="translate({cx - 15} {y + 18}) scale({30 / 24})" '
                     f'fill="{t["fg"] if mono(brand) else readable(brand, t["bg"])}" d="{path}"/>')
        else:  # code glyph in VS Code blue
            b.append(f'<path transform="translate({cx - 15} {y + 18}) scale({30 / 24})" fill="none" stroke="{readable("#007ACC", t["bg"])}" '
                     f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M8 5 2 12l6 7M16 5l6 7-6 7"/>')
        size = 11 if len(name) <= 12 else 9.5
        b.append(f'<text x="{cx}" y="{y + 72}" text-anchor="middle" font-family="{FONT}" font-size="{size}" fill="{t["muted"]}">{escape(name)}</text>')
    # Seams between the tiles, so they read as one block of cubes pressed together.
    for c in range(1, COLS):
        b.append(f'<line x1="{c * TILE}" x2="{c * TILE}" y1="0" y2="{H}" stroke="{t["border"]}"/>')
    for r in range(1, rows):
        b.append(f'<line x1="0" x2="{W}" y1="{r * TILE}" y2="{r * TILE}" stroke="{t["border"]}"/>')
    b.append("</g>")
    return svg(W, H, "".join(b), "Tech stack: " + ", ".join(n for n, _ in items), css)


USER = "espinajc2004-max"
QUERY = ("query($login:String!){user(login:$login){contributionsCollection{contributionCalendar"
         "{totalContributions weeks{contributionDays{weekday contributionCount}}}}}}")


def calendar():
    """Last year's contributions via the gh CLI (uses your gh login, or GH_TOKEN in CI)."""
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={USER}"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def mix(a, b, f):
    """Blend hex a toward hex b by f (0..1)."""
    pa, pb = ([int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in (a, b))
    return "#" + "".join(f"{round(x + (y - x) * f):02x}" for x, y in zip(pa, pb))


def contrib(t, cal):
    # Oblique cube grid: weeks run right (U), weekdays run down-left (V); taller, brighter cubes = busier days.
    U, V, GAP, MAXH, PAD, TOP = (13.6, 1.2), (-4.2, 8.0), .84, 80, 30, 50
    days = [(w, d["weekday"], d["contributionCount"]) for w, wk in enumerate(cal["weeks"]) for d in wk["contributionDays"]]
    peak = max(c for *_, c in days) or 1
    shade = "#000000" if _lum(t["bg"]) > .5 else "#00101f"

    def pt(w, d, dx=0., dy=0.):
        return (w + dx) * U[0] + (d + dy) * V[0], (w + dx) * U[1] + (d + dy) * V[1]

    xs = [pt(w, d, a, b)[0] for w, d, _ in days for a in (0, 1) for b in (0, 1)]
    ox = PAD - min(xs) + (900 - 2 * PAD - (max(xs) - min(xs))) / 2  # centre the slab
    oy = TOP + MAXH
    H = int(oy + max(pt(w, d, 1, 1)[1] for w, d, _ in days)) + PAD
    b = [f'<defs><clipPath id="card"><rect width="900" height="{H}" rx="18"/></clipPath></defs>',
         f'<g clip-path="url(#card)"><rect width="900" height="{H}" fill="{t["bg"]}"/>',
         f'<text x="{PAD}" y="42" font-family="{FONT}" font-size="15" font-weight="600" fill="{t["fg"]}">'
         f'{cal["totalContributions"]} contributions in the last year</text>']
    for w, d, c in sorted(days, key=lambda x: (x[0] + x[1], x[1])):  # back to front
        f = math.log1p(c) / math.log1p(peak)  # log scale so a 1-commit day still shows next to a 30
        h = 3 + MAXH * f if c else 2
        top = mix(t["border"], t["accent"], .35 + .65 * f) if c else t["border"]
        g0, g1 = (1 - GAP) / 2, (1 + GAP) / 2
        corners = [pt(w, d, g0, g0), pt(w, d, g1, g0), pt(w, d, g1, g1), pt(w, d, g0, g1)]
        P = [(ox + x, oy + y - h) for x, y in corners]   # top face
        B = [(ox + x, oy + y) for x, y in corners]       # ground
        poly = lambda pts, col: b.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{col}"/>')
        poly([P[3], P[2], B[2], B[3]], mix(top, shade, .25))  # front face
        poly([P[1], P[2], B[2], B[1]], mix(top, shade, .45))  # right face
        poly(P, top)
    b.append("</g>")
    return svg(900, H, "".join(b), f'{cal["totalContributions"]} GitHub contributions in the last year, drawn as 3D cubes')


cal = calendar()
for mode, t in THEMES.items():
    (OUT / f"hero-{mode}.svg").write_text(hero(t), encoding="utf-8")
    (OUT / f"stack-{mode}.svg").write_text(stack(t), encoding="utf-8")
    (OUT / f"contrib-{mode}.svg").write_text(contrib(t, cal), encoding="utf-8")
    print("built", mode)
