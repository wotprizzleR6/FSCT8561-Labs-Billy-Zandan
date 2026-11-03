from pathlib import Path
from PIL import Image, ExifTags
import base64
import xml.etree.ElementTree as ET

image_dir = Path("Lab6/Images")

print("--- Investigation 1: Activation.png ---")
image_path = image_dir / "Activation.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
    raw_comment = sub_ifd.get(37510)
    if raw_comment:
        if raw_comment.startswith(b"ASCII\x00\x00\x00"):
            secret = raw_comment[8:].decode("utf-8")
        else:
            secret = raw_comment.decode("utf-8", errors="ignore")
        print("Found in UserComment (Sub-IFD 37510):", secret)

print("\n--- Investigation 2: Brain-Channel.png ---")
image_path = image_dir / "Brain-Channel.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    secret = exif.get(270)
    print("Found in EXIF ImageDescription (tag 270):", secret)

print("\n--- Investigation 3: Brain.png ---")
image_path = image_dir / "Brain.png"
with Image.open(image_path) as img:
    secret = img.info.get("Software")
    print("Found in PNG text chunk 'Software':", secret)

print("\n--- Investigation 4: Chemicals.png ---")
image_path = image_dir / "Chemicals.png"
with Image.open(image_path) as img:
    secret = img.info.get("ImageDescription")
    print("Found in PNG text chunk 'ImageDescription':", secret)

print("\n--- Investigation 5: Dopamine.png ---")
image_path = image_dir / "Dopamine.png"
with Image.open(image_path) as img:
    xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="replace")
    clean_xmp = xmp.lstrip("\ufeff")
    root = ET.fromstring(clean_xmp)
    for elem in root.iter():
        if elem.tag.endswith("MakerNote"):
            secret = elem.text
            print("Found in XMP <exif:MakerNote>:", secret)
            break

print("\n--- Investigation 6: Music.png ---")
image_path = image_dir / "Music.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    b64_val = exif.get(33432) or img.info.get("Copyright")
    secret = base64.b64decode(b64_val).decode("utf-8")
    print("Found in EXIF/PNG Copyright (Base64 decoded):", secret)
