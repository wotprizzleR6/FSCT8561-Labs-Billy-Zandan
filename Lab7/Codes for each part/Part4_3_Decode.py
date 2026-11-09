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

expected_port_text = "80,443,3478,5060"

print(" Part 4 - Step 3: Task 4B Decode and Verify ")

# Ensure stego image exists before decoding
if not PROFILE_STEGO.exists():
    print(f"'{PROFILE_STEGO.name}' not found; generating it now with stepic.encode()...")
    with Image.open(PROFILE) as source:
        rgb_image = source.convert("RGB")
        stego_image = stepic.encode(rgb_image, expected_port_text.encode("utf-8"))
        stego_image.save(PROFILE_STEGO)

# Open and decode using Stepic
with Image.open(PROFILE_STEGO) as target:
    recovered_raw = stepic.decode(target)
    
    # Normalize bytes to text if necessary
    if isinstance(recovered_raw, bytes):
        recovered_port_text = recovered_raw.decode("utf-8")
    else:
        recovered_port_text = str(recovered_raw)

print(f"Stego image inspected  : {PROFILE_STEGO}")
print(f"Raw decoded output     : {recovered_raw}")
print(f"Recovered port text    : '{recovered_port_text}'")
print(f"Expected port text     : '{expected_port_text}'")

# Notebook assertion
assert recovered_port_text == expected_port_text, f"Mismatch: expected '{expected_port_text}', got '{recovered_port_text}'"

print("\nAll Task 4B Stepic decode assertions passed successfully.")
