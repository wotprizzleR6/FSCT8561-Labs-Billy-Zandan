from pathlib import Path
from PIL import Image

image_dir = Path("Lab6/Images")
for image_path in sorted(image_dir.glob("*.png")):
    with Image.open(image_path) as img:
        print(image_path.name, "->", img.format, "| fields:", len(img.info))
