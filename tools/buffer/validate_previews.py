from pathlib import Path
import json


BUFFER_DIR = Path(__file__).resolve().parent
PREVIEW_FILE = BUFFER_DIR / "bluesky_previews.json"
PATREON_FILE = BUFFER_DIR / "patreon_queue.json"

MAX_CHARS = 260


def validate_posts(file_path, text_field, label):
    if not file_path.exists():
        raise RuntimeError(f"{file_path.name} not found.")

    posts = json.loads(
        file_path.read_text(encoding="utf-8")
    )

    passed = 0
    failed = 0

    print()
    print(label)
    print("-" * len(label))
    print(f"Maximum characters: {MAX_CHARS}")
    print()

    for number, post in enumerate(posts, start=1):
        text = post.get(text_field, "")
        count = len(text)

        post["characters"] = count

        failure_reason = None

        # Safety rail #1: FlowTherapy character limit
        if count > MAX_CHARS:
            failure_reason = (
                f"exceeds {MAX_CHARS}-character limit"
            )

        # Safety rail #2: video posts require a video URL
        elif post.get("media_type") == "video":
            video_url = post.get("video_url", "").strip()

            if not video_url:
                failure_reason = "video_url is required"

        if failure_reason:
            post["validation"] = "FAIL"
            failed += 1
            symbol = "FAIL"
        else:
            post["validation"] = "PASS"
            passed += 1
            symbol = "PASS"

        print(
            f"{number:02}. {symbol} | "
            f"{count}/{MAX_CHARS} | "
            f"{post.get('title', 'Untitled')}"
        )

        if failure_reason:
            print(
                f"    REASON: {failure_reason}"
            )

    file_path.write_text(
        json.dumps(
            posts,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print()
    print("-" * len(label))
    print(f"PASS: {passed}")
    print(f"FAIL: {failed}")
    print()

    return failed


def main():
    total_failed = 0

    total_failed += validate_posts(
        PREVIEW_FILE,
        "text",
        "FlowTherapy Bluesky Validator",
    )

    total_failed += validate_posts(
        PATREON_FILE,
        "caption",
        "FlowTherapy Patreon Validator",
    )

    if total_failed:
        print(
            "STOP — one or more posts failed "
            "FlowTherapy validation."
        )
    else:
        print(
            "ALL CLEAR — every post passed "
            "FlowTherapy validation."
        )


if __name__ == "__main__":
    main()