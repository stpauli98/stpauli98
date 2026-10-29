"""Pravi dark_mode.svg i light_mode.svg.

ASCII portret se cita iz ascii_dark.txt i ascii_light.txt. Kad promijenis portrait.png,
napravi ih ponovo (treba Pillow i numpy):
    python ascii.py portrait.png 56 44 dark > ascii_dark.txt
    python ascii.py portrait.png 56 44 light > ascii_light.txt

GitHub statistika se cita uzivo preko GraphQL API-ja. Token se uzima iz GH_TOKEN,
a lokalno iz `gh auth token`.
"""
import json, os, subprocess, urllib.request
from datetime import date
from html import escape

USER = "stpauli98"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

W = 60          # sirina desne kolone u znacima
X_INFO = 430
ASCII_COLS, ASCII_ROWS, ASCII_FS, ASCII_LH = 56, 44, 12, 15

THEMES = {
    "dark": dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff", cc="#616e7f"),
    "light": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069", cc="#c2cfde"),
}


def uptime(born=date(1998, 11, 15), today=date.today()):
    y = today.year - born.year
    m = today.month - born.month
    d = today.day - born.day
    if d < 0:
        m -= 1
        prev = date(today.year, today.month, 1).toordinal() - 1
        d += date.fromordinal(prev).day
    if m < 0:
        y -= 1
        m += 12
    return f"{y} years, {m} months, {d} days"


def t(s, cls=None, id=None):
    a = (f' class="{cls}"' if cls else "") + (f' id="{id}"' if id else "")
    return f"<tspan{a}>{escape(s)}</tspan>"


def kv(keys, value, width, vid=None):
    """'. Key.Sub: ..... value' tacno `width` znakova."""
    keytxt = ".".join(keys)
    dots = width - len(". ") - len(keytxt) - len(": ") - len(" ") - len(value)
    assert dots >= 1, (keys, value, dots)
    keyparts = ".".join(t(k, "key") for k in keys)
    dotsid = f"{vid}_dots" if vid else None
    return keyparts + ":" + t(" " + "." * dots + " ", "cc", dotsid) + t(value, "value", vid)


def row(*parts):
    return t(". ", "cc") + "".join(parts)


def header(title):
    fill = W - len(title) - len(" -") - len("-—-")
    return escape(title) + " -" + "—" * fill + "-—-"


def graphql(query):
    token = os.environ.get("GH_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}"})
    res = json.load(urllib.request.urlopen(req))
    if "errors" in res:
        raise SystemExit(res["errors"])
    return res["data"]["user"]


def github_stats():
    u = graphql(f"""{{ user(login: "{USER}") {{
        repositories(ownerAffiliations: OWNER) {{ totalCount }}
        public: repositories(ownerAffiliations: OWNER, privacy: PUBLIC) {{ totalCount }}
        repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY]) {{ totalCount }}
        contributionsCollection {{ contributionYears }}
    }} }}""")
    years = u["contributionsCollection"]["contributionYears"]
    per_year = graphql("{ user(login: \"%s\") { %s } }" % (USER, " ".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") '
        "{ totalCommitContributions totalPullRequestContributions contributionCalendar { totalContributions } }"
        for y in years)))
    this_year = per_year.get(f"y{date.today().year}")
    return {
        "repos": u["repositories"]["totalCount"],
        "public": u["public"]["totalCount"],
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "commits": sum(v["totalCommitContributions"] for v in per_year.values()),
        "prs": sum(v["totalPullRequestContributions"] for v in per_year.values()),
        "year": this_year["contributionCalendar"]["totalContributions"] if this_year else 0,
    }


STATS = github_stats()

INFO = [
    ("raw", header("nikola@milosevic")),
    ("row", kv(["Status"], "Open to full-time roles · Graz / Remote", W)),
    ("row", kv(["Uptime"], uptime(), W, "age_data")),
    ("row", kv(["Host"], "Graz, Austria", W)),
    ("row", kv(["Kernel"], "Full-Stack Software Engineer", W)),
    ("row", kv(["Experience"], "NextPixel, Rabensteiner Engineering", W)),
    ("row", kv(["Education"], "BSc Health Informatics, FH JOANNEUM", W)),
    ("row", ""),
    ("row", kv(["Languages", "Programming"], "TypeScript, JavaScript, Python", W)),
    ("row", kv(["Languages", "Computer"], "HTML, CSS, SQL, JSON", W)),
    ("row", kv(["Languages", "Real"], "Serbian, German (C1+), English", W)),
    ("row", ""),
    ("row", kv(["Stack", "Frontend"], "React, Next.js, Tailwind CSS", W)),
    ("row", kv(["Stack", "Backend"], "Node.js, NestJS, Flask, PostgreSQL", W)),
    ("row", kv(["Stack", "Mobile"], "React Native, Expo", W)),
    ("row", kv(["Stack", "Cloud"], "Docker, Cloud Run, Vercel, Supabase", W)),
    ("row", kv(["Stack", "AI"], "OpenAI API, RAG, n8n", W)),
    ("row", kv(["Tools"], "Claude Code, Git, Figma, Stripe", W)),
    (None, None),
    ("raw", header("- Projects")),
    ("row", kv(["Forecast Engine"], "forecast-engine.com", W)),
    ("row", kv(["AddMemories"], "dodajuspomenu.com", W)),
    ("row", kv(["Termin"], "terminonlineapp.com", W)),
    ("row", kv(["Servisna Knjižica"], "servisnaknjizica.app", W)),
    (None, None),
    ("raw", header("- Contact")),
    ("row", kv(["Email"], "nikola@nextpixel.dev", W)),
    ("row", kv(["Web"], "nextpixel.dev", W)),
    (None, None),
    ("raw", header("- GitHub Stats")),
]


def half(keys, value, width, vid):
    return kv(keys, value, width, vid)


L = 29  # sirina lijeve polovine statistike, ukljucujuci '. '
R = W - L - len(" | ") + len(". ")
INFO += [
    ("row", half(["Repos"], f"{STATS['repos']} {{Public: {STATS['public']}}}", L, "repo_data")
            + " | " + half(["Commits"], f"{STATS['commits']:,}", R, "commit_data")),
    ("row", half(["Pull Requests"], f"{STATS['prs']:,}", L, "pr_data")
            + " | " + half(["Contributions", str(date.today().year)], f"{STATS['year']:,}", R, "year_data")),
]


def build(theme):
    c = THEMES[theme]
    art = open(f"{HERE}/ascii_{theme}.txt").read().splitlines()
    art += [""] * (ASCII_ROWS - len(art))
    height = 30 + (ASCII_ROWS - 1) * ASCII_LH + 20
    info_h = 30 + (len(INFO) - 1) * 20 + 20
    height = max(height, info_h)
    width = X_INFO + int(W * 9.6) + 20

    out = [f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{width}px" height="{height}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {c['key']};}}
.value {{fill: {c['value']};}}
.cc {{fill: {c['cc']};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="{width}px" height="{height}px" fill="{c['bg']}" rx="15"/>
<text x="15" y="30" fill="{c['text']}" font-size="{ASCII_FS}px" class="ascii">"""]
    for i, line in enumerate(art):
        out.append(f'<tspan x="15" y="{30 + i * ASCII_LH}">{escape(line)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="{X_INFO}" y="30" fill="{c["text"]}">')
    for i, (kind, body) in enumerate(INFO):
        if kind is None:
            continue
        y = 30 + i * 20
        if kind == "raw":
            title, rest = body.split(" -", 1)
            out.append(f'<tspan x="{X_INFO}" y="{y}">{title}</tspan> -{rest}')
        else:
            out.append(f'<tspan x="{X_INFO}" y="{y}" class="cc">. </tspan>{body}')
    out.append("</text>\n</svg>\n")
    open(f"{OUT}/{theme}_mode.svg", "w").write("\n".join(out))


for th in THEMES:
    build(th)
print("ok")
