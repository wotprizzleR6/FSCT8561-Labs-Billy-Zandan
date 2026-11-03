from pathlib import Path
import pypdf

lab6_dir = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6")
pdf_files = list(lab6_dir.glob("*.pdf"))

for pdf_path in pdf_files:
    print("=" * 60)
    print("PDF:", pdf_path.name)
    reader = pypdf.PdfReader(str(pdf_path))
    num_pages = len(reader.pages)
    print(f"Total pages: {num_pages}")

    # Search for keywords
    keywords = ["exif", "metadata", "Pillow", "PIL", "covert", "steganography", "xmp"]
    matches = {kw: [] for kw in keywords}

    for page_idx in range(num_pages):
        try:
            text = reader.pages[page_idx].extract_text() or ""
            text_lower = text.lower()
            for kw in keywords:
                if kw in text_lower:
                    matches[kw].append(page_idx + 1)
        except Exception as e:
            pass

    print("Keyword page occurrences:")
    for kw, pages in matches.items():
        print(f"  {kw}: {len(pages)} pages -> {pages[:15]}...")

    # Let's check table of contents or outline
    print("\nOutline / Bookmarks:")
    try:
        outline = reader.outline
        def print_outline(items, depth=0):
            for item in items:
                if isinstance(item, list):
                    print_outline(item, depth + 1)
                else:
                    title = getattr(item, 'title', str(item))
                    page = reader.get_destination_page_number(item) if hasattr(reader, 'get_destination_page_number') else '?'
                    if any(term in title.lower() for term in ['forensic', 'meta', 'image', 'exif', 'crypto', 'covert', 'steg']):
                        print("  " * depth + f"- {title} (page {page})")
        print_outline(outline[:30] if isinstance(outline, list) else [])
    except Exception as e:
        print("  Outline error:", e)
