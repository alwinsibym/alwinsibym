"""Contribution heatmap + streak stats, drawn in the emerald/gold theme."""
import datetime as dt

GOLD = "#d4a843"
LEVELS = ["#0f2a20", "#14573e", "#1f8a5b", "#6fbf73", "#d4a843"]


def level(n, cuts):
    if n <= 0:
        return 0
    return 1 + sum(n > c for c in cuts)


def build(days, total_all, cur, best):
    vals = sorted(n for _, n in days if n)
    cuts = [vals[len(vals) * q // 4] for q in (1, 2, 3)] if len(vals) >= 4 else [1, 2, 4]
    year = sum(n for _, n in days)
    first = dt.date.fromisoformat(days[0][0])
    off = (first.weekday() + 1) % 7  # Sunday-first rows
    x0, y0, cell, gap = 28, 62, 12, 2
    cells, months, seen = [], [], set()
    for i, (d, n) in enumerate(days):
        idx = i + off
        col, row = idx // 7, idx % 7
        c = LEVELS[level(n, cuts)]
        cx, cy = x0 + col * (cell + gap), y0 + row * (cell + gap)
        cls = ' class="pulse"' if level(n, cuts) == 4 and i > len(days) - 20 else ""
        cells.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" fill="{c}"{cls}><title>{d}: {n}</title></rect>')
        m = dt.date.fromisoformat(d)
        if m.day <= 7 and (m.year, m.month) not in seen and row == 0 or (m.day == 1 and (m.year, m.month) not in seen):
            seen.add((m.year, m.month))
            months.append(f'<text x="{cx}" y="52" font-family="monospace" font-size="10" fill="#6f9784">{m.strftime("%b")}</text>')
    legend = "".join(f'<rect x="{610 + i * 16}" y="188" width="12" height="12" fill="{c}"/>' for i, c in enumerate(LEVELS))

    def stat(y, label, val, unit=""):
        return (f'<text x="800" y="{y}" font-family="monospace" font-size="10" letter-spacing="1.5" fill="#6f9784">{label}</text>'
                f'<text x="800" y="{y + 26}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-weight="700" font-size="26" fill="#f1ead2">'
                f'{val}<tspan dx="5" font-size="13" fill="{GOLD}">{unit}</tspan></text>')
    stats = (stat(58, "CURRENT STREAK", cur, "days") + stat(100, "BEST STREAK", best, "days")
             + stat(142, "THIS YEAR", year) + stat(184, "ALL-TIME TOTAL", max(total_all, year)))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="224" viewBox="0 0 960 224" role="img" aria-label="Contribution activity">
<style>.pulse{{animation:p 2.2s ease-in-out infinite alternate}}@keyframes p{{from{{opacity:.65}}to{{opacity:1}}}}</style>
<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GOLD}"/><stop offset=".5" stop-color="#1f8a5b"/><stop offset="1" stop-color="{GOLD}"/></linearGradient></defs>
<rect x="1" y="1" width="958" height="222" rx="14" fill="#07130e" stroke="url(#b)" stroke-width="1.6"/>
<text x="28" y="32" font-family="monospace" font-size="12" letter-spacing="3" fill="{GOLD}">&gt; ACTIVITY</text>
<text x="196" y="32" font-family="monospace" font-size="11" fill="#6f9784">{year} contributions in the last year</text>
{''.join(months)}{''.join(cells)}
<text x="560" y="198" font-family="monospace" font-size="10" fill="#6f9784">Less</text>{legend}
<text x="694" y="198" font-family="monospace" font-size="10" fill="#6f9784">More</text>
<line x1="780" y1="40" x2="780" y2="200" stroke="#1d4a37"/>{stats}
</svg>"""
