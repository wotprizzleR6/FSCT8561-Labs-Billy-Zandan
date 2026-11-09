import hashlib
import warnings
from pathlib import Path
from PIL import Image

warnings.filterwarnings("ignore")

# Setup directories
ASSET_DIR = Path("Lab7") if Path("Lab7/python.png").exists() else Path(".")
PYTHON_IMG = ASSET_DIR / "python.png"
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
TEST_STEGO = OUTPUT_DIR / "python_test_stego.png"

# Ensure test stego file exists
if not TEST_STEGO.exists():
    import sys
    if str(ASSET_DIR.resolve()) not in sys.path:
        sys.path.insert(0, str(ASSET_DIR.resolve()))
    from steganography_LSB import hide_message
    hide_message(str(PYTHON_IMG), "HI", str(TEST_STEGO))

def sha256_file(path):
    """Calculate the SHA-256 digest of a file's exact bytes."""
    with open(path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()

def compare_images(original_path, stego_path):
    """Compare two images across file sizes, SHA-256 hashes, changed pixels, and channels."""
    with Image.open(original_path) as original, Image.open(stego_path) as stego:
        a = list(original.convert("RGBA").getdata())
        b = list(stego.convert("RGBA").getdata())
        if original.size != stego.size:
            raise ValueError("Image dimensions differ")

    changed_pixels = sum(p != q for p, q in zip(a, b))
    changed_channels = sum(x != y for p, q in zip(a, b) for x, y in zip(p, q))
    return {
        "original_bytes": Path(original_path).stat().st_size,
        "stego_bytes": Path(stego_path).stat().st_size,
        "original_sha256": sha256_file(original_path),
        "stego_sha256": sha256_file(stego_path),
        "same_file_bytes": sha256_file(original_path) == sha256_file(stego_path),
        "changed_pixels": changed_pixels,
        "changed_channels": changed_channels,
        "total_pixels": len(a),
    }

print(" Part 5 - Step 1: Worked Comparison Function (Reference Test) ")
stats = compare_images(PYTHON_IMG, TEST_STEGO)

print(f"Original image      : {PYTHON_IMG.name} ({stats['original_bytes']:,} bytes)")
print(f"Stego image         : {TEST_STEGO.name} ({stats['stego_bytes']:,} bytes)")
print(f"Original SHA-256    : {stats['original_sha256']}")
print(f"Stego SHA-256       : {stats['stego_sha256']}")
print(f"Identical bytes?    : {stats['same_file_bytes']}")
print(f"Total pixels        : {stats['total_pixels']:,}")
print(f"Changed pixels      : {stats['changed_pixels']:,} ({(stats['changed_pixels']/stats['total_pixels'])*100:.4f}%)")
print(f"Changed channels    : {stats['changed_channels']:,}")
print("\nRaw dictionary output:")
print(stats)
