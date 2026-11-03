from PIL import Image
import xml.etree.ElementTree as ET
import defusedxml.ElementTree as DefusedET

dopamine_path = r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images\Dopamine.png"
with Image.open(dopamine_path) as img:
    xmp_raw = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp_raw, bytes):
        xmp_str = xmp_raw.decode("utf-8", errors="replace")
    else:
        xmp_str = xmp_raw
    
    # Strip any BOM or leading whitespace
    xmp_str = xmp_str.strip("\ufeff")
    
    # Parse with defusedxml / ElementTree
    root = DefusedET.fromstring(xmp_str)
    for elem in root.iter():
        text = (elem.text or "").strip()
        tail = (elem.tail or "").strip()
        attrib = elem.attrib
        if text or attrib:
            print(f"Elem: {elem.tag} | text: {text!r} | attrib: {attrib}")
