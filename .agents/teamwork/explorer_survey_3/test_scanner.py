import csv
import base64
import re
import sys
from pathlib import Path
from PIL import Image, ExifTags

sys.stdout.reconfigure(encoding='utf-8')

image_dir = Path(r'c:\Users\BillyZ\Desktop\FSCT8561-Labs-Billy-Zandan\Lab6\Images')
results = []

def is_base64(s):
    if not isinstance(s, str) or len(s) < 8 or len(s) % 4 != 0:
        return False, ''
    if not re.match(r'^[A-Za-z0-9+/]+={0,2}$', s.strip()):
        return False, ''
    try:
        decoded = base64.b64decode(s.strip()).decode('utf-8')
        if any(c.isprintable() for c in decoded) and len(decoded) > 4:
            return True, decoded
    except Exception:
        pass
    return False, ''

for img_path in sorted(image_dir.glob('*.png')):
    with Image.open(img_path) as img:
        filename = img_path.name
        img_format = img.format
        suspected_field = ''
        encoding = 'None'
        risk_score = 0
        reasons = []
        covert_content = ''
        all_fields = []

        # 1. Check EXIF top-level
        exif = img.getexif()
        for tag_id, val in exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            all_fields.append(f'EXIF:{tag_name}')
            b64_ok, b64_dec = is_base64(str(val))
            if b64_ok and any(kwd in b64_dec for kwd in ['RECON', 'VULN', 'EXPLOIT', 'PERSIST', 'LATERAL', 'EXFIL']):
                suspected_field = f'EXIF:{tag_name}'
                encoding = 'Base64'
                covert_content = b64_dec
            elif any(kwd in str(val) for kwd in ['RECON', 'VULN', 'EXPLOIT', 'PERSIST', 'LATERAL', 'EXFIL', 'Mimikatz', 'CVE', 'SQL Injection']):
                suspected_field = f'EXIF:{tag_name}'
                encoding = 'Plain text'
                covert_content = str(val)

        # Check EXIF sub-IFDs
        for ifd_id in (ExifTags.IFD.Exif, ExifTags.IFD.GPSInfo):
            try:
                sub_ifd = exif.get_ifd(ifd_id)
                for tag_id, val in sub_ifd.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    all_fields.append(f'EXIF_IFD:{tag_name}')
                    val_str = ''
                    if isinstance(val, bytes):
                        if val.startswith(b'ASCII\x00\x00\x00'):
                            val_str = val[8:].decode('utf-8', errors='replace')
                            cur_enc = 'ASCII (null-prefixed)'
                        else:
                            val_str = val.decode('utf-8', errors='replace')
                            cur_enc = 'Binary/Raw'
                    else:
                        val_str = str(val)
                        cur_enc = 'Plain text'

                    if any(kwd in val_str for kwd in ['RECON', 'VULN', 'EXPLOIT', 'PERSIST', 'LATERAL', 'EXFIL', 'CVE']):
                        suspected_field = f'EXIF_IFD:{tag_name}'
                        encoding = cur_enc
                        covert_content = val_str
            except Exception:
                pass

        # 2. Check PNG info chunks (tEXt)
        for k, v in img.info.items():
            if k in ('exif', 'XML:com.adobe.xmp', 'xmp'):
                continue
            all_fields.append(f'PNG:{k}')
            b64_ok, b64_dec = is_base64(str(v))
            if b64_ok and any(kwd in b64_dec for kwd in ['RECON', 'VULN', 'EXPLOIT', 'PERSIST', 'LATERAL', 'EXFIL']):
                suspected_field = f'PNG:{k}'
                encoding = 'Base64'
                covert_content = b64_dec
            elif any(kwd in str(v) for kwd in ['RECON', 'VULN', 'EXPLOIT', 'PERSIST', 'LATERAL', 'EXFIL', 'DNS', 'SQL Injection']):
                suspected_field = f'PNG:{k}'
                encoding = 'Plain text'
                covert_content = str(v)

        # 3. Check XMP metadata
        xmp_raw = img.info.get('XML:com.adobe.xmp') or img.info.get('xmp')
        if xmp_raw:
            all_fields.append('XMP')
            xmp_str = xmp_raw.decode('utf-8', errors='replace') if isinstance(xmp_raw, bytes) else str(xmp_raw)
            m = re.search(r'<exif:MakerNote>(.*?)</exif:MakerNote>', xmp_str, re.DOTALL)
            if m:
                suspected_field = 'XMP:exif:MakerNote'
                encoding = 'XML element'
                covert_content = m.group(1).strip()

        # Risk scoring logic:
        # Classroom heuristic:
        # +10 for confirmed covert-message field
        # +5 for suspicious encoded value requiring decoding/investigation
        # +5 for additional unusual metadata indicator
        if covert_content:
            risk_score += 10
            reasons.append(f'Confirmed covert payload detected in {suspected_field}')
            if encoding in ('Base64', 'ASCII (null-prefixed)'):
                risk_score += 5
                reasons.append(f'Obfuscated payload requiring decoding ({encoding})')
            elif 'XMP' in suspected_field or 'Software' in suspected_field:
                risk_score += 5
                reasons.append(f'Non-standard metadata field carrier ({suspected_field})')
            else:
                risk_score += 5
                reasons.append(f'Anomalous narrative metadata embedded in standard tag')

        results.append({
            'filename': filename,
            'format': img_format,
            'metadata_fields': ', '.join(dict.fromkeys(all_fields)),
            'suspected_field': suspected_field,
            'encoding': encoding,
            'risk_score': risk_score,
            'reason': '; '.join(reasons),
            'covert_content': covert_content
        })

for r in results:
    print(f"File: {r['filename']}")
    print(f"  Suspected Field: {r['suspected_field']}")
    print(f"  Encoding: {r['encoding']}")
    print(f"  Risk Score: {r['risk_score']}")
    print(f"  Reason: {r['reason']}")
    print(f"  Payload: {r['covert_content']}")
    print("-" * 50)
