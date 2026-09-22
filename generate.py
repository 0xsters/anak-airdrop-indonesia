import html
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone

ROOT = Path(__file__).parent

# =========================
# LOAD CONFIG
# =========================

CFG = json.loads(
    (ROOT / "config.json").read_text(encoding="utf-8")
)

SITE = CFG["site_url"].rstrip("/")
USER = CFG["channel_username"].lstrip("@")
CHANNEL = CFG.get(
    "channel_url",
    f"https://t.me/{USER}"
)

MAX_POSTS = int(
    CFG.get("max_posts", 100)
)

# =========================
# FETCH TELEGRAM POSTS
# =========================

print(f"Fetching Telegram channel: {USER}")

req = Request(
    f"https://t.me/s/{USER}",
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urlopen(req, timeout=30) as response:
    source = response.read().decode(
        "utf-8",
        errors="ignore"
    )

# =========================
# FIND TELEGRAM MESSAGE BLOCKS
# =========================

blocks = re.findall(
    r'<div[^>]+class="[^"]*tgme_widget_message[^"]*"[^>]*>'
    r'(.*?)(?=<div[^>]+class="[^"]*tgme_widget_message\b|</main>)',
    source,
    flags=re.S
)

posts = []

for block in blocks[-MAX_POSTS:]:

    # Find message text
    match = re.search(
        r'tgme_widget_message_text[^>]*>(.*?)</div>',
        block,
        flags=re.S
    )

    if not match:
        continue

    text = match.group(1)

    # Convert <br> to new lines
    text = re.sub(
        r"<br\s*/?>",
        "\n",
        text,
        flags=re.I
    )

    # Remove HTML tags
    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    # Decode HTML entities
    text = html.unescape(text).strip()

    if not text:
        continue

    # Find Telegram post ID
    id_match = re.search(
        r'href="https://t\.me/[^"]+/(\d+)"',
        block
    )

    if id_match:
        post_id = id_match.group(1)
    else:
        post_id = str(
            abs(hash(text))
        )

    posts.append(
        (post_id, text)
    )

print(f"Found {len(posts)} Telegram posts.")

# =========================
# CREATE POSTS DIRECTORY
# =========================

POSTS_DIR = ROOT / "posts"

POSTS_DIR.mkdir(
    exist_ok=True
)

# =========================
# GENERATE POST PAGES
# =========================

post_links = []

urls = [
    SITE + "/"
]

for post_id, text in posts:

    # Create SEO-friendly slug
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        text.lower()
    ).strip("-")[:70]

    if slug:
        slug = f"{slug}-{post_id}"
    else:
        slug = f"telegram-post-{post_id}"

    # IMPORTANT:
    # Always use SITE here.
    # This prevents GitHub Pages project-path 404 errors.
    page_url = f"{SITE}/posts/{slug}.html"

    title = re.sub(
        r"\s+",
        " ",
        text
    ).strip()[:100]

    description = re.sub(
        r"\s+",
        " ",
        text
    ).strip()[:155]

    # Create paragraphs
    paragraphs = "".join(
        f"<p>{html.escape(line)}</p>"
        for line in text.splitlines()
        if line.strip()
    )

    # =========================
    # POST HTML
    # =========================

    page = f"""<!doctype html>
<html lang="en">
<head>

<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>
{html.escape(title)} | Anak Airdrop Indonesia
</title>

<meta
    name="description"
    content="{html.escape(description)}"
>

<link
    rel="canonical"
    href="{html.escape(page_url)}"
>

<meta
    property="og:title"
    content="{html.escape(title)} | Anak Airdrop Indonesia"
>

<meta
    property="og:description"
    content="{html.escape(description)}"
>

<meta
    property="og:url"
    content="{html.escape(page_url)}"
>

<meta
    property="og:type"
    content="article"
>

</head>

<body>

<main>

<h1>
{html.escape(title)}
</h1>

{paragraphs}

<p>
<a href="{CHANNEL}">
Join Anak Airdrop Indonesia on Telegram
</a>
</p>

<p>
<a href="{CHANNEL}/{post_id}">
View original Telegram post
</a>
</p>

<p>
<a href="{SITE}/">
Back to Anak Airdrop Indonesia
</a>
</p>

</main>

</body>
</html>
"""

    # Write post page
    post_file = POSTS_DIR / f"{slug}.html"

    post_file.write_text(
        page,
        encoding="utf-8"
    )

    # =========================
    # IMPORTANT FIX
    # =========================
    #
    # OLD:
    # /posts/example.html
    #
    # WRONG for:
    # https://0xsters.github.io/anak-airdrop-indonesia/
    #
    # NEW:
    # https://0xsters.github.io/anak-airdrop-indonesia/posts/example.html
    #

    post_links.append(
        f'<li>'
        f'<a href="{SITE}/posts/{slug}.html">'
        f'{html.escape(title)}'
        f'</a>'
        f'</li>'
    )

    urls.append(
        page_url
    )

# =========================
# GENERATE INDEX.HTML
# =========================
#
# IMPORTANT:
# We completely regenerate index.html
# instead of replacing {{POST_LINKS}}.
#
# This fixes the previous problem where
# old links remained after the first run.
# =========================

index_html = f"""<!doctype html>
<html lang="en">

<head>

<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1"
>

<title>
Anak Airdrop Indonesia | Crypto Airdrop, Testnet & Web3
</title>

<meta
    name="description"
    content="Anak Airdrop Indonesia — info crypto airdrop, testnet, mainnet, faucet and Web3 opportunities."
>

<link
    rel="canonical"
    href="{SITE}/"
>

<meta
    property="og:title"
    content="Anak Airdrop Indonesia"
>

<meta
    property="og:description"
    content="Info crypto airdrop, testnet, mainnet, faucet and Web3 Indonesia."
>

<meta
    property="og:url"
    content="{SITE}/"
>

<meta
    property="og:type"
    content="website"
>

</head>

<body>

<main>

<h1>
Anak Airdrop Indonesia
</h1>

<p>
Info airdrop crypto, testnet, mainnet, faucet and Web3 Indonesia.
</p>

<p>
<a href="{CHANNEL}">
Join Anak Airdrop Indonesia on Telegram
</a>
</p>

<h2>
Latest Airdrop Updates
</h2>

<ul>

{chr(10).join(post_links)}

</ul>

</main>

</body>

</html>
"""

(ROOT / "index.html").write_text(
    index_html,
    encoding="utf-8"
)

print("Generated index.html")

# =========================
# GENERATE ROBOTS.TXT
# =========================

robots = f"""User-agent: *
Allow: /

Sitemap: {SITE}/sitemap.xml
"""

(ROOT / "robots.txt").write_text(
    robots,
    encoding="utf-8"
)

print("Generated robots.txt")

# =========================
# GENERATE SITEMAP.XML
# =========================

today = datetime.now(
    timezone.utc
).date().isoformat()

items = ""

for url in urls:

    items += (
        "<url>"
        f"<loc>{html.escape(url)}</loc>"
        f"<lastmod>{today}</lastmod>"
        "</url>"
    )

sitemap = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset '
    'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    f"{items}"
    "</urlset>"
)

(ROOT / "sitemap.xml").write_text(
    sitemap,
    encoding="utf-8"
)

print("Generated sitemap.xml")

# =========================
# FINISHED
# =========================

print(
    f"Generated {len(posts)} Telegram post pages."
)

print(
    f"Website: {SITE}"
)

print(
    "Generation completed successfully."
)
