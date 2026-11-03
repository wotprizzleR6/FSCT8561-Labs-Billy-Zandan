import os
import base64
from pathlib import Path
from PIL import Image, ExifTags

images_dir = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images")
images = sorted(list(images_dir.glob("*.png")))

print(f"Total images found: {len(images)}")

for img_path in images:
    print("\n" + "=" * 60)
    print(f"Image: {img_path.name}")
    with Image.open(img_path) as img:
        print(f"Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
        
        # 1. EXIF check
        exif = img.getexif()
        print(f"EXIF tags count: {len(exif)}")
        if len(exif) > 0:
            for tag_id, val in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                print(f"  [EXIF] {tag_name} (ID {tag_id}): {val!r}")
        
        # 2. info dictionary (PNG text chunks and other metadata)
        print(f"img.info keys ({len(img.info)}): {list(img.info.keys())}")
        for k, v in img.info.items():
            if isinstance(v, str):
                preview = v if len(v) < 120 else v[:120] + "... [truncated]"
                print(f"  [info str] {k}: {preview!r}")
            elif isinstance(v, bytes):
                preview = v if len(v) < 120 else v[:120] + b"... [truncated]"
                print(f"  [info bytes] {k}: {preview!r}")
            else:
                print(f"  [info other] {k}: {type(v)} = {v}")
