"""Regenerates every asset the profile README uses. Run by .github/workflows/update.yml."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import activity, cards, data, scene

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", name, len(text), "bytes")


def inject(tag, html):
    path = os.path.join(OUT, "..", "README.md")
    text = open(path, encoding="utf-8").read()
    a, b = text.find(f"<!--{tag}:START-->"), text.find(f"<!--{tag}:END-->")
    if a >= 0 and b >= 0:
        open(path, "w", encoding="utf-8").write(text[:a] + f"<!--{tag}:START-->\n{html}\n" + text[b:])


def inject_cards(pins):
    """Fill the CARDS block in README.md so each card links to the right repo."""
    path = os.path.join(OUT, "..", "README.md")
    text = open(path, encoding="utf-8").read()
    a, b = text.find("<!--CARDS:START-->"), text.find("<!--CARDS:END-->")
    if a < 0 or b < 0:
        return
    cells = [f'<td><a href="{r["html_url"]}"><img src="assets/card-{i}.svg" width="410" alt="{r["name"]}"/></a></td>'
             for i, r in enumerate(pins, 1)]
    rows = ["<tr>" + "".join(cells[i:i + 2]) + "</tr>" for i in range(0, len(cells), 2)]
    block = '<!--CARDS:START-->\n<div align="center"><table>' + "".join(rows) + "</table></div>\n"
    open(path, "w", encoding="utf-8").write(text[:a] + block + text[b:])


def main():
    os.makedirs(OUT, exist_ok=True)
    now, w = data.now_ist(), data.weather()
    ph = data.phase(now, w)
    allr = data.repos()
    print(f"{now:%H:%M} IST · {ph} · code {w['code']} · {w['temp']}°C")
    write("scene.svg", scene.build(now, w, ph, data.commits(), data.language_mix(allr)))
    pins = data.pinned(allr)
    for i, r in enumerate(pins, 1):
        write(f"card-{i}.svg", cards.card(r, data.og_image(r["name"])))
    inject_cards(pins)
    st, repo = data.activity_stats(), data.latest_repo()
    write("activity.svg", activity.build(st, repo, now))
    inject("LATEST", f'<p align="center"><sub>Latest push: <a href="{repo["url"]}"><b>{repo["name"]}</b></a>'
                     f' · {repo["msg"]} · {repo["ago"]}</sub></p>')
    p = data.profile(allr)
    print("profile:", p)


if __name__ == "__main__":
    main()
