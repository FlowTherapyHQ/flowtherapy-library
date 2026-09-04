from pathlib import Path
import re
import sys


# ============================================================
# FLOWTHERAPY LIBRARY ARTICLE MIGRATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"

LINKTREE = "https://linktr.ee/flow.therapy"

ARTICLE_CSS = "../assets/css/library-article.css"

MARKER = "<!-- FLOWLIBRARY BATCH SHELL -->"


HEADER = f"""
{MARKER}
<header class="flowlibrary-header">
  <nav class="flowlibrary-nav">

    <a class="flowlibrary-brand" href="../index.html">

      <span class="flowlibrary-brand-name">
        FlowTherapy <span>Library</span>
      </span>

      <span class="flowlibrary-tagline">
        Prepare • Recover • Learn • Continue
      </span>

    </a>

    <div class="flowlibrary-links">

      <a href="../index.html#library">
        FlowNotes
      </a>

      <a href="../index.html#about">
        About
      </a>

      <a
        class="flowlibrary-return"
        href="{LINKTREE}"
      >
        FlowTherapy →
      </a>

    </div>

  </nav>
</header>
""".strip()


AUTHOR = f"""
<section class="library-author-card">

  <div class="library-author-photo">

    <img
      src="../assets/brandy-flowtherapist.png"
      alt="Brandy Hennigan, LMT"
    />

  </div>

  <div class="library-author-content">

    <span class="library-author-label">
      The Therapist Behind the Library
    </span>

    <h2>
      Brandy Hennigan, LMT
    </h2>

    <p>
      Brandy is a licensed massage therapist and founder of
      <strong>FlowTherapy Massage Co.</strong>
      The FlowTherapy Library was created to make information
      about massage, movement, recovery and everyday body
      mechanics easier to understand and more practical to use.
    </p>

  </div>

  <div class="library-author-actions">

    <a
      class="library-author-button primary"
      href="{LINKTREE}"
    >
      Return to FlowTherapy
    </a>

    <a
      class="library-author-button secondary"
      href="../index.html#library"
    >
      Explore FlowNotes
    </a>

  </div>

</section>
""".strip()


FOOTER = f"""
<footer class="flowlibrary-footer">

  © 2026 FlowTherapy Massage Co.
  &nbsp;•&nbsp;

  <a href="{LINKTREE}">
    Return to FlowTherapy
  </a>

  <div class="flowlibrary-footer-tagline">
    Move Better. Feel Better. Live Better.
  </div>

</footer>
""".strip()


def replace_once(pattern, replacement, text, flags=0):
    """
    Replace first occurrence only.
    Returns: updated_text, replacements_made
    """
    return re.subn(
        pattern,
        replacement,
        text,
        count=1,
        flags=flags,
    )


def convert_article(path: Path, apply_changes: bool):
    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    original = text
    changes = []


    # --------------------------------------------------------
    # Skip pages already converted
    # --------------------------------------------------------

    if MARKER in text:
        return "SKIP", [
            "already contains FlowLibrary shell"
        ]


    # --------------------------------------------------------
    # 1. Add shared FlowLibrary article CSS
    # --------------------------------------------------------

    if "library-article.css" not in text:

        css_link = (
            f'\n    <link rel="stylesheet" '
            f'href="{ARTICLE_CSS}" />\n'
        )

        text, count = replace_once(
            r"</head>",
            css_link + "  </head>",
            text,
            flags=re.IGNORECASE,
        )

        if count:
            changes.append(
                "added FlowLibrary article stylesheet"
            )


    # --------------------------------------------------------
    # 2. Replace old generated header placeholder
    # --------------------------------------------------------

    text, count = replace_once(
        r"""
        <!--\s*Shared\ header\ generated\ by\ site-layout\.js\s*-->
        \s*
        <div\s+id=["']site-header["']\s*>\s*</div>
        """,
        HEADER,
        text,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    if not count:

        text, count = replace_once(
            r'<div\s+id=["\']site-header["\']\s*>\s*</div>',
            HEADER,
            text,
            flags=re.IGNORECASE,
        )

    if count:
        changes.append(
            "replaced FlowHub header"
        )


    # --------------------------------------------------------
    # 3. Standardize TOP article-back link
    #
    # Preserve the container, but return to FlowLibrary.
    # --------------------------------------------------------

    top_back_pattern = r"""
        <div\s+class=["']article-back["']\s*>
        .*?
        </div>
    """

    top_back = """
<div class="article-back">
  <a href="../index.html#library">
    ← Back to FlowTherapy Library
  </a>
</div>
""".strip()

    text, count = replace_once(
        top_back_pattern,
        top_back,
        text,
        flags=re.IGNORECASE
        | re.DOTALL
        | re.VERBOSE,
    )

    if count:
        changes.append(
            "standardized top Library return link"
        )


    # --------------------------------------------------------
    # 4. Replace existing author-card
    # --------------------------------------------------------

    author_pattern = r"""
        <section\s+
        class=["']author-card["']
        \s*>
        .*?
        </section>
    """

    text, count = replace_once(
        author_pattern,
        AUTHOR,
        text,
        flags=re.IGNORECASE
        | re.DOTALL
        | re.VERBOSE,
    )

    if count:
        changes.append(
            "standardized Brandy author panel"
        )


    # --------------------------------------------------------
    # 5. Change old booking URLs to FlowTherapy Linktree
    #
    # This prevents old Setmore/legacy booking links
    # remaining in migrated educational content.
    # --------------------------------------------------------

    replacements = [
        (
            r'https?://flowtherapy\.setmore\.com[^"\']*',
            LINKTREE,
        ),
        (
            r'https?://(?:www\.)?discoverflowtherapy\.com[^"\']*',
            LINKTREE,
        ),
    ]

    for pattern, replacement in replacements:

        updated, count = re.subn(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE,
        )

        if count:
            text = updated

            changes.append(
                f"updated {count} legacy FlowTherapy destination(s)"
            )


    # --------------------------------------------------------
    # 6. Standardize Schedule/CTA button language
    #
    # URL is Linktree, so change old scheduling text.
    # --------------------------------------------------------

    text, count = re.subn(
        r">\s*Schedule Your Session\s*</a>",
        ">Return to FlowTherapy</a>",
        text,
        flags=re.IGNORECASE,
    )

    if count:
        changes.append(
            "updated legacy scheduling button text"
        )


    # --------------------------------------------------------
    # 7. Standardize BOTTOM article-back link
    # --------------------------------------------------------

    bottom_pattern = r"""
        <div\s+
        class=["']article-back\s+article-back-bottom["']
        \s*>
        .*?
        </div>
    """

    bottom_replacement = """
<div class="article-back article-back-bottom">
  <a href="../index.html#library">
    ← Return to FlowTherapy Library
  </a>
</div>
""".strip()

    text, count = replace_once(
        bottom_pattern,
        bottom_replacement,
        text,
        flags=re.IGNORECASE
        | re.DOTALL
        | re.VERBOSE,
    )

    if count:
        changes.append(
            "standardized bottom Library return link"
        )


    # --------------------------------------------------------
    # 8. REMOVE obsolete Future FlowNotes
    # --------------------------------------------------------

    future_pattern = r"""
        <section\s+
        class=["']future-flownotes-static["']
        \s*>
        .*?
        </section>
    """

    text, count = re.subn(
        future_pattern,
        "",
        text,
        flags=re.IGNORECASE
        | re.DOTALL
        | re.VERBOSE,
    )

    if count:
        changes.append(
            "removed obsolete Future FlowNotes"
        )


    # --------------------------------------------------------
    # 9. Replace old generated footer placeholder
    # --------------------------------------------------------

    footer_pattern = r"""
        <!--\s*Shared\ footer\ generated\ by\ site-layout\.js\s*-->
        \s*
        <div\s+id=["']site-footer["']\s*>\s*</div>
    """

    text, count = replace_once(
        footer_pattern,
        FOOTER,
        text,
        flags=re.IGNORECASE
        | re.VERBOSE,
    )

    if not count:

        text, count = replace_once(
            r'<div\s+id=["\']site-footer["\']\s*>\s*</div>',
            FOOTER,
            text,
            flags=re.IGNORECASE,
        )

    if count:
        changes.append(
            "replaced FlowHub footer"
        )


    # --------------------------------------------------------
    # 10. Remove site-layout.js
    #
    # Header/footer are now static.
    # --------------------------------------------------------

    text, count = re.subn(
        r"""
        \s*
        <script
        \s+
        src=["']
        /?assets/js/site-layout\.js
        ["']
        \s*
        >
        \s*
        </script>
        """,
        "",
        text,
        flags=re.IGNORECASE
        | re.VERBOSE,
    )

    if count:
        changes.append(
            "removed obsolete site-layout.js"
        )


    # --------------------------------------------------------
    # 11. Fix absolute asset paths
    #
    # /assets/... fails when GitHub Pages is hosted
    # underneath a repository path.
    # --------------------------------------------------------

    text, href_count = re.subn(
        r'href=(["\'])/assets/',
        r'href=\1../assets/',
        text,
        flags=re.IGNORECASE,
    )

    text, src_count = re.subn(
        r'src=(["\'])/assets/',
        r'src=\1../assets/',
        text,
        flags=re.IGNORECASE,
    )

    asset_count = href_count + src_count

    if asset_count:
        changes.append(
            f"fixed {asset_count} absolute asset path(s)"
        )


    # --------------------------------------------------------
    # 12. Make old FlowNotes-page links return to Library
    # --------------------------------------------------------

    text, count = re.subn(
        r'href=(["\'])\.\./pages/flownotes\.html\1',
        'href="../index.html#library"',
        text,
        flags=re.IGNORECASE,
    )

    if count:
        changes.append(
            "updated old FlowNotes-page link"
        )


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if text == original:
        return "UNCHANGED", []


    if apply_changes:

        path.write_text(
            text,
            encoding="utf-8",
        )

        return "UPDATED", changes


    return "WOULD UPDATE", changes


def main():
    apply_changes = "--apply" in sys.argv

    if not ARTICLES_DIR.exists():
        print(
            f"ERROR: Articles directory not found:\n"
            f"{ARTICLES_DIR}"
        )
        sys.exit(1)


    files = sorted(
        ARTICLES_DIR.glob("*.html")
    )


    if not files:
        print(
            "ERROR: No HTML files found in articles/"
        )
        sys.exit(1)


    print()
    print("=" * 62)
    print("FLOWTHERAPY LIBRARY ARTICLE BATCH")
    print("=" * 62)

    if apply_changes:
        print("MODE: APPLY CHANGES")
    else:
        print("MODE: DRY RUN — NO FILES WILL BE CHANGED")

    print()
    print(
        f"Found {len(files)} HTML files."
    )
    print()


    updated = 0
    skipped = 0
    unchanged = 0


    for path in files:

        status, changes = convert_article(
            path,
            apply_changes,
        )


        print(
            f"{status:12} {path.name}"
        )


        for change in changes:
            print(
                f"             • {change}"
            )


        if status in (
            "UPDATED",
            "WOULD UPDATE",
        ):
            updated += 1

        elif status == "SKIP":
            skipped += 1

        else:
            unchanged += 1


    print()
    print("=" * 62)

    if apply_changes:

        print(
            f"Completed: {updated} updated, "
            f"{skipped} skipped, "
            f"{unchanged} unchanged."
        )

    else:

        print(
            f"Dry run: {updated} would update, "
            f"{skipped} already converted, "
            f"{unchanged} unchanged."
        )

        print()
        print(
            "If everything above looks correct, run:"
        )

        print()
        print(
            "python tools/batch-library-articles.py --apply"
        )


    print("=" * 62)
    print()


if __name__ == "__main__":
    main()