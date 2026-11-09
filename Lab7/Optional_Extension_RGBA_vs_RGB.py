import sys
import warnings
from pathlib import Path
from PIL import Image

warnings.filterwarnings("ignore")

# Setup directories
ASSET_DIR = Path("Lab7") if Path("Lab7/compay_logo.png").exists() else Path(".")
LOGO = ASSET_DIR / "compay_logo.png"
PROFILE = ASSET_DIR / "profile.png"
PYTHON_IMG = ASSET_DIR / "python.png"
OUTPUT_DIR = ASSET_DIR / "Lab8_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# 1. Capacity Mathematical Comparison
def calc_capacity(width, height, channels, terminator_bytes=1):
    total_bits = width * height * channels
    return max(0, (total_bits // 8) - terminator_bytes)


print(" OPTIONAL EXTENSION: RGBA vs. RGB-ONLY STEGANOGRAPHY DESIGN ANALYSIS")
print("\n 1. Mathematical Capacity Tradeoff Analysis ")
print(f"{'Image Asset':<18} {'Dimensions':<14} {'RGBA (4 ch) Capacity':<22} {'RGB (3 ch) Capacity':<22} {'Delta':<12}")
print("-" * 88)

assets = [
    ("100x100 Sample", 100, 100),
    (PYTHON_IMG.name, 100, 100),
    (PROFILE.name, 1408, 768),
    (LOGO.name, 1024, 1024),
]

for label, w, h in assets:
    rgba_cap = calc_capacity(w, h, 4)
    rgb_cap = calc_capacity(w, h, 3)
    diff = rgba_cap - rgb_cap
    pct_reduction = (diff / rgba_cap) * 100 if rgba_cap else 0
    print(f"{label:<18} {f'{w}x{h}':<14} {f'{rgba_cap:,} bytes':<22} {f'{rgb_cap:,} bytes':<22} -{pct_reduction:.1f}% ({diff:,} B)")

# 2. Experimental Code Comparison on compay_logo.png
print("\n 2. Experimental Verification: Alpha Channel Preservation ")
PAYLOAD = "TARGET:192.168.1.50"
payload_bytes = PAYLOAD.encode("utf-8") + b"\x00"  # 20 bytes

# Method A: RGBA Embedding (Modifies R, G, B, and A)
# 4 bits per pixel -> 2 pixels per byte
with Image.open(LOGO) as img:
    rgba_pixels = list(img.convert("RGBA").getdata())

# Count how many Alpha values change under RGBA method
rgba_modified_alpha = 0
for byte_idx, b in enumerate(payload_bytes):
    bits = format(b, "08b")
    # First pixel gets bits 0..3 (R, G, B, A)
    orig_p1 = rgba_pixels[byte_idx * 2]
    target_a1 = (orig_p1[3] & 254) if bits[3] == "0" else (orig_p1[3] | 1)
    if target_a1 != orig_p1[3]:
        rgba_modified_alpha += 1
    
    # Second pixel gets bits 4..7 (R, G, B, A)
    orig_p2 = rgba_pixels[byte_idx * 2 + 1]
    target_a2 = (orig_p2[3] & 254) if bits[7] == "0" else (orig_p2[3] | 1)
    if target_a2 != orig_p2[3]:
        rgba_modified_alpha += 1

print("[Method A: Supplied RGBA Algorithm]")
print("  Total channels used per pixel : 4 (Red, Green, Blue, Alpha)")
print(f"  Pixels required for payload   : {len(payload_bytes) * 2} pixels (2 pixels per byte)")
print(f"  Alpha channel bits modified   : {rgba_modified_alpha} bits flipped in opacity channel")
print("  Alpha channel integrity       : COMPROMISED (Introduces noise into alpha bitplane)")

# Method B: RGB-Only Embedding (Leaves Alpha 100% untouched)
# 3 bits per pixel -> 8 bits requires 3 pixels (3+3+2 bits)
print("\n[Method B: RGB-Only Alternative Design]")
print("  Total channels used per pixel : 3 (Red, Green, Blue only)")
pixels_needed_rgb = (len(payload_bytes) * 8 + 2) // 3
print(f"  Pixels required for payload   : {pixels_needed_rgb} pixels (approx. 2.67 pixels per byte)")
print("  Alpha channel bits modified   : 0 bits (100% preserved)")
print("  Alpha channel integrity       : PERFECT (Zero noise in alpha bitplane)")
