from pathlib import Path
from PIL import Image, ExifTags

image_dir = Path("Lab6/Images") if Path("Lab6").exists() else Path("Images")
image_path = image_dir / "Activation.png"

# Investigation 1: Activation.png
# Step 1 - Try EXIF (IFD0). Clue is NOT here, but tag 34665 (ExifOffset) points to a sub-IFD.
with Image.open(image_path) as img:
    exif = img.getexif()
    print("EXIF tags (IFD0):", len(exif))
    for tag_id, value in exif.items():
        print(" ", ExifTags.TAGS.get(tag_id, tag_id), ":", value)

    # Step 2 - Follow ExifOffset into the Exif sub-IFD, where UserComment lives.
    sub = exif.get_ifd(0x8769)
    print("\nEXIF tags (Exif sub-IFD):", len(sub))
    for tag_id, value in sub.items():
        print(" ", ExifTags.TAGS.get(tag_id, tag_id), ":", value)

    # Step 3 - Clean the UserComment (first 8 bytes are the 'ASCII\0\0\0' charset header).
    comment = sub.get(0x9286)  # 0x9286 = UserComment
    if isinstance(comment, bytes):
        comment = comment[8:].decode("ascii", errors="replace")
    print("\nPartial secret:", comment)

