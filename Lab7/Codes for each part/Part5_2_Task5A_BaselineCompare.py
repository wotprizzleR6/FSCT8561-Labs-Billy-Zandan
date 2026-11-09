import hashlib
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

def sha256_file(path):
    """Calculate the SHA-256 digest of a file's exact bytes."""
    with open(path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()

# Ensure stego files exist
if not LOGO_STEGO.exists():
    import sys
    if str(ASSET_DIR.resolve()) not in sys.path:
        sys.path.insert(0, str(ASSET_DIR.resolve()))
    from steganography_LSB import hide_message
    hide_message(str(LOGO), "TARGET:192.168.1.50", str(LOGO_STEGO))

if not PROFILE_STEGO.exists():
    import stepic
    with Image.open(PROFILE) as src:
        stego = stepic.encode(src.convert("RGB"), "80,443,3478,5060".encode("utf-8"))
        stego.save(PROFILE_STEGO)

def compare_images(original_path, stego_path):
    """Compare two images across file sizes, SHA-256 hashes, changed pixels, and channels."""
    with Image.open(original_path) as original, Image.open(stego_path) as stego:
        a = list(original.convert("RGBA").getdata())
        b = list(stego.convert("RGBA").getdata())
        if original.size != stego.size:
            raise ValueError("Image dimensions differ")

    changed_pixels = sum(p != q for p, q in zip(a, b))
    changed_channels = sum(x != y for p, q in zip(a, b) for x, y in zip(p, q))
    total_pixels = len(a)
    pct_pixels = (changed_pixels / total_pixels) * 100

    return {
        "original_bytes": Path(original_path).stat().st_size,
        "stego_bytes": Path(stego_path).stat().st_size,
        "original_sha256": sha256_file(original_path),
        "stego_sha256": sha256_file(stego_path),
        "same_file_bytes": sha256_file(original_path) == sha256_file(stego_path),
        "changed_pixels": changed_pixels,
        "changed_channels": changed_channels,
        "total_pixels": total_pixels,
        "pct_changed_pixels": pct_pixels,
    }

print(" Part 5 - Step 2: Task 5A Reuse Baseline Hashes ")

# Baseline values from Part 0
original_logo_hash = sha256_file(LOGO)
original_profile_hash = sha256_file(PROFILE)

logo_stats = compare_images(LOGO, LOGO_STEGO)
profile_stats = compare_images(PROFILE, PROFILE_STEGO)

print("\n 1. Baseline Integrity Checks ")
print("Original logo baseline matches current original     :", original_logo_hash == sha256_file(LOGO))
print("Original logo vs. stego identical (should be False) :", original_logo_hash == sha256_file(LOGO_STEGO))
print("Original profile vs. stego identical (should be False):", original_profile_hash == sha256_file(PROFILE_STEGO))

print("\n 2. Detailed Pixel & Channel Metrics ")
print("[Company Logo - Manual LSB]")
print(f"  Original SHA-256    : {logo_stats['original_sha256']}")
print(f"  Stego SHA-256       : {logo_stats['stego_sha256']}")
print(f"  File size delta     : {logo_stats['original_bytes']:,} -> {logo_stats['stego_bytes']:,} bytes")
print(f"  Changed pixels      : {logo_stats['changed_pixels']:,} / {logo_stats['total_pixels']:,} ({logo_stats['pct_changed_pixels']:.4f}%)")
print(f"  Changed channels    : {logo_stats['changed_channels']:,}")

print("\n[Profile Picture - Stepic LSB]")
print(f"  Original SHA-256    : {profile_stats['original_sha256']}")
print(f"  Stego SHA-256       : {profile_stats['stego_sha256']}")
print(f"  File size delta     : {profile_stats['original_bytes']:,} -> {profile_stats['stego_bytes']:,} bytes")
print(f"  Changed pixels      : {profile_stats['changed_pixels']:,} / {profile_stats['total_pixels']:,} ({profile_stats['pct_changed_pixels']:.4f}%)")
print(f"  Changed channels    : {profile_stats['changed_channels']:,}")
