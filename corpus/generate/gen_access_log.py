#!/usr/bin/env python3
"""Generate a deterministic synthetic web-server access log (Apache combined
format). Seeded RNG => identical bytes on every run, so the committed corpus
file can be regenerated and checked against MANIFEST.sha256.

Usage: gen_access_log.py <out.log>
"""
import random
import sys

LINES = 4000
random.seed(20260709)

PATHS = (
    ["/", "/index.html", "/about.html", "/contact.html", "/pricing.html",
     "/blog/", "/feed.xml", "/robots.txt", "/favicon.ico", "/sitemap.xml"]
    + [f"/blog/post-{i}.html" for i in range(1, 40)]
    + [f"/static/css/style-{i}.css" for i in range(1, 6)]
    + [f"/static/js/app-{i}.js" for i in range(1, 8)]
    + [f"/static/img/photo-{i}.jpg" for i in range(1, 60)]
    + [f"/api/v1/items/{i}" for i in range(1, 120)]
)
AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Bingbot/2.0 (+http://www.bing.com/bingbot.htm)",
    "curl/8.6.0",
]
REFERERS = ["-", "-", "-", "https://www.google.com/", "https://news.ycombinator.com/",
            "https://duckduckgo.com/", "https://example.com/links.html"]
STATUS = [200] * 80 + [304] * 10 + [404] * 5 + [301, 302, 500, 403, 206]
METHODS = ["GET"] * 90 + ["POST"] * 7 + ["HEAD"] * 3

MONTH = "Jul"
DAY_START = 1


def main(dst: str) -> None:
    lines = []
    ts_day, ts_h, ts_m, ts_s = DAY_START, 0, 0, 0
    for _ in range(LINES):
        ts_s += random.randint(1, 45)
        if ts_s > 59:
            ts_m += ts_s // 60
            ts_s %= 60
        if ts_m > 59:
            ts_h += ts_m // 60
            ts_m %= 60
        if ts_h > 23:
            ts_day += ts_h // 24
            ts_h %= 24
        ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        when = f"{ts_day:02d}/{MONTH}/2026:{ts_h:02d}:{ts_m:02d}:{ts_s:02d} +0000"
        method = random.choice(METHODS)
        path = random.choice(PATHS)
        status = random.choice(STATUS)
        size = random.randint(180, 250000) if status in (200, 206) else 0
        ref = random.choice(REFERERS)
        agent = random.choice(AGENTS)
        lines.append(f'{ip} - - [{when}] "{method} {path} HTTP/1.1" {status} {size} "{ref}" "{agent}"')
    with open(dst, "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
