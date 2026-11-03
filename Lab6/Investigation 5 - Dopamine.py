import re
from pathlib import Path
from PIL import Image, ExifTags

image_dir = Path("Lab6/Images") if Path("Lab6").exists() else Path("Images")
image_path = image_dir / "Dopamine.png"

# Investigation 5: Dopamine.png
with Image.open(image_path) as img:
    # Step 1 - Try EXIF. Returns 0 tags.
    print("EXIF tags:", len(img.getexif()))

    # Step 2 - Inspect PNG text. No readable clue (only the XMP packet).
    print("PNG text keys:", [k for k, v in img.info.items() if isinstance(v, (str, bytes))])

    # Step 3 - Inspect XMP. The clue is in the <exif:MakerNote> element.
    xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="replace")
    if xmp:
        xmp = xmp.replace("\ufeff", "")  # strip BOM so the Windows console can print it
    print("\nXMP packet:\n" + (xmp if xmp else "No XMP found"))

    match = re.search(r"<exif:MakerNote>(.*?)</exif:MakerNote>", xmp or "", re.S)
    print("Partial secret:", match.group(1).strip() if match else "not found")

