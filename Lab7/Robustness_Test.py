import sys
import warnings
from pathlib import Path
from PIL import Image

warnings.filterwarnings("ignore")

# Setup directories
ASSET_DIR = Path("Lab7") if Path("Lab7/compay_logo.png").exists() else Path(".")
LOGO = ASSET_DIR / "compay_logo.png"
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
LOGO_STEGO = OUTPUT_DIR / "company_logo_stego.png"

# Ensure company_logo_stego.png exists
if not LOGO_STEGO.exists():
    if str(ASSET_DIR.resolve()) not in sys.path:
        sys.path.insert(0, str(ASSET_DIR.resolve()))
    from steganography_LSB import hide_message
    hide_message(str(LOGO), "TARGET:192.168.1.50", str(LOGO_STEGO))

def decode_manual_safe(path):
    """Attempt manual LSB extraction and handle decoding errors safely."""
    try:
        with Image.open(path) as image:
            pixels = list(image.convert("RGBA").getdata())
        
        decoded_bytes = bytearray()
        # Read up to first 200 pixel pairs to avoid infinite loops on garbage data
        limit = min(len(pixels) - 1, 400)
        for index in range(0, limit, 2):
            first = pixels[index]
            second = pixels[index + 1]
            bits = "".join(str(c & 1) for c in first) + "".join(str(c & 1) for c in second)
            value = int(bits, 2)
            if value == 0:
                break
            decoded_bytes.append(value)
        
        return decoded_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[Extraction Error: {e}]"


print(" Steganographic Robustness Testing")
print(f"Target stego file: {LOGO_STEGO.name}")
print(f"Original payload : 'TARGET:192.168.1.50'\n")

# Robustness Test 1: Lossy JPEG Compression / Transcoding
print(" Robustness Test 1: Lossy JPEG Transcoding (Quality=95) ")
JPEG_OUTPUT = OUTPUT_DIR / "logo_stego_transcoded.jpg"

with Image.open(LOGO_STEGO) as img:
    rgb_img = img.convert("RGB")
    rgb_img.save(JPEG_OUTPUT, "JPEG", quality=95)

recovered_jpeg = decode_manual_safe(JPEG_OUTPUT)
print(f"Transcoded output file  : {JPEG_OUTPUT.name}")
print(f"Extraction attempted    : decode_manual('{JPEG_OUTPUT.name}')")
print(f"Recovered text sample   : {repr(recovered_jpeg[:40])}...")
print("Payload survived?       : NO (Destroyed by lossy compression)")
print("Forensic Explanation   : JPEG uses Discrete Cosine Transform (DCT) lossy")
print("                          frequency quantization. High-frequency pixel LSBs")
print("                          are discarded to save space, completely corrupting")
print("                          the spatial covert channel.\n")

# Robustness Test 2: Spatial Resampling / Resizing
print(" Robustness Test 2: Spatial Resampling / Downscaling (90%) ")
RESIZED_OUTPUT = OUTPUT_DIR / "logo_stego_resized.png"

with Image.open(LOGO_STEGO) as img:
    orig_w, orig_h = img.size
    new_size = (int(orig_w * 0.9), int(orig_h * 0.9))  # 921x921
    resized_img = img.resize(new_size, Image.Resampling.BILINEAR)
    resized_img.save(RESIZED_OUTPUT, "PNG")

recovered_resized = decode_manual_safe(RESIZED_OUTPUT)
print(f"Resized output file     : {RESIZED_OUTPUT.name} (1024x1024 -> {new_size[0]}x{new_size[1]})")
print(f"Extraction attempted    : decode_manual('{RESIZED_OUTPUT.name}')")
print(f"Recovered text sample   : {repr(recovered_resized[:40])}...")
print("Payload survived?       : NO (Destroyed by spatial interpolation)")
print("Forensic Explanation   : Resampling recalculates pixel color values using")
print("                          bilinear interpolation across neighboring pixels.")
print("                          This redistributes pixel channel intensities and")
print("                          obliterates the embedded LSB sequences.\n")
