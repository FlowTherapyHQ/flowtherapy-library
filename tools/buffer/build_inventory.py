from pathlib import Path
from html.parser import HTMLParser
import json
import re


ROOT = Path(__file__).resolve().parents[2]
ARTICLES_DIR = ROOT / "articles"
OUTPUT_FILE = Path(__file__).resolve().parent / "content_queue.json"

SITE_BASE = "https://library.discoverflowtherapy.com/articles/"


class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_h1 = False
        self.in_description = False

        self.title = ""
        self.h1 = ""
        self.description = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "title":
            self.in_title = True

        elif tag == "h1" and not self.h1:
            self.in_h1 = True

        elif tag == "meta":
            name = attrs.get("name", "").lower()

            if name == "description":
                self.description = attrs.get("content", "").strip()

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

        elif tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data

        if self.in_h1:
            self.h1 += data


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def read_article(path):
    parser = ArticleParser()

    try:
        html = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        html = path.read_text(encoding="utf-8", errors="replace")

    parser.feed(html)

    title = clean_text(parser.h1) or clean_text(parser.title)

    # Remove common site-title suffixes if <title> was used.
    title = re.sub(
        r"\s*[|\-–—]\s*FlowTherapy.*$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    return {
        "slug": path.stem,
        "title": title,
        "description": clean_text(parser.description),
        "url": f"{SITE_BASE}{path.name}",
        "source_file": f"articles/{path.name}",
        "status": "ready",
        "buffer_status": "not_sent",
    }


def main():
    if not ARTICLES_DIR.exists():
        raise RuntimeError(f"Articles folder not found: {ARTICLES_DIR}")

    articles = []

    for path in sorted(ARTICLES_DIR.glob("*.html")):
        article = read_article(path)

        if not article["title"]:
            print(f"SKIPPED — no title found: {path.name}")
            continue

        articles.append(article)

    OUTPUT_FILE.write_text(
        json.dumps(articles, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("FlowTherapy Content Inventory")
    print("-----------------------------")
    print(f"Articles found: {len(articles)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print()

    for article in articles:
        print(f"- {article['title']}")
        print(f"  {article['url']}")


if __name__ == "__main__":
    main()