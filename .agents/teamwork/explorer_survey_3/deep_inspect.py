from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import base64
import xml.etree.ElementTree as ET

# Check Activation.png EXIF IFD / GPS / UserComment / etc
activation_path = r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images\Activation.png"
with Image.open(activation_path) as img:
    exif = img.getexif()
    print("Activation.png - Root EXIF:")
    for tag_id, val in exif.items():
        print(f"  {TAGS.get(tag_id, tag_id)}: {val}")
    
    # Check Exif sub-IFD (tag 34665 = 0x8769)
    try:
        sub_ifd = exif.get_ifd(34665)
        print("Activation.png - Sub-IFD (0x8769):")
        for tag_id, val in sub_ifd.items():
            print(f"  {TAGS.get(tag_id, tag_id)}: {val}")
    except Exception as e:
        print("Error getting sub-ifd:", e)
        
    # Check GPS IFD (tag 34853 = 0x8825)
    try:
        gps_ifd = exif.get_ifd(34853)
        print("Activation.png - GPS IFD (0x8825):")
        for tag_id, val in gps_ifd.items():
            print(f"  {GPSTAGS.get(tag_id, tag_id)}: {val}")
    except Exception as e:
        print("Error getting gps-ifd:", e)

# Check Dopamine.png XMP
dopamine_path = r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images\Dopamine.png"
with Image.open(dopamine_path) as img:
    xmp_raw = img.info.get("XML:com.adobe.xmp") or img.info.get("xmp")
    if isinstance(xmp_raw, bytes):
        xmp_str = xmp_raw.decode("utf-8", errors="replace")
    else:
        xmp_str = xmp_raw
    print("\nDopamine.png - Full XMP:")
    print(xmp_str)

# Check Music.png Base64 decoding
music_path = r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images\Music.png"
with Image.open(music_path) as img:
    val = img.info.get("Copyright")
    print(f"\nMusic.png Copyright raw: {val}")
    print(f"Music.png Copyright decoded: {base64.b64decode(val).decode('utf-8')}")
