from pathlib import Path
from PIL import Image, ExifTags

image_path = Path("Lab6/Images/Dopamine.png") if Path("Lab6").exists() else Path("Images/Dopamine.png")

with Image.open(image_path) as img:
    exif = img.getexif()
    print(f"{image_path.name} EXIF IFD0")
    print(f"Total Tags: {len(exif)}")
    for tag_id, val in exif.items():
        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
        print(f"Tag {tag_id} ({tag_name}): {val}")