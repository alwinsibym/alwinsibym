"""Cobalt activity banner: isometric 3D contribution bars, a glowing rotating tesseract and live-ish stats."""
import datetime as dt, math
from xml.sax.saxutils import escape
import tesseract

ICE, COBALT, NAVY = "#9fd3ff", "#2f6bff", "#050b1f"
TOP = ["#0f2253", "#1d46b8", "#2f6bff", "#5b9dff", "#a9dcff"]
SANS = "Segoe UI,Helvetica,Arial,sans-serif"
U, V = (9.5, 2.4), (-3.0, 5.5)  # screen vectors for one week step and one weekday step


def mix(a, b, t):
    pa, pb = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


def level(n, cuts):
    return 0 if n <= 0 else 1 + sum(n > c for c in cuts)


def clip(t, n):
    return t if len(t) <= n else t[: n - 1] + "…"


def bars(days, ox, oy):
    vals = sorted(n for _, n in days if n)
    cuts = [vals[len(vals) * q // 4] for q in (1, 2, 3)] if len(vals) >= 4 else [1, 2, 4]
    mx = max([n for _, n in days] + [1])
    off = (dt.date.fromisoformat(days[0][0]).weekday() + 1) % 7
    ncols = (len(days) + off + 6) // 7
    P = lambda c, r: (ox + c * U[0] + r * V[0], oy + c * U[1] + r * V[1])
    pt = lambda p, h=0: f"{p[0]:.1f},{p[1] - h:.1f}"
    out = []
    for row in range(7):              # back row first, so nearer bars paint over farther ones
        for col in range(ncols):
            i = col * 7 + row - off
            if not 0 <= i < len(days):
                continue
            d, n = days[i]
            lv = level(n, cuts)
            h = 1.5 if n == 0 else 4 + 34 * math.sqrt(n / mx)
            a, b, c, e = P(col + .1, row + .1), P(col + .9, row + .1), P(col + .9, row + .9), P(col + .1, row + .9)
            top = TOP[lv]
            cls = ' class="pulse"' if lv == 4 and i > len(days) - 25 else ""
            out.append(f'<g{cls}><title>{d}: {n}</title>'
                       f'<polygon points="{pt(e)} {pt(c)} {pt(c, h)} {pt(e, h)}" fill="{mix(top, NAVY, .35)}"/>'
                       f'<polygon points="{pt(b)} {pt(c)} {pt(c, h)} {pt(b, h)}" fill="{mix(top, NAVY, .55)}"/>'
                       f'<polygon points="{pt(a, h)} {pt(b, h)} {pt(c, h)} {pt(e, h)}" fill="{top}"/></g>')
    return "".join(out)


def tile(x, label, val, unit=""):
    u = f'<tspan dx="4" font-size="12" fill="{COBALT}">{unit}</tspan>' if unit else ""
    return (f'<text x="{x}" y="46" font-family="monospace" font-size="9.5" letter-spacing="1.4" fill="#7f9bd6">{label}</text>'
            f'<text x="{x}" y="78" font-family="{SANS}" font-weight="700" font-size="27" fill="#eef4ff">{val:,}{u}</text>')


def build(st, repo, now):
    year = sum(n for _, n in st["days"])
    tiles = (tile(32, "CURRENT STREAK", st["current"], "days") + tile(188, "BEST STREAK", st["best"], "days")
             + tile(344, "COMMITS THIS YEAR", st["year_commits"]) + tile(512, "ALL-TIME COMMITS", st["total_commits"])
             + tile(690, "LAST 12 MONTHS", year, "contributions"))
    seps = "".join(f'<line x1="{x}" y1="34" x2="{x}" y2="86" stroke="#14275a"/>' for x in (172, 328, 496, 674))
    legend = "".join(f'<rect x="{64 + i * 16}" y="289" width="12" height="12" fill="{c}"/>' for i, c in enumerate(TOP))
    now_card = (
        f'<circle cx="676" cy="288" r="4" fill="{ICE}" class="blink"/>'
        f'<text x="688" y="292" font-family="monospace" font-size="9.5" letter-spacing="1.4" fill="#7f9bd6">NOW WORKING ON</text>'
        f'<text x="676" y="318" font-family="{SANS}" font-weight="700" font-size="19" fill="{ICE}">{escape(clip(repo["name"], 18))}</text>'
        f'<text x="676" y="338" font-family="monospace" font-size="10" fill="#9bb0de">{escape(clip(repo["msg"], 34))} · {escape(repo["ago"])}</text>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-label="Contribution activity: current streak {st['current']} days, best streak {st['best']} days, {st['year_commits']} commits this year, {st['total_commits']} in total; working on {escape(repo['name'])}">
<style>.pulse{{animation:p 2.4s ease-in-out infinite alternate}}@keyframes p{{from{{opacity:.65}}to{{opacity:1}}}}
.blink{{animation:b 1.6s ease-in-out infinite}}@keyframes b{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
.breathe{{transform-box:fill-box;transform-origin:center;animation:br 4.5s ease-in-out infinite alternate}}
@keyframes br{{from{{opacity:.5;transform:scale(.88)}}to{{opacity:1;transform:scale(1.08)}}}}</style>
<defs><linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{COBALT}"/><stop offset=".5" stop-color="#14275a"/><stop offset="1" stop-color="{ICE}"/></linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#07112e"/><stop offset="1" stop-color="{NAVY}"/></linearGradient>
<radialGradient id="core" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#6fb0ff" stop-opacity=".75"/><stop offset=".45" stop-color="{COBALT}" stop-opacity=".32"/><stop offset="1" stop-color="{COBALT}" stop-opacity="0"/></radialGradient></defs>
<rect x="1" y="1" width="958" height="358" rx="16" fill="url(#bg)" stroke="url(#bd)" stroke-width="1.6"/>
{tiles}{seps}
<line x1="28" y1="104" x2="932" y2="104" stroke="#14275a"/>
<text x="32" y="128" font-family="monospace" font-size="10.5" letter-spacing="3" fill="{ICE}">&gt; ACTIVITY · 12 MONTHS</text>
<g transform="translate(0 -4)">{bars(st["days"], 64, 168)}</g>
<text x="32" y="298" font-family="monospace" font-size="9.5" fill="#7f9bd6">Less</text>{legend}
<text x="152" y="298" font-family="monospace" font-size="9.5" fill="#7f9bd6">More</text>
<text x="32" y="346" font-family="monospace" font-size="9" fill="#3d5590">synced {now:%H:%M} IST</text>
<line x1="656" y1="116" x2="656" y2="346" stroke="#14275a"/>
<circle cx="800" cy="188" r="96" fill="url(#core)" class="breathe"/>
{tesseract.svg(800, 188, scale=78, c_cube=ICE, c_w=COBALT, blur=2.6, wc=1.8)}
{now_card}
</svg>"""
