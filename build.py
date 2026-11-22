"""Builds the profile images in assets/ (light + dark) from the portfolio's palette.

Edit STACK below, then run:  py build.py
Logos come from simple-icons; VS Code has no simple-icons logo, so it gets a code glyph.
"""
import datetime, json, math, pathlib, re, subprocess, urllib.request
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
         "{totalContributions weeks{contributionDays{date weekday contributionCount contributionLevel}}}}}}")

# Sequential ramp, one hue (teal), per theme: empty step + GitHub's four quartile levels.
# Dark mode is its own set of steps (dim -> bright), not an inverted copy of light.
RAMP = {
    "light": ["#cfe0dc", "#a6d6cf", "#62b3aa", "#2a8c8c", "#18615f"],
    "dark": ["#123a59", "#1d5a68", "#2f8689", "#4fb3b0", "#9fe1d6"],
}
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def calendar():
    """Last year's contributions via the gh CLI (uses your gh login, or GH_TOKEN in CI)."""
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={USER}"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def summary(cal):
    days = [d for wk in cal["weeks"] for d in wk["contributionDays"]]
    streak = best = 0
    for d in days:
        streak = streak + 1 if d["contributionCount"] else 0
        best = max(best, streak)
    top = max(days, key=lambda d: d["contributionCount"])
    when = datetime.date.fromisoformat(top["date"])
    return [("Contributions", f'{cal["totalContributions"]:,}'),
            ("Active days", str(sum(1 for d in days if d["contributionCount"]))),
            ("Longest streak", f'{best} day{"s" * (best != 1)}'),
            ("Busiest day", f'{top["contributionCount"]} on {when:%b} {when.day}')]


assert summary({"totalContributions": 3, "weeks": [{"contributionDays": [
    {"date": "2026-01-01", "contributionCount": 1}, {"date": "2026-01-02", "contributionCount": 2},
    {"date": "2026-01-03", "contributionCount": 0}]}]})[2:] == [("Longest streak", "2 days"), ("Busiest day", "2 on Jan 2")]


def contrib(t, cal, mode):
    ramp, PAD, CELL, GAP = RAMP[mode], 32, 12, 3
    STEP = CELL + GAP
    b = []
    # KPI row: four stat tiles, label above value.
    for i, (label, value) in enumerate(summary(cal)):
        x = PAD + i * 210
        if i:
            b.append(f'<line x1="{x - 24}" x2="{x - 24}" y1="30" y2="74" stroke="{t["border"]}"/>')
        b.append(f'<text x="{x}" y="42" font-family="{FONT}" font-size="12.5" fill="{t["muted"]}">{label}</text>')
        b.append(f'<text x="{x}" y="70" font-family="{FONT}" font-size="24" font-weight="600" fill="{t["fg"]}">{escape(value)}</text>')
    # Heatmap: weeks across, weekdays down.
    gx, gy = PAD + 30, 124
    last_month = None
    for w, wk in enumerate(cal["weeks"]):
        first = datetime.date.fromisoformat(wk["contributionDays"][0]["date"])
        if first.month != last_month and w < len(cal["weeks"]) - 2:
            if last_month is not None or first.day <= 7:
                b.append(f'<text x="{gx + w * STEP}" y="{gy - 10}" font-family="{FONT}" font-size="11" fill="{t["muted"]}">{first:%b}</text>')
            last_month = first.month
        for d in wk["contributionDays"]:
            b.append(f'<rect x="{gx + w * STEP}" y="{gy + d["weekday"] * STEP}" width="{CELL}" height="{CELL}" rx="2.5" '
                     f'fill="{ramp[LEVEL[d["contributionLevel"]]]}"/>')
    for d, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        b.append(f'<text x="{PAD}" y="{gy + d * STEP + 10}" font-family="{FONT}" font-size="11" fill="{t["muted"]}">{name}</text>')
    # Legend, right-aligned under the grid.
    ly, right = gy + 7 * STEP + 14, gx + len(cal["weeks"]) * STEP - GAP
    lx = right - 5 * STEP - 30
    b.append(f'<text x="{lx - 8}" y="{ly + 10}" text-anchor="end" font-family="{FONT}" font-size="11" fill="{t["muted"]}">Less</text>')
    for i, c in enumerate(ramp):
        b.append(f'<rect x="{lx + i * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    b.append(f'<text x="{right}" y="{ly + 10}" text-anchor="end" font-family="{FONT}" font-size="11" fill="{t["muted"]}">More</text>')
    W, H = 900, ly + CELL + PAD
    body = f'<rect width="{W}" height="{H}" rx="18" fill="{t["bg"]}"/>' + "".join(b)
    stats = ". ".join(f"{k}: {v}" for k, v in summary(cal))
    return svg(W, H, body, f"GitHub contributions in the last year. {stats}.")


cal = calendar()
for mode, t in THEMES.items():
    (OUT / f"hero-{mode}.svg").write_text(hero(t), encoding="utf-8")
    (OUT / f"stack-{mode}.svg").write_text(stack(t), encoding="utf-8")
    (OUT / f"contrib-{mode}.svg").write_text(contrib(t, cal, mode), encoding="utf-8")
    print("built", mode)
