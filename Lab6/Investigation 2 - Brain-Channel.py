from pathlib import Path
from PIL import Image, ExifTags

image_dir = Path("Lab6/Images") if Path("Lab6").exists() else Path("Images")
image_path = image_dir / "Brain-Channel.png"

# Investigation 2: Brain-Channel.png
# Step 1 - Try EXIF. The clue is visible in the ImageDescription tag.
with Image.open(image_path) as img:
    exif = img.getexif()
    print("EXIF tags:", len(exif))
    for tag_id, value in exif.items():
        print(" ", ExifTags.TAGS.get(tag_id, tag_id), ":", value)

    print("\nPartial secret:", exif.get(0x010E))  # 0x010E = ImageDescription

