import struct
import zlib
from pathlib import Path

img_dir = Path(r'c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images')

for img_path in sorted(img_dir.glob('*.png')):
    print('========================================')
    print('FILE:', img_path.name)
    with open(img_path, 'rb') as f:
        sig = f.read(8)
        assert sig == b'\x89PNG\r\n\x1a\n', 'Not a valid PNG'
        chunks = []
        while True:
            length_bytes = f.read(4)
            if not length_bytes or len(length_bytes) < 4:
                break
            length = struct.unpack('>I', length_bytes)[0]
            chunk_type = f.read(4).decode('latin1', errors='replace')
            data = f.read(length)
            crc = f.read(4)
            chunks.append((chunk_type, length, data))
            if chunk_type == 'IEND':
                break

    for ctype, clen, cdata in chunks:
        if ctype in ('tEXt', 'zTXt', 'iTXt', 'eXIf'):
            print(f'  Chunk: {ctype}, Length: {clen}')
            if ctype == 'tEXt':
                parts = cdata.split(b'\x00', 1)
                keyword = parts[0].decode('latin1', errors='replace')
                text = parts[1].decode('latin1', errors='replace') if len(parts) > 1 else ''
                print(f'    [tEXt] Keyword: {keyword!r}, Text: {text!r}')
            elif ctype == 'zTXt':
                parts = cdata.split(b'\x00', 2)
                keyword = parts[0].decode('latin1', errors='replace')
                comp_method = parts[1][0] if len(parts) > 1 and len(parts[1]) > 0 else None
                decompressed = zlib.decompress(parts[2]) if len(parts) > 2 else b''
                print(f'    [zTXt] Keyword: {keyword!r}, Text: {decompressed.decode("latin1", errors="replace")!r}')
            elif ctype == 'iTXt':
                # keyword\0 comp_flag comp_method lang_tag\0 trans_key\0 text
                null1 = cdata.find(b'\x00')
                keyword = cdata[:null1].decode('latin1', errors='replace')
                comp_flag = cdata[null1+1]
                comp_method = cdata[null1+2]
                rest = cdata[null1+3:]
                null2 = rest.find(b'\x00')
                lang = rest[:null2].decode('latin1', errors='replace')
                rest2 = rest[null2+1:]
                null3 = rest2.find(b'\x00')
                trans_key = rest2[:null3].decode('utf-8', errors='replace')
                text_bytes = rest2[null3+1:]
                if comp_flag == 1:
                    text_bytes = zlib.decompress(text_bytes)
                text = text_bytes.decode('utf-8', errors='replace')
                print(f'    [iTXt] Keyword: {keyword!r}, Comp: {comp_flag}, Lang: {lang!r}, TransKey: {trans_key!r}')
                print(f'           Text preview: {text[:200]!r}')
                if 'MakerNote' in text or 'PERSIST' in text or 'VULN' in text or 'RECON' in text or 'EXPLOIT' in text or 'LATERAL' in text or 'EXFIL' in text:
                    print(f'           MATCH IN iTXt TEXT!')
                    for line in text.splitlines():
                        if any(k in line for k in ('MakerNote', 'PERSIST', 'VULN', 'RECON', 'EXPLOIT', 'LATERAL', 'EXFIL')):
                            print(f'             Line: {line.strip()}')
            elif ctype == 'eXIf':
                print(f'    [eXIf] Raw bytes ({clen} bytes): {cdata[:50]!r}...')
        elif ctype not in ('IDAT', 'IHDR', 'IEND', 'sRGB', 'gAMA', 'pHYs'):
            print(f'  Other Chunk: {ctype}, Length: {clen}')
