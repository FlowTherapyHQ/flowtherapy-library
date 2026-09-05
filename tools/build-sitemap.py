from pathlib import Path
from datetime import datetime, timezone
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "articles"
SITEMAP_FILE = ROOT / "sitemap.xml"

BASE_URL = "https://library.discoverflowtherapy.com"


def last_modified(path):
    timestamp = path.stat().st_mtime
    return datetime.fromtimestamp(
        timestamp, tz=timezone.utc
    ).date().isoformat()


def make_url(location, modified):
    return f"""  <url>
    <loc>{escape(location)}</loc>
    <lastmod>{modified}</lastmod>
  </url>"""


def main():
    if not ARTICLES_DIR.exists():
        raise RuntimeError("articles directory not found.")

    article_files = sorted(ARTICLES_DIR.glob("*.html"))

    urls = []

    # FlowTherapy Library homepage
    homepage = ROOT / "index.html"
    if homepage.exists():
        urls.append(
            make_url(
                f"{BASE_URL}/",
                last_modified(homepage),
            )
        )

    # Every published FlowNote
    for article in article_files:
        urls.append(
            make_url(
                f"{BASE_URL}/articles/{article.name}",
                last_modified(article),
            )
        )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )

    SITEMAP_FILE.write_text(sitemap, encoding="utf-8")

    print("FlowTherapy Sitemap Builder")
    print("---------------------------")
    print(f"Homepage: 1")
    print(f"FlowNotes: {len(article_files)}")
    print(f"Total URLs: {len(urls)}")
    print(f"Created: {SITEMAP_FILE}")


if __name__ == "__main__":
    main()