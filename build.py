"""Builds the profile images in assets/ (light + dark) from the portfolio's palette.

Edit STACK below, then run:  py build.py
Logos come from simple-icons; VS Code has no simple-icons logo, so it gets a code glyph.
"""
import base64, json, math, pathlib, random, re, subprocess, urllib.request
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
BODIES = ["white", "black", "asagi", "tea", "gold", "platinum"]  # git-koi's six bodies, one GIF each in koi/<body>/
POND = {"light": dict(water="#cfe3df", deep="#b9d6d1", pad="#7fb069", pad2="#5f9450", ripple="#ffffff"),
        "dark": dict(water="#0b2a45", deep="#082036", pad="#3f7d4f", pad2="#2f6340", ripple="#4fb3b0")}


def contributions():
    """Last year's contribution total via the gh CLI (your gh login locally, GH_TOKEN in the Action)."""
    q = "query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions}}}}"
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}", "-F", f"login={USER}"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]


def koi_count(total):
    return max(3, min(14, total // 10 + 1))  # one koi per 10 contributions, kept between 3 and 14


assert [koi_count(n) for n in (0, 83, 500)] == [3, 9, 14]


def git_koi(body):
    """(data URI, union bbox of the fish across all frames) for a git-koi GIF, or None if not drawn yet."""
    path = pathlib.Path(__file__).parent / "koi" / body / "koi.gif"
    if not path.exists():
        return None
    from PIL import Image, ImageSequence  # only needed when the GIFs exist (the Action installs it)
    box = None
    for frame in ImageSequence.Iterator(Image.open(path)):
        b = frame.convert("RGBA").getchannel("A").getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    return "data:image/gif;base64," + base64.b64encode(path.read_bytes()).decode(), box


def lap(cx, cy, half, radius, clockwise):
    """A stadium loop (two straights joined by half circles): wide, even turns instead of spinning on the spot."""
    if clockwise:
        return (f"M{cx - half} {cy - radius}H{cx + half}A{radius} {radius} 0 0 1 {cx + half} {cy + radius}"
                f"H{cx - half}A{radius} {radius} 0 0 1 {cx - half} {cy - radius}Z")
    return (f"M{cx + half} {cy - radius}H{cx - half}A{radius} {radius} 0 0 0 {cx - half} {cy + radius}"
            f"H{cx + half}A{radius} {radius} 0 0 0 {cx + half} {cy - radius}Z")


def pond(t, mode, total, fish):
    W, H, GAP = 900, 360, 78
    # As big as possible (up to .45) while two turning koi still fit in the 78 px between the loops.
    SCALE = min(.45, (GAP / 2 - 1) / max(math.hypot(x1 - x0, y1 - y0) / 2 for _, (x0, y0, x1, y1) in fish))
    p, rnd = POND[mode], random.Random(7)  # fixed seed: same pond every build
    n = koi_count(total)
    b = [f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
         f'<radialGradient id="depth" cx=".5" cy=".55" r=".7"><stop offset="0" stop-color="{p["water"]}"/>'
         f'<stop offset="1" stop-color="{p["deep"]}"/></radialGradient>']
    sprites = []
    for k, (uri, (x0, y0, x1, y1)) in enumerate(fish):
        w, h = (x1 - x0) * SCALE, (y1 - y0) * SCALE
        b.append(f'<svg id="k{k}" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" width="{w:.1f}" height="{h:.1f}">'
                 f'<image href="{uri}" width="512" height="512" style="image-rendering:pixelated"/></svg>')
        sprites.append((w, h, math.hypot(w, h) / 2))  # radius of the disc a turning fish sweeps
    for i in range(n):  # every koi gets its own spot on the colour wheel, starting at koi red/orange, so no two look alike
        b.append(f'<filter id="hue{i}"><feColorMatrix type="hueRotate" values="{(160 + i * 360 / n) % 360:.0f}"/></filter>')
    b.append(f'</defs><g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="url(#depth)"/>')
    for i in range(6):  # ripples
        x, y = rnd.uniform(60, W - 60), rnd.uniform(40, H - 40)
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2" fill="none" stroke="{p["ripple"]}" stroke-width="1.2">'
                 f'<animate attributeName="r" values="2;34" dur="5s" begin="{i * .9:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".5;0" dur="5s" begin="{i * .9:.1f}s" repeatCount="indefinite"/></circle>')
    # Two loops around the same centre, same straights, radii 78 px apart: the gap is 78 px all the way round.
    # Koi on one loop share a speed and are spaced evenly, so they never catch up; the loops never come within
    # two fish-widths of each other, so koi on different loops never meet either.
    cx, cy, half = W // 2, H // 2, 270
    lanes = [(128, True, 28), (128 - GAP, False, 22)]  # (turn radius, clockwise, px per second)
    r_max = max(r for *_, r in sprites)
    assert lanes[0][0] - lanes[1][0] >= 2 * r_max, "koi on the two loops could touch"
    outer = math.ceil(n * .6)
    for lane, ((radius, clockwise, speed), count) in enumerate(zip(lanes, (outer, n - outer))):
        length = 4 * half + 2 * math.pi * radius
        assert length / max(count, 1) >= 2 * r_max, "koi on one loop could touch"
        dur = length / speed
        for j in range(count):
            i = j if lane == 0 else outer + j
            k = i % len(fish)
            w, h, _ = sprites[k]
            sway = rnd.uniform(1.4, 2.0)
            b.append(f'<g><animateMotion path="{lap(cx, cy, half, radius, clockwise)}" dur="{dur:.1f}s" '
                     f'begin="-{dur * j / count:.2f}s" repeatCount="indefinite" rotate="auto"/>'
                     f'<g><animateTransform attributeName="transform" type="rotate" values="-6;6;-6" keyTimes="0;.5;1" '
                     f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" dur="{sway:.2f}s" repeatCount="indefinite"/>'
                     f'<use href="#k{k}" x="{-w / 2:.1f}" y="{-h / 2:.1f}" filter="url(#hue{i})"/></g></g>')
    for cx, cy, r, rot in ((60, 40, 26, 20), (850, 322, 32, 200), (842, 34, 18, 110), (52, 328, 20, 300)):  # lily pads in the corners
        a1, a2 = math.radians(rot), math.radians(rot + 330)
        b.append(f'<path d="M{cx} {cy}L{cx + r * math.cos(a1):.1f} {cy + r * math.sin(a1):.1f}'
                 f'A{r} {r} 0 1 1 {cx + r * math.cos(a2):.1f} {cy + r * math.sin(a2):.1f}Z" fill="{p["pad"]}"/>'
                 f'<circle cx="{cx}" cy="{cy}" r="{r * .55:.1f}" fill="none" stroke="{p["pad2"]}" stroke-width="1"/>')
    b.append("</g>")
    return svg(W, H, "".join(b), f"An animated koi pond with {n} git-koi koi, one for every 10 of {total} GitHub contributions this year")


fish = [f for f in map(git_koi, BODIES) if f]
total = contributions() if fish else 0
for mode, t in THEMES.items():
    (OUT / f"hero-{mode}.svg").write_text(hero(t), encoding="utf-8")
    (OUT / f"stack-{mode}.svg").write_text(stack(t), encoding="utf-8")
    if fish:  # the koi GIFs come from git-koi in the Action; skip the pond until they exist
        (OUT / f"pond-{mode}.svg").write_text(pond(t, mode, total, fish), encoding="utf-8")
    print("built", mode)
