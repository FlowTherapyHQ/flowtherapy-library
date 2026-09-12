import os
import json
import re
import urllib.request
from pathlib import Path


BUFFER_API_URL = "https://api.buffer.com"
CHANNEL_ID = "6a9c3848065799be46942349"
MAX_CHARS = 260
UTM_QUERY = "utm_source=bs"
# ============================================================
# FLOWTHERAPY PUBLISHING MODE
#
# "review" = send approved posts to Buffer Drafts
# "auto"   = send approved posts to Buffer Queue
#
# AUTO NEVER MEANS "PUBLISH NOW."
# Buffer will use your Tue / Thu / Sun posting schedule.
# ============================================================

PUBLISH_MODE = "review"

BUFFER_DIR = Path(__file__).resolve().parent

CONTENT_SOURCES = [
    {
        "name": "FlowNotes",
        "file": BUFFER_DIR / "bluesky_previews.json",
        "text_field": "text",
    },
    {
        "name": "Flow Table Talk",
        "file": BUFFER_DIR / "patreon_queue.json",
        "text_field": "caption",
    },
]


def load_env():
    env_file = Path(__file__).resolve().parents[2] / ".env"

    if not env_file.exists():
        raise RuntimeError(".env file not found.")

    for line in env_file.read_text(
        encoding="utf-8"
    ).splitlines():
        line = line.strip()

        if (
            not line
            or line.startswith("#")
            or "=" not in line
        ):
            continue

        key, value = line.split("=", 1)

        os.environ.setdefault(
            key.strip(),
            value.strip(),
        )


def buffer_graphql(query, variables=None):
    api_key = os.environ.get("BUFFER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "BUFFER_API_KEY was not found."
        )

    payload = {
        "query": query
    }

    if variables is not None:
        payload["variables"] = variables

    request = urllib.request.Request(
        BUFFER_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )

def add_utm_tracking(text, source_name):
    """
    Add FlowTherapy UTM tracking to FlowNote URLs only.

    Flow Table Talk is intentionally left unchanged for now
    because its current captions may already be near the
    260-character FlowTherapy limit.
    """
    if source_name != "FlowNotes":
        return text

    url_pattern = (
        r"https://library\.discoverflowtherapy\.com/"
        r"[^\s]+"
    )

    def add_tracking(match):
        url = match.group(0)

        if "utm_source=" in url:
            return url

        separator = "&" if "?" in url else "?"

        return f"{url}{separator}{UTM_QUERY}"

    return re.sub(
        url_pattern,
        add_tracking,
        text,
    )
def create_buffer_post(text):
    save_to_draft = PUBLISH_MODE == "review"

    query = """
    mutation CreatePost(
        $text: String!,
        $saveToDraft: Boolean!
    ) {
      createPost(
        input: {
          text: $text
          channelId: "6a9c3848065799be46942349"
          schedulingType: automatic
          mode: addToQueue
          saveToDraft: $saveToDraft
        }
      ) {
        ... on PostActionSuccess {
          post {
            id
            text
            status
          }
        }

        ... on MutationError {
          message
        }
      }
    }
    """

    return buffer_graphql(
        query,
        variables={
            "text": text,
            "saveToDraft": save_to_draft,
        },
    )


def process_source(source):
    file_path = source["file"]
    source_name = source["name"]
    text_field = source["text_field"]

    if not file_path.exists():
        raise RuntimeError(
            f"{file_path.name} not found."
        )

    posts = json.loads(
        file_path.read_text(
            encoding="utf-8"
        )
    )

    action_name = (
        "DRAFT CREATED"
        if PUBLISH_MODE == "review"
        else "QUEUED"
    )

    status_name = (
        "draft"
        if PUBLISH_MODE == "review"
        else "queued"
    )

    print()
    print(source_name)
    print("-" * len(source_name))

    sent = 0
    skipped = 0
    failed = 0

    for number, post in enumerate(
        posts,
        start=1,
    ):
        text = post.get(
            text_field,
            "",
        )

        # Safety rail #1:
        # Human approval required.
        if not post.get("approved"):
            print(
                f"{number:02}. SKIP — "
                "not approved"
            )
            skipped += 1
            continue

        # Safety rail #2:
        # Validator must have passed.
        if post.get("validation") != "PASS":
            print(
                f"{number:02}. SKIP — "
                "not validated"
            )
            skipped += 1
            continue

        # Safety rail #3:
        # Text cannot be blank.
        if not text.strip():
            print(
                f"{number:02}. SKIP — "
                "empty content"
            )
            skipped += 1
            continue

        # Safety rail #4:
        # Hard FlowTherapy character limit.
        if len(text) > MAX_CHARS:
            print(
                f"{number:02}. SKIP — "
                f"{len(text)}/{MAX_CHARS} "
                "characters"
            )
            skipped += 1
            continue

        # Safety rail #5:
        # Never send the same record twice.
        if (
            post.get("buffer_status")
            != "not_sent"
        ):
            print(
                f"{number:02}. SKIP — "
                "already processed"
            )
            skipped += 1
            continue

        result = create_buffer_post(text)

        created = (
            result.get("data", {})
            .get("createPost", {})
            .get("post")
        )

        if created:
            post["buffer_status"] = status_name
            post["buffer_post_id"] = created["id"]

            print(
                f"{number:02}. "
                f"{action_name} — "
                f"{len(text)}/{MAX_CHARS} | "
                f"{post.get('title', 'Untitled')}"
            )

            sent += 1

        else:
            print(
                f"{number:02}. ERROR — "
                f"{post.get('title', 'Untitled')}"
            )

            print(
                json.dumps(
                    result,
                    indent=2,
                )
            )

            failed += 1

    file_path.write_text(
        json.dumps(
            posts,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Sent: {sent}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")

    return {
        "sent": sent,
        "skipped": skipped,
        "failed": failed,
    }


def send_content_batch():
    if PUBLISH_MODE not in (
        "review",
        "auto",
    ):
        raise RuntimeError(
            'PUBLISH_MODE must be '
            '"review" or "auto".'
        )

    print()
    print("FlowTherapy Content Engine")
    print("--------------------------")
    print(
        f"MODE: {PUBLISH_MODE.upper()}"
    )

    if PUBLISH_MODE == "review":
        print(
            "Destination: Buffer Drafts"
        )
    else:
        print(
            "Destination: Buffer Queue"
        )

    totals = {
        "sent": 0,
        "skipped": 0,
        "failed": 0,
    }

    for source in CONTENT_SOURCES:
        result = process_source(source)

        for key in totals:
            totals[key] += result[key]

    print()
    print("--------------------------")
    print("TOTAL")

    if PUBLISH_MODE == "review":
        print(
            f"DRAFTS CREATED: "
            f"{totals['sent']}"
        )
    else:
        print(
            f"POSTS QUEUED: "
            f"{totals['sent']}"
        )

    print(
        f"SKIPPED: {totals['skipped']}"
    )
    print(
        f"FAILED: {totals['failed']}"
    )
    print()


if __name__ == "__main__":
    load_env()
    send_content_batch()