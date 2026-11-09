import warnings
from pathlib import Path
from PIL import Image

warnings.filterwarnings("ignore")

# Setup directories
ASSET_DIR = Path("Lab7") if Path("Lab7/compay_logo.png").exists() else Path(".")
LOGO = ASSET_DIR / "compay_logo.png"
PROFILE = ASSET_DIR / "profile.png"
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
LOGO_STEGO = OUTPUT_DIR / "company_logo_stego.png"
PROFILE_STEGO = OUTPUT_DIR / "profile_secret.png"

def create_side_by_side(orig_path, stego_path, out_path, thumb_size=(400, 400)):
    """Generate a combined side-by-side image for visual comparison."""
    with Image.open(orig_path) as orig, Image.open(stego_path) as stego:
        im1 = orig.convert("RGBA").resize(thumb_size)
        im2 = stego.convert("RGBA").resize(thumb_size)
        
        combined = Image.new("RGBA", (thumb_size[0] * 2 + 20, thumb_size[1] + 40), (255, 255, 255, 255))
        combined.paste(im1, (0, 30))
        combined.paste(im2, (thumb_size[0] + 20, 30))
        combined.save(out_path)
    return out_path

print(" Part 5 - Step 4: Task 5C Visual Inspection & Perceptual Analysis ")

# Create visual side-by-side comparison artifacts
logo_vis = create_side_by_side(LOGO, LOGO_STEGO, OUTPUT_DIR / "logo_visual_comparison.png")
profile_vis = create_side_by_side(PROFILE, PROFILE_STEGO, OUTPUT_DIR / "profile_visual_comparison.png")

print(f"Generated visual comparison for Logo    : {logo_vis}")
print(f"Generated visual comparison for Profile : {profile_vis}")
