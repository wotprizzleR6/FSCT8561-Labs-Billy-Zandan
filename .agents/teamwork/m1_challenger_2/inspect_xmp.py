"""
Inspect XMP in Dopamine.png with utf-8 representation.
"""
from pathlib import Path
from PIL import Image

p = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images\Dopamine.png")
with Image.open(p) as img:
    print("img.info keys:", list(img.info.keys()))
    xmp = img.info.get("XML:com.adobe.xmp")
    print("XMP content repr:\n", repr(xmp))
