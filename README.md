# Anak Airdrop Indonesia — Telegram SEO Indexer

This project creates SEO-friendly static pages from the public Telegram preview of
https://t.me/AnakAirdropIndonesia.

It automatically:
- fetches recent public Telegram posts
- creates one HTML page per post
- creates sitemap.xml
- creates robots.txt
- links pages back to the Telegram channel
- runs every 6 hours with GitHub Actions
- optionally submits generated URLs to Bing Webmaster API

## Setup

1. Create a GitHub repository.
2. Upload these files to the repository.
3. Edit `config.json` and replace `site_url` with your GitHub Pages URL.
4. Enable GitHub Pages from Settings → Pages → Deploy from branch → main → root.
5. Run Actions → Update Telegram SEO Pages → Run workflow.
6. Add your generated website to Google Search Console and submit `/sitemap.xml`.
7. Add the same website to Bing Webmaster Tools.

Optional Bing automation:
- Repository secret `BING_SITE_URL`
- Repository secret `BING_API_KEY`

Never put API keys directly in the files.

Important: this does not force Google or Bing to index Telegram itself. It creates a
website you control that makes the Telegram channel and its public posts easier for
search crawlers to discover.
