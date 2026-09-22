import html, json, re
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone

ROOT = Path(__file__).parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
SITE = CFG["site_url"].rstrip("/")
USER = CFG["channel_username"].lstrip("@")
CHANNEL = CFG.get("channel_url", f"https://t.me/{USER}")
MAX_POSTS = int(CFG.get("max_posts", 100))

req = Request(f"https://t.me/s/{USER}", headers={"User-Agent": "Mozilla/5.0"})
with urlopen(req, timeout=30) as r:
    source = r.read().decode("utf-8", errors="ignore")

blocks = re.findall(
    r'<div[^>]+class="[^"]*tgme_widget_message[^"]*"[^>]*>(.*?)(?=<div[^>]+class="[^"]*tgme_widget_message\b|</main>)',
    source, flags=re.S
)

posts = []
for block in blocks[-MAX_POSTS:]:
    m = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', block, flags=re.S)
    if not m:
        continue
    text = re.sub(r"<br\s*/?>", "\n", m.group(1), flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).strip()
    if not text:
        continue
    lm = re.search(r'href="https://t\.me/[^"]+/(\d+)"', block)
    post_id = lm.group(1) if lm else str(abs(hash(text)))
    posts.append((post_id, text))

(ROOT / "posts").mkdir(exist_ok=True)
post_links = []
urls = [SITE + "/"]

for post_id, text in posts:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:70]
    slug = f"{slug}-{post_id}" if slug else f"telegram-post-{post_id}"
    page_url = f"{SITE}/posts/{slug}.html"
    title = re.sub(r"\s+", " ", text).strip()[:100]
    description = re.sub(r"\s+", " ", text).strip()[:155]

    paragraphs = "".join(
        f"<p>{html.escape(x)}</p>" for x in text.splitlines() if x.strip()
    )

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | Anak Airdrop Indonesia</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{html.escape(page_url)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
</head>
<body>
<main>
<h1>{html.escape(title)}</h1>
{paragraphs}
<p><a href="{CHANNEL}">Join Anak Airdrop Indonesia on Telegram</a></p>
<p><a href="{CHANNEL}/{post_id}">View original Telegram post</a></p>
</main>
</body>
</html>"""

    (ROOT / "posts" / f"{slug}.html").write_text(page, encoding="utf-8")
    post_links.append(f'<li><a href="{SITE}/posts/{slug}.html">{html.escape(title)}</a></li>')
    urls.append(page_url)

template = (ROOT / "index.html").read_text(encoding="utf-8")
(ROOT / "index.html").write_text(
    template.replace("{{SITE_URL}}", SITE).replace("{{POST_LINKS}}", "\n".join(post_links)),
    encoding="utf-8"
)

robots = (ROOT / "robots.txt").read_text(encoding="utf-8").replace("{{SITE_URL}}", SITE)
(ROOT / "robots.txt").write_text(robots, encoding="utf-8")

today = datetime.now(timezone.utc).date().isoformat()
items = "".join(f"<url><loc>{html.escape(u)}</loc><lastmod>{today}</lastmod></url>" for u in urls)
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
sitemap += items + "</urlset>"
(ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

print(f"Generated {len(posts)} Telegram post pages.")
