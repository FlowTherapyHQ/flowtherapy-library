from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[2]
BUFFER_DIR = Path(__file__).resolve().parent

QUEUE_FILE = BUFFER_DIR / "content_queue.json"
PREVIEW_FILE = BUFFER_DIR / "bluesky_previews.json"


def load_articles():
    if not QUEUE_FILE.exists():
        raise RuntimeError(
            "content_queue.json not found. Run build_inventory.py first."
        )

    return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))


def build_post(article):
    title = article["title"]
    description = article.get("description", "").strip()
    url = article["url"]

    # First-pass template only.
    # We will improve voice after reviewing the batch.
    if description:
        text = (
            f"{title}\n\n"
            f"{description}\n\n"
            f"Read the FlowNote ↓\n"
            f"{url}"
        )
    else:
        text = (
            f"{title}\n\n"
            f"A new FlowNote from the FlowTherapy Library.\n\n"
            f"Read the FlowNote ↓\n"
            f"{url}"
        )

    return {
        "slug": article["slug"],
        "title": title,
        "url": url,
        "text": text,
        "characters": len(text),
        "approved": False,
        "buffer_status": "not_sent",
    }


def main():
    articles = load_articles()

    # First 10 only while we establish the FlowTherapy social voice.
    batch = articles[:10]

    previews = [build_post(article) for article in batch]

    PREVIEW_FILE.write_text(
        json.dumps(previews, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print()
    print("FlowTherapy Bluesky Preview Batch")
    print("---------------------------------")
    print(f"Drafts generated: {len(previews)}")
    print(f"Saved to: {PREVIEW_FILE}")
    print()

    for number, preview in enumerate(previews, start=1):
        print("=" * 60)
        print(f"{number}. {preview['title']}")
        print(f"Characters: {preview['characters']}")
        print("-" * 60)
        print(preview["text"])
        print()

    print("=" * 60)
    print("PREVIEW ONLY — nothing was sent to Buffer.")


if __name__ == "__main__":
    main()