import base64
from pathlib import Path
from PIL import Image, ExifTags

image_dir = Path("Lab6/Images") if Path("Lab6").exists() else Path("Images")
image_path = image_dir / "Music.png"

# Investigation 6: Music.png
with Image.open(image_path) as img:
    # Step 1 - Try EXIF. Copyright holds a Base64-looking string (ends in '=').
    exif = img.getexif()
    print("EXIF tags:", len(exif))
    for tag_id, value in exif.items():
        print(" ", ExifTags.TAGS.get(tag_id, tag_id), ":", value)

    # Step 2 - PNG text also holds the same Copyright value.
    print("\nPNG text fields:")
    for key, value in img.info.items():
        if isinstance(value, str):
            print(" ", key, ":", value)

    # Step 4 - Decode (needed here): Base64 -> UTF-8.
    encoded_message = exif.get(0x8298) or img.info.get("Copyright")  # 0x8298 = Copyright
    print("\nEncoded value:", encoded_message)
    print("Partial secret:", base64.b64decode(encoded_message).decode("utf-8"))

