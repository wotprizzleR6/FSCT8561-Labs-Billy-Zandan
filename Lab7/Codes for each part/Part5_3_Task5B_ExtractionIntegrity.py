import hashlib
import warnings
from pathlib import Path
from PIL import Image
import stepic

warnings.filterwarnings("ignore")

# Setup directories
ASSET_DIR = Path("Lab7") if Path("Lab7/compay_logo.png").exists() else Path(".")
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
LOGO_STEGO = OUTPUT_DIR / "company_logo_stego.png"
PROFILE_STEGO = OUTPUT_DIR / "profile_secret.png"

def sha256_file(path):
    """Calculate the SHA-256 digest of a file's exact bytes."""
    with open(path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()

def decode_manual(path):
    """Manually extract an LSB-encoded message from RGBA pixel pairs stopping at 0x00."""
    with Image.open(path) as image:
        pixels = list(image.convert("RGBA").getdata())

    decoded_bytes = bytearray()
    for index in range(0, len(pixels) - 1, 2):
        first = pixels[index]
        second = pixels[index + 1]
        bits = "".join(str(c & 1) for c in first) + "".join(str(c & 1) for c in second)
        value = int(bits, 2)
        if value == 0:
            break
        decoded_bytes.append(value)
    return decoded_bytes.decode("utf-8")

print(" Part 5 - Step 3: Task 5B Verify Extraction Immutability ")

#  1. Test Manual Decoder on company_logo_stego.png 
print("\n 1. Manual Decoder Immutability Check (Company Logo) ")
before_logo = sha256_file(LOGO_STEGO)
recovered_logo = decode_manual(LOGO_STEGO)
after_logo = sha256_file(LOGO_STEGO)

print(f"Target file         : {LOGO_STEGO.name}")
print(f"Recovered message   : '{recovered_logo}'")
print(f"SHA-256 before read : {before_logo}")
print(f"SHA-256 after read  : {after_logo}")
print(f"Hashes identical?   : {before_logo == after_logo}")

assert before_logo == after_logo, "Extraction unexpectedly modified the logo stego file!"
assert recovered_logo == "TARGET:192.168.1.50", "Recovered text mismatch!"
print("Assertion PASSED: Extraction did not modify company_logo_stego.png.")

#  2. Test Stepic Decoder on profile_secret.png 
print("\n 2. Stepic Decoder Immutability Check (Profile Picture) ")
before_profile = sha256_file(PROFILE_STEGO)

with Image.open(PROFILE_STEGO) as target:
    rec_raw = stepic.decode(target)
    recovered_profile = rec_raw.decode("utf-8") if isinstance(rec_raw, bytes) else str(rec_raw)

after_profile = sha256_file(PROFILE_STEGO)

print(f"Target file         : {PROFILE_STEGO.name}")
print(f"Recovered message   : '{recovered_profile}'")
print(f"SHA-256 before read : {before_profile}")
print(f"SHA-256 after read  : {after_profile}")
print(f"Hashes identical?   : {before_profile == after_profile}")

assert before_profile == after_profile, "Extraction unexpectedly modified the profile stego file!"
assert recovered_profile == "80,443,3478,5060", "Recovered text mismatch!"
print("Assertion PASSED: Extraction did not modify profile_secret.png.")

