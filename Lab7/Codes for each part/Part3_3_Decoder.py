import sys
import warnings
from pathlib import Path
from PIL import Image

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Setup paths
ASSET_DIR = Path("Lab7") if Path("Lab7/compay_logo.png").exists() else Path(".")
LOGO = ASSET_DIR / "compay_logo.png"
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
LOGO_STEGO = OUTPUT_DIR / "company_logo_stego.png"

# Add asset directory to sys.path to import steganography_LSB
if str(ASSET_DIR.resolve()) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR.resolve()))

from steganography_LSB import extract_message, hide_message

def decode_manual(path):
    """
    Manually extract an LSB-encoded message from RGBA pixel pairs stopping at 0x00.
    Does NOT call extract_message().
    """
    with Image.open(path) as image:
        pixels = list(image.convert("RGBA").getdata())

    decoded_bytes = bytearray()
    for index in range(0, len(pixels) - 1, 2):
        first = pixels[index]
        second = pixels[index + 1]

        # Step 1: Collect 4 LSBs from first pixel and 4 LSBs from second pixel
        bits = "".join(str(c & 1) for c in first) + "".join(str(c & 1) for c in second)

        # Step 2: Convert the 8-bit string to an integer
        value = int(bits, 2)

        # Step 3: Stop at null terminator (0x00)
        if value == 0:
            break
        decoded_bytes.append(value)

    # Step 4: Decode collected bytes as UTF-8
    return decoded_bytes.decode("utf-8")

print(" Part 3 - Step 3: Task 3C Manual Decoder ")

# Ensure stego file exists before decoding
if not LOGO_STEGO.exists():
    print(f"{LOGO_STEGO.name} not found; generating it now...")
    hide_message(str(LOGO), "TARGET:192.168.1.50", str(LOGO_STEGO))

# Run manual decode
recovered = decode_manual(LOGO_STEGO)
print(f"Target stego file           : {LOGO_STEGO}")
print(f"Manual decoder recovered    : '{recovered}'")

# Cross-verify with reference extract_message
ref_recovered = extract_message(str(LOGO_STEGO))
print(f"Reference extract recovered : '{ref_recovered}'")

# Assertions from notebook Cell 18
assert recovered == "TARGET:192.168.1.50", "Manual decoder mismatch!"
assert ref_recovered == "TARGET:192.168.1.50", "Reference decoder mismatch!"

print("\nAll Task 3C decoder assertions passed successfully.")
