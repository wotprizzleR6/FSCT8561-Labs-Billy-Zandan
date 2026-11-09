import warnings
from pathlib import Path
from PIL import Image
import stepic

warnings.filterwarnings("ignore")

# Setup directories
ASSET_DIR = Path("Lab7") if Path("Lab7/profile.png").exists() else Path(".")
PROFILE = ASSET_DIR / "profile.png"
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
PROFILE_STEGO = OUTPUT_DIR / "profile_secret.png"

print(" Part 4 - Step 2: Task 4A Encode and Save ")

# 1. Prepare payload
ports = [80, 443, 3478, 5060]
port_text = ",".join(str(port) for port in ports)
port_bytes = port_text.encode("utf-8")

print(f"Source carrier image : {PROFILE.name}")
print(f"Payload to hide      : '{port_text}' ({len(port_bytes)} bytes)")

# 2. Encode using Stepic (requires RGB mode)
with Image.open(PROFILE) as source:
    rgb_image = source.convert("RGB")
    print(f"Converted {PROFILE.name} to RGB mode: {rgb_image.size}, {rgb_image.mode}")
    
    # Stepic embedding
    stego_image = stepic.encode(rgb_image, port_bytes)
    stego_image.save(PROFILE_STEGO)

print(f"Successfully saved stego image to: {PROFILE_STEGO}")
print(f"Stego image exists on disk       : {PROFILE_STEGO.exists()}")
print(f"Stego file size                  : {PROFILE_STEGO.stat().st_size:,} bytes")
print("Task 4A encoding completed successfully.")
