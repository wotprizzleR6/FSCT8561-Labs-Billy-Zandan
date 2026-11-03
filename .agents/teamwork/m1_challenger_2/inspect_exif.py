"""
Inspect EXIF structures across all images in detail.
"""
from pathlib import Path
from PIL import Image, ExifTags

IMAGES_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images")

def inspect_exif(png_path: Path):
    print(f"\n=================== EXIF: {png_path.name} ===================")
    with Image.open(png_path) as img:
        exif = img.getexif()
        print(f"Primary EXIF tags count: {len(exif)}")
        for k, v in exif.items():
            name = ExifTags.TAGS.get(k, str(k))
            print(f"  [IFD0] {k} ({name}): {v!r}")
            
        # Check sub-IFDs
        for ifd_id in (ExifTags.IFD.Exif, ExifTags.IFD.GPSInfo, ExifTags.IFD.Makernote, ExifTags.IFD.Interop):
            try:
                sub = exif.get_ifd(ifd_id)
                if sub:
                    print(f"  Sub-IFD {ifd_id.name} tags count: {len(sub)}")
                    for sk, sv in sub.items():
                        sname = ExifTags.TAGS.get(sk, str(sk))
                        if ifd_id == ExifTags.IFD.GPSInfo:
                            sname = ExifTags.GPSTAGS.get(sk, str(sk))
                        print(f"    [{ifd_id.name}] {sk} ({sname}): {sv!r}")
            except Exception as e:
                print(f"  Error reading sub-IFD {ifd_id}: {e}")

if __name__ == "__main__":
    for img in sorted(IMAGES_DIR.glob("*.png")):
        inspect_exif(img)
