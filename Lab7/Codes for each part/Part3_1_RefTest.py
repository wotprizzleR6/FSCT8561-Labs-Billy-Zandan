import sys
from pathlib import Path
from PIL import Image

# Setup paths
ASSET_DIR = Path("Lab7") if Path("Lab7/python.png").exists() else Path(".")
PYTHON_IMG = ASSET_DIR / "python.png"
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Add asset directory to sys.path to import steganography_LSB
if str(ASSET_DIR.resolve()) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR.resolve()))

from steganography_LSB import hide_message, extract_message

print(" Part 3 - Step 1: Guided Reference Test ")
TEST_STEGO = OUTPUT_DIR / "python_test_stego.png"

# Hide 'HI' in python.png
hide_message(str(PYTHON_IMG), "HI", str(TEST_STEGO))
print(f"Hiding 'HI' in {PYTHON_IMG.name} -> Saved to {TEST_STEGO.name}")

# Extract and verify
recovered = extract_message(str(TEST_STEGO))
print(f"Recovered message: '{recovered}'")

assert recovered == "HI", f"Expected 'HI', got '{recovered}'"
print("Reference test passed successfully.")
