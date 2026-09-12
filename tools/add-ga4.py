from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GA4_BLOCK = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-N1Q7YEW5MF"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-N1Q7YEW5MF');
</script>
"""

html_files = [ROOT / "index.html"] + sorted((ROOT / "articles").glob("*.html"))

updated = 0
skipped = 0

for path in html_files:
    text = path.read_text(encoding="utf-8")

    if "G-N1Q7YEW5MF" in text:
        print(f"SKIP  {path.relative_to(ROOT)}")
        skipped += 1
        continue

    if "<head>" not in text:
        print(f"NO HEAD  {path.relative_to(ROOT)}")
        continue

    text = text.replace("<head>", "<head>\n" + GA4_BLOCK, 1)
    path.write_text(text, encoding="utf-8")

    print(f"ADD   {path.relative_to(ROOT)}")
    updated += 1

print()
print(f"Updated: {updated}")
print(f"Skipped: {skipped}")
print(f"Checked: {len(html_files)}")