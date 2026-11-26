"""Project cards (social preview + name + stars + description + url + language) and the activity panel."""
import hashlib, textwrap
from xml.sax.saxutils import escape
from data import LANG_COLORS

GOLD, EM = "#d4a843", "#1f8a5b"
BG, BG2, LINE = "#07130e", "#0c2217", "#1d4a37"


def wrap(text, width=50, lines=2):
    parts = textwrap.wrap(text or "No description yet.", width)
    if len(parts) > lines:
        parts = parts[:lines]
        parts[-1] = parts[-1][: width - 1].rstrip(" .,") + "…"
    return parts


def fallback_preview(name):
    """Deterministic pixel banner used when the social preview can't be fetched."""
    h = hashlib.sha256(name.encode()).digest()
    cells = []
    for j in range(7):
        for i in range(12):
            v = h[(i * 7 + j) % len(h)]
            if v % 3 == 0:
                shade = ("#0f4d36", "#1f8a5b", "#d4a843")[v % 3 + (v >> 5) % 3 % 2]
                for mx in (i, 23 - i):
                    cells.append(f'<rect x="{mx * 16 + 6}" y="{j * 16 + 4}" width="14" height="14" fill="{shade}" opacity=".55"/>')
    return (f'<rect width="396" height="120" fill="{BG2}"/>' + "".join(cells)
            + f'<text x="198" y="68" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="22" '
              f'fill="#e8f5ee">{escape(name)}</text>')


def card(repo, preview_uri):
    name = repo["name"]
    stars = repo.get("stargazers_count", 0)
    lang = repo.get("language") or "—"
    col = LANG_COLORS.get(lang, "#8aa")
    url = repo.get("html_url", "").replace("https://", "")
    desc = "".join(f'<text x="22" y="{176 + i * 17}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="13" '
                   f'fill="#a9c4b6">{escape(t)}</text>' for i, t in enumerate(wrap(repo.get("description"))))
    img = (f'<image href="{preview_uri}" x="0" y="0" width="396" height="198" preserveAspectRatio="xMidYMid slice" '
           f'transform="translate(0 -39)"/>' if preview_uri else fallback_preview(name))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="272" viewBox="0 0 420 272" role="img" aria-label="{escape(name)} repository card">
<defs><clipPath id="r"><rect x="12" y="12" width="396" height="120" rx="8"/></clipPath>
<linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD}"/><stop offset=".5" stop-color="{EM}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient></defs>
<rect x="1" y="1" width="418" height="270" rx="14" fill="{BG}" stroke="url(#b)" stroke-width="1.6"/>
<g clip-path="url(#r)" transform="translate(12 12)">{img}</g>
<rect x="12" y="12" width="396" height="120" rx="8" fill="none" stroke="{LINE}"/>
<text x="22" y="156" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-weight="700" font-size="18" fill="#f1ead2">{escape(name)}</text>
<text x="398" y="156" text-anchor="end" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="14" fill="{GOLD}">★ {stars}</text>
{desc}
<line x1="22" y1="222" x2="398" y2="222" stroke="{LINE}"/>
<text x="22" y="247" font-family="monospace" font-size="11.5" fill="#6f9784">{escape(url)}</text>
<circle cx="338" cy="243" r="5" fill="{col}"/>
<text x="348" y="247" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="12" fill="#cfe3d8">{escape(lang)}</text>
</svg>"""
