from pathlib import Path
from PIL import Image, ExifTags
import base64

image_dir = Path("Lab6/Images")
image_path = image_dir / "Music.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    print("EXIF tags:", len(exif))
    for k, v in exif.items():
        name = ExifTags.TAGS.get(k, k)
        print(f"  {name}: {v}")
    
    print("img.info keys:", list(img.info.keys()))
    if "Copyright" in img.info:
        print("img.info['Copyright']:", img.info["Copyright"])
    
    b64_val = exif.get(33432) or img.info.get("Copyright")
    print("Base64 string:", b64_val)
    decoded = base64.b64decode(b64_val).decode("utf-8")
    print("Decoded string:", decoded)
