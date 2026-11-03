import os
import sys
import io
import contextlib
from pathlib import Path
from PIL import Image, PngImagePlugin

WORK_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\.agents\teamwork\m2_auditor_1")
MUTATION_DIR = WORK_DIR / "temp_mutation"
MUTATION_DIR.mkdir(parents=True, exist_ok=True)

# Create synthetic mutated image for Brain.png
target_img = MUTATION_DIR / "Brain.png"
img = Image.new("RGB", (100, 100), color="blue")
meta = PngImagePlugin.PngInfo()
meta.add_text("Software", "RECON: Synthetic mutation payload for forensic audit test 98765")
img.save(target_img, pnginfo=meta)

# Run extraction logic from Cell 26 (code cell 12)
captured_stdout = io.StringIO()
kernel_globals = {
    "image_dir": MUTATION_DIR,
    "Image": Image,
}

code = """
image_path = image_dir / "Brain.png"
with Image.open(image_path) as img:
    secret = img.info.get("Software")
    print("Found in PNG text chunk 'Software':", secret)
"""

with contextlib.redirect_stdout(captured_stdout):
    exec(code, kernel_globals)

result = captured_stdout.getvalue().strip()
print("Mutation test result:")
print(result)

if "Synthetic mutation payload for forensic audit test 98765" in result:
    print("[PASS] Genuine dynamic extraction confirmed! Code extracts live file contents.")
else:
    print("[FAIL] Code failed to reflect mutated payload!")
