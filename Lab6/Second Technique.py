from pathlib import Path
from PIL import Image

for filename in ["Brain.png", "Chemicals.png"]:
    image_path = Path("Images") / filename
    with Image.open(image_path) as img:
        print(f"{filename} (img.info inspection)")
        print(f"Keys discovered: {list(img.info.keys())}")
        for key, value in img.info.items():
            if isinstance(value, str):
                print(f"  {key}: {value}")