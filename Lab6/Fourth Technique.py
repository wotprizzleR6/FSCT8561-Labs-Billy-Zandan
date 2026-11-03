import base64
from pathlib import Path
from PIL import Image

image_path = Path("Images") / "Music.png"

with Image.open(image_path) as img:
    raw_val = img.info.get("Copyright")
    print(f"Suspicious metadata field: Copyright")
    print(f"Raw Value: {raw_val}")
    
    # Validation: Length is multiple of 4, character set validation
    if len(raw_val) % 4 == 0:
        try:
            decoded_bytes = base64.b64decode(raw_val, validate=True)
            decoded_text = decoded_bytes.decode("utf-8")
            print(f"Decoded Plaintext: {decoded_text}")
        except Exception as err:
            print(f"Decoding failed: {err}")