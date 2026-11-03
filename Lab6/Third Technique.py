import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

# Reconfigure stdout to handle UTF-8 cleanly on Windows hosts
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

image_path = Path("Images") / "Dopamine.png"

with Image.open(image_path) as img:
    xmp_raw = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp_raw, bytes):
        xmp_raw = xmp_raw.decode("utf-8", errors="replace")
    
    # Strip Windows / ExifTool Byte Order Mark (\ufeff)
    xmp_clean = xmp_raw.lstrip("\ufeff")
    print(f"Raw XMP Packet Excerpt (first 300 chars):\n{xmp_clean[:300]}\n")
    
    # Parse XML structure
    root = ET.fromstring(xmp_clean)
    for elem in root.iter():
        if elem.tag.endswith("MakerNote") and elem.text:
            print(f"Recovered XML Element: <{elem.tag}>")
            print(f"Extracted Secret: {elem.text.strip()}")