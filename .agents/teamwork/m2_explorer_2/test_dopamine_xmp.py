from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET

image_dir = Path("Lab6/Images")
image_path = image_dir / "Dopamine.png"
with Image.open(image_path) as img:
    xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="replace")
    
    clean_xmp = xmp.replace('\ufeff', '')
    print("XMP length:", len(clean_xmp))
    print("XMP preview:\n", clean_xmp[:300])
    
    root = ET.fromstring(clean_xmp)
    for elem in root.iter():
        if "MakerNote" in elem.tag:
            print("Found tag:", elem.tag, "-> Value:", elem.text)
