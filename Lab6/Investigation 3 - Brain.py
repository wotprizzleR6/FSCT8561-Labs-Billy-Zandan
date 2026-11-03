from pathlib import Path
from PIL import Image, ExifTags

image_dir = Path("Lab6/Images") if Path("Lab6").exists() else Path("Images")
image_path = image_dir / "Brain.png"

# Investigation 3: Brain.png
with Image.open(image_path) as img:
    # Step 1 - Try EXIF. Returns 0 tags, so the clue is not in EXIF.
    exif = img.getexif()
    print("EXIF tags:", len(exif))

    # Step 2 - Inspect PNG text chunks. The clue is in the Software key.
    print("\nPNG text fields:")
    for key, value in img.info.items():
        if isinstance(value, str):
            print(" ", key, ":", value)

    print("\nPartial secret:", img.info.get("Software"))

