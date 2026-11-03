from pathlib import Path
from PIL import Image

image_dir = Path("Lab6/Images")
image_path = image_dir / "Dopamine.png"
with Image.open(image_path) as img:
    xmp = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="replace")
    print(xmp if xmp else "No XMP found")
