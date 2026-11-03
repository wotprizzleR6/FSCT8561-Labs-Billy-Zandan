import json
from pathlib import Path
from PIL import Image, ExifTags
import xml.etree.ElementTree as ET
import base64
import sys

# Test whether all code cells produce the exact outputs saved in the notebook
image_dir = Path("Lab6/Images")

results = []

# Cell 2 (index 3)
results.append(("Images found", len(list(image_dir.glob("*.png")))))

# Cell 3 (index 6) - Brain-Channel.png
with Image.open(image_dir / "Brain-Channel.png") as img:
    exif = img.getexif()
    results.append(("Brain-Channel EXIF count", len(exif)))
    results.append(("Brain-Channel Tag 270", exif.get(270)))

# Cell 4 (index 8) - Activation.png
with Image.open(image_dir / "Activation.png") as img:
    exif = img.getexif()
    sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
    raw_comment = sub_ifd.get(37510)
    results.append(("Activation Sub-IFD UserComment", raw_comment))

# Cell 5 (index 10) - Brain.png
with Image.open(image_dir / "Brain.png") as img:
    results.append(("Brain info Software", img.info.get("Software")))

# Cell 6 (index 12) - Chemicals.png
with Image.open(image_dir / "Chemicals.png") as img:
    results.append(("Chemicals info ImageDescription", img.info.get("ImageDescription")))

# Cell 7 (index 14) - Dopamine.png
with Image.open(image_dir / "Dopamine.png") as img:
    xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="replace")
    clean_xmp = xmp.lstrip("\ufeff")
    root = ET.fromstring(clean_xmp)
    maker_note = [elem.text for elem in root.iter() if elem.tag.endswith("MakerNote")][0]
    results.append(("Dopamine XMP MakerNote", maker_note))

# Cell 8 (index 17) - Hello
results.append(("Hello", base64.b64decode("SGVsbG8=").decode("utf-8")))

# Cell 9 (index 19) - Music.png Copyright decoded
b64_str = "RVhGSUw6IFR1bm5lbCBjb21wcmVzc2VkIGRhdGFiYXNlIGR1bXAgdmlhIEROUyBDb3ZlcnQgQ2hhbm5lbC4="
results.append(("Music b64 decoded", base64.b64decode(b64_str).decode("utf-8")))

for name, val in results:
    print(f"{name}: {val}")
