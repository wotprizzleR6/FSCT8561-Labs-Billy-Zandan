"""
Direct Binary PNG Chunk Parser and Raw Inspection Tool
"""
import struct
import zlib
from pathlib import Path

IMAGES_DIR = Path(r"c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images")

def inspect_png(png_path: Path):
    print(f"\n=================== {png_path.name} ===================")
    with open(png_path, "rb") as f:
        sig = f.read(8)
        assert sig == b"\x89PNG\r\n\x1a\n", "Not a valid PNG!"
        
        while True:
            chunk_len_bytes = f.read(4)
            if not chunk_len_bytes or len(chunk_len_bytes) < 4:
                break
            chunk_len = struct.unpack(">I", chunk_len_bytes)[0]
            chunk_type = f.read(4).decode("latin-1")
            chunk_data = f.read(chunk_len)
            crc = f.read(4)
            
            print(f"Chunk: {chunk_type}, Length: {chunk_len}")
            
            if chunk_type == "tEXt":
                parts = chunk_data.split(b"\x00", 1)
                keyword = parts[0].decode("latin-1")
                text = parts[1].decode("latin-1") if len(parts) > 1 else ""
                print(f"  [tEXt] Keyword: {keyword!r}, Text: {text!r}")
            elif chunk_type == "zTXt":
                parts = chunk_data.split(b"\x00", 1)
                keyword = parts[0].decode("latin-1")
                rest = parts[1]
                comp_method = rest[0]
                compressed_data = rest[1:]
                decompressed = zlib.decompress(compressed_data).decode("latin-1")
                print(f"  [zTXt] Keyword: {keyword!r}, Text: {decompressed!r}")
            elif chunk_type == "iTXt":
                parts = chunk_data.split(b"\x00", 1)
                keyword = parts[0].decode("utf-8", errors="replace")
                rest = parts[1]
                comp_flag = rest[0]
                comp_method = rest[1]
                sub_parts = rest[2:].split(b"\x00", 2)
                lang_tag = sub_parts[0].decode("ascii", errors="replace")
                trans_key = sub_parts[1].decode("utf-8", errors="replace")
                text_bytes = sub_parts[2]
                if comp_flag == 1:
                    text = zlib.decompress(text_bytes).decode("utf-8", errors="replace")
                else:
                    text = text_bytes.decode("utf-8", errors="replace")
                print(f"  [iTXt] Keyword: {keyword!r}, Text: {text[:100]!r} (total {len(text)} chars)")
            elif chunk_type == "eXIf":
                print(f"  [eXIf] Raw bytes ({len(chunk_data)}): {chunk_data[:50]!r}...")

if __name__ == "__main__":
    for img in sorted(IMAGES_DIR.glob("*.png")):
        inspect_png(img)
