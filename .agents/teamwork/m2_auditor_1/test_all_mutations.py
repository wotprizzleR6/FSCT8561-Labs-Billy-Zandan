import os
import sys
import io
import contextlib
import base64
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, PngImagePlugin, ExifTags

WORK_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_auditor_1")
MUTATION_DIR = WORK_DIR / "temp_mutation"
MUTATION_DIR.mkdir(parents=True, exist_ok=True)

# 1. Brain-Channel.png (EXIF 270)
img1 = Image.new("RGB", (100, 100), color="red")
exif1 = img1.getexif()
exif1[270] = "LATERAL: Mutated Mimikatz vector test 111"
img1.save(MUTATION_DIR / "Brain-Channel.png", exif=exif1)

# 2. Chemicals.png (PNG tEXt ImageDescription)
img2 = Image.new("RGB", (100, 100), color="green")
meta2 = PngImagePlugin.PngInfo()
meta2.add_text("ImageDescription", "EXPLOIT: Mutated SQLi vector test 222")
img2.save(MUTATION_DIR / "Chemicals.png", pnginfo=meta2)

# 3. Dopamine.png (XMP XML MakerNote)
img3 = Image.new("RGB", (100, 100), color="yellow")
meta3 = PngImagePlugin.PngInfo()
xmp_xml = """<x:xmpmeta xmlns:x='adobe:ns:meta/'><rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'><rdf:Description xmlns:exif='http://ns.adobe.com/exif/1.0/'><exif:MakerNote>PERSIST: Mutated cron job test 333</exif:MakerNote></rdf:Description></rdf:RDF></x:xmpmeta>"""
meta3.add_text("XML:com.adobe.xmp", xmp_xml)
img3.save(MUTATION_DIR / "Dopamine.png", pnginfo=meta3)

# 4. Music.png (Base64 Copyright)
img4 = Image.new("RGB", (100, 100), color="purple")
meta4 = PngImagePlugin.PngInfo()
b64_payload = base64.b64encode(b"EXFIL: Mutated DNS exfil test 444").decode("ascii")
meta4.add_text("Copyright", b64_payload)
img4.save(MUTATION_DIR / "Music.png", pnginfo=meta4)

# Test each snippet from notebook
tests = [
    ("Brain-Channel.png", """
image_path = image_dir / "Brain-Channel.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    secret = exif.get(270)
    print("Found in EXIF ImageDescription (tag 270):", secret)
""", "Mutated Mimikatz vector test 111"),
    ("Chemicals.png", """
image_path = image_dir / "Chemicals.png"
with Image.open(image_path) as img:
    secret = img.info.get("ImageDescription")
    print("Found in PNG text chunk 'ImageDescription':", secret)
""", "Mutated SQLi vector test 222"),
    ("Dopamine.png", """
import xml.etree.ElementTree as ET
image_path = image_dir / "Dopamine.png"
with Image.open(image_path) as img:
    xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="replace")
    clean_xmp = xmp.lstrip("\\ufeff")
    root = ET.fromstring(clean_xmp)
    secret = ""
    for elem in root.iter():
        if elem.tag.endswith("MakerNote"):
            secret = elem.text
            print("Found in XMP <exif:MakerNote>:", secret)
            break
""", "Mutated cron job test 333"),
    ("Music.png", """
import base64
image_path = image_dir / "Music.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    b64_val = exif.get(33432) or img.info.get("Copyright")
    secret = base64.b64decode(b64_val).decode("utf-8")
    print("Found in EXIF/PNG Copyright (Base64 decoded):", secret)
""", "Mutated DNS exfil test 444"),
]

all_passed = True
for img_name, snippet, expected_snippet in tests:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(snippet, {"image_dir": MUTATION_DIR, "Image": Image})
    res = buf.getvalue().strip()
    if expected_snippet in res:
        print(f"[PASS] {img_name}: Correctly extracted mutated payload -> {res}")
    else:
        print(f"[FAIL] {img_name}: Mutation not found -> {res}")
        all_passed = False

print(f"\nAll mutation tests passed: {all_passed}")
