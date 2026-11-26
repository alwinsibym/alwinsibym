"""Data layer: GitHub + weather fetching, each with an offline fallback."""
import base64, datetime as dt, json, os, random, re, urllib.request

USER = "alwinsibym"
CITY, LAT, LON = "Kottayam, Kerala", 9.5916, 76.5222
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
TOKEN = os.environ.get("GITHUB_TOKEN", "")
PROJECTS = ["BluePrint", "mediaforge", "malayalam-meme-extension", "personal_website"]


def http(url, data=None, headers=None, raw=False):
    h = {"User-Agent": "profile-readme-builder"}
    if TOKEN and "github" in url:
        h["Authorization"] = f"Bearer {TOKEN}"
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read()
    return body if raw else json.loads(body)


def safe(fn, fallback):
    try:
        return fn()
    except Exception as e:  # network blocked, rate limit, etc.
        print(f"[fallback] {fn.__name__}: {e}")
        return fallback


def now_ist():
    return dt.datetime.now(IST)


def weather():
    def go():
        u = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
             "&current=temperature_2m,weather_code&daily=sunrise,sunset"
             "&timezone=Asia%%2FKolkata&forecast_days=1" % (LAT, LON))
        j = http(u)
        t = lambda s: dt.datetime.fromisoformat(s).replace(tzinfo=IST)
        return dict(code=j["current"]["weather_code"], temp=j["current"]["temperature_2m"],
                    sunrise=t(j["daily"]["sunrise"][0]), sunset=t(j["daily"]["sunset"][0]))
    d = now_ist().replace(hour=0, minute=0, second=0, microsecond=0)
    return safe(go, dict(code=2, temp=29.0, sunrise=d.replace(hour=6, minute=15),
                         sunset=d.replace(hour=18, minute=10)))


def phase(now, w):
    """dawn / day / evening / dusk / night."""
    m = dt.timedelta(minutes=1)
    sr, ss = w["sunrise"], w["sunset"]
    if sr - 50 * m <= now < sr + 40 * m:
        return "dawn"
    if sr + 40 * m <= now < ss - 70 * m:
        return "day"
    if ss - 70 * m <= now < ss + 5 * m:
        return "evening"
    if ss + 5 * m <= now < ss + 50 * m:
        return "dusk"
    return "night"


LANG_COLORS = {"Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
               "HTML": "#e34c26", "CSS": "#9b6bd6", "Java": "#b07219", "C++": "#f34b7d",
               "C": "#8a8a8a", "SCSS": "#c6538c", "Jupyter Notebook": "#da5b0b"}


def repos():
    def go():
        r = http(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
        return [x for x in r if not x["fork"]]
    sample = [dict(name=n, description=d, stargazers_count=1, language=l, html_url=f"https://github.com/{USER}/{n}")
              for n, d, l in [
        ("BluePrint", "AI-assisted software planning platform with local multi-agent LLMs.", "TypeScript"),
        ("mediaforge", "A media converter that runs on your own machine.", "Python"),
        ("malayalam-meme-extension", "A fun, interactive browser extension that shows alerts in Malayalam.", "TypeScript"),
        ("personal_website", "Responsive portfolio with live GitHub data.", "HTML")]]
    return safe(go, sample)


def pinned(all_repos):
    """Pinned repos via GraphQL; otherwise the PROJECTS list."""
    def go():
        q = '{user(login:"%s"){pinnedItems(first:6,types:REPOSITORY){nodes{... on Repository{name}}}}}' % USER
        j = http("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
                 headers={"Content-Type": "application/json"})
        return [n["name"] for n in j["data"]["user"]["pinnedItems"]["nodes"]]
    names = safe(go, []) or PROJECTS
    by = {r["name"].lower(): r for r in all_repos}
    out = [by[n.lower()] for n in names if n.lower() in by]
    return out[:4]


def og_image(repo):
    """Repo social preview image as a data URI (SVG images cannot hotlink)."""
    def go():
        b = http(f"https://opengraph.githubassets.com/1/{USER}/{repo}", raw=True)
        return "data:image/png;base64," + base64.b64encode(b).decode()
    return safe(go, None)


def language_mix(all_repos):
    c = {}
    for r in all_repos:
        if r.get("language"):
            c[r["language"]] = c.get(r["language"], 0) + 1
    return sorted(c.items(), key=lambda kv: -kv[1])[:7]


def commits():
    """Latest commit messages from public push events."""
    out = []
    for e in events():
        if e["type"] == "PushEvent":
            repo = e["repo"]["name"].split("/")[-1]
            for c in reversed(e["payload"].get("commits", [])):
                out.append((repo, c["message"].splitlines()[0]))
    return out[:7] or [("mediaforge", "release: 1.5.0"), ("mediaforge", "ci: run smoke test"),
                       ("BluePrint", "feat: architecture agent"), ("personal_website", "style: dark theme"),
                       ("minnal_murali", "feat: audio controls"), ("mediaforge", "docs: car presets")]


START_YEAR = 2022  # account created Sep 2022


def calendar():
    """Every day since START_YEAR plus commit counts per year."""
    def go():
        if not TOKEN:
            raise RuntimeError("no token")
        today = now_ist().date()
        seen, commits = {}, {}
        for y in range(START_YEAR, today.year + 1):
            frm, to = f"{y}-01-01T00:00:00Z", f"{min(dt.date(y, 12, 31), today)}T23:59:59Z"
            q = ('{user(login:"%s"){contributionsCollection(from:"%s",to:"%s"){totalCommitContributions '
                 'contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}' % (USER, frm, to))
            j = http("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
                     headers={"Content-Type": "application/json"})
            cc = j["data"]["user"]["contributionsCollection"]
            commits[y] = cc["totalCommitContributions"]
            for w in cc["contributionCalendar"]["weeks"]:
                for d in w["contributionDays"]:
                    seen[d["date"]] = max(seen.get(d["date"], 0), d["contributionCount"])
        return sorted(i for i in seen.items() if i[0] <= str(today)), commits

    def sample():
        rnd = random.Random(7)
        today = now_ist().date()
        days = []
        for i in range(365 * 3, -1, -1):
            d = today - dt.timedelta(days=i)
            n = rnd.choice([0, 0, 0, 1, 2, 3, 5, 8]) if i > 11 else rnd.choice([3, 5, 8, 12])
            days.append((d.isoformat(), n))
        return days, {today.year - 2: 80, today.year - 1: 140, today.year: 254}
    return safe(go, sample())


def streaks(days):
    """(current, best) over the whole history; today may still be empty."""
    best = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        best = max(best, run)
    cur = 0
    for i, (_, n) in enumerate(reversed(days)):
        if n:
            cur += 1
        elif i > 0:
            break
    return cur, best


def activity_stats():
    days, commits = calendar()
    cur, best = streaks(days)
    yr = now_ist().year
    return dict(days=days[-365:], current=cur, best=best,
                year_commits=commits.get(yr, 0), total_commits=sum(commits.values()))


_events = []


def events():
    if not _events:
        _events.extend(safe(lambda: http(f"https://api.github.com/users/{USER}/events/public?per_page=30"), []))
    return _events


def ago(then, now):
    s = int((now - then).total_seconds())
    if s < 3600:
        return f"{max(1, s // 60)}m ago"
    return f"{s // 3600}h ago" if s < 86400 else f"{s // 86400}d ago"


def latest_repo():
    """The repo of the most recent push."""
    for e in events():
        if e["type"] == "PushEvent":
            cs = e["payload"].get("commits", [])
            name = e["repo"]["name"].split("/")[-1]
            when = dt.datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
            return dict(name=name, url=f"https://github.com/{e['repo']['name']}",
                        msg=(cs[-1]["message"].splitlines()[0] if cs else ""), ago=ago(when, now_ist()))
    return dict(name="mediaforge", url=f"https://github.com/{USER}/mediaforge", msg="release: 1.5.0", ago="2h ago")


def profile(all_repos):
    def go():
        j = http(f"https://api.github.com/users/{USER}")
        return dict(followers=j["followers"], repos=j["public_repos"])
    p = safe(go, dict(followers=7, repos=len(all_repos)))
    p["stars"] = sum(r["stargazers_count"] for r in all_repos)
    return p
