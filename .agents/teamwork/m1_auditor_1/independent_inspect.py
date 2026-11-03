"""
Independent Ground-Truth Extraction Script for Images in Lab6/Images.
Does NOT import or use metadata_scanner.py.
"""

from pathlib import Path
from PIL import Image, ExifTags
import base64
import re
import xml.etree.ElementTree as ET

images_dir = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images")

print("=== Independent Forensic Inspection of Lab6 Images ===")

for img_path in sorted(images_dir.glob("*.png")):
    print(f"\n--- File: {img_path.name} ({img_path.stat().st_size} bytes) ---")
    with Image.open(img_path) as img:
        print(f"Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
        print(f"Native info keys: {list(img.info.keys())}")
        for k, v in img.info.items():
            if k == "exif":
                print(f"  [info] exif binary payload: {len(v)} bytes")
            elif k in ("XML:com.adobe.xmp", "xmp"):
                print(f"  [info] XMP packet: {len(v)} chars/bytes")
                val_str = v if isinstance(v, str) else v.decode('utf-8', errors='replace')
                # Parse MakerNote
                m = re.search(r"<exif:MakerNote>(.*?)</exif:MakerNote>", val_str)
                if m:
                    print(f"    --> Found <exif:MakerNote>: {m.group(1)}")
            else:
                print(f"  [info] {k}: {repr(v)}")

        exif = img.getexif()
        if exif:
            print(f"Primary EXIF tags count: {len(exif)}")
            for tag_id, val in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                val_repr = repr(val) if len(repr(val)) < 100 else repr(val)[:100] + "..."
                print(f"  [EXIF primary] {tag_id} ({tag_name}): {val_repr}")

            sub_ifd = exif.get_ifd(ExifTags.IFD.Exif)
            if sub_ifd:
                print(f"Exif Sub-IFD tags count: {len(sub_ifd)}")
                for sub_id, sub_val in sub_ifd.items():
                    sub_name = ExifTags.TAGS.get(sub_id, str(sub_id))
                    sub_repr = repr(sub_val) if len(repr(sub_val)) < 100 else repr(sub_val)[:100] + "..."
                    print(f"  [EXIF Sub-IFD] {sub_id} ({sub_name}): {sub_repr}")

            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
            if gps_ifd:
                print(f"GPS Sub-IFD tags count: {len(gps_ifd)}")
                for gps_id, gps_val in gps_ifd.items():
                    gps_name = ExifTags.GPSTAGS.get(gps_id, str(gps_id))
                    print(f"  [GPS Sub-IFD] {gps_id} ({gps_name}): {repr(gps_val)}")
        else:
            print("No EXIF data found.")
