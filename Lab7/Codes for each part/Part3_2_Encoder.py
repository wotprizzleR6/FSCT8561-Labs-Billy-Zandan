import sys
from pathlib import Path
from PIL import Image

# Setup paths
ASSET_DIR = Path("Lab7") if Path("Lab7/compay_logo.png").exists() else Path(".")
LOGO = ASSET_DIR / "compay_logo.png"
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Add asset directory to sys.path to import steganography_LSB
if str(ASSET_DIR.resolve()) not in sys.path:
    sys.path.insert(0, str(ASSET_DIR.resolve()))

from steganography_LSB import hide_message

def encode_checked(source_path, message, output_path):
    """Validate a short ASCII message and capacity, then call the supplied encoder."""
    source_path = Path(source_path)
    output_path = Path(output_path)

    # Validation checks
    if not source_path.is_file():
        raise FileNotFoundError(f"Source file does not exist: {source_path}")
    if not message:
        raise ValueError("Message must not be empty")
    if "\x00" in message:
        raise ValueError("Zero byte is reserved as a terminator")

    with Image.open(source_path) as image:
        available_pixels = image.width * image.height

    needed_pixels = 2 * (len(message.encode("utf-8")) + 1)
    if needed_pixels > available_pixels:
        raise ValueError(
            f"Message requires {needed_pixels} pixels, but image only provides {available_pixels} pixels."
        )

    # Encode message and write output
    hide_message(str(source_path), message, str(output_path))
    return output_path

print(" Part 3 - Step 2: Task 3B Validated Encoder ")
payload = "TARGET:192.168.1.50"
LOGO_STEGO = encode_checked(LOGO, payload, OUTPUT_DIR / "company_logo_stego.png")

print(f"Source image        : {LOGO.name}")
print(f"Payload to encode   : '{payload}'")
print(f"Output stego image  : {LOGO_STEGO}")
print(f"File exists on disk : {LOGO_STEGO.exists()}")
print("Task 3B encoding completed successfully.")
