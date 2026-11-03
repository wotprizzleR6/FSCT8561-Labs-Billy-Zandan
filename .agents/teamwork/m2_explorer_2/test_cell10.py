from pathlib import Path
from PIL import Image

image_dir = Path("Lab6/Images")
image_path = image_dir / "Brain.png"
with Image.open(image_path) as img:
    for key, value in img.info.items():
        if isinstance(value, str):
            print(key, ":", value)
