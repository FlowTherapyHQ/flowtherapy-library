from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"
INDEX_FILE = ROOT / "index.html"

MEASUREMENT_ID = "G-N1Q7YEW5MF"

GA_TAG = f"""  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={MEASUREMENT_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', '{MEASUREMENT_ID}');
  </script>

"""


def install_ga(path: Path, apply_changes: bool):
    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    # Already installed — never duplicate it.
    if MEASUREMENT_ID in text:
        return "SKIP"

    if "<head>" not in text:
        return "NO HEAD"

    updated = text.replace(
        "<head>",
        "<head>\n" + GA_TAG,
        1,
    )

    if apply_changes:
        path.write_text(
            updated,
            encoding="utf-8",
        )
        return "UPDATED"

    return "WOULD UPDATE"


def main():
    apply_changes = "--apply" in sys.argv

    files = [INDEX_FILE]
    files.extend(
        sorted(ARTICLES_DIR.glob("*.html"))
    )

    print()
    print("=" * 60)
    print("FLOWTHERAPY GA4 INSTALLER")
    print("=" * 60)

    if apply_changes:
        print("MODE: APPLY CHANGES")
    else:
        print("MODE: DRY RUN — NO FILES WILL BE CHANGED")

    print(f"Measurement ID: {MEASUREMENT_ID}")
    print()

    updated = 0
    skipped = 0
    errors = 0

    for path in files:
        status = install_ga(
            path,
            apply_changes,
        )

        relative = path.relative_to(ROOT)

        print(
            f"{status:12} {relative}"
        )

        if status in ("UPDATED", "WOULD UPDATE"):
            updated += 1
        elif status == "SKIP":
            skipped += 1
        else:
            errors += 1

    print()
    print("=" * 60)

    if apply_changes:
        print(
            f"Completed: {updated} updated, "
            f"{skipped} already tagged, "
            f"{errors} problems."
        )
    else:
        print(
            f"Dry run: {updated} would update, "
            f"{skipped} already tagged, "
            f"{errors} problems."
        )

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()