from pathlib import Path
from PIL import Image, ExifTags

image_dir = Path("Lab6/Images")
image_path = image_dir / "Brain-Channel.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    print("EXIF tags:", len(exif))
    for tag_id, value in exif.items():
        print(ExifTags.TAGS.get(tag_id, tag_id), ":", value)
