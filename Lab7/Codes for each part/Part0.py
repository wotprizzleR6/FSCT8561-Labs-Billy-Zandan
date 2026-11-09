import hashlib
from pathlib import Path
from PIL import Image

# Setup paths (works whether run from repository root or inside Lab7 folder)
ASSET_DIR = Path("Lab7") if Path("Lab7/compay_logo.png").exists() else Path(".")
LOGO = ASSET_DIR / "compay_logo.png"
PROFILE = ASSET_DIR / "profile.png"
PYTHON_IMG = ASSET_DIR / "python.png"
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=== Part 0: Setup and Evidence Inventory ===")
for path in [LOGO, PROFILE, PYTHON_IMG]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Check where you extracted assets.")
    with Image.open(path) as image:
        print(f"{path.name:<16} Size: {str(image.size):<12} Mode: {image.mode:<6} Bytes: {path.stat().st_size:,} bytes")

def sha256_file(path):
    """Calculate the SHA-256 digest of a file's exact bytes."""
    with open(path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()

print("\n=== Baseline SHA-256 Hashes ===")
original_logo_hash = sha256_file(LOGO)
original_profile_hash = sha256_file(PROFILE)

print("Original logo SHA-256:   ", original_logo_hash)
print("Original profile SHA-256:", original_profile_hash)
