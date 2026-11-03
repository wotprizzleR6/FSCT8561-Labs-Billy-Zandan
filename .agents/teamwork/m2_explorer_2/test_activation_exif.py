from pathlib import Path
from PIL import Image, ExifTags

image_dir = Path("Lab6/Images")
image_path = image_dir / "Activation.png"
with Image.open(image_path) as img:
    exif = img.getexif()
    print("EXIF tags:", len(exif))
    for tag_id, value in exif.items():
        print(ExifTags.TAGS.get(tag_id, tag_id), ":", value)
    
    # Check Sub-IFDs
    for ifd_id in (ExifTags.IFD.Exif, ExifTags.IFD.GPSInfo):
        try:
            sub = exif.get_ifd(ifd_id)
            print(f"Sub-IFD {ifd_id} tags:", len(sub))
            for k, v in sub.items():
                print(" ", ExifTags.TAGS.get(k, k), ":", v)
        except Exception as e:
            print("Sub-IFD error:", e)
