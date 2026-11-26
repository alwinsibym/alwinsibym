"""Builds assets/scene.svg: a pixel study that reflects live data."""
import os
from xml.sax.saxutils import escape

W, H = 240, 135
GOLD, GOLD2 = "#d4a843", "#8a6a1f"
EM, EM2, EM3 = "#1f8a5b", "#0f4d36", "#0a2a1f"
INK = "#06100c"


def R(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def pix(grid, pal, x, y, s=1):
    """Draw an ASCII pixel map as merged horizontal runs."""
    out = []
    for j, row in enumerate(grid):
        i = 0
        while i < len(row):
            c = row[i]
            if c in pal:
                k = i
                while k < len(row) and row[k] == c:
                    k += 1
                out.append(R(x + i * s, y + j * s, (k - i) * s, s, pal[c]))
                i = k
            else:
                i += 1
    return "".join(out)


SKY = {"dawn": ("#2b2d5c", "#f0a07a"), "day": ("#3f9fe6", "#bfe6ff"),
       "evening": ("#3a2a5e", "#ff8a3d"), "dusk": ("#161638", "#a8456b"),
       "night": ("#040a18", "#12234a")}


def window(ph, code, temp):
    x, y, w, h = 8, 14, 56, 54
    top, bot = SKY[ph]
    o = [f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
         f'<stop offset="1" stop-color="{bot}"/></linearGradient>',
         '<clipPath id="win"><rect x="8" y="14" width="56" height="54"/></clipPath>']
    g = ['<g clip-path="url(#win)">', R(x, y, w, h, "url(#sky)")]
    if ph in ("night", "dusk", "dawn"):
        for i, (sx, sy) in enumerate([(14, 20), (26, 30), (40, 18), (52, 28), (20, 40), (58, 40), (34, 24)]):
            g.append(R(sx, sy, 1, 1, "#fff", f'class="tw" style="animation-delay:{i * .4}s"'))
    if ph in ("night", "dusk"):
        g.append(f'<circle cx="46" cy="24" r="5" fill="#f4f1d0"/>'
                 f'<circle cx="48.5" cy="22.5" r="4.2" fill="{SKY[ph][0]}"/>')
    else:
        sx, sy = {"dawn": (22, 52), "day": (40, 26), "evening": (50, 50)}[ph]
        col = "#ffe27a" if ph == "day" else "#ffb55c"
        g.append(f'<circle cx="{sx}" cy="{sy}" r="6" fill="{col}"/>')
    if code >= 2 or code in (45, 48):
        for cx, cy, s in [(18, 28, 1), (44, 38, 1.3)]:
            g.append(f'<g class="cl"><g transform="translate({cx} {cy}) scale({s})">'
                     + R(0, 3, 14, 3, "#c9d3e6", 'opacity=".85"') + R(3, 0, 8, 3, "#dfe7f5", 'opacity=".85"') + "</g></g>")
    if code >= 3:
        g.append(R(x, y, w, h, "#2a3140", 'opacity=".28"'))
    rain = code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99)
    if rain:
        for i in range(14):
            g.append(R(10 + i * 4, 14, 1, 3, "#9fc4ff", f'class="rn" style="animation-delay:{(i * .17) % 1:.2f}s"'))
    if code >= 95:
        g.append(R(x, y, w, h, "#fff", 'class="fl"'))
    # hills + palm silhouette (Kerala)
    g.append(f'<path d="M8 62 L8 56 Q22 48 34 56 Q48 46 64 55 L64 68 L8 68Z" fill="{INK}" opacity=".9"/>')
    g.append(R(52, 40, 1, 16, INK) + R(47, 40, 11, 1, INK) + R(49, 38, 7, 1, INK) + R(46, 42, 3, 1, INK) + R(56, 42, 3, 1, INK))
    g.append("</g>")
    frame = (R(x - 3, y - 3, w + 6, 3, GOLD2) + R(x - 3, y + h, w + 6, 4, GOLD2) + R(x - 3, y, 3, h, GOLD2)
             + R(x + w, y, 3, h, GOLD2) + R(x + w // 2 - 1, y, 2, h, GOLD2) + R(x, y + h // 2 - 1, w, 2, GOLD2))
    return "".join(o) + "".join(g) + frame


def wallpaper():
    o = [f'<pattern id="wp" width="12" height="12" patternUnits="userSpaceOnUse">'
         f'{R(0, 0, 12, 12, EM3)}{R(0, 0, 6, 12, "#0c3324")}'
         f'<path d="M9 3 L11 5 L9 7 L7 5Z" fill="{GOLD2}" opacity=".55"/></pattern>']
    o.append(R(0, 0, W, 96, "url(#wp)"))
    o.append(R(0, 0, W, 3, GOLD2) + R(0, 3, W, 1, GOLD))
    o.append(R(0, 92, W, 4, "#3d2b10") + R(0, 92, W, 1, GOLD))
    fl = [R(0, 96, W, 39, "#1a120a")]
    for i, yy in enumerate(range(96, 135, 6)):
        fl.append(R(0, yy, W, 1, "#0d0905"))
    for xx in range(0, W, 24):
        fl.append(R(xx + 12, 96, 1, 39, "#0d0905"))
    fl.append(R(60, 112, 120, 18, "#0d3a2a") + R(60, 112, 120, 1, GOLD) + R(60, 129, 120, 1, GOLD)
              + R(64, 116, 112, 10, "#0a2c20"))
    for xx in range(70, 172, 14):
        fl.append(f'<path d="M{xx + 4} 121 l3 -3 l3 3 l-3 3z" fill="{GOLD2}"/>')
    return "".join(o) + "".join(fl)


def monitor(commits, ph):
    x, y, w, h = 108, 38, 62, 38
    o = [R(x - 2, y - 2, w + 4, h + 4, "#10151a"), R(x, y, w, h, "#04120c"),
         '<clipPath id="scr"><rect x="110" y="46" width="58" height="28"/></clipPath>',
         R(x, y, w, 7, "#0b2a1d"),
         f'<text x="{x + 3}" y="{y + 5}" font-family="monospace" font-size="3.4" fill="{GOLD}">$ git log --oneline</text>']
    lines = []
    for r, m in commits:
        t = f"{r[:9]}: {m}"
        lines.append(t if len(t) <= 24 else t[:23] + "…")
    lines = lines or ["no recent commits"]
    lh = 5.2
    rows = []
    for rep in range(2):
        for i, t in enumerate(lines):
            yy = 51 + (rep * len(lines) + i) * lh
            rows.append(f'<text x="111" y="{yy:.1f}" font-family="monospace" font-size="3" fill="#4be3a0">'
                        f'{escape(t)}</text>')
    dist = len(lines) * lh
    o.append('<g clip-path="url(#scr)"><g class="sc" style="--d:%.1fpx;animation-duration:%ds">%s</g></g>'
             % (dist, max(8, len(lines) * 3), "".join(rows)))
    o.append(R(x + w // 2 - 4, y + h + 2, 8, 6, "#10151a") + R(x + w // 2 - 10, y + h + 7, 20, 2, "#10151a"))
    return "".join(o)


def desk():
    return (R(66, 82, 110, 4, "#4a2f12") + R(66, 82, 110, 1, GOLD2) + R(70, 86, 3, 10, "#2e1d0a")
            + R(169, 86, 3, 10, "#2e1d0a") + R(73, 86, 96, 3, "#33200b")
            + R(150, 78, 8, 4, "#e8e2d0") + R(151, 79, 6, 2, "#6b4a2a")  # mug
            + R(124, 80, 20, 2, "#10151a") + R(126, 80, 16, 1, "#2a323a"))  # keyboard


def chair():
    return (R(122, 84, 24, 4, "#0b1612") + R(130, 88, 8, 14, "#0b1612") + R(120, 100, 28, 2, "#0b1612")
            + R(132, 102, 4, 4, "#0b1612"))


def lamp(on):
    shade = "#ffd45a" if on else "#7a6a3a"
    o = [R(90, 80, 12, 2, "#10151a"), R(95, 62, 2, 18, "#10151a"), R(90, 54, 14, 3, "#10151a"),
         f'<path d="M89 58 L97 48 L105 58Z" fill="{shade}"/>']
    if on:
        o.insert(0, '<polygon points="89,58 105,58 120,96 78,96" fill="url(#cone)" class="gl"/>')
        o.append('<ellipse cx="97" cy="82" rx="20" ry="3" fill="#ffd45a" opacity=".22"/>')
    return "".join(o)


def clock(now):
    import math
    h = (now.hour % 12 + now.minute / 60) * 30
    m = (now.minute + now.second / 60) * 6
    sec = now.second * 6
    o = [f'<circle r="12" fill="{GOLD2}"/><circle r="10" fill="#f1ead2"/>']
    for k in range(12):
        a_ = math.radians(k * 30)
        o.append(R(round(8.2 * math.sin(a_) - .5, 1), round(-8.2 * math.cos(a_) - .5, 1), 1, 1,
                   "#2a2a2a" if k % 3 else "#8a1f1f"))
    o.append(f'<g transform="rotate({h:.1f})"><rect class="sp12" x="-.8" y="-5" width="1.6" height="5.5" fill="#1a1a1a"/></g>'
             f'<g transform="rotate({m:.1f})"><rect class="sp1" x="-.6" y="-8" width="1.2" height="8.5" fill="#1a1a1a"/></g>'
             f'<g transform="rotate({sec})"><rect class="sp60" x="-.3" y="-8.5" width=".6" height="9" fill="#c0392b"/></g>'
             '<circle r="1.2" fill="#c0392b"/>')
    return '<g transform="translate(208 17) scale(.8)">' + "".join(o) + "</g>"


BADGE = {"JavaScript": "JS", "TypeScript": "TS", "HTML": "<>", "CSS": "#", "Python": "Py", "Java": "J",
         "C++": "C+", "C": "C", "SCSS": "S", "Jupyter Notebook": "Nb", "Shell": "$_", "PHP": "ph"}


def book(x, shelf, h, name, col):
    top = shelf - h
    o = [R(x, top, 9, h, col), R(x, top, 1, h, "#00000050"), R(x + 7, top, 2, h, "#00000030"),
         R(x + 1, top, 6, 1, "#ffffff60")]
    o.append(R(x + 1, top + 2, 7, 7, "#101418") + R(x + 1, top + 2, 7, 1, "#ffffff30"))
    lab = BADGE.get(name, name[:2])
    o.append(f'<text x="{x + 4.5}" y="{top + 7.3}" text-anchor="middle" font-family="monospace" font-weight="bold" '
             f'font-size="3.6" fill="#fff">{escape(lab)}</text>')
    avail = h - 13
    nat = len(name) * 1.75
    if nat <= avail * 1.18:  # name fits (squeezed a little if needed); else logo only
        o.append(f'<text transform="translate({x + 5.4} {shelf - 2}) rotate(-90)" font-family="monospace" font-size="3.1" '
                 f'font-weight="bold" fill="#0b0b0b" textLength="{min(nat, avail):.1f}" lengthAdjust="spacingAndGlyphs">'
                 f'{escape(name)}</text>')
    return "".join(o)


def bookshelf(langs):
    from data import LANG_COLORS
    sx, ex = 182, 238
    shelves = (58, 88)
    o = []
    for sy in shelves:
        o.append(R(sx - 2, sy, ex - sx + 2, 3, "#4a2f12") + R(sx - 2, sy, ex - sx + 2, 1, GOLD2)
                 + R(sx - 2, sy + 3, ex - sx + 2, 1, "#00000060"))
    items = langs[:8]
    rows = [items[:5], items[5:]]
    heights = [[26, 24, 25, 26, 24], [24, 22, 23, 24, 22]]
    for r, row in enumerate(rows):
        x = sx
        for i, (name, _) in enumerate(row):
            o.append(book(x, shelves[r], heights[r][i], name, LANG_COLORS.get(name, "#5aa7a0")))
            x += 9.6
        if x + 9 <= ex:  # decor in the leftover space
            if r == 0:
                o.append(R(x + 1, shelves[r] - 7, 6, 7, "#7a4a22") + R(x, shelves[r] - 9, 8, 2, "#2f8a4b")
                         + R(x + 2, shelves[r] - 12, 4, 3, "#2f8a4b"))
            else:
                o.append(R(x + 1, shelves[r] - 7, 6, 7, "#e8e2d0")
                         + '<rect x="%.1f" y="%d" width="4" height="4" fill="#ffb347" class="gl"/>' % (x + 2, shelves[r] - 11))
    return "".join(o)


def cat():
    k, e = "#0f1714", "#38e08a"
    o = [R(184, 110, 44, 4, EM2) + R(184, 110, 44, 1, GOLD) + R(186, 114, 40, 2, EM3), R(196, 104, 22, 8, k) + R(214, 98, 10, 10, k) + R(214, 96, 2, 3, k) + R(222, 96, 2, 3, k)
         + R(216, 101, 2, 2, e) + R(220, 101, 2, 2, e) + R(196, 104, 22, 1, "#24382f") + R(214, 98, 10, 1, "#24382f") + R(190, 108, 8, 2, k) + R(188, 104, 3, 5, k)]
    o.append(f'<text class="zz" x="227" y="97" font-family="monospace" font-size="6" fill="{GOLD}">z</text>')
    o.append(f'<text class="zz" style="animation-delay:1s" x="232" y="91" font-family="monospace" font-size="4.5" fill="{GOLD}">z</text>')
    return "".join(o)


def plant():
    return (R(16, 100, 14, 12, "#7a3a22") + R(15, 98, 16, 3, "#9a4a2a") + R(22, 76, 2, 22, "#1a6b3a")
            + R(14, 82, 9, 3, "#2f9a5a") + R(24, 78, 10, 3, "#2f9a5a") + R(12, 90, 11, 3, "#1f8a4b") + R(24, 88, 10, 3, "#1f8a4b"))


EMBLEM = ["...yyyyy...", "..y.....y..", ".y..ggg..y.", ".y.gGGGg.y.", ".ygGyGyGgy.", ".ygGGGGGgy.",
          ".y.gGGGg.y.", ".y..gGg..y.", ".y...r...y.", ".y..r.r..y.", ".y.......y.", "..y.....y..",
          "...yyyyy...", "..........."]


def portrait():
    """Wall frame. Uses assets/portrait.png if the owner adds one, else an original serpent emblem."""
    x, y, w, h = 76, 12, 26, 34
    o = [R(x - 2, y - 2, w + 4, h + 4, GOLD2) + R(x - 1, y - 1, w + 2, h + 2, GOLD) + R(x, y, w, h, "#06180f")]
    path = os.path.join(os.path.dirname(__file__), "..", "assets", "portrait.png")
    if os.path.exists(path):
        import base64
        b = base64.b64encode(open(path, "rb").read()).decode()
        o.append(f'<image href="data:image/png;base64,{b}" x="{x}" y="{y}" width="{w}" height="{h}" '
                 f'preserveAspectRatio="xMidYMid slice" style="image-rendering:pixelated"/>')
    else:
        pal = {"y": GOLD, "g": "#1f9a63", "G": "#46d48f", "r": "#d8344a"}
        o.append(pix(EMBLEM, pal, x + 2, y + 3, 2))
    o.append(R(x + 6, y + h + 4, 14, 3, "#10151a") + R(x + 7, y + h + 5, 12, 1, GOLD2))
    return "".join(o)


def nameplate():
    return (R(106, 12, 66, 18, GOLD2) + R(107, 13, 64, 16, GOLD) + R(108, 14, 62, 14, "#0a1a12")
            + f'<text x="139" y="25" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="9.5" '
              f'textLength="50" lengthAdjust="spacingAndGlyphs" fill="{GOLD}">ALWIN SIBY</text>')


TINT = {"day": None, "dawn": (255, 140, 110, .16), "evening": (255, 100, 30, .20),
        "dusk": (40, 10, 90, .42), "night": (0, 6, 20, .66)}


def overlay(ph):
    t = TINT[ph]
    if not t:
        return ""
    r, g, b, a = t
    return ('<radialGradient id="dim" gradientUnits="userSpaceOnUse" cx="97" cy="62" r="175">'
            f'<stop offset="0" stop-color="rgb({r},{g},{b})" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="rgb({r},{g},{b})" stop-opacity="{a * .85:.2f}"/>'
            f'<stop offset="1" stop-color="rgb({r},{g},{b})" stop-opacity="{min(a * 1.1, .75):.2f}"/></radialGradient>'
            + R(0, 0, W, H, "url(#dim)"))


def css(dist, nlines):
    return f"""
.tw{{animation:tw 2.4s ease-in-out infinite}}@keyframes tw{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
.cl{{animation:cl 40s ease-in-out infinite alternate}}@keyframes cl{{to{{transform:translateX(10px)}}}}
.rn{{animation:rn .8s linear infinite}}@keyframes rn{{from{{transform:translateY(0);opacity:.9}}to{{transform:translateY(54px);opacity:0}}}}
.fl{{opacity:0;animation:fl 7s infinite}}@keyframes fl{{0%,92%,100%{{opacity:0}}94%{{opacity:.6}}96%{{opacity:0}}98%{{opacity:.4}}}}
.sc{{animation:sc linear infinite}}@keyframes sc{{to{{transform:translateY(-{dist:.1f}px)}}}}
.sp12{{animation:sp 43200s linear infinite}}.sp1{{animation:sp 3600s linear infinite}}.sp60{{animation:sp 60s steps(60) infinite}}
@keyframes sp{{to{{transform:rotate(360deg)}}}}
.gl{{animation:gl 3s ease-in-out infinite alternate}}@keyframes gl{{from{{opacity:.7}}to{{opacity:1}}}}
.zz{{animation:zz 3.4s ease-in-out infinite;opacity:0}}@keyframes zz{{0%{{opacity:0;transform:translateY(2px)}}50%{{opacity:1}}100%{{opacity:0;transform:translateY(-4px)}}}}
"""


def build(now, w, ph, commits, langs):
    from data import CITY
    on = ph != "day"
    nl = max(1, len(commits))
    dist = nl * 5.2
    defs = ('<linearGradient id="cone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd45a" stop-opacity=".5"/>'
            '<stop offset="1" stop-color="#ffd45a" stop-opacity="0"/></linearGradient>')
    body = [wallpaper(), plant(), chair(), cat(), desk(), portrait(), nameplate(), bookshelf(langs),
            lamp(on), overlay(ph), window(ph, w["code"], w["temp"]), monitor(commits, ph), clock(now)]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="960" height="540" '
            f'shape-rendering="crispEdges" role="img" aria-label="Pixel study in {CITY}: {ph}, {w["temp"]:.0f}°C">'
            f'<style>{css(dist, nl)}</style><defs>{defs}</defs>' + "".join(body) + "</svg>")
